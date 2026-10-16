import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engines/zk"))
from proof_receipt import *

FIXTURES = Path(__file__).parent / "fixtures"

def fixture():
    return tuple(load_state(FIXTURES / f"{s}.json") for s in ("S3_model", "S1", "S4_eval"))

class ReceiptTests(unittest.TestCase):
    def test_existing_m4_validation_and_receipt(self):
        states = fixture()
        job = strict_load(ROOT / "demos/cancer-collaboration/m4/private-nn-job.json")
        self.assertEqual(make_receipt(*states, job), strict_load(FIXTURES / "receipt.json"))

    def test_domains_and_claim(self):
        r = strict_load(FIXTURES / "receipt.json")
        self.assertEqual(RECEIPT_DOMAIN, b"KRYPTROOM-TRANSITION-RECEIPT-V1\x00")
        self.assertEqual(CLAIM_DOMAIN, b"KRYPTROOM-STATE-PROOF-V1")
        self.assertEqual(ID_DOMAIN, b"KRYPTROOM-STATE-PROOF-ID-V1\x00")
        self.assertEqual(len(public_claim(r)), 64)
        self.assertEqual(public_claim(r)[32:].hex(), receipt_hash(r))

    def test_golden_canonical_hashes(self):
        for v in strict_load(FIXTURES / "hashes.json"):
            self.assertEqual(canonical_json(v["value"]).hex(), v["canonicalHex"])
            self.assertEqual(digest(v["value"]), v["sha256"])

    def test_canonical_reordering_and_arrays(self):
        a = {"z": 42, "é": "\n\t\u0001", "a": False}
        self.assertEqual(canonical_json(a), canonical_json(dict(reversed(list(a.items())))))
        self.assertEqual(canonical_json(json.loads(json.dumps(a, indent=2))), canonical_json(a))
        self.assertNotEqual(digest([1, 2]), digest([2, 1]))

    def test_receipt_schema_closed(self):
        original = strict_load(FIXTURES / "receipt.json")
        for key in original:
            for mode in ("missing", "null"):
                v = copy.deepcopy(original)
                if mode == "missing": del v[key]
                else: v[key] = None
                with self.subTest(key=key, mode=mode), self.assertRaises(Exception):
                    validate_schema(v, "transition-receipt.schema.json")
        v = {**original, "extra": True}
        with self.assertRaises(Exception): validate_schema(v, "transition-receipt.schema.json")

    def test_order_and_exact_artifact_names(self):
        original = strict_load(FIXTURES / "receipt.json")
        for field in ("orderedParents", "orderedInputs"):
            v = copy.deepcopy(original); v[field].reverse()
            with self.assertRaises(Exception): validate_schema(v, "transition-receipt.schema.json")

    def test_parent_content_hashes_are_exact_python_bytes(self):
        m, d, c = fixture()
        r = strict_load(FIXTURES / "receipt.json")
        for s, expected in ((m,r["orderedParents"][0]["stateCommitment"]),(d,r["orderedParents"][1]["stateCommitment"]),(c,r["outputStateCommitment"])):
            self.assertEqual(hashlib.sha256(canonical_json(s.content_dict())).hexdigest(), expected)

    def test_witness_metadata_only_and_temporary(self):
        m,d,c = fixture(); r = strict_load(FIXTURES / "receipt.json")
        w = make_witness(m,d,c,r)
        self.assertEqual(set(w), {"version","modelParentContentBase64","dataParentContentBase64","childContentBase64","receiptCanonicalBase64"})
        for key,value in w.items():
            if key != "version": self.assertIsInstance(json.loads(base64.b64decode(value)), dict)
        self.assertFalse(list(FIXTURES.glob("*witness*")))

    def test_explicit_metadata_paths_only(self):
        for p in ("model.share.enc", "keys/room-state-v1.key", "patient.csv"):
            with self.assertRaises(ValueError): strict_load(p)

    def test_proof_id(self):
        args = ("0"*64,"0x"+"1"*64,"2"*64)
        self.assertEqual(proof_id(*args),proof_id(*args))
        self.assertNotEqual(proof_id(*args),proof_id("3"*64,*args[1:]))

    def test_source_has_no_secret_io(self):
        source = (ROOT / "engines/zk/state-transition-proof/host/src/main.rs").read_text()
        for bad in ("EncryptedShareReader", "load_local_dataset", "SecretFlow", "from_env()", ".mock()", ".network()"):
            self.assertNotIn(bad, source)
        self.assertIn(".cpu().build()",source)
        self.assertIn("fs::remove_file(path)",source)

    def test_public_documents_exclude_private_metadata(self):
        r = strict_load(FIXTURES / "receipt.json")
        public = canonical_json(r)
        for bad in (b"local://", b"ciphertexts", b"sizeBytes", b"authorizedReveals", b"backendVersion", b"lab-a\"", b"lab-b\"", b"p1\"", b"room-state-v1.key"):
            self.assertNotIn(bad,public)
        self.assertNotIn(b"MSE",public_claim(r))

if __name__ == "__main__": unittest.main()
