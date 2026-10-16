//! M5 proves committed metadata consistency. It does not prove MPC arithmetic,
//! execution of the committed code, or participant signatures/approval.
use base64::{engine::general_purpose::STANDARD, Engine};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};

pub const RECEIPT_DOMAIN: &[u8] = b"KRYPTROOM-TRANSITION-RECEIPT-V1\0";
pub const CLAIM_DOMAIN: &[u8] = b"KRYPTROOM-STATE-PROOF-V1";
pub const ID_DOMAIN: &[u8] = b"KRYPTROOM-STATE-PROOF-ID-V1\0";
pub const PROGRAM_VERSION: &str = "kryptroom-m5-evaluation-v1";
pub const OP: &str = "private_model_evaluation";
pub const MODEL_IDS: [&str; 4] = [
    "model-nn-layer1-weight",
    "model-nn-layer1-bias",
    "model-nn-output-weight",
    "model-nn-output-bias",
];
pub const DATA_IDS: [&str; 3] = ["match-mask", "lab-a-features", "lab-b-features"];
pub const OUTPUT: &str = "model-evaluation-mse";
pub const REVEAL: &str = "model.evaluation.mse";
pub type Result<T> = std::result::Result<T, String>;
fn need(ok: bool) -> Result<()> {
    if ok {
        Ok(())
    } else {
        Err("invalid M5 metadata relation".into())
    }
}
pub fn hash(bytes: &[u8]) -> String {
    hex::encode(Sha256::digest(bytes))
}

