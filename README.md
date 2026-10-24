# GB-InSAR deformation zoning — submission package v1.1

Companion analysis code for **Deformation zoning for open-pit mines using ground-based interferometric synthetic aperture radar**. Corresponding author: Zhuangzhuang Chen, 2025220214@jou.edu.cn.

## Scope and data boundaries

This package contains the authors' portable analysis code, synthetic examples, public-source rainfall inputs, Sentinel-1 acquisition metadata, DEM inputs, and released final satellite SBAS products. The repository is being prepared for public submission by the authors. It contains **no original ground-based radar observations, proprietary radar decoder/protocol, ground-radar pixel features/labels, or ground-radar displacement series**. Satellite-derived study-area rasters, masks and coordinates ARE included; this is not a package with all mine-related spatial information removed.

The synthetic example demonstrates execution; it does not reproduce the observed mine deformation. With the supplied satellite rasters, the regional SBAS summaries can be recalculated. Raw-SLC SARscape inversion and the full original ground-radar processing chain cannot be reproduced from this repository. See METHODS.md and DATA_AVAILABILITY.md.

## Installation

Tested interpreter: Python 3.14.2 on Windows. Use an isolated environment and run from the repository root:

```text
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

On macOS/Linux use `.venv/bin/python` instead; those platforms are not yet validated. In the commands below, `python` means the interpreter in the activated environment. Dependencies are pinned; see environment/VALIDATION_ENVIRONMENT.json for the environment actually checked in v1.1.

## Run the synthetic example

```text
python code/generate_demo.py --output outputs/synthetic
python code/radar_zoning.py run --config config/demo.json --output outputs/main
python code/radar_zoning.py compare --config config/demo.json --output outputs/comparison
python code/radar_zoning.py augmentation --config config/demo.json --output outputs/augmentation
python code/radar_zoning.py parameters --config config/demo.json --output outputs/parameters
python code/radar_zoning.py windows --config config/demo_windows.json --output outputs/windows
python code/plot_results.py partition --input outputs/main/partition.npz --shape 30 40 --output outputs/figures/demo_partition
python code/public_data.py --rain public_data/gpm_daily_precipitation.csv
python -m unittest discover -s tests -v
```

The packaged `examples/` are synthetic. Generation above writes a fresh copy to `outputs/synthetic`; demo configs intentionally read the packaged examples. This avoids overwriting supplied files during verification. K-Shape/DTW can take time on their first run due to compilation. Outputs are created locally and excluded from publication by .gitignore.

## Recalculate the released satellite results

```text
python code/sbas_statistics.py --raster public_data/sbas_backup55/G_SI_velocity_geo --header public_data/sbas_backup55/G_SI_velocity_geo.hdr --mask public_data/sbas_backup55/study_area_mask.npy --output outputs/sbas_velocity.json
python code/summarize_sbas_series.py --directory public_data/sbas_backup55 --mask public_data/sbas_backup55/study_area_mask.npy --output outputs/recalculated_SBAS_series.csv
```

Expected: 25 epochs; 4,564 polygon cells; 2,724 velocity-valid cells; mean velocity about -31.44774 mm/year; minimum about -121.17358 mm/year; final regional mean about -25.74370 mm. These are satellite quantities, not ground-radar validation. See VALIDATION.md for actual checks, limits and tolerances.

## Use separately authorized ground-radar inputs

Copy `config/paper.example.json`, supply your own authorized input and output locations, and run the same commands. NPZ keys: `y_mm` [pixels, epochs], `final_mm` [pixels], `grid_pos` [pixels]. HDF5 keys are configurable. Inputs must be finite, screened and re-referenced. `final_mm` is the unsmoothed final displacement. Grid indices are zero-based row-major indices. Units and stage handling are defined in METHODS.md.

The public implementation starts after proprietary decoding and screening. Archived performance trials include earlier stages; their exact paper runtimes cannot be reproduced with this demo. Do not interpret ARI as accuracy, synthetic clusters as mine observations, or the quadratic coefficient as physical acceleration.

## Contents

- `code/`: zoning, comparisons, parameter analysis, public-data summaries and plotting.
- `config/`, `examples/`: configurations and reproducible synthetic inputs.
- `public_data/`: released satellite/precipitation/DEM materials and provenance limits.
- `results_summary/`: archived runtime metadata, not mine displacement arrays.
- `tests/`: scientific and input/output checks.
- `SUBMISSION_NOTES.md`: GitHub upload and manuscript consistency guidance.

## Rights

Public inspection does not mean an open-source license. See LICENSE for the existing author rights notice; obtain permission for uses not granted there. Third-party data retain provider terms. Do not apply a repository-wide MIT or CC BY license without authorization. The release does not independently establish dataset provenance or legal redistribution rights.
