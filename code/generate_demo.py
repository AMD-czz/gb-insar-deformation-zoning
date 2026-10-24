"""Generate synthetic sequences; no values are taken from mine observations."""
import argparse
import datetime as dt
from pathlib import Path
import numpy as np
from scipy.ndimage import uniform_filter1d


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    rng = np.random.RandomState(7)
    rows, cols, n = 30, 40, 71
    r, c = np.indices((rows, cols))
    group = ((r - 15)**2 / 60 + (c - 23)**2 / 85 < 1).ravel()
    t = np.arange(n, dtype=float)
    raw = rng.normal(0, .3, (rows * cols, n))
    raw += rng.normal(0, .003, (rows * cols, 1)) * t
    raw[group] += (.07 * t + .002 * t**2)
    raw -= raw[:, :1]
    smooth = uniform_filter1d(raw, size=9, axis=1, mode='nearest')[:, :n - 8]
    np.savez_compressed(a.output / 'synthetic_preprocessed.npz', y_mm=smooth.astype('f4'),
                        final_mm=raw[:, -1].astype('f4'), grid_pos=np.arange(rows * cols))
    np.savez_compressed(a.output / 'synthetic_decoded_referenced.npz', y_mm=raw.astype('f4'),
                        final_mm=raw[:, -1].astype('f4'), grid_pos=np.arange(rows * cols))
    with (a.output / 'synthetic_zone_series.csv').open('w', encoding='utf-8') as f:
        f.write('date,cumulative_LOS_mm\n')
        for i, v in enumerate(np.median(raw[group], axis=0)):
            f.write(f'{dt.date(2025,5,1)+dt.timedelta(days=i)},{v:.8f}\n')
    print('Synthetic inputs generated. They are NOT field measurements.')


if __name__ == '__main__':
    main()
