"""Statistics of independently provided public-source ENVI LOS rasters.

This is postprocessing, NOT an implementation or distribution of SARscape.
"""
import argparse
import json
from pathlib import Path
import re
import numpy as np


def read_envi(raster, header):
    text = Path(header).read_text(encoding='utf-8', errors='replace')
    def field(name, default=None):
        m = re.search(r'^\s*' + re.escape(name) + r'\s*=\s*([^\r\n]+)', text, re.M | re.I)
        if m:
            return m[1].strip()
        if default is None:
            raise ValueError('Missing ENVI header field: ' + name)
        return default
    types = {2: 'i2', 3: 'i4', 4: 'f4', 5: 'f8', 12: 'u2'}
    code = int(field('data type'))
    if code not in types or int(field('bands', '1')) != 1:
        raise ValueError('Only supported one-band numeric rasters are accepted')
    shape = int(field('lines')), int(field('samples'))
    dtype = np.dtype(('>' if int(field('byte order', '0')) else '<') + types[code])
    arr = np.fromfile(raster, dtype=dtype, offset=int(field('header offset', '0')))
    if arr.size != np.prod(shape):
        raise ValueError('Raster size differs from header')
    nodata = field('data ignore value', 'nan')
    return arr.reshape(shape), float(nodata)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raster', required=True, type=Path)
    p.add_argument('--header', required=True, type=Path)
    p.add_argument('--mask', required=True, type=Path,
                   help='Boolean .npy raster mask generated for the declared study polygon')
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    z, nd = read_envi(a.raster, a.header)
    mask = np.load(a.mask, allow_pickle=False)
    if mask.shape != z.shape or mask.dtype != bool:
        raise ValueError('Mask must be boolean and match raster shape')
    valid = mask & np.isfinite(z)
    if np.isfinite(nd):
        valid &= z != nd
    v = z[valid]
    if not len(v):
        raise ValueError('No valid pixels')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps({'polygon_grid_cells': int(mask.sum()),
        'valid_cells': len(v), 'mean': float(v.mean()), 'minimum': float(v.min()),
        'negative_fraction': float((v < 0).mean()),
        'units': 'same as source raster; must be declared by caller'}, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
