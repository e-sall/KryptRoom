from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engines.chain_anchor.commitment import EVIDENCE_NONE, ZERO32, anchor_commitment
from engines.chain_anchor.model import ChainAnchor, derive_anchor_id
from engines.chain_anchor.verifier import BASE_SEPOLIA_CHAIN_ID, verify_package_layer

M6_TEST = ROOT / "tests" / "fhe_state_transition" / "test_contract.py"
SPEC = importlib.util.spec_from_file_location("kryptroom_m6_contract_fixture", M6_TEST)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load the M6 contract fixture")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
Fixture = MODULE.Fixture
TEMP_ROOT = ROOT / ".tmp-m7" / "m6-state-only"
TEMP_ROOT.mkdir(parents=True, exist_ok=True)


class M6StateOnlyAnchorTests(unittest.TestCase):
    def test_s6_metadata_can_be_anchored_after_all_artifacts_are_gone(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp:
            fixture = Fixture(Path(temp))
            state = fixture.child.to_dict()
            local_files = [path for root in fixture.roots.values() for path in root.rglob("*")]
            self.assertTrue(any(path.is_file() for path in local_files))
        self.assertTrue(all(not path.exists() for path in local_files))

        subject_commitment = state["commitment"]["value"]
        commitment = anchor_commitment(
            output_state_commitment=subject_commitment,
            evidence_type=EVIDENCE_NONE,
        )
        contract = "0x" + "11" * 20
        transaction = "0x" + "22" * 32
        anchor = ChainAnchor(
            version="1",
            anchor_id=derive_anchor_id(
                chain_id=BASE_SEPOLIA_CHAIN_ID,
                contract_address=contract,
                transaction_hash=transaction,
                log_index=0,
            ),
            anchor_commitment=commitment,
            subject_type="ROOM_STATE_V1",
            subject_commitment=subject_commitment,
            evidence_type="NONE",
            evidence_commitment=ZERO32.hex(),
            room_id=state["roomId"],
            transition_id=state["transition"]["id"],
            output_state_id=state["id"],
            backend="base-op-stack",
            chain_id=BASE_SEPOLIA_CHAIN_ID,
            contract_address=contract,
            contract_runtime_code_hash="0x" + "33" * 32,
            transaction_hash=transaction,
            log_index=0,
            submitter="0x" + "44" * 20,
            block_number=1,
            block_hash="0x" + "55" * 32,
            block_timestamp="2026-10-19T00:00:00Z",
            created_at="2026-10-19T00:01:00Z",
        )
        result = verify_package_layer(anchor, state, None)
        self.assertEqual(result.anchor_commitment, commitment)
        self.assertFalse(result.m5_proof_validation_required)


if __name__ == "__main__":
    unittest.main()
