# Submission and upload notes

## Before upload
1. Confirm all authors agree to release the supplied code and satellite products. Keep the original GB-InSAR observations outside this repository.
2. Read DATA_AVAILABILITY.md and LICENSE. The rights notice is unchanged except for clarification of its existing scope; no new open-source license is imposed.
3. Review VALIDATION.md. Local runtime validation is not full mine-result reproduction or a new timing benchmark.
4. Replace manuscript availability placeholders with the real URL/version and a verified ground-radar access restriction. Add the required Disclosures separately.

## GitHub
Create an empty repository (or initialize it with a README only if you will avoid duplicate files). Upload the CONTENTS of this folder so README.md is at the repository root. The package contains large satellite products: browser upload may need multiple batches, each at most 100 files and each file at most 25 MiB. Prefer GitHub Desktop for the complete directory; alternatively archive large public satellite products externally and update all paths/docs before splitting the package. Do not delete only binaries while retaining claims they are bundled.

Commit the checked files, then create a `v1.1.0` release. Use a descriptive release title, record the manuscript version, and do not claim a DOI unless one has actually been assigned. Open the public repository in a signed-out window and verify source/download access. Ordinary private repository URLs do not grant anonymous reviewers access. Paste the actual accessible code URL into the JARS submission form.

## Manuscript issues requiring author verification
- The retained smoothing implementation keeps the FIRST N-T+1 nearest-endpoint-smoothed values. With 71 rows/T=9, original index labels are 0..62; no +4-day offset is applied. Verify Fig. 3 dates against the original plotting workflow. This package does not silently change that method.
- Original reset/jump/coverage preprocessing and proprietary decoding are not distributed. Describe the public-code boundary accurately.
- k/window scans fit on up to 8,000 retained training rows. This is a documented diagnostic subset, not automatically the full-sample paper experiment.
- Fixed-k contamination scans do not prove the optimal k remains unchanged. v1.1 additionally exports contamination/k diagnostics; original mine claims still require authorized original inputs.
- Window diagnostics now include common-full-field ARI versus T=9. Demo ARI is not evidence for the numerical paper ARI.
- Table 2 adds features; call it feature augmentation unless removal experiments are actually performed.
- PCA sample fit / transformation scope and K-Shape sampling must match the manuscript explanation.
- SBAS parameters are partial manuscript-reported information, NOT a restored SARscape project; see processing_parameters.json.
- DEM distribution version and vertical datum remain unverified. Sentinel import identifiers are not complete SAFE IDs.
- Archived timing includes omitted decoding. Do not compare demo times as repetitions of paper timings.

This folder is a submission-ready software package with explicitly documented limits, not certification of editorial acceptance or full scientific reproducibility.
