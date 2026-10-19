#!/usr/bin/env bash
set -euo pipefail
started=$SECONDS
rustup toolchain install 1.96.0 --profile minimal
rustup default 1.96.0
# Immutable official release source; the installer receives an exact release.
curl --fail --location --retry 3 https://raw.githubusercontent.com/succinctlabs/sp1/b8387fa61e1361d90ee7de49f551863418ca0f08/sp1up/sp1up -o "$RUNNER_TEMP/kryptroom-sp1up"
bash "$RUNNER_TEMP/kryptroom-sp1up" --version 6.9.0
export PATH="$HOME/.sp1/bin:$PATH"
echo "$HOME/.sp1/bin" >> "$GITHUB_PATH"
cargo prove --version
rustc --version
rustc +succinct --version
echo "SP1_SETUP_SECONDS=$((SECONDS-started))"