/// Python json-sort-keys-v1 compatibility for the restricted M5 structures.
/// Floats and null are rejected; historical S3 bytes are hashed without reserialization.
pub fn canonical(value: &Value) -> Result<Vec<u8>> {
    fn emit(v: &Value, out: &mut String) -> Result<()> {
        match v {
            Value::Object(o) => {
                out.push('{');
                let mut keys: Vec<_> = o.keys().collect();
                keys.sort();
                for (i, k) in keys.iter().enumerate() {
                    if i > 0 {
                        out.push(',');
                    }
                    out.push_str(&serde_json::to_string(k).map_err(|_| "string")?);
                    out.push(':');
                    emit(&o[*k], out)?;
                }
                out.push('}');
            }
            Value::Array(a) => {
                out.push('[');
                for (i, x) in a.iter().enumerate() {
                    if i > 0 {
                        out.push(',');
                    }
                    emit(x, out)?;
                }
                out.push(']');
            }
            Value::String(s) => {
                need(!s.chars().any(|c| c == '\u{7f}'))?;
                out.push_str(&serde_json::to_string(s).map_err(|_| "string")?);
            }
            Value::Number(n) => {
                need(n.is_i64() || n.is_u64())?;
                out.push_str(&n.to_string());
            }
            Value::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
            _ => return Err("unsupported canonical JSON value".into()),
        }
        Ok(())
    }
    let mut out = String::new();
    emit(value, &mut out)?;
    Ok(out.into_bytes())
}
pub fn digest(v: &Value) -> Result<String> {
    Ok(hash(&canonical(v)?))
}
fn keys(v: &Value, expected: &[&str]) -> Result<()> {
    let o = v.as_object().ok_or("object required")?;
    need(o.len() == expected.len() && expected.iter().all(|k| o.contains_key(*k)))
}
fn text<'a>(v: &'a Value, key: &str) -> Result<&'a str> {
    v[key].as_str().ok_or_else(|| "string required".into())
}
fn array<'a>(v: &'a Value, key: &str) -> Result<&'a Vec<Value>> {
    v[key].as_array().ok_or_else(|| "array required".into())
}
// Reject ambiguous duplicate keys recursively, including historical parent bytes.
struct StrictJson(Value);
impl<'de> Deserialize<'de> for StrictJson {
    fn deserialize<D: serde::Deserializer<'de>>(de: D) -> std::result::Result<Self, D::Error> {
        struct Visitor;
        impl<'de> serde::de::Visitor<'de> for Visitor {
            type Value = StrictJson;
            fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
                f.write_str("unambiguous JSON")
            }
            fn visit_bool<E: serde::de::Error>(
                self,
                v: bool,
            ) -> std::result::Result<StrictJson, E> {
                Ok(StrictJson(json!(v)))
            }
            fn visit_i64<E: serde::de::Error>(self, v: i64) -> std::result::Result<StrictJson, E> {
                Ok(StrictJson(json!(v)))
            }
            fn visit_u64<E: serde::de::Error>(self, v: u64) -> std::result::Result<StrictJson, E> {
                Ok(StrictJson(json!(v)))
            }
            fn visit_f64<E: serde::de::Error>(self, v: f64) -> std::result::Result<StrictJson, E> {
                serde_json::Number::from_f64(v)
                    .map(|n| StrictJson(Value::Number(n)))
                    .ok_or_else(|| E::custom("nonfinite number"))
            }
            fn visit_str<E: serde::de::Error>(self, v: &str) -> std::result::Result<StrictJson, E> {
                Ok(StrictJson(json!(v)))
            }
            fn visit_string<E: serde::de::Error>(
                self,
                v: String,
            ) -> std::result::Result<StrictJson, E> {
                Ok(StrictJson(json!(v)))
            }
            fn visit_unit<E: serde::de::Error>(self) -> std::result::Result<StrictJson, E> {
                Ok(StrictJson(Value::Null))
            }
            fn visit_seq<A: serde::de::SeqAccess<'de>>(
                self,
                mut a: A,
            ) -> std::result::Result<StrictJson, A::Error> {
                let mut values = vec![];
                while let Some(v) = a.next_element::<StrictJson>()? {
                    values.push(v.0);
                }
                Ok(StrictJson(Value::Array(values)))
            }
            fn visit_map<A: serde::de::MapAccess<'de>>(
                self,
                mut a: A,
            ) -> std::result::Result<StrictJson, A::Error> {
                let mut values = serde_json::Map::new();
                while let Some((k, v)) = a.next_entry::<String, StrictJson>()? {
                    if values.insert(k, v.0).is_some() {
                        return Err(serde::de::Error::custom("duplicate key"));
                    }
                }
                Ok(StrictJson(Value::Object(values)))
            }
        }
        de.deserialize_any(Visitor)
    }
}
fn parse_metadata(bytes: &[u8]) -> Result<Value> {
    serde_json::from_slice::<StrictJson>(bytes)
        .map(|s| s.0)
        .map_err(|_| "invalid metadata JSON".into())
}
pub fn is_hash(s: &str) -> bool {
    s.len() == 64
        && s.bytes()
            .all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c))
}
pub fn safe_id(s: &str) -> bool {
    !s.is_empty()
        && s.len() <= 128
        && s.as_bytes()[0].is_ascii_alphanumeric()
        && s.bytes()
            .all(|c| c.is_ascii_alphanumeric() || b"._-".contains(&c))
}

