"""Authoritative real CPU Groth16 acceptance. Never reads collaborative payloads."""
import argparse
import copy
import datetime
import json
import os
import shutil
import subprocess
import struct
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engines/zk"))
from proof_receipt import *

F = Path(__file__).parent / "fixtures"
def run(command, success=True, env=None, cwd=None):
    p = subprocess.run([str(v) for v in command], capture_output=True, text=True, env=env, cwd=cwd)
    # Never print witness or captured guest/prover diagnostics containing witness.
    if (p.returncode == 0) != success:
        forbidden = ("local://", "authorizedReveals", "ContentBase64", "ciphertexts", "artifactRef")
        for line in p.stderr.splitlines()[-30:]:
            if any(x in line.lower() for x in ("error:", "failed", "memory", "killed", "sigkill", "panic")) and not any(x in line for x in forbidden):
                print(line[:500], file=sys.stderr)
        raise RuntimeError(f"Unexpected status {p.returncode} for {Path(str(command[0])).name} {command[1]}")
    return p.stdout

def dump(path,value): path.write_bytes(canonical_json(value))

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--binary",required=True);parser.add_argument("--output-root",required=True);parser.add_argument("--execute-only",action="store_true");args=parser.parse_args()
    binary=Path(args.binary).resolve()
    assert not list(F.rglob("*.share.enc")) and not list(F.rglob("*.key")) and not list(F.rglob("*.csv"))
    model,data,child=(load_state(F/f"{s}.json") for s in ("S3_model","S1","S4_eval"))
    job=strict_load(ROOT/"demos/cancer-collaboration/m4/private-nn-job.json")
    receipt=make_receipt(model,data,child,job);witness=make_witness(model,data,child,receipt)
    with tempfile.TemporaryDirectory(prefix="kryptroom-m5-private-") as tmp:
        temp=Path(tmp)
        # Cross-language golden vectors execute in the independent Rust implementation.
        for i,v in enumerate(strict_load(F/"hashes.json")):
            p=temp/f"golden-{i}.json";dump(p,v["value"])
            assert run([binary,"hash","--json",p]).strip()==v["sha256"]
        # Class A: mutate committed relation, then recompute parent/child content
        # hashes where needed. Authorization must be checked, not merely hashes.
        mutations=[("unauthorized-reveal",lambda d:d["policy"]["authorizedReveals"].pop()),
                   ("unauthorized-operator",lambda d:d["policy"]["allowedOperators"].remove("private_model_evaluation")),
                   ("wrong-context",lambda d:d["cryptoContext"].update(field="FM64")),
                   ("wrong-input",lambda d:d["artifacts"][0].update(includesIdentifiers=True)),
                   ("wrong-recipients",lambda d:d["policy"]["authorizedReveals"][-1].update(recipients=["ui"]))]
        for name,change in mutations:
            w=copy.deepcopy(witness);d=json.loads(base64.b64decode(w["dataParentContentBase64"]));change(d)
            rr=copy.deepcopy(receipt);rr["orderedParents"][1]["stateCommitment"]=digest(d);rr["orderedParents"][1]["policyHash"]=digest(d["policy"])
            w["dataParentContentBase64"]=base64.b64encode(canonical_json(d)).decode();w["receiptCanonicalBase64"]=base64.b64encode(canonical_json(rr)).decode()
            p=temp/f"witness-{name}.json";dump(p,w)
            run([binary,"execute","--witness",p],success=False)
            p.unlink(missing_ok=True)
        p=temp/"witness-valid.json";dump(p,witness)
        if args.execute_only:
            run([binary,"execute","--witness",p]);assert not p.exists();print("M5_GUEST_RELATION_TESTS_PASSED");return
        started=time.monotonic()
        output=run([binary,"prove","--witness",p,"--output-root",args.output_root,"--created-at",datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")])
        assert not p.exists()
        metrics=json.loads(output.strip().splitlines()[-1]);directory=Path(metrics["proofDirectory"])
        rpath=directory/"receipt.json";spath=directory/"state-proof.json";ppath=directory/"proof.bin"
        stateproof=strict_load(spath);validate_schema(stateproof,"state-proof.schema.json")
        assert stateproof["receiptHash"]==receipt_hash(receipt)
        assert stateproof["publicValuesSha256"]==hashlib.sha256(public_claim(receipt)).hexdigest()
        standalone=temp/"standalone-public";standalone.mkdir()
        for source in (rpath,spath,ppath,binary):shutil.copy2(source,standalone/source.name)
        assert set(x.name for x in standalone.iterdir())=={"receipt.json","state-proof.json","proof.bin",binary.name}
        verifier_env={**os.environ,"DOCKER_HOST":"tcp://127.0.0.1:9",
                      "HTTP_PROXY":"http://127.0.0.1:9","HTTPS_PROXY":"http://127.0.0.1:9",
                      "ALL_PROXY":"http://127.0.0.1:9","NO_PROXY":""}
        def verify(r=rpath,s=spath,p=ppath,extra=(),success=True,expect=True):
            expectations=["--expect-room",receipt["roomId"],"--expect-transition",receipt["transitionId"]] if expect else []
            return run([binary,"verify","--receipt",r,"--state-proof",s,"--proof",p,*expectations,*extra],success,env=verifier_env,cwd=standalone)
        # A separate process with only PUBLIC documents, no metadata/witness cwd.
        verify_started=time.monotonic()
        assert "VERIFIED" in run([standalone/binary.name,"verify","--receipt","receipt.json","--state-proof","state-proof.json","--proof","proof.bin","--expect-room",receipt["roomId"],"--expect-transition",receipt["transitionId"]],env=verifier_env,cwd=standalone)
        metrics["standaloneVerificationSeconds"]=time.monotonic()-verify_started
        # Class B: tampering public receipts without regenerating proof.
        edits={"roomId":"another-room","transitionId":"another-transition","operator":"private_nn_training","outputStateCommitment":"0"*64,"requestedReveals":["model.evaluation.rmse"],"codeHash":"1"*64,"workflowHash":"2"*64,"transitionCommitment":"3"*64,"outputStateId":"another-state","keyEpoch":"wrong","cryptoContextHash":"4"*64,"requestedRevealsHash":"5"*64,"outputPolicyHash":"6"*64}
        for key,value in edits.items():
            rr=copy.deepcopy(receipt);rr[key]=value;p=temp/"receipt-tampered.json";dump(p,rr);verify(r=p,success=False)
        # Rebind all untrusted outer metadata too; exact proof public values must
        # reject another room/transition/S4 without relying on caller expectations.
        for key,value in (("roomId","another-room"),("transitionId","another-transition"),("outputStateCommitment","a"*64),("codeHash","b"*64),("workflowHash","c"*64)):
            rr=copy.deepcopy(receipt);rr[key]=value;p=temp/"receipt-rebound.json";dump(p,rr)
            ss=copy.deepcopy(stateproof)
            for field in ("roomId","transitionId","outputStateId","outputStateCommitment","transitionCommitment"):ss[field]=rr[field]
            ss["receiptHash"]=receipt_hash(rr);ss["proofId"]=proof_id(ss["receiptHash"],ss["programVKey"],ss["proofArtifact"]["sha256"])
            ss["proofArtifact"]["uri"]=f'proofs/rooms/{ss["roomId"]}/transitions/{ss["transitionId"]}/{ss["proofId"]}/proof.bin'
            s=temp/"state-proof-rebound.json";dump(s,ss);verify(r=p,s=s,success=False,expect=False)
        for field,key in (("orderedParents","stateCommitment"),("orderedParents","stateId"),("orderedParents","policyHash"),("orderedInputs","artifactCommitment"),("orderedInputs","artifactId"),("orderedOutputs","artifactCommitment"),("orderedOutputs","artifactId")):
            rr=copy.deepcopy(receipt);rr[field][0][key]="0"*64;p=temp/"receipt-tampered.json";dump(p,rr);verify(r=p,success=False)
        for field in ("orderedParents","orderedInputs"):
            rr=copy.deepcopy(receipt);rr[field].reverse();p=temp/"receipt-tampered.json";dump(p,rr);verify(r=p,success=False)
        # Class C: immutable proof metadata and program identity.
        for field,value in {"version":"2","proofSystemVersion":"6.8.1","programVersion":"other","programVKey":"0x"+"0"*64,"elfSha256":"0"*64,"receiptHash":"0"*64}.items():
            ss=copy.deepcopy(stateproof);ss[field]=value
            if field=="programVKey":
                ss["proofId"]=proof_id(ss["receiptHash"],ss["programVKey"],ss["proofArtifact"]["sha256"])
                ss["proofArtifact"]["uri"]=f'proofs/rooms/{ss["roomId"]}/transitions/{ss["transitionId"]}/{ss["proofId"]}/proof.bin'
            p=temp/"state-proof-tampered.json";dump(p,ss);verify(s=p,success=False)
        proof=ppath.read_bytes()
        # SDK 6.9.0 bincode layout: enum u32, five strings, encoded proof string.
        # Mutate actual encoded Groth16 material while keeping deserialization valid.
        offset=4
        for _ in range(5):
            length=struct.unpack_from("<Q",proof,offset)[0];offset+=8+length
        length=struct.unpack_from("<Q",proof,offset)[0];offset+=8
        assert length>=512 and all(c in b"0123456789abcdefABCDEF" for c in proof[offset:offset+length])
        cryptographic_tamper=bytearray(proof);cryptographic_tamper[offset]=ord("0") if proof[offset]!=ord("0") else ord("1")
        for data in (proof[:-1],bytes([proof[0]^1])+proof[1:],bytes(cryptographic_tamper)):
            p=temp/"altered.bin";p.write_bytes(data);verify(p=p,success=False)
            # Update public descriptor/id too, forcing real cryptographic/deserialization rejection.
            ss=copy.deepcopy(stateproof);ss["proofArtifact"]["sha256"]=hashlib.sha256(data).hexdigest();ss["proofArtifact"]["sizeBytes"]=len(data)
            ss["proofId"]=proof_id(ss["receiptHash"],ss["programVKey"],ss["proofArtifact"]["sha256"])
            ss["proofArtifact"]["uri"]=f'proofs/rooms/{ss["roomId"]}/transitions/{ss["transitionId"]}/{ss["proofId"]}/proof.bin'
            s=temp/"state-proof-altered.json";dump(s,ss);verify(s=s,p=p,success=False)
        wrong=temp/"wrong.elf";wrong.write_bytes(b"not the M5 program");verify(extra=["--candidate-elf",wrong],success=False)
        public=rpath.read_bytes()+spath.read_bytes()+public_claim(receipt)
        for forbidden in (b"local://",b"ciphertexts",b"authorizedReveals",b"backendVersion",b"room-state-v1.key",b"patient_id",b"p1\"",b"p2\"",b"252,",b"438,"):
            assert forbidden not in public
        assert set(p.name for p in directory.iterdir())=={"receipt.json","proof.bin","state-proof.json"}
        metrics.update(realGroth16=True,independentVerification=True,verifierDockerDisabled=True,verifierNetworkProxiesDisabled=True,negativeTestsPassed=True,witnessDeleted=True,noSecretPayloadReads=True,totalSeconds=time.monotonic()-started)
        # Only public metrics and cryptographic identities leave this process.
        print(json.dumps(metrics,sort_keys=True))

if __name__=="__main__": main()
