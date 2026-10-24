# Public input data

## Sentinel-1
The CSV lists all 25 acquisition identifiers retained in the SARscape import directory. Sentinel-1A, ascending IW/VV are checked against each retained first IW1 burst metadata file. Its UTC acquisition time is read from the ENVI header. The measurement dataset name, absolute orbit and datatake ID are retained where present, to identify source acquisitions more precisely. Relative orbit 113 agrees with the import identifiers and manuscript. The import and measurement identifiers are NOT full original SAFE product names. No full SAFE ID, checksum or precision-orbit match is invented.

Retrieve candidate Sentinel-1A SLC images from Copernicus Data Space using the acquisition date, absolute orbit/datatake ID when available, the manuscript study area, relative orbit 113, ascending pass and IW mode. Match the exact source product and orbit validity before repeating the SBAS processing. Retained import metadata is not a complete SAFE-level provenance record.

## GPM
gpm_daily_precipitation.csv contains only dates and daily satellite precipitation at 39.55 N, 110.55 E, from 2025-05-01 through 2026-07-01. The 427-day retained extraction is rounded to 0.01 mm. GPM_3IMERGDL_07, Late Run, V07, DOI 10.5067/GPM/IMERGDL/DAY/07. No mine displacement columns are included. See gpm_metadata.json for units and limitations.

## Final SBAS products
See sbas_backup55/ for 25 final LOS displacement rasters, final velocity, quality layers, exact study masks, geographic polygon, partial manuscript-reported processing parameters and regional summaries. These are the public-source satellite results selected for release; provider terms still apply. No ground-radar data are included.

## DEM
See dem/. The final output metadata identifies StudyArea_DEM_30m_bil. Its full 1331-by-1331 elevation array exactly matches a window of the provided N39E110.hgt tile. Both are included. The exact original product release/version and vertical datum are still not established; no unverified version attribution is added.
