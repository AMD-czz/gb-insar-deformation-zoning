# Methods and implementation scope

The manuscript uses final unsmoothed segment displacement c, the linear coefficient beta1 and quadratic coefficient kappa fitted against frame index. kappa is a2, not 2*a2. Units are mm, mm/frame, mm/frame^2. The input is already screened and referenced. Centered nearest-endpoint smoothing retains the FIRST N-T+1 outputs. For 71 frames and T=9 this is 63 outputs. No centered-date or trailing-date offset is silently applied; original manuscript figure-date labels require separate checking.

The public HDF5 adapter accepts y_ma, cum_disp, coverage_idx, with configurable keys. Generic NPZ accepts y_mm, final_mm, grid_pos. Raw X/Z parsing, radar packet descriptions, reference-control interpretation, raw-zero/PS rules and proprietary authentication are absent. Final displacement must be supplied separately; it is not replaced by the smoothed last value.

Training uses sorted RandomState(42) sampling (50,000 in the paper), IsolationForest on raw feature units (0.05), RobustScaler on retained training rows, KMeans k-means++/n_init=10, projection to nearest retained real samples, and assignment of every eligible row including training outliers. This is not standard iterative PAM. The focus cluster is defined by the highest median signed c, not by a fixed label ID.

Table 2 is feature AUGMENTATION, not leave-one-feature-out ablation. A common 3D inlier mask is used. sigma_seas is the population std of residuals from a linear fit (no seasonal mechanism is inferred); v_max is max absolute adjacent smoothed difference. The best DTW feature uses three KShape templates fitted on the first 5,000 normalized training sequences, max_iter=10/n_init=1; DTW radius is 50. Coordinates are flattened row/column indices normalized by grid dimensions. Table 2 reports common-training-inlier PCS and adjacent agreement, not full-field values.

PCA and single-reference DTW replace the feature construction while retaining the downstream pipeline. PCA represents 50% variance; the original sampled-data comparison and the full-field timing implementation differ in fit/transform scope, so both are described rather than pooled. The comparison command uses sample-fitted PCA and full-field assignment, matching the full-field implementation. Native KShape uses a deterministic up-to-20,000-row subset of the sampled series and chunked prediction; it does not receive the IsolationForest/projection pipeline.

PCS is the unweighted mean of within-cluster majority displacement-sign fractions; exact zero values belong to neither sign. Spatial agreement counts only valid horizontal/vertical pixel pairs once. LCC uses four-neighbor connectivity and divides the largest focus-component size by the focus-pixel count. ARI measures label agreement, not accuracy.

The parameter command preserves common 3D inliers for k/seed scans. Contamination output fixes k; it is not evidence that k stays optimal under all contamination settings. Window scanning needs decoded_referenced input. Other segments can be processed with separate configs; no full-field mine segment arrays are bundled; a processed 50,000-row S6 training subset is provided separately under S6/.

Rainfall response uses differences of zone median unsmoothed displacement. This is not the median of per-pixel differences. Lag is explicitly an observation-row lag; elapsed-day gaps are retained. SBAS code only postprocesses independently provided ENVI rasters and a declared polygon mask; it does not replicate SARscape inversion or provide independent ground truth.


## v1.1 diagnostic additions

`parameters` retains the fixed-k contamination outputs and additionally exports `contamination_k_scan.csv`, fitting each candidate k separately for each contamination rate on a documented up-to-8,000-row diagnostic subset. `windows` adds `window_stability.csv`: fixed-k full-field ARI versus T=9 (or `window_reference`). These extra diagnostics do not recover unavailable original mine inputs or establish the manuscript numbers.

## Time labels and missingness

The input sequence is ordered by observation frame, not elapsed days. The retained centered filter at index i uses clipped indices i-h..i+h and keeps indices 0..N-T. No calendar dates are inferred. To attach dates, retain the corresponding original frame labels and investigate any historical +h date offset separately. Real zero displacement and missing observations must be distinguished upstream; this package does not infer missingness from zero.

## Outputs

Use different output directories for modes to avoid overwriting `partition.npz`/`model.json`. Configuration paths resolve relative to the parent of the config directory. Synthetic comparisons are methodological demonstrations, not labeled ground truth or independent mine accuracy assessment.
