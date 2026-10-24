# Final public-source SBAS products

The backup55 final geocoded satellite LOS products selected by the authors for public release are included. Binary rasters are paired with their ENVI HDR files, preserving the original grids, NaN mask and numeric values. The 25 displacement rasters span 2025-08-16 to 2026-06-24. G_SI_velocity_geo is final LOS velocity, not the first-inversion G_FI_velocity_geo. Coherence and RMSE arrays are provided as output quality context, not independent accuracy validation.

study_area_mask.npy and valid_velocity_mask.npy are full-grid boolean masks for the exact manuscript statistics. The latter has 2,724 cells; the polygon has 4,564 cells. regional_LOS_timeseries.csv uses the velocity-valid study pixels with finite observations at each epoch and follows the same fixed minimum-velocity pixel across all epochs. The final mean is -25.7437019 mm; the fixed point is -106.2100 mm. These are satellite results, not ground-radar zone medians.

The parameter JSON provides only partial parameters explicitly reported in the manuscript and identifies unrecovered settings. It is not a transcription of a recovered final project and is not a SARscape executable project. Actual reference/control-point input and exact precision-orbit association have not been restored; this package is sufficient to inspect/recalculate the provided geocoded summaries, not to claim a full raw-SLC inversion rerun.

No VD products, first-estimate displacement, first-inversion velocity, cache files or older alternatives are included. Generate Vertical Direction Results is FALSE in the retained parameter record even though VD files exist in the original directory; they must not be presented as independently measured vertical displacement.

Ground-based radar observations and proprietary decoding remain excluded. Public satellite products being released here do not lift those separate restrictions.

## Recalculate the released series
From the package root:
```
python code/summarize_sbas_series.py --directory public_data/sbas_backup55 --mask public_data/sbas_backup55/study_area_mask.npy --output outputs/recalculated_SBAS_series.csv
```
This computes the summaries from the 25 released satellite rasters; it does not invoke the proprietary ground-radar decoder or repeat SARscape inversion.
