"""M5 metadata export. Never opens share payloads, keys, or participant input.

The proof establishes metadata consistency, not confidential MPC execution or
arithmetic correctness, nor participant cryptographic approval/signatures.
"""
from __future__ import annotations
import base64
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engines/mpc"))
from room_state import canonical_json, room_state_from_dict
from analytics_contract import artifact_commitment, digest, KEY_EPOCH
from nn_contract import validate_evaluation_child

RECEIPT_DOMAIN = b"KRYPTROOM-TRANSITION-RECEIPT-V1\0"
CLAIM_DOMAIN = b"KRYPTROOM-STATE-PROOF-V1"
ID_DOMAIN = b"KRYPTROOM-STATE-PROOF-ID-V1\0"

def strict_load(path):
    path = Path(path)
    if path.suffix != ".json" or path.is_symlink():
        raise ValueError("Only explicit regular metadata JSON documents are accepted")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite JSON")))

def validate_schema(value, name):
    from jsonschema import Draft202012Validator, FormatChecker
    schema = strict_load(ROOT / "packages/manifests" / name)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)

def load_state(path):
    value = strict_load(path)
    state = room_state_from_dict(value)
    state.verify()
    # from_dict must not silently discard unknown fields or change semantics.
    if canonical_json(state.to_dict()) != canonical_json(value):
        raise ValueError("Noncanonical state structure")
    return state

def make_receipt(model, data, child, job):
    bindings = json.loads(child.transition.bindings_json)
    request = bindings["request"]
    validate_evaluation_child(child, model, data, job,
                              request["codeHash"], request["workflowHash"])
    value = {
        "version": "1", "proofDomain": "kryptroom.state-transition-proof.v1",
        "roomId": child.room_id, "transitionId": child.transition.id,
        "operator": "private_model_evaluation",
        "orderedParents": [{"stateId": s.id, "stateCommitment": s.commitment.value,
                            "policyHash": digest(s.policy.to_dict())} for s in (model, data)],
        "orderedInputs": [{"parentIndex": index, "artifactId": a.id,
                           "artifactCommitment": artifact_commitment(a, s.crypto_context)}
                          for index, s in enumerate((model, data)) for a in s.artifacts],
        "keyEpoch": KEY_EPOCH, "cryptoContextHash": digest(child.crypto_context.to_dict()),
        "codeHash": request["codeHash"], "workflowHash": request["workflowHash"],
        "requestedReveals": request["transition"]["requestedReveals"],
        "requestedRevealsHash": request["requestedRevealsHash"],
        "outputPolicyHash": digest(child.policy.to_dict()), "outputStateId": child.id,
        "orderedOutputs": [{"artifactId": a.id, "artifactCommitment": artifact_commitment(a, child.crypto_context)} for a in child.artifacts],
        "transitionCommitment": bindings["transitionCommitment"],
        "outputStateCommitment": child.commitment.value,
    }
    validate_schema(value, "transition-receipt.schema.json")
    return value

def receipt_hash(receipt):
    validate_schema(receipt, "transition-receipt.schema.json")
    return hashlib.sha256(RECEIPT_DOMAIN + canonical_json(receipt)).hexdigest()

def public_claim(receipt):
    return hashlib.sha256(CLAIM_DOMAIN).digest() + bytes.fromhex(receipt_hash(receipt))

def make_witness(model, data, child, receipt):
    values = [model.content_dict(), data.content_dict(), child.content_dict(), receipt]
    names = ["modelParentContentBase64", "dataParentContentBase64", "childContentBase64", "receiptCanonicalBase64"]
    return {"version": "1", **{name: base64.b64encode(canonical_json(v)).decode("ascii")
                              for name, v in zip(names, values, strict=True)}}

def proof_id(receipt_hash_hex, vkey, proof_hash):
    material = ID_DOMAIN + bytes.fromhex(receipt_hash_hex) + bytes.fromhex(vkey.removeprefix("0x")) + bytes.fromhex(proof_hash)
    return "stateproof-" + hashlib.sha256(material).hexdigest()[:32]
