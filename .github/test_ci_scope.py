"""Synthetic filter tests. No crypto, containers, network, or transaction calls."""

from pathlib import Path
import subprocess
import unittest

from ci_scope import CONDITION, GATE, classify_event, requires_core, workflow_execution


OLD = "name: Test\non:\n  push:\n    branches: [dev]\n\njobs:\n  integration:\n    runs-on: ubuntu-latest\n    steps:\n      - run: real-core-command\n"
NEW = OLD.replace("jobs:\n", "jobs:\n" + GATE).replace(
    "  integration:\n", "  integration:\n" + CONDITION)


class ScopeTests(unittest.TestCase):
    def test_frontend_and_m8_docs(self):
        self.assertFalse(requires_core(
            ["apps/web/package-lock.json", "apps/web/src/page.tsx",
             "docs/m8/pr2/README.md", "PROJECT_CONTEXT.md"],
            lambda _: None, lambda _: None))

    def test_every_core_surface_and_unknown_path_runs(self):
        for path in ["engines/mpc/private_nn.py", "engines/zk/Cargo.lock",
                     "engines/psi/index.js", "nodes/krypt-node/foo.py",
                     "packages/manifests/room-state.schema.json",
                     "chain/contracts/src/Anchor.sol", "services/control-api/main.py",
                     "tests/privacy/example.test.mjs", "package.json",
                     "package-lock.json", "compose.private-join.yml",
                     "Dockerfile", "unknown-new-runtime-file", "docs/STATE_PROOF.md"]:
            with self.subTest(path=path):
                self.assertTrue(requires_core(
                    ["apps/web/src/page.tsx", path], lambda _: None, lambda _: None))

    def test_empty_diff_runs(self):
        self.assertTrue(requires_core([], lambda _: None, lambda _: None))

    def test_trigger_only_change_is_not_runtime_change(self):
        self.assertEqual(workflow_execution(OLD), workflow_execution(NEW))
        self.assertFalse(requires_core(
            [".github/workflows/private-nn.yml"], lambda _: OLD, lambda _: NEW))

    def test_workflow_runtime_and_security_changes_run(self):
        for replacement in [
            NEW.replace("real-core-command", "new-core-command"),
            NEW.replace("ubuntu-latest", "ubuntu-24.04"),
            NEW.replace("jobs:", "permissions:\n  contents: write\n\njobs:"),
            NEW.replace(CONDITION, "    if: false\n"),
            NEW.replace("steps:", "env:\n      PROTOCOL: OTHER\n    steps:"),
        ]:
            self.assertTrue(requires_core(
                [".github/workflows/private-nn.yml"], lambda _: OLD,
                lambda _: replacement))

    def test_workflow_add_delete_run(self):
        for before, after in [(None, OLD), (OLD, None)]:
            self.assertTrue(requires_core(
                [".github/workflows/new.yml"], lambda _: before, lambda _: after))

    def test_manual_event_always_runs(self):
        self.assertTrue(classify_event("workflow_dispatch", {}))
        self.assertTrue(classify_event("schedule", {}))

    def test_pr_uses_merge_base_and_complete_no_rename_diff(self):
        calls = []
        def git(*args):
            calls.append(args)
            return "a" * 40 if args[0] == "merge-base" else "apps/web/page.tsx\0"
        self.assertFalse(classify_event("pull_request", {
            "pull_request": {"base": {"sha": "b" * 40}, "head": {"sha": "c" * 40}}
        }, git))
        self.assertEqual(calls, [
            ("merge-base", "b" * 40, "c" * 40),
            ("diff", "--no-renames", "--name-only", "-z", "a" * 40, "c" * 40)])

    def test_new_branch_compares_dev_not_only_last_commit(self):
        calls = []
        def git(*args):
            calls.append(args)
            return "a" * 40 if args[0] == "merge-base" else "engines/mpc/file.py\0apps/web/file.tsx\0"
        self.assertTrue(classify_event("push", {
            "before": "0" * 40, "after": "c" * 40}, git))
        self.assertEqual(calls[0], ("merge-base", "origin/dev", "c" * 40))

    def test_push_uses_before_and_after(self):
        calls = []
        def git(*args):
            calls.append(args)
            return "apps/web/file.tsx\0"
        self.assertFalse(classify_event("push", {
            "before": "b" * 40, "after": "c" * 40}, git))
        self.assertEqual(calls[0][-2:], ("b" * 40, "c" * 40))

    def test_more_than_300_files_and_core_rename_are_not_hidden(self):
        paths = [f"apps/web/{i}.tsx" for i in range(500)]
        self.assertTrue(requires_core(
            paths + ["engines/mpc/deleted.py"], lambda _: None, lambda _: None))

    def test_missing_revision_is_an_error_not_frontend_success(self):
        def git(*_):
            raise subprocess.CalledProcessError(1, "git")
        with self.assertRaises(subprocess.CalledProcessError):
            classify_event("push", {"before": "0" * 40, "after": "c" * 40}, git)

    def test_repository_gate_and_job_conditions_remain_exact(self):
        root = Path(__file__).resolve().parent
        jobs = {
            "private-join.yml": "cryptographic-integration",
            "persistent-state.yml": "cryptographic-integration",
            "private-analytics.yml": "cryptographic-integration",
            "private-nn.yml": "cryptographic-integration",
            "fhe-state-transition.yml": "real-openfhe-bgv",
            "state-proof-acceptance.yml": "real-sp1-groth16-proof",
        }
        for filename, job in jobs.items():
            text = (root / "workflows" / filename).read_text()
            self.assertEqual(text.count(GATE), 1, filename)
            self.assertIn(f"  {job}:\n{CONDITION}", text)


if __name__ == "__main__":
    unittest.main()
