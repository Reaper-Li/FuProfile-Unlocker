# RAW compatibility corpus

This directory contains camera RAW samples used to verify profile generation.
The layout is always `RAW/<brand>/<camera>/`.

The current broad corpus contains 921 files from 57 brand directories (about
21 GB on disk). It selects one compact CC0 sample per available camera model,
while retaining a few explicit observation samples. Coverage includes the
major interchangeable-lens brands, medium format, compact cameras, drones,
cinema cameras, scanners, action cameras, Raspberry Pi modules, and mobile
phone DNG files including six Apple iPhone models.

Samples are downloaded from [raw.pixls.us](https://raw.pixls.us/), which is
maintained as a regression corpus for open-source RAW software. See
`manifest.json` for the source URL, expected camera identity, and verification
status of each sample.

The three `Fujifilm/GFX 100 II` files are observation samples in different RAF
encoding modes. They are excluded from custom test-profile generation so they
can be used to inspect Lightroom's unmodified native Camera Matching list.

To refresh or resume the corpus from the current raw.pixls.us inventory:

```sh
tools/download_raw_samples.sh
```

The synchronizer validates every completed file against the source SHA-256,
resumes `.part` downloads, and updates `manifest.json`. Use `--brand Apple` to
limit a run to one brand or `--plan-only` to update the plan without downloading.

The RAW binaries are intentionally ignored by Git. The manifest and generated
verification reports remain versioned so the corpus can be reproduced.
