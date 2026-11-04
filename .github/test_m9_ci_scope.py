"""Publication routing regressions. No dependency install, crypto or network execution."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from ci_scope import (
    M9_WORKFLOW, M9_WORKFLOW_HASHES, classify_paths, classify_scopes_event, requires_core,
)

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = (ROOT / ".github/fixtures/control-api-foundation.c99.yml").read_bytes().decode("utf-8").replace("\r\n", "\n")


class M9ScopeTests(unittest.TestCase):
    def flags(self, paths, before=None, after=None):
        return classify_paths(paths, (before or {}).get, (after or {}).get)

    def test_owned_m9_sources_dependencies_migrations_docs_and_security(self):
        for path in ["services/control-api/src/kryptroom_control/app.py",
                     "services/control-api/tests/test_foundation.py",
                     "services/control-api/migrations/versions/new.py",
                     "services/control-api/compose.yml", "services/control-api/pyproject.toml",
                     "services/control-api/uv.lock", "services/control-api/.gitattributes",
                     "docs/m9/pr1/SECURITY-REVIEW.md"]:
            self.assertEqual(self.flags([path]), {"core": False, "web": False, "m9": True}, path)

    def test_exact_workflow_addition_is_m9_only_and_hash_is_complete(self):
        scoped = (ROOT / ".github/fixtures/control-api-foundation.scoped.yml").read_bytes().decode("utf-8").replace("\r\n", "\n")
        self.assertEqual({hashlib.sha256(value.encode()).hexdigest() for value in [CANONICAL, scoped]},
                         M9_WORKFLOW_HASHES)
        for recipe in [CANONICAL, scoped]:
            self.assertEqual(self.flags([M9_WORKFLOW], after={M9_WORKFLOW: recipe}),
                             {"core": False, "web": False, "m9": True})
        self.assertEqual(self.flags([M9_WORKFLOW], {M9_WORKFLOW: CANONICAL}, {M9_WORKFLOW: scoped}),
                         {"core": False, "web": False, "m9": True})

    def test_arbitrary_missing_deleted_or_security_modified_m9_workflow_fails_closed(self):
        for old, new in [(None, None), (CANONICAL, None), (None, CANONICAL + "# extra\n"),
                         (None, CANONICAL.replace("contents: read", "contents: write")),
                         (CANONICAL, CANONICAL.replace("workflow_dispatch:", "# removed:")),
                         (CANONICAL, CANONICAL.replace("pip_audit", "echo audit-disabled")),
                         ("unknown previous recipe", CANONICAL)]:
            self.assertEqual(self.flags([M9_WORKFLOW], {M9_WORKFLOW: old}, {M9_WORKFLOW: new}),
                             {"core": True, "web": True, "m9": True})

    def test_m1_through_m7_changes_never_hide_behind_m9(self):
        for path in ["engines/psi/a.js", "nodes/krypt-node/a.py", "engines/mpc/join.py",
                     "engines/mpc/persistent_state.py", "engines/mpc/analytics.py",
                     "engines/mpc/nn.py", "engines/zk/proof.py", "engines/fhe/fhe.py",
                     "chain/contracts/src/KryptRoomAnchor.sol",
                     "tests/state_proof/fixtures/S4_eval.json",
                     "tests/state_proof/generate_fixture.py", "tests/chain_anchor/fixtures/vectors.json"]:
            with self.subTest(path=path):
                flags = self.flags(["services/control-api/README.md", path])
                self.assertTrue(flags["core"])
                self.assertTrue(flags["m9"])

    def test_shared_contracts_dependencies_policies_and_ci_are_conservative(self):
        for path in ["packages/manifests/room-state.schema.json", "packages/shared/new.json",
                     "SECURITY.md", "THREAT_MODEL.md", "infra/security-policy.yml",
                     ".github/ci_scope.py", ".github/test_ci_scope.py", ".github/test_m9_ci_scope.py",
                     ".github/workflows/ci-scope.yml", ".github/workflows/web-foundation.yml",
                     "unknown-new-runtime-file"]:
            self.assertEqual(self.flags([path]), {"core": True, "web": True, "m9": True}, path)
        for path in ["package.json", "package-lock.json"]:
            self.assertTrue(self.flags([path])["core"])

    def test_removing_manual_or_changing_generic_workflow_events_requires_core(self):
        path = ".github/workflows/private-nn.yml"
        old = "name: Test\non:\n  workflow_dispatch:\n  push:\n    branches: [dev]\njobs:\n  test:\n    steps:\n      - run: preserved-command\n"
        for new in [old.replace("  workflow_dispatch:\n", ""),
                    old.replace("branches: [dev]", "branches: [other]"),
                    old.replace("  push:\n", "  pull_request:\n")]:
            self.assertEqual(self.flags([path], {path: old}, {path: new}),
                             {"core": True, "web": True, "m9": True})

    def test_m8_only_mixed_m8_m9_and_core_m8(self):
        self.assertEqual(self.flags(["apps/web/src/app/page.tsx", "docs/m8/README.md"]),
                         {"core": False, "web": True, "m9": False})
        self.assertEqual(self.flags(["apps/web/package-lock.json", "services/control-api/uv.lock"]),
                         {"core": False, "web": True, "m9": True})
        self.assertEqual(self.flags(["apps/web/src/page.tsx", "engines/mpc/a.py"]),
                         {"core": True, "web": True, "m9": False})

    def test_generic_changelog_is_contextual_and_alone_is_explicit(self):
        metadata = ["CHANGELOG.md", "TODO.md", "docs/DECISIONS.md"]
        self.assertEqual(self.flags(metadata + ["services/control-api/README.md"]),
                         {"core": False, "web": False, "m9": True})
        self.assertEqual(self.flags(metadata), {"core": False, "web": True, "m9": True})

    def test_empty_manual_schedule_and_unknown_events_remain_full(self):
        self.assertEqual(self.flags([]), {"core": True, "web": True, "m9": True})
        for event in ["workflow_dispatch", "schedule", "future_event"]:
            self.assertEqual(classify_scopes_event(event, {}),
                             {"core": True, "web": True, "m9": True})

    def test_large_diff_core_rename_deletion_and_unknown_m9_path_remain_core(self):
        paths = [f"services/control-api/tests/test_{i}.py" for i in range(501)]
        for extra in ["engines/mpc/deleted.py", "services/control-api/unknown-runtime"]:
            self.assertTrue(self.flags(paths + [extra])["core"])

    def test_pr_and_new_branch_consider_the_complete_diff(self):
        calls = []
        def git(*args):
            calls.append(args)
            return "a" * 40 if args[0] == "merge-base" else "engines/mpc/a.py\0services/control-api/README.md\0"
        flags = classify_scopes_event("push", {"before": "0" * 40, "after": "c" * 40}, git)
        self.assertTrue(flags["core"])
        self.assertEqual(calls[0], ("merge-base", "origin/dev", "c" * 40))
        self.assertIn("--no-renames", calls[1])

    def test_cli_emits_all_flags_and_missing_revision_is_not_a_success(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p / "event.json").write_text("{}", encoding="utf-8")
            import os
            env = {**os.environ, "GITHUB_EVENT_PATH": str(p / "event.json"),
                   "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_OUTPUT": str(p / "out"),
                   "GITHUB_STEP_SUMMARY": str(p / "summary")}
            result = subprocess.run([sys.executable, str(ROOT / ".github/ci_scope.py")],
                                    env=env, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout), {"core": True, "web": True, "m9": True})
            self.assertEqual((p / "out").read_text().splitlines(),
                             ["core=true", "web=true", "m9=true"])
            (p / "event.json").write_text(json.dumps({"before": "bad", "after": "c" * 40}))
            env["GITHUB_EVENT_NAME"] = "push"
            self.assertNotEqual(subprocess.run([sys.executable, str(ROOT / ".github/ci_scope.py")],
                                              env=env, capture_output=True).returncode, 0)

    def test_original_frontend_and_m9_commands_remain_mandatory_when_applicable(self):
        def operations(text):
            return re.findall(r"^(?:      - |        )(uses|run): (.+)$", text, re.M)
        old_web = subprocess.check_output([
            "git", "show", "7fde54f86b8df11d162eb317414dc1d2f932b70a:.github/workflows/web-foundation.yml"
        ], cwd=ROOT).decode()
        new_web = (ROOT / ".github/workflows/web-foundation.yml").read_text(encoding="utf-8")
        added_web = {
            ("run", "python3 -m unittest discover -s .github -p 'test_*ci_scope.py' -v"),
            ("run", "python3 .github/ci_scope.py"),
            ("run", 'echo "Frontend checks not applicable; classification succeeded"'),
        }
        self.assertEqual([op for op in operations(new_web) if op not in added_web], operations(old_web))
        scoped = (ROOT / ".github/fixtures/control-api-foundation.scoped.yml").read_text(encoding="utf-8")
        added_m9 = {("run", "python3 ../../.github/ci_scope.py"),
                    ("run", 'echo "M9 checks not applicable; classification succeeded"')}
        self.assertEqual([op for op in operations(scoped) if op not in added_m9], operations(CANONICAL))
        for text, key in [(new_web, "web"), (scoped, "m9")]:
            self.assertNotIn("paths:", text)
            self.assertIn("workflow_dispatch:", text)
            self.assertNotIn("continue-on-error", text)
            self.assertNotIn("if: false", text)
            steps = re.split(r"(?=^      - )", text, flags=re.M)[1:]
            for step in steps:
                ops = operations(step)
                if not ops or "actions/checkout@" in ops[0][1] or ops[0] in added_web | added_m9:
                    continue
                if "actions/upload-artifact@" in ops[0][1] or "Remove disposable" in step:
                    self.assertIn(f"if: always() && steps.scope.outputs.{key} == 'true'", step)
                else:
                    self.assertIn(f"if: steps.scope.outputs.{key} == 'true'", step)

    def test_unique_classification_and_foundation_contexts_are_never_path_filtered(self):
        policy = (ROOT / ".github/workflows/ci-scope.yml").read_text(encoding="utf-8")
        web = (ROOT / ".github/workflows/web-foundation.yml").read_text(encoding="utf-8")
        self.assertIn("  ci-scope-classification:", policy)
        self.assertIn("  foundation:", web)
        for text in [policy, web]:
            self.assertNotIn("paths:", text)
            self.assertIn("contents: read", text)
            self.assertIn("persist-credentials: false", text)
            self.assertIn("fetch-depth: 0", text)
            self.assertIn("python3 .github/ci_scope.py", text)


if __name__ == "__main__":
    unittest.main()
