# PUF-ECC-BatchAuth: formal-verification models and benchmark

Supplementary code for the paper *"PUF-ECC-BatchAuth: A Pairing-Free, PUF-Anchored Lightweight Authentication Protocol with CRL-Free Revocation and Batch RSU Handover for VANETs"*.

| File | Purpose |
|---|---|
| `puf_ecc_batchauth.pv` | ProVerif 2.05 model (Dolev-Yao, Diffie-Hellman equation, ideal signatures) |
| `pufeccbatchauth.spdl` | Scyther 1.3.0 model (agreement / replay properties) |
| `benchmark_crypto_ops.py` | Micro-benchmark of ECC scalar multiplication and hash cost |

## Run
```
proverif puf_ecc_batchauth.pv
scyther pufeccbatchauth.spdl --max-runs=0      # or scyther-mac / scyther-linux
```

## Expected results (as reported in the paper)
ProVerif: OBU session-key secrecy **true**; handover-key secrecy **false** (RSU-RSU backhaul is modelled as public, as a disclosed limitation); the three injective correspondences (RSU accepts M1, OBU accepts M2, OBU/RSU key agreement) **true**.
Scyther: all 13 claims **Ok**.

## Scope and limits
Scyther has no Diffie-Hellman algebra, so DH secrecy is covered by the paper's proof and by ProVerif. Signatures are ideal. Performance figures in the paper are analytical, not hardware measurements.

## Citation
Please cite the paper (details to be added on publication). DOI: _add Zenodo DOI after release_.

## Licence
MIT (see `LICENSE`).
