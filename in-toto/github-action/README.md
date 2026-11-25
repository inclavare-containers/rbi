# Reusable in-toto GitHub Actions Library

This directory provides a generic, reusable [in-toto](https://in-toto.io/) CI/CD library for GitHub Actions, enabling pipelines in `inclavare-containers/rbi` (such as `kata-agent`, `kernel`, and `rootfs-img`) to execute build steps under `in-toto-run`, issue cryptographically signed `.link` provenance files, generate signed `root.layout` policies, and verify end-to-end integrity with `in-toto-verify`.

## Components

| Component | Path | Purpose |
| --- | --- | --- |
| CLI Helper | `in-toto/github-action/intoto_ci.py` | Keygen, layout signing, step execution (`in-toto-run`), and verification (`in-toto-verify`) |
| `in-toto-run` Action | `.github/actions/in-toto-run/action.yml` | Runs a specified step command, hashes materials/products, and emits `<step>.<keyid>.link` |
| `in-toto-layout` Action | `.github/actions/in-toto-layout/action.yml` | Generates and signs `root.layout` from a JSON spec + functionary public keys |
| `in-toto-verify` Action | `.github/actions/in-toto-verify/action.yml` | Verifies `root.layout` and all `.link` files against the trusted owner public key |
| `kata-agent` Demo | `.github/workflows/in-toto-kata-agent-demo.yml` | End-to-end demo pipeline for `kata-agent` patch manifest & build artifact provenance |

## Key Management Model

1. **Production / Protected Branches (GitHub Secrets)**:
   Generate keys offline with:
   ```bash
   python3 in-toto/github-action/intoto_ci.py keygen --out-dir ./keys --name owner
   python3 in-toto/github-action/intoto_ci.py keygen --out-dir ./keys --name builder
   ```
   Store the PEM private keys (`owner.pem`, `builder.pem`) in GitHub Actions Secrets (e.g. `INTOTO_OWNER_KEY`, `INTOTO_STEP_BUILD_KEY`) and pass them via `signing-key: ${{ secrets.INTOTO_STEP_BUILD_KEY }}`. Keep `owner.pub` in a trusted location for relying parties (such as RVPS / Attestation Service) to verify `root.layout`.

2. **PRs / Ephemeral CI Validation**:
   When `signing-key` and `signing-key-path` are omitted (for example on forked PRs where secrets are unavailable), the actions automatically generate ephemeral Ed25519 keypairs per run and emit `public-key-path` and `keyid` outputs so the pipeline can still exercise full provenance generation and verification.

3. **SLSA Alignment**:
   - Step isolation and non-falsifiable provenance can be strengthened by running `in-toto-run` inside reproducible build containers (`rbi.sh`) and storing private signing keys in protected GitHub Environments or external KMS/Sigstore signers.

## Local Testing

```bash
python3 -m pip install -r in-toto/github-action/requirements.txt
python3 -m unittest discover -s in-toto/github-action/tests -v
```
