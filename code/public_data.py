"""Public rainfall validation and user-supplied time-series comparison.

No credentials, download session files or mine displacement records included.
"""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import numpy as np
from scipy.stats import pearsonr, spearmanr


def read_rain(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ['date', 'precip_mm']:
            raise ValueError('Rainfall input must contain ONLY date,precip_mm')
        rows = list(reader)
    dates = [dt.date.fromisoformat(r['date']) for r in rows]
    values = np.array([float(r['precip_mm']) for r in rows])
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise ValueError('Dates must be sorted and unique')
    if not np.isfinite(values).all() or np.any(values < 0):
        raise ValueError('Rainfall must be finite and nonnegative')
    return dates, values


def rainfall_response(rain_path, series_path, lag, start=None, end=None):
    """Lag is a number of observation rows, NOT necessarily elapsed days.

    Difference of zone medians is deliberately not median of pixel differences.
    The series must be supplied externally as date,cumulative_LOS_mm.
    """
    dates, values = read_rain(rain_path)
    rain = dict(zip(dates, values))
    with Path(series_path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ['date', 'cumulative_LOS_mm']:
            raise ValueError('Series requires date,cumulative_LOS_mm')
        rows = list(reader)
    d = [dt.date.fromisoformat(r['date']) for r in rows]
    c = np.array([float(r['cumulative_LOS_mm']) for r in rows])
    if d != sorted(d) or len(set(d)) != len(d) or not np.isfinite(c).all():
        raise ValueError('Series must be finite with unique sorted dates')
    if lag < 0:
        raise ValueError('lag must be nonnegative')
    out = []
    for i in range(max(1, lag), len(d)):
        if start and d[i] < start or end and d[i] > end:
            continue
        rd = d[i - lag]
        if rd not in rain:
            continue
        out.append({'observation_date': d[i].isoformat(),
                    'rain_date': rd.isoformat(), 'rain_mm': float(rain[rd]),
                    'increment_mm': float(c[i] - c[i - 1]),
                    'elapsed_days': (d[i] - d[i - 1]).days,
                    'rain_lag_days': (d[i] - rd).days})
    x = [r['rain_mm'] for r in out]
    y = [r['increment_mm'] for r in out]
    valid = len(out) >= 3 and np.ptp(x) > 0 and np.ptp(y) > 0
    return out, {'n': len(out), 'lag_observation_rows': lag,
                 'pearson': float(pearsonr(x, y).statistic) if valid else None,
                 'spearman': float(spearmanr(x, y).statistic) if valid else None}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rain', type=Path, required=True)
    p.add_argument('--series', type=Path)
    p.add_argument('--lag', type=int, default=1)
    p.add_argument('--start', type=dt.date.fromisoformat)
    p.add_argument('--end', type=dt.date.fromisoformat)
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    d, r = read_rain(a.rain)
    result = {'days': len(d), 'start': str(d[0]), 'end': str(d[-1]),
              'total_mm': float(r.sum()), 'events_ge5mm': int((r >= 5).sum())}
    if a.series:
        rows, result = rainfall_response(a.rain, a.series, a.lag, a.start, a.end)
        if not a.output:
            p.error('--output is required when a displacement series is supplied')
        a.output.mkdir(parents=True, exist_ok=True)
        if rows:
            with (a.output / 'rain_response.csv').open('w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        (a.output / 'rain_response.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
