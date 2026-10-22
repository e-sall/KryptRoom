"""Synthetic filter tests. No crypto, containers, network, or transaction calls."""

from pathlib import Path
import hashlib
import json
import subprocess
import unittest

from ci_scope import (
    CONDITION, GATE, MIGRATION_FILES, MIGRATION_S1, MIGRATION_WORKFLOW,
    classify_event, requires_core, workflow_execution,
)


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


class ExactMigrationTests(unittest.TestCase):
    """Read-only tests against pinned, committed source blobs; never regenerate."""

    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.baseline = "2915b421180739897b8ffd754f8c228cee4b62d9"
        paths = set(MIGRATION_FILES) | set(MIGRATION_S1) | {MIGRATION_WORKFLOW}
        cls.before = {p: subprocess.check_output(
            ["git", "show", f"{cls.baseline}:{p}"], cwd=cls.root
        ).decode("utf-8") for p in paths}
        cls.after = {p: (cls.root / p).read_bytes().decode("utf-8").replace("\r\n", "\n")
                     for p in paths}

    def decision(self, extra=(), before=None, after=None, paths=None):
        return requires_core(
            list(MIGRATION_FILES) + list(extra) if paths is None else paths,
            (self.before if before is None else before).get,
            (self.after if after is None else after).get,
        )

    def test_exact_authorized_migration_and_trigger_only_pr(self):
        self.assertFalse(self.decision())
        before = dict(self.before)
        before[MIGRATION_WORKFLOW] = subprocess.check_output(
            ["git", "show", "acf5f262b03d6c0db3ff36b413f330b61f1181d2:" + MIGRATION_WORKFLOW],
            cwd=self.root,
        ).decode()
        self.assertFalse(self.decision(
            [MIGRATION_WORKFLOW, "apps/web/src/page.tsx", "docs/m8/pr2/CI-SCOPE.md"],
            before=before))

    def test_arbitrary_fixture_bytes_require_core(self):
        for path in MIGRATION_FILES:
            with self.subTest(path=path):
                self.assertTrue(self.decision(after={**self.after, path: self.after[path] + " "}))

    def test_additional_file_generator_code_relation_assertion_require_core(self):
        for path in [
            "tests/state_proof/fixtures/extra.json", "tests/state_proof/generate_fixture.py",
            "engines/zk/proof_receipt.py", "engines/zk/state-transition-proof/shared/src/lib.rs",
            "tests/state_proof/test_receipt.py", "engines/mpc/nn_contract.py",
            "packages/manifests/state-proof.schema.json", "tests/state_proof/requirements.txt",
            "package-lock.json",
        ]:
            with self.subTest(path=path):
                self.assertTrue(self.decision([path]))

    def test_policy_change_requires_core(self):
        path = "tests/state_proof/fixtures/S3_model.json"
        value = json.loads(self.after[path])
        value["policy"]["defaultReveal"] = "allow"
        self.assertTrue(self.decision(after={**self.after, path: json.dumps(value)}))

    def test_workflow_runtime_change_requires_core(self):
        altered = self.after[MIGRATION_WORKFLOW].replace("node-version: 22", "node-version: 24")
        self.assertNotEqual(altered, self.after[MIGRATION_WORKFLOW])
        self.assertTrue(self.decision([MIGRATION_WORKFLOW], after={
            **self.after, MIGRATION_WORKFLOW: altered}))

    def test_partial_deleted_or_wrong_baseline_fixture_requires_core(self):
        for path in MIGRATION_FILES:
            with self.subTest(path=path):
                self.assertTrue(self.decision(paths=[p for p in MIGRATION_FILES if p != path]))
                self.assertTrue(self.decision(after={**self.after, path: None}))
                self.assertTrue(self.decision(before={**self.before, path: self.before[path] + " "}))

    def test_s1_change_requires_core_even_if_omitted_from_supplied_paths(self):
        for path in MIGRATION_S1:
            self.assertEqual(self.before[path], self.after[path])
            self.assertTrue(self.decision(after={**self.after, path: self.after[path] + " "}))

    def test_exception_does_not_apply_to_subsequent_fixture_edits_or_rollback(self):
        self.assertTrue(self.decision(before=self.after))
        self.assertTrue(self.decision(before=self.after, after=self.before))

    def test_only_derived_hash_fields_changed_and_canonical_vectors_are_exact(self):
        changes = []

        def compare(a, b, path):
            self.assertEqual(type(a), type(b), path)
            if isinstance(a, dict):
                self.assertEqual(a.keys(), b.keys(), path)
                for key in a:
                    compare(a[key], b[key], path + "/" + key)
            elif isinstance(a, list):
                self.assertEqual(len(a), len(b), path)
                for i, (x, y) in enumerate(zip(a, b)):
                    compare(x, y, path + "/" + str(i))
            elif a != b:
                changes.append((path, a, b))

        for filename in MIGRATION_FILES:
            compare(json.loads(self.before[filename]), json.loads(self.after[filename]), filename)
        self.assertEqual(len(changes), 35)
        allowed = {"workflowHash", "stateCommitment", "outputStateCommitment", "transitionCommitment"}
        for path, old, new in changes:
            if path.endswith("/canonicalHex"):
                continue
            self.assertTrue(
                path.rsplit("/", 1)[-1] in allowed or path.endswith("/commitment/value")
                or ("/hashes.json/" in path and path.endswith("/sha256")), path)
            self.assertRegex(old, r"^[0-9a-f]{64}$")
            self.assertRegex(new, r"^[0-9a-f]{64}$")
        # Every other leaf is identical: codeHash, policies, CryptoContexts, artifact
        # identifiers/commitments, recipients, operators, lineage IDs and parameters.
        for snapshot in (self.before, self.after):
            for vector in json.loads(snapshot["tests/state_proof/fixtures/hashes.json"]):
                canonical = json.dumps(vector["value"], sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=False).encode()
                self.assertEqual(canonical.hex(), vector["canonicalHex"])
                self.assertEqual(hashlib.sha256(canonical).hexdigest(), vector["sha256"])
        for i in (1, 2, 3, 5):  # policy, context, artifact/context, output policy
            self.assertEqual(
                json.loads(self.before["tests/state_proof/fixtures/hashes.json"])[i],
                json.loads(self.after["tests/state_proof/fixtures/hashes.json"])[i])

    def test_documented_hash_inventory_matches_every_fixture_and_frozen_source(self):
        evidence = json.loads((self.root / "docs/m8/pr2/M5-FIXTURE-HASHES.json").read_text())
        self.assertFalse(evidence["newGroth16Proof"])
        self.assertEqual(evidence["baselineCommit"], self.baseline)
        count = 0
        for name, entry in evidence["fixtures"].items():
            path = "tests/state_proof/fixtures/" + name
            for label, snapshot in (("before", self.before), ("after", self.after)):
                self.assertEqual(hashlib.sha256(snapshot[path].encode()).hexdigest(),
                                 entry[label + "Sha256"])
                document = json.loads(snapshot[path])
                for change in entry["changedLeaves"]:
                    value = document
                    for part in change["pointer"].lstrip("/").split("/"):
                        value = value[int(part)] if isinstance(value, list) else value[part]
                    if change["pointer"].endswith("/canonicalHex"):
                        raw = bytes.fromhex(value)
                        self.assertEqual(len(raw), change[label + "ByteLength"])
                        self.assertEqual(hashlib.sha256(raw).hexdigest(), change[label + "Sha256"])
                    else:
                        self.assertEqual(value, change[label])
            count += len(entry["changedLeaves"])
        self.assertEqual(count, 35)
        for path, expected in evidence["unchangedSourceAndHistoricalReportsLfSha256"].items():
            raw = (self.root / path).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(hashlib.sha256(raw).hexdigest(), expected, path)


if __name__ == "__main__":
    unittest.main()
