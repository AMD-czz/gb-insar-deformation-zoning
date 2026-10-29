# Code, data and materials availability

The repository contains analysis code, public-source precipitation inputs, Sentinel-1 acquisition metadata, final satellite SBAS products, documented DEM inputs and a processed S6 training subset. See public_data/ and S6/S6_processed_subset/ for contents and provenance limits.

The S6 subset contains 50,000 measured-data-derived samples, each with 63 retained smoothed displacement values, an unsmoothed final segment-relative displacement, three physical features, a common inlier flag and a reference label. It supports sample-level feature derivation, Isolation Forest screening, robust standardization and projected-center clustering. It provides inputs for further sample-level comparisons, not a claim that every manuscript table has been revalidated. Original spatial/sample-position identifiers are absent.

Original site GB-InSAR observations, proprietary protocol/decoder and restricted full-field ground-radar arrays remain excluded. Complete raw processing and full-field spatial statistics cannot be independently reconstructed from this release alone. Synthetic examples remain separate from the measured-data-derived S6 subset. Dataset access does not establish independent physical accuracy or confer rights beyond the existing author/provider notices.

S6 was added after v1.1.1. Cite the actual new version/commit that contains it in the manuscript and submission form; do not claim that the unchanged v1.1.1 tag includes these samples. A source repository and data availability statement are not substitutes for authorization to distribute measured-data-derived materials.
