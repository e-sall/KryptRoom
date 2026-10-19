//! Metadata-only CPU proving and independent witness-free verification.
use anyhow::{ensure, Context, Result};
use base64::{engine::general_purpose::STANDARD, Engine};
use kryptroom_proof_relation::*;
use serde_json::json;
use sp1_sdk::{
    blocking::{ProveRequest, Prover, ProverClient},
    HashableKey, ProvingKey, SP1Proof, SP1ProofWithPublicValues, SP1Stdin, SP1_CIRCUIT_VERSION,
};
use std::{collections::BTreeMap, fs, io::Write, path::Path, time::Instant};
// Trusted identity is embedded at build time, never taken from StateProof/URI.
const ELF: &[u8] = include_bytes!(env!("KRYPTROOM_M5_ELF"));
const GNARK_IMAGE: &str = "ghcr.io/succinctlabs/sp1-gnark:v6.1.0@sha256:e1a1cd62838b561ca301f9b2c26475c4a92bfe0e2c916e9bba213062e1548c4d";
fn read_json<T: serde::de::DeserializeOwned>(p: &str) -> Result<T> {
    Ok(serde_json::from_slice(&read_document(
        p, "json", 2_000_000,
    )?)?)
}
fn read_document(p: &str, extension: &str, limit: u64) -> Result<Vec<u8>> {
    let path = Path::new(p);
    ensure!(
        path.extension().and_then(|s| s.to_str()) == Some(extension),
        "unsupported document path"
    );
    let metadata = fs::symlink_metadata(path)?;
    ensure!(
        metadata.is_file() && !metadata.file_type().is_symlink() && metadata.len() <= limit,
        "invalid document file"
    );
    Ok(fs::read(path)?)
}
fn write_new(p: &Path, b: &[u8]) -> Result<()> {
    let mut f = fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(p)?;
    f.write_all(b)?;
    f.sync_all()?;
    Ok(())
}
fn flag<'a>(a: &'a BTreeMap<String, String>, k: &str) -> Result<&'a str> {
    Ok(a.get(k).with_context(|| format!("missing {k}"))?)
}
fn main() -> Result<()> {
    let mut raw = std::env::args().skip(1);
    let cmd = raw.next().context("expected command")?;
    let mut args = BTreeMap::new();
    while let Some(k) = raw.next() {
        ensure!(k.starts_with("--"), "invalid argument");
        let v = raw.next().context("missing flag value")?;
        ensure!(args.insert(k, v).is_none(), "duplicate flag");
    }
    if cmd == "hash" {
        let v: serde_json::Value = read_json(flag(&args, "--json")?)?;
        println!("{}", digest(&v).map_err(anyhow::Error::msg)?);
        return Ok(());
    }
    if cmd == "check" {
        let w: Witness = read_json(flag(&args, "--witness")?)?;
        verify_relation(&w).map_err(anyhow::Error::msg)?;
        println!("RELATION_VALID");
        return Ok(());
    }
    ensure!(
        ["prove", "execute", "verify"].contains(&cmd.as_str()),
        "unsupported command"
    );
    // Explicit CPU builder; no network prover or mock fallback.
    ensure!(
        std::env::var("SP1_PROVER").unwrap_or_else(|_| "cpu".into()) == "cpu",
        "SP1_PROVER must be cpu"
    );
    if let Ok(image) = std::env::var("SP1_GNARK_IMAGE") {
        ensure!(
            image == GNARK_IMAGE,
            "unexpected local Groth16 wrapping image"
        );
    }
    std::env::set_var("SP1_GNARK_IMAGE", GNARK_IMAGE);
    if let Some(p) = args.get("--candidate-elf") {
        ensure!(
            read_document(p, "elf", 20_000_000)? == ELF,
            "unexpected guest ELF"
        );
    }
    let started = Instant::now();
    if cmd == "verify" {
        let r: Receipt = read_json(flag(&args, "--receipt")?)?;
        r.validate().map_err(anyhow::Error::msg)?;
        let s: StateProof = read_json(flag(&args, "--state-proof")?)?;
        s.validate(&r).map_err(anyhow::Error::msg)?;
        if let Some(x) = args.get("--expect-room") {
            ensure!(*x == r.room_id, "unexpected room");
        }
        if let Some(x) = args.get("--expect-transition") {
            ensure!(*x == r.transition_id, "unexpected transition");
        }
        let bytes = read_document(flag(&args, "--proof")?, "bin", 2_000_000)?;
        ensure!(
            bytes.len() as u64 == s.proof_artifact.size_bytes
                && hash(&bytes) == s.proof_artifact.sha256,
            "proof descriptor mismatch"
        );
        ensure!(s.elf_sha256 == hash(ELF), "guest ELF hash mismatch");
        let client = ProverClient::builder().light().build();
        let pk = client
            .setup(ELF.into())
            .map_err(|e| anyhow::anyhow!("setup failed: {e}"))?;
        let vk = pk.verifying_key();
        let vkey = vk.bytes32();
        ensure!(s.program_v_key == vkey, "program verification key mismatch");
        let proof = SP1ProofWithPublicValues::load(flag(&args, "--proof")?)?;
        // SDK load also accepts a shorter network transport format. M5 uses
        // one exact SDK serialization, rejecting truncation and trailing data.
        ensure!(
            bincode::serialize(&proof)? == bytes,
            "noncanonical proof serialization"
        );
        ensure!(
            matches!(proof.proof, SP1Proof::Groth16(_))
                && !proof.bytes().is_empty()
                && proof.tee_proof.is_none(),
            "real Groth16 required"
        );
        ensure!(
            proof.sp1_version == SP1_CIRCUIT_VERSION,
            "circuit version mismatch"
        );
        ensure!(
            proof.public_values.as_slice() == r.claim().map_err(anyhow::Error::msg)?
                && hash(proof.public_values.as_slice()) == s.public_values_sha256,
            "public values mismatch"
        );
        // Independent verification uses the official pure Rust verifier. It
        // requires no Docker daemon, circuit files, or prover witness.
        sp1_verifier::Groth16Verifier::verify(
            &proof.bytes(),
            proof.public_values.as_slice(),
            &vkey,
            &sp1_verifier::GROTH16_VK_BYTES,
        )
        .map_err(|_| anyhow::anyhow!("encoded Groth16 verification failed"))?;
        println!("VERIFIED");
        println!(
            "{}",
            json!({"verificationSeconds":started.elapsed().as_secs_f64()})
        );
        return Ok(());
    }
    let path = flag(&args, "--witness")?;
    let w: Witness = read_json(path)?;
    fs::remove_file(path)?;
    let rb = STANDARD.decode(&w.receipt_canonical_base64)?;
    let r: Receipt = serde_json::from_slice(&rb)?;
    let mut stdin = SP1Stdin::new();
    stdin.write(&w);
    // execute sends invalid relations into the actual guest for Class A tests.
    if cmd == "execute" {
        // The official execution-only backend runs the real guest and cannot
        // generate a proof. It is not a mock or a final proof mode.
        let client = ProverClient::builder().light().build();
        let (pv, report) = client
            .execute(ELF.into(), stdin)
            .run()
            .map_err(|_| anyhow::anyhow!("guest rejected"))?;
        // SDK execution may return Ok with a nonzero guest exit code. A
        // guest panic is rejection, never successful execution/public values.
        ensure!(report.exit_code == 0, "guest rejected");
        ensure!(
            pv.as_slice() == r.claim().map_err(anyhow::Error::msg)?,
            "claim mismatch"
        );
        println!("EXECUTED");
        return Ok(());
    }
    let claim = verify_relation(&w).map_err(anyhow::Error::msg)?;
    let setup = Instant::now();
    let client = ProverClient::builder().cpu().build();
    let pk = client
        .setup(ELF.into())
        .map_err(|e| anyhow::anyhow!("setup failed: {e}"))?;
    let setup_seconds = setup.elapsed().as_secs_f64();
    let vk = pk.verifying_key();
    let vkey = vk.bytes32();
    let prove_start = Instant::now();
    let proof = client
        .prove(&pk, stdin)
        .groth16()
        .run()
        .map_err(|e| anyhow::anyhow!("CPU Groth16 proving failed: {e}"))?;
    let seconds = prove_start.elapsed().as_secs_f64();
    ensure!(
        matches!(proof.proof, SP1Proof::Groth16(_)) && !proof.bytes().is_empty(),
        "Groth16 required"
    );
    ensure!(proof.public_values.as_slice() == claim, "claim mismatch");
    client
        .verify(&proof, vk, None)
        .context("local verification failed")?;
    let bytes = bincode::serialize(&proof)?;
    let ph = hash(&bytes);
    let rh = r.hash().map_err(anyhow::Error::msg)?;
    let id = proof_id(&rh, &vkey, &ph).map_err(anyhow::Error::msg)?;
    let uri = format!(
        "proofs/rooms/{}/transitions/{}/{}/proof.bin",
        r.room_id, r.transition_id, id
    );
    let s = StateProof {
        version: "1".into(),
        proof_id: id,
        proof_system: "sp1-groth16".into(),
        proof_system_version: "6.9.0".into(),
        program_version: PROGRAM_VERSION.into(),
        room_id: r.room_id.clone(),
        transition_id: r.transition_id.clone(),
        transition_commitment: r.transition_commitment.clone(),
        output_state_id: r.output_state_id.clone(),
        output_state_commitment: r.output_state_commitment.clone(),
        receipt_hash: rh,
        program_v_key: vkey.clone(),
        elf_sha256: hash(ELF),
        public_values_sha256: hash(proof.public_values.as_slice()),
        proof_artifact: ProofArtifactRef {
            media_type: "application/vnd.kryptroom.sp1-groth16-proof".into(),
            uri: uri.clone(),
            sha256: ph.clone(),
            size_bytes: bytes.len() as u64,
        },
        created_at: flag(&args, "--created-at")?.into(),
    };
    s.validate(&r).map_err(anyhow::Error::msg)?;
    let dir = Path::new(flag(&args, "--output-root")?).join(Path::new(&uri).parent().unwrap());
    fs::create_dir_all(dir.parent().unwrap())?;
    fs::create_dir(&dir)?;
    write_new(&dir.join("receipt.json"), &rb)?;
    write_new(&dir.join("proof.bin"), &bytes)?;
    let sb = canonical(&serde_json::to_value(&s)?).map_err(anyhow::Error::msg)?;
    write_new(&dir.join("state-proof.json"), &sb)?;
    println!(
        "{}",
        json!({"proofDirectory":dir,"elfSha256":s.elf_sha256,"programVKey":vkey,"sp1Version":"6.9.0","circuitVersion":SP1_CIRCUIT_VERSION,"proverSetupSeconds":setup_seconds,"proofGenerationSeconds":seconds,"proofBytes":bytes.len(),"receiptBytes":rb.len(),"stateProofBytes":sb.len(),"proofSha256":ph})
    );
    Ok(())
}
