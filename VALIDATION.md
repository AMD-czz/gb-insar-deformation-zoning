# Validation of submission package v1.1.0

Checked on 2026-10-24. See environment/VALIDATION_ENVIRONMENT.json. An existing environment matched the pinned versions; this is not a fresh-install certification.

## Executed checks

- All 8 unittest cases passed, including independent DTW recurrence, polynomial coefficients, projected representatives, grid gaps, explicit rainfall lag, ENVI byte order and malformed input rejection.
- All 12 command-line workflows below completed with exit code 0.
- Synthetic inputs regenerated from the fixed seed match every array in the two supplied synthetic NPZ files exactly.
- All 68 non-document/non-JSON public-data files match the original v1.0 bytes (SHA-256).
- The 1,771,561-cell DEM crop equals the declared source HGT window exactly; this does not establish vertical datum or full georeferencing correctness.

| Command | Exit code |
|---|---|
| `python code/generate_demo.py --output outputs/synthetic` | 0 |
| `python code/radar_zoning.py run --config config/demo.json --output outputs/main` | 0 |
| `python code/radar_zoning.py compare --config config/demo.json --output outputs/comparison` | 0 |
| `python code/radar_zoning.py augmentation --config config/demo.json --output outputs/augmentation` | 0 |
| `python code/radar_zoning.py parameters --config config/demo.json --output outputs/parameters` | 0 |
| `python code/radar_zoning.py windows --config config/demo_windows.json --output outputs/windows` | 0 |
| `python code/public_data.py --rain public_data/gpm_daily_precipitation.csv` | 0 |
| `python code/public_data.py --rain public_data/gpm_daily_precipitation.csv --series examples/synthetic_zone_series.csv --lag 1 --output outputs/rain_demo` | 0 |
| `python code/sbas_statistics.py --raster public_data/sbas_backup55/G_SI_velocity_geo --header public_data/sbas_backup55/G_SI_velocity_geo.hdr --mask public_data/sbas_backup55/study_area_mask.npy --output outputs/sbas_velocity.json` | 0 |
| `python code/summarize_sbas_series.py --directory public_data/sbas_backup55 --mask public_data/sbas_backup55/study_area_mask.npy --output outputs/recalculated_SBAS_series.csv` | 0 |
| `python code/plot_results.py partition --input outputs/main/partition.npz --shape 30 40 --output outputs/figures/demo_partition` | 0 |
| `python code/plot_results.py series --input SBAS=outputs/recalculated_SBAS_series.csv --value-column regional_mean_LOS_mm --start 2025-08-16 --end 2026-06-24 --output outputs/figures/sbas_series` | 0 |

## Released satellite numerical checks

- Polygon cells: 4564; valid velocity cells: 2724.
- Mean LOS velocity: -31.4477386475 mm/year; minimum: -121.1735839844 mm/year.
- Negative velocity fraction: 0.9919236417.
- Epochs: 25; final regional mean: -25.7437019348 mm; fixed minimum-velocity point: -106.2099990845 mm.
- Compared velocity values against metadata at tolerance 1e-5; final series mean at 1e-5 and fixed point at 1e-3 mm.

## Limits

- No original GB-InSAR observations are supplied or tested. No original mine-zone accuracy or complete result reproduction is certified.
- SARscape inversion, original screening/reset processing and proprietary decoding are outside scope.
- Runtime observations are not benchmarks and do not reproduce archived original timings.
- tslearn emitted one informational warning when interpreting 2D input as univariate time series; the comparison completed.
- Demo ARI=1 across the window scan belongs to synthetic inputs, not the manuscript observations.
- Figures were generated; the synthetic partition image was visually inspected.
- No new data access rights, confidentiality agreements or licenses are inferred from successful execution.
