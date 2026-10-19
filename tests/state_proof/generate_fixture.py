"""Generate deterministic metadata-only golden vectors using unchanged M4 builders.

These are synthetic ciphertext DESCRIPTORS, not a claim that MPC executed for
this fixture. M4's independent workflow tests actual confidential execution.
No witness, payload, key, CSV, trained value, or private MSE is generated here.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engines/zk"))
sys.path.insert(0, str(ROOT / "tests/private_nn"))
from test_contract import s1, s3, s4, job
from nn_contract import bind_training_request, bind_evaluation_request, source_hash, workflow_hash
from room_state import canonical_json
from analytics_contract import digest, artifact_commitment
from proof_receipt import make_receipt

def generate(destination):
    destination.mkdir(parents=True, exist_ok=True)
    data = s1()
    code = source_hash(ROOT / "engines/mpc")
    flow = workflow_hash(ROOT / ".github/workflows/private-nn.yml")
    model = s3(data, bind_training_request(data, job(), code, flow))
    request = bind_evaluation_request(model, data, job(), code, flow)
    child = s4(model, data, request)
    receipt = make_receipt(model, data, child, job())
    for state in (data, model, child):
        (destination / (state.id + ".json")).write_bytes(canonical_json(state.to_dict()))
        (destination / (state.id + ".content.json")).write_bytes(canonical_json(state.content_dict()))
    (destination / "receipt.json").write_bytes(canonical_json(receipt))
    values = [receipt, model.policy.to_dict(), data.crypto_context.to_dict(),
              {"artifact": model.artifacts[0].to_dict(), "cryptoContext": model.crypto_context.to_dict()},
              request, child.policy.to_dict(),
              {k:v for k,v in json.loads(child.transition.bindings_json).items() if k != "transitionCommitment"},
              child.content_dict()]
    vectors = [{"value": v, "canonicalHex": canonical_json(v).hex(), "sha256": digest(v)} for v in values]
    (destination / "hashes.json").write_bytes(canonical_json(vectors))

if __name__ == "__main__":
    generate(Path(__file__).parent / "fixtures")
