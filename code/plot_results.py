"""Generic plotting only. All numerical inputs must be supplied explicitly."""
import argparse
import csv
import datetime as dt
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.colors import BoundaryNorm


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='mode', required=True)
    z = sub.add_parser('partition')
    z.add_argument('--input', required=True, type=Path)
    z.add_argument('--shape', nargs=2, required=True, type=int)
    z.add_argument('--output', required=True, type=Path)
    s = sub.add_parser('series')
    s.add_argument('--input', action='append', required=True,
                   help='label=CSV; CSV requires date,displacement_mm')
    s.add_argument('--value-column', default='displacement_mm',
                   help='Numeric column, e.g. cumulative_LOS_mm or regional_mean_LOS_mm')
    s.add_argument('--start', required=True, type=dt.date.fromisoformat)
    s.add_argument('--end', required=True, type=dt.date.fromisoformat)
    s.add_argument('--ylabel', default='Cumulative LOS displacement (mm)')
    s.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                         'pdf.fonttype': 42, 'svg.fonttype': 'none'})
    fig, ax = plt.subplots(figsize=(6.5, 2.6), layout='constrained')
    if a.mode == 'partition':
        with np.load(a.input, allow_pickle=False) as h:
            grid, labels = h['grid_pos'], h['labels']
        if len(np.unique(grid)) != len(grid) or np.any(grid < 0) or np.any(grid >= np.prod(a.shape)):
            raise ValueError('Invalid grid indices')
        full = np.full(np.prod(a.shape), np.nan)
        full[grid] = labels
        levels = np.unique(labels)
        boundaries = np.r_[levels - .5, levels[-1] + .5]
        colors = plt.get_cmap('viridis', len(levels))
        im = ax.imshow(full.reshape(a.shape), interpolation='nearest', aspect='auto',
                       cmap=colors, norm=BoundaryNorm(boundaries, len(levels)))
        fig.colorbar(im, ax=ax, ticks=levels, label='Cluster label')
        ax.set(xlabel='Range pixel column', ylabel='Azimuth pixel row')
    else:
        if a.end < a.start:
            raise ValueError('End date precedes start date')
        for arg in a.input:
            name, path = arg.split('=', 1)
            with Path(path).open(encoding='utf-8-sig', newline='') as f:
                rows = list(csv.DictReader(f))
            dates = [dt.date.fromisoformat(r['date']) for r in rows]
            values = np.array([float(r[a.value_column]) for r in rows])
            if dates != sorted(dates):
                raise ValueError('Dates must be sorted')
            keep = np.array([a.start <= d <= a.end for d in dates])
            if not keep.any():
                raise ValueError('No observations in common window: ' + name)
            ax.plot(np.array(dates)[keep], values[keep], label=name, linewidth=1)
        ax.set_xlim(a.start, a.end)
        ax.xaxis.set_major_locator(md.AutoDateLocator(minticks=4, maxticks=10))
        ax.xaxis.set_major_formatter(md.DateFormatter('%Y-%m'))
        ax.set(xlabel='Date', ylabel=a.ylabel)
        ax.grid(alpha=.25)
        ax.legend(fontsize=7)
        # Separate input files are separate curves: no across-segment interpolation.
    a.output.parent.mkdir(parents=True, exist_ok=True)
    for ext in ['png', 'svg', 'pdf']:
        fig.savefig(a.output.with_suffix('.'+ext), dpi=300)
    plt.close(fig)


if __name__ == '__main__':
    main()