#[derive(Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Witness {
    pub version: String,
    pub model_parent_content_base64: String,
    pub data_parent_content_base64: String,
    pub child_content_base64: String,
    pub receipt_canonical_base64: String,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Parent {
    pub state_id: String,
    pub state_commitment: String,
    pub policy_hash: String,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Input {
    pub parent_index: usize,
    pub artifact_id: String,
    pub artifact_commitment: String,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Output {
    pub artifact_id: String,
    pub artifact_commitment: String,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Receipt {
    pub version: String,
    pub proof_domain: String,
    pub room_id: String,
    pub transition_id: String,
    pub operator: String,
    pub ordered_parents: Vec<Parent>,
    pub ordered_inputs: Vec<Input>,
    pub key_epoch: String,
    pub crypto_context_hash: String,
    pub code_hash: String,
    pub workflow_hash: String,
    pub requested_reveals: Vec<String>,
    pub requested_reveals_hash: String,
    pub output_policy_hash: String,
    pub output_state_id: String,
    pub ordered_outputs: Vec<Output>,
    pub transition_commitment: String,
    pub output_state_commitment: String,
}
impl Receipt {
    pub fn validate(&self) -> Result<()> {
        need(
            self.version == "1"
                && self.proof_domain == "kryptroom.state-transition-proof.v1"
                && self.operator == OP,
        )?;
        need(
            safe_id(&self.room_id)
                && safe_id(&self.transition_id)
                && self.output_state_id == "S4_eval",
        )?;
        need(
            self.key_epoch == "room-state-v1"
                && self.ordered_parents.len() == 2
                && self.ordered_inputs.len() == 7
                && self.ordered_outputs.len() == 1,
        )?;
        need(
            self.ordered_parents[0].state_id == "S3_model"
                && self.ordered_parents[1].state_id == "S1",
        )?;
        need(self.requested_reveals == [REVEAL] && self.ordered_outputs[0].artifact_id == OUTPUT)?;
        let mut hashes = vec![
            &self.crypto_context_hash,
            &self.code_hash,
            &self.workflow_hash,
            &self.requested_reveals_hash,
            &self.output_policy_hash,
            &self.transition_commitment,
            &self.output_state_commitment,
        ];
        for p in &self.ordered_parents {
            hashes.extend([&p.state_commitment, &p.policy_hash]);
        }
        for (i, a) in self.ordered_inputs.iter().enumerate() {
            need(
                a.parent_index == if i < 4 { 0 } else { 1 }
                    && a.artifact_id == if i < 4 { MODEL_IDS[i] } else { DATA_IDS[i - 4] },
            )?;
            hashes.push(&a.artifact_commitment);
        }
        hashes.push(&self.ordered_outputs[0].artifact_commitment);
        need(hashes.into_iter().all(|s| is_hash(s)))
    }
    pub fn hash(&self) -> Result<String> {
        self.validate()?;
        let mut bytes = RECEIPT_DOMAIN.to_vec();
        bytes.extend(canonical(
            &serde_json::to_value(self).map_err(|_| "receipt")?,
        )?);
        Ok(hash(&bytes))
    }
    pub fn claim(&self) -> Result<Vec<u8>> {
        let mut b = Sha256::digest(CLAIM_DOMAIN).to_vec();
        b.extend(hex::decode(self.hash()?).map_err(|_| "hash")?);
        Ok(b)
    }
}
pub fn expected_context() -> Value {
    json!({"id":"secretflow-spu-cheetah-fm128-v1","backend":"SecretFlow SPU","backendVersion":"1.14.0b0","protocol":"CHEETAH","field":"FM128","securityModel":"semi-honest","participants":["lab-a","lab-b"],"artifactCipher":"AES-256-GCM","keyScope":"per-kryptnode-local"})
}
fn policy(p: &Value) -> Result<()> {
    let mut ks = vec![
        "defaultReveal",
        "plaintextMaterialization",
        "matchedIdentifierReveal",
        "futureIdentifierDisclosure",
        "authorizedReveals",
    ];
    if p.get("allowedOperators").is_some() {
        ks.extend(["allowedOperators", "allowedInputArtifactIds"]);
    }
    keys(p, &ks)?;
    need(
        p["defaultReveal"] == "deny"
            && p["plaintextMaterialization"] == "forbidden"
            && p["matchedIdentifierReveal"] == "forbidden"
            && p["futureIdentifierDisclosure"] == json!({"requiresExplicitOptIn":true}),
    )?;
    let rs = array(p, "authorizedReveals")?;
    let mut seen = std::collections::BTreeSet::new();
    for r in rs {
        keys(r, &["name", "recipients"])?;
        need(seen.insert(text(r, "name")?))?;
        let recipients = array(r, "recipients")?;
        need(!recipients.is_empty())?;
        let mut names = std::collections::BTreeSet::new();
        for x in recipients {
            need(names.insert(x.as_str().ok_or("recipient")?))?;
        }
    }
    if p.get("allowedOperators").is_some() {
        array(p, "allowedOperators")?;
        array(p, "allowedInputArtifactIds")?;
    }
    Ok(())
}
fn authorizes(p: &Value, name: &str) -> bool {
    p["authorizedReveals"].as_array().is_some_and(|rs| {
        rs.iter().any(|r| {
            r["name"] == name
                && r["recipients"].as_array().is_some_and(|a| {
                    a.len() == 2 && a.contains(&json!("lab-a")) && a.contains(&json!("lab-b"))
                })
        })
    })
}
pub fn derived_policy() -> Value {
    json!({"defaultReveal":"deny","plaintextMaterialization":"forbidden","matchedIdentifierReveal":"forbidden","futureIdentifierDisclosure":{"requiresExplicitOptIn":true},"authorizedReveals":[{"name":"ciphertext-metadata","recipients":["lab-a","lab-b"]},{"name":REVEAL,"recipients":["lab-a","lab-b"]}]})
}
pub fn artifact_hash(a: &Value, c: &Value) -> Result<String> {
    digest(&json!({"artifact":a,"cryptoContext":c}))
}
fn state(s: &Value, room: &str, id: &str) -> Result<()> {
    keys(
        s,
        &[
            "schemaVersion",
            "id",
            "roomId",
            "parentStateIds",
            "artifacts",
            "transition",
            "policy",
            "cryptoContext",
        ],
    )?;
    need(
        s["schemaVersion"] == "1"
            && s["id"] == id
            && s["roomId"] == room
            && s["cryptoContext"] == expected_context(),
    )?;
    need(s["parentStateIds"] == s["transition"]["parentStateIds"])?;
    keys(
        &s["transition"],
        &[
            "id",
            "operation",
            "parentStateIds",
            "inputJobId",
            "outputArtifactIds",
            "effectiveAt",
            "bindings",
        ],
    )?;
    need(safe_id(text(&s["transition"], "id")?) && safe_id(text(&s["transition"], "inputJobId")?))?;
    text(&s["transition"], "effectiveAt")?;
    array(s, "artifacts")?;
    array(s, "parentStateIds")?;
    policy(&s["policy"])
}
fn artifact(a: &Value, s: &Value, shape: &Value, dtype: &str) -> Result<()> {
    keys(
        a,
        &[
            "id",
            "kind",
            "mediaType",
            "visibility",
            "cryptoContextId",
            "shape",
            "dtype",
            "includesIdentifiers",
            "ciphertexts",
        ],
    )?;
    need(
        a["kind"] == "spu-secret-share"
            && a["mediaType"] == "application/vnd.kryptroom.spu-share+encrypted"
            && a["visibility"] == "secret-shared"
            && a["includesIdentifiers"] == false
            && a["cryptoContextId"] == s["cryptoContext"]["id"]
            && a["dtype"] == dtype
            && a["shape"] == *shape,
    )?;
    let holders = array(a, "ciphertexts")?;
    need(holders.len() == 2)?;
    for (h, party) in holders.iter().zip(["lab-a", "lab-b"]) {
        keys(h, &["party", "uri", "sha256", "sizeBytes"])?;
        let uri = format!(
            "local://{party}/rooms/{}/states/{}/artifacts/{}.share.enc",
            text(s, "roomId")?,
            text(s, "id")?,
            text(a, "id")?
        );
        need(
            h["party"] == party
                && h["uri"] == uri
                && is_hash(text(h, "sha256")?)
                && h["sizeBytes"].as_u64().is_some_and(|n| n > 0),
        )?;
    }
    Ok(())
}
pub fn model_spec() -> Value {
    json!({"type":"feedforward_neural_network","inputDim":1,"layers":[{"type":"dense","inputDim":1,"outputDim":2},{"type":"square"},{"type":"dense","inputDim":2,"outputDim":1}],"outputInterpretation":"normalized_continuous_treatment_response"})
}
pub fn evaluation_spec() -> Value {
    json!({"loss":"masked_mse","feature":{"artifact":"lab-a-features","column":0,"divideBy":10},"label":{"artifact":"lab-b-features","column":0,"divideBy":1000}})
}

/// All relation checks execute INSIDE the guest. Host validation alone is insufficient.
pub fn verify_relation(w: &Witness) -> Result<Vec<u8>> {
    need(w.version == "1")?;
    let decode = |s: &str| -> Result<Vec<u8>> {
        need(s.len() <= 2_000_000)?;
        STANDARD.decode(s).map_err(|_| "base64".into())
    };
    let mb = decode(&w.model_parent_content_base64)?;
    let db = decode(&w.data_parent_content_base64)?;
    let cb = decode(&w.child_content_base64)?;
    let rb = decode(&w.receipt_canonical_base64)?;
    let r: Receipt = serde_json::from_slice(&rb).map_err(|_| "receipt schema")?;
    r.validate()?;
    need(canonical(&serde_json::to_value(&r).map_err(|_| "receipt")?)? == rb)?;
    need(
        hash(&mb) == r.ordered_parents[0].state_commitment
            && hash(&db) == r.ordered_parents[1].state_commitment
            && hash(&cb) == r.output_state_commitment,
    )?;
    let m = parse_metadata(&mb)?;
    let d = parse_metadata(&db)?;
    let c = parse_metadata(&cb)?;
    // Never regenerate historical model content containing floating-point configuration.
    state(&m, &r.room_id, "S3_model")?;
    state(&d, &r.room_id, "S1")?;
    state(&c, &r.room_id, "S4_eval")?;
    need(canonical(&c)? == cb)?;
    need(
        m["parentStateIds"] == json!(["S1"])
            && d["parentStateIds"] == json!([])
            && c["parentStateIds"] == json!(["S3_model", "S1"]),
    )?;
    need(
        m["transition"]["operation"] == "private_nn_training"
            && m["transition"]["outputArtifactIds"] == json!(MODEL_IDS)
            && m["transition"]["inputJobId"] == m["transition"]["id"],
    )?;
    need(
        d["transition"]["operation"] == "private-join"
            && d["transition"]["outputArtifactIds"] == json!(DATA_IDS),
    )?;
    let ctx = expected_context();
    need(digest(&ctx)? == r.crypto_context_hash)?;
    for (s, p) in [&m, &d].iter().zip(&r.ordered_parents) {
        need(digest(&s["policy"])? == p.policy_hash)?;
        need(array(&s["policy"], "allowedOperators")?.contains(&json!(OP)))?;
        need(authorizes(&s["policy"], REVEAL) && authorizes(&s["policy"], "ciphertext-metadata"))?;
    }
    need(
        m["policy"]["allowedOperators"] == json!([OP])
            && m["policy"]["allowedInputArtifactIds"] == json!(MODEL_IDS)
            && d["policy"]["allowedInputArtifactIds"] == json!(DATA_IDS),
    )?;
    let mut model_policy = derived_policy();
    model_policy["allowedOperators"] = json!([OP]);
    model_policy["allowedInputArtifactIds"] = json!(MODEL_IDS);
    need(m["policy"] == model_policy)?;
    let ma = array(&m, "artifacts")?;
    let da = array(&d, "artifacts")?;
    let ca = array(&c, "artifacts")?;
    need(ma.len() == 4 && da.len() == 3 && ca.len() == 1)?;
    let shapes = [json!([1, 2]), json!([2]), json!([2, 1]), json!([1])];
    for (i, a) in ma.iter().enumerate() {
        need(a["id"] == MODEL_IDS[i])?;
        artifact(a, &m, &shapes[i], "float32")?;
    }
    let grid = da[0]["shape"].as_array().ok_or("grid")?;
    need(
        grid.len() == 2
            && grid[0] == grid[1]
            && grid[0].as_u64().is_some_and(|n| n > 0 && n <= 128),
    )?;
    for (i, a) in da.iter().enumerate() {
        need(a["id"] == DATA_IDS[i])?;
        artifact(
            a,
            &d,
            &if i == 0 {
                json!(grid)
            } else {
                json!([grid[0], grid[1], 1])
            },
            "int32",
        )?;
    }
    let count = d["transition"]["bindings"]["cohortCardinality"]
        .as_u64()
        .ok_or("cardinality")?;
    need(count > 0 && count <= grid[0].as_u64().ok_or("grid")?)?;
    for (a, i) in ma.iter().chain(da.iter()).zip(&r.ordered_inputs) {
        need(artifact_hash(a, &ctx)? == i.artifact_commitment)?;
    }
    need(ca[0]["id"] == OUTPUT)?;
    artifact(&ca[0], &c, &json!([1]), "float32")?;
    let out_hash = artifact_hash(&ca[0], &ctx)?;
    need(out_hash == r.ordered_outputs[0].artifact_commitment)?;
    let policy = derived_policy();
    need(c["policy"] == policy && digest(&policy)? == r.output_policy_hash)?;
    need(digest(&json!([REVEAL]))? == r.requested_reveals_hash)?;
    let t = &c["transition"];
    let bindings = &t["bindings"];
    let req = &bindings["request"];
    let ts = &req["transition"];
    keys(
        ts,
        &[
            "operator",
            "inputStateIds",
            "outputStateId",
            "transitionId",
            "effectiveAt",
            "requestedReveals",
        ],
    )?;
    need(
        ts["operator"] == OP
            && ts["inputStateIds"] == json!(["S3_model", "S1"])
            && ts["outputStateId"] == r.output_state_id
            && ts["transitionId"] == r.transition_id
            && ts["requestedReveals"] == json!([REVEAL]),
    )?;
    text(ts, "effectiveAt")?;
    let parents = json!([{"stateId":"S3_model","stateCommitment":r.ordered_parents[0].state_commitment,"policyHash":r.ordered_parents[0].policy_hash},{"stateId":"S1","stateCommitment":r.ordered_parents[1].state_commitment,"policyHash":r.ordered_parents[1].policy_hash}]);
    let inputs = |a: &Vec<Value>| -> Result<Vec<Value>> {
        a.iter()
            .map(|a| Ok(json!({"artifactRef":a,"commitment":artifact_hash(a,&ctx)?})))
            .collect()
    };
    let expected_req = json!({"version":"1","operator":OP,"parents":parents,"modelInputs":inputs(ma)?,"dataInputs":inputs(da)?,"modelSpec":model_spec(),"modelSpecHash":digest(&model_spec())?,"evaluationSpec":evaluation_spec(),"evaluationSpecHash":digest(&evaluation_spec())?,"codeHash":r.code_hash,"workflowHash":r.workflow_hash,"cryptoContextHash":r.crypto_context_hash,"inputPolicyHashes":[r.ordered_parents[0].policy_hash,r.ordered_parents[1].policy_hash],"outputPolicy":policy,"outputPolicyHash":r.output_policy_hash,"requestedRevealsHash":r.requested_reveals_hash,"outputStateId":r.output_state_id,"transition":ts});
    need(*req == expected_req)?;
    let mut payload = json!({"operator":OP,"request":expected_req,"outputStateId":r.output_state_id,"outputArtifactCommitments":[out_hash]});
    let tc = digest(&payload)?;
    need(tc == r.transition_commitment)?;
    payload["transitionCommitment"] = json!(tc);
    need(*bindings == payload)?;
    need(
        *t == json!({"id":r.transition_id,"operation":OP,"parentStateIds":["S3_model","S1"],"inputJobId":r.transition_id,"outputArtifactIds":[OUTPUT],"effectiveAt":ts["effectiveAt"],"bindings":payload}),
    )?;
    r.claim()
}

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct ProofArtifactRef {
    pub media_type: String,
    pub uri: String,
    pub sha256: String,
    pub size_bytes: u64,
}
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct StateProof {
    pub version: String,
    pub proof_id: String,
    pub proof_system: String,
    pub proof_system_version: String,
    pub program_version: String,
    pub room_id: String,
    pub transition_id: String,
    pub transition_commitment: String,
    pub output_state_id: String,
    pub output_state_commitment: String,
    pub receipt_hash: String,
    pub program_v_key: String,
    pub elf_sha256: String,
    pub public_values_sha256: String,
    pub proof_artifact: ProofArtifactRef,
    pub created_at: String,
}
pub fn proof_id(receipt_hash: &str, vkey: &str, proof_hash: &str) -> Result<String> {
    let mut b = ID_DOMAIN.to_vec();
    for s in [
        receipt_hash,
        vkey.strip_prefix("0x").ok_or("vkey")?,
        proof_hash,
    ] {
        b.extend(hex::decode(s).map_err(|_| "hash")?);
    }
    Ok(format!("stateproof-{}", &hash(&b)[..32]))
}
impl StateProof {
    pub fn validate(&self, r: &Receipt) -> Result<()> {
        need(self.receipt_hash == r.hash()?)?;
        need(
            self.version == "1"
                && self.proof_system == "sp1-groth16"
                && self.proof_system_version == "6.9.0"
                && self.program_version == PROGRAM_VERSION,
        )?;
        need(
            self.room_id == r.room_id
                && self.transition_id == r.transition_id
                && self.transition_commitment == r.transition_commitment
                && self.output_state_id == r.output_state_id
                && self.output_state_commitment == r.output_state_commitment
                && self.receipt_hash == r.hash()?,
        )?;
        need(
            is_hash(&self.elf_sha256)
                && is_hash(&self.public_values_sha256)
                && is_hash(&self.proof_artifact.sha256)
                && self.program_v_key.starts_with("0x")
                && is_hash(&self.program_v_key[2..]),
        )?;
        need(
            self.proof_artifact.media_type == "application/vnd.kryptroom.sp1-groth16-proof"
                && self.proof_artifact.size_bytes > 0,
        )?;
        need(
            self.proof_id
                == proof_id(
                    &self.receipt_hash,
                    &self.program_v_key,
                    &self.proof_artifact.sha256,
                )?,
        )?;
        need(
            self.proof_artifact.uri
                == format!(
                    "proofs/rooms/{}/transitions/{}/{}/proof.bin",
                    self.room_id, self.transition_id, self.proof_id
                ),
        )?;
        // V1 restricts creation timestamps to the unambiguous UTC RFC3339 form.
        let b = self.created_at.as_bytes();
        need(
            b.len() == 20
                && b[4] == b'-'
                && b[7] == b'-'
                && b[10] == b'T'
                && b[13] == b':'
                && b[16] == b':'
                && b[19] == b'Z'
                && b.iter()
                    .enumerate()
                    .all(|(i, c)| [4, 7, 10, 13, 16, 19].contains(&i) || c.is_ascii_digit()),
        )?;
        let number = |start: usize, end: usize| {
            self.created_at[start..end]
                .parse::<u32>()
                .map_err(|_| "timestamp".to_string())
        };
        let year = number(0, 4)?;
        let month = number(5, 7)?;
        let day = number(8, 10)?;
        let days = match month {
            1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
            4 | 6 | 9 | 11 => 30,
            2 => {
                if year % 4 == 0 && (year % 100 != 0 || year % 400 == 0) {
                    29
                } else {
                    28
                }
            }
            _ => 0,
        };
        need(
            year > 0
                && day > 0
                && day <= days
                && number(11, 13)? < 24
                && number(14, 16)? < 60
                && number(17, 19)? < 60,
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Witness {
        Witness {
            version: "1".into(),
            model_parent_content_base64: STANDARD.encode(include_bytes!(
                "../../../../../tests/state_proof/fixtures/S3_model.content.json"
            )),
            data_parent_content_base64: STANDARD.encode(include_bytes!(
                "../../../../../tests/state_proof/fixtures/S1.content.json"
            )),
            child_content_base64: STANDARD.encode(include_bytes!(
                "../../../../../tests/state_proof/fixtures/S4_eval.content.json"
            )),
            receipt_canonical_base64: STANDARD.encode(include_bytes!(
                "../../../../../tests/state_proof/fixtures/receipt.json"
            )),
        }
    }
    #[test]
    fn domains() {
        assert_eq!(RECEIPT_DOMAIN.last(), Some(&0));
        assert_ne!(CLAIM_DOMAIN.last(), Some(&0));
        assert_eq!(ID_DOMAIN.last(), Some(&0));
        assert_eq!(Sha256::digest(CLAIM_DOMAIN).len(), 32);
    }
    #[test]
    fn canonicalization() {
        assert_eq!(
            canonical(&json!({"z":1,"a":"é\n\t\u{0001}"})).unwrap(),
            "{\"a\":\"é\\n\\t\\u0001\",\"z\":1}".as_bytes()
        );
        assert!(canonical(&json!(0.4)).is_err());
        assert!(canonical(&Value::Null).is_err());
    }
    #[test]
    fn fixture_and_golden() {
        let w = fixture();
        assert_eq!(verify_relation(&w).unwrap().len(), 64);
        let vectors: Value = serde_json::from_str(include_str!(
            "../../../../../tests/state_proof/fixtures/hashes.json"
        ))
        .unwrap();
        for v in vectors.as_array().unwrap() {
            assert_eq!(
                hex::encode(canonical(&v["value"]).unwrap()),
                v["canonicalHex"]
            );
            assert_eq!(digest(&v["value"]).unwrap(), v["sha256"]);
        }
    }
    #[test]
    fn duplicate_keys_rejected() {
        assert!(parse_metadata(br#"{"a":1,"a":2}"#).is_err());
        assert!(parse_metadata(br#"{"x":{"a":1,"a":2}}"#).is_err());
    }
    #[test]
    fn invalid_relation_matrix() {
        let changes = [
            ("/policy/defaultReveal", json!("allow")),
            ("/policy/allowedOperators", json!([])),
            ("/policy/allowedInputArtifactIds", json!(["patient-id"])),
            ("/policy/authorizedReveals", json!([])),
            ("/policy/authorizedReveals/1/recipients", json!(["ui"])),
            ("/cryptoContext/field", json!("FM64")),
            ("/cryptoContext/participants", json!(["lab-a", "outsider"])),
            ("/artifacts/0/includesIdentifiers", json!(true)),
            ("/artifacts/0/id", json!("unauthorized")),
            ("/artifacts/0/ciphertexts/0/sha256", json!("0".repeat(64))),
            ("/artifacts/0/ciphertexts/0/sizeBytes", json!(0)),
            ("/artifacts/0/ciphertexts/0/party", json!("outsider")),
        ];
        for (path, value) in changes {
            for parent in 0..2 {
                let mut w = fixture();
                let encoded = if parent == 0 {
                    &mut w.model_parent_content_base64
                } else {
                    &mut w.data_parent_content_base64
                };
                let mut s = parse_metadata(&STANDARD.decode(&*encoded).unwrap()).unwrap();
                *s.pointer_mut(path).unwrap() = value.clone();
                let bytes = serde_json::to_vec(&s).unwrap();
                *encoded = STANDARD.encode(&bytes);
                let mut r: Value =
                    serde_json::from_slice(&STANDARD.decode(&w.receipt_canonical_base64).unwrap())
                        .unwrap();
                // Keep commitment and policy hash bindings consistent to test the relation.
                r["orderedParents"][parent]["stateCommitment"] = json!(hash(&bytes));
                r["orderedParents"][parent]["policyHash"] = json!(digest(&s["policy"]).unwrap());
                w.receipt_canonical_base64 = STANDARD.encode(canonical(&r).unwrap());
                assert!(
                    verify_relation(&w).is_err(),
                    "accepted {path} for parent {parent}"
                );
            }
        }
        let changes = [
            ("/parentStateIds", json!(["S1", "S3_model"])),
            ("/policy/authorizedReveals/1/recipients", json!(["ui"])),
            (
                "/transition/bindings/request/cryptoContextHash",
                json!("0".repeat(64)),
            ),
            (
                "/transition/bindings/request/modelSpec/layers/1/type",
                json!("relu"),
            ),
            (
                "/transition/bindings/request/evaluationSpec/feature/divideBy",
                json!(11),
            ),
            (
                "/transition/bindings/request/codeHash",
                json!("1".repeat(64)),
            ),
            (
                "/transition/bindings/request/workflowHash",
                json!("2".repeat(64)),
            ),
            (
                "/transition/bindings/request/transition/requestedReveals",
                json!(["model.weight"]),
            ),
            (
                "/transition/bindings/transitionCommitment",
                json!("3".repeat(64)),
            ),
            ("/transition/inputJobId", json!("other-job")),
            ("/artifacts/0/id", json!("model-weight")),
            ("/artifacts/0/shape", json!([2])),
        ];
        for (path, value) in changes {
            let mut w = fixture();
            let mut c = parse_metadata(&STANDARD.decode(&w.child_content_base64).unwrap()).unwrap();
            *c.pointer_mut(path).unwrap() = value;
            let cb = canonical(&c).unwrap();
            w.child_content_base64 = STANDARD.encode(&cb);
            let mut r: Value =
                serde_json::from_slice(&STANDARD.decode(&w.receipt_canonical_base64).unwrap())
                    .unwrap();
            r["outputStateCommitment"] = json!(hash(&cb));
            w.receipt_canonical_base64 = STANDARD.encode(canonical(&r).unwrap());
            assert!(verify_relation(&w).is_err(), "accepted child {path}");
        }
    }
}
