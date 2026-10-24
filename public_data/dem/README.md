# DEM inputs

The final backup55 SARscape output metadata explicitly names StudyArea_DEM_30m_bil as its source DEM. This release preserves the actual binary and its HDR/PRJ plus the matching N39E110.hgt tile. All 1,771,561 elevation cells exactly match the source window stated in metadata.json. No elevation or header values were changed.

The manuscript reports SRTM 30 m. The local HGT format and numerical provenance are verified, but the original download provider/release/version and height datum have not been independently established. Do not invent a version-3/EGM96 claim solely from the filename. HGT is a point grid; original ENVI map referencing is preserved. Numerical identity is not a complete georeferencing validation.

The separate UTM49N dataset is not substituted for this geographic DEM; its pixels are approximately 23.8703 by 30.84064 m, not a 30-by-30 m square. The final processing metadata identifies the geographic file.

The broad regional Figure 1 mosaic uses 24 tiles listed in regional_map_source_tiles.csv. That large mosaic and 23 irrelevant-to-this-crop tiles are not redundantly bundled. The N39E110 tile and actual SBAS crop are sufficient to inspect this local DEM input, not to reproduce the entire broad regional map.
