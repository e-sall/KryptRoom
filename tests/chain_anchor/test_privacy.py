from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PrivacyTests(unittest.TestCase):
    def test_contract_has_only_the_opaque_commitment_payload(self):
        source = (ROOT / "chain/contracts/src/KryptRoomAnchorV1.sol").read_text()
        self.assertIn("anchor(bytes32 anchorCommitment)", source)
        self.assertIn("AnchorRecorded(bytes32 indexed anchorCommitment", source)
        for forbidden in (
            "roomId",
            "stateId",
            "transitionId",
            "artifact",
            "policy",
            "ciphertext",
            "proof.bin",
            "feature",
            "label",
            "weight",
            "mse",
        ):
            self.assertNotIn(forbidden, source)

    def test_m7_sources_contain_no_secret_or_generated_artifact(self):
        roots = [
            ROOT / "chain",
            ROOT / "engines/chain_anchor",
            ROOT / "tests/chain_anchor",
            ROOT / "packages/manifests",
        ]
        forbidden_suffixes = (
            ".pem",
            ".key",
            ".p12",
            ".pfx",
            ".share.enc",
            ".openfhe.bin",
            "proof.bin",
        )
        secret_patterns = re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----|"
            r"\bAKIA[0-9A-Z]{16}\b|\bghp_[A-Za-z0-9]{36}\b|"
            r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"
        )
        for root in roots:
            for path in root.rglob("*"):
                if not path.is_file() or path.name == "test_privacy.py":
                    continue
                relative = path.relative_to(ROOT).as_posix().lower()
                self.assertFalse(relative.endswith(forbidden_suffixes), relative)
                if path.suffix in {".py", ".sol", ".json", ".md", ".yml", ".toml"}:
                    self.assertIsNone(secret_patterns.search(path.read_text()), relative)


if __name__ == "__main__":
    unittest.main()
