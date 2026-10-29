# S6 processed training subset

This is measured-data-derived material, NOT a synthetic example. It contains 50,000 original training sample rows after coverage screening, within-segment referencing and T=9 smoothing, BEFORE Isolation Forest and robust scaling. There are 63 retained smoothed values per row. The separate final displacement is the unsmoothed segment-relative final value.

No original X/Z records, radar protocol, decoder, full-field arrays, original grid IDs, physical coordinates, original sample-position mapping or observation timestamps are included. Anonymous IDs preserve the original training row order. Removing these fields does not guarantee that every temporal or amplitude detail is non-sensitive; author/data-owner review remains necessary before public deposition.

NPZ fields: sample_id, smoothed_LOS_mm [50000,63], final_displacement_mm [50000], features [c,beta1,kappa], common_inlier_mask, reference_labels. CSV repeats the feature-level material for convenient inspection; do not treat the CSV and NPZ as different experiments. Feature units: mm, mm/frame, mm/frame^2. Kappa is a2, not 2*a2.

The package supports sample-level feature derivation, IF mask checking, robust standardization and projected-center clustering. It can provide inputs for further temporal-feature experiments, but no guarantee is made that every original PCA/DTW/KShape table or template result has been revalidated here. It cannot reproduce raw decoding, raw validity interpretation, coverage screening, full-field maps, spatial adjacency/LCC or coordinate-feature augmentation. Training rows are NOT all inliers: preserve all 50,000 rows and the separate 47,500-row mask.

Run: python reproduce_subset.py
Inspected environment: Python 3.14.2, NumPy 2.4.6, SciPy 1.17.0, scikit-learn 1.8.0, threadpoolctl 3.6.0. With those settings: feature difference 0, IF mask identical, sample-label ARI 1.0. This is computational agreement, not accuracy against field truth.

This subset supplements the earlier v1.1.1 code/data release. Publication of this folder is determined by the enclosing repository release or release asset. The v1.1.1 tag alone must not be cited as containing this subset. Use the actual new release link in the manuscript. Distribution rights for the original code repository and the processed sample observations must be handled separately; no new dataset license is invented here.

Installation in the inspected Python environment: python -m pip install -r requirements.txt
Checksums refer only to the files in this subset folder, not the entire companion repository. Do not replace the companion repository root FILE_MANIFEST.csv with this subset checksum file.
