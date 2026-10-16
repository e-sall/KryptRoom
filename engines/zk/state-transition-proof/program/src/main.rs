//! Proves metadata consistency only, never MPC execution or numeric correctness.
#![no_main]
sp1_zkvm::entrypoint!(main);

pub fn main() {
    let witness: kryptroom_proof_relation::Witness = sp1_zkvm::io::read();
    let claim = kryptroom_proof_relation::verify_relation(&witness).expect("invalid M5 relation");
    sp1_zkvm::io::commit_slice(&claim);
}
