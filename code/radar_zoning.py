"""Portable implementation of the manuscript's author-written analysis.

Input starts AFTER proprietary decoding. No radar protocol is included.
The projected representatives below are not an iterative PAM/k-medoids fit.
"""
import argparse
import csv
import json
import os
from pathlib import Path

# Set before NumPy imports; the runtime also limits existing thread pools.
for _key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_key] = '1'

import numpy as np
from scipy.ndimage import label, uniform_filter1d
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (adjusted_rand_score, silhouette_score,
                             calinski_harabasz_score, davies_bouldin_score)
from sklearn.metrics.pairwise import pairwise_distances_argmin
from sklearn.preprocessing import RobustScaler
from threadpoolctl import threadpool_limits


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False,
                                   allow_nan=False), encoding='utf-8')


def save_csv(path, rows):
    if not rows:
        raise ValueError('No output records')
    with Path(path).open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def normalize(y):
    y = np.asarray(y, dtype=np.float64)
    span = np.ptp(y, axis=1, keepdims=True)
    span[span < 1e-6] = 1
    return (y - y.min(axis=1, keepdims=True)) / span * 2 - 1


def smooth_decoded(y, window):
    """Already re-referenced, already coverage-screened [pixels, epochs] mm.

    Reproduce nearest-endpoint centered MA, then retain FIRST N-T+1 outputs.
    Invalid entries must have been handled by the input provider; no decoder,
    raw-zero validity interpretation, reference reset or X/Z matching is done.
    """
    if window < 1 or window % 2 != 1 or window > y.shape[1]:
        raise ValueError('window must be odd and no larger than epoch count')
    return uniform_filter1d(np.asarray(y, dtype=np.float64), size=window,
                            axis=1, mode='nearest')[:, :y.shape[1] - window + 1]


def physical_features(y, final, extended=False, batch=60000):
    y = np.asarray(y)
    if y.ndim != 2 or y.shape[1] < 3 or np.asarray(final).shape != (len(y),):
        raise ValueError('Need >=3 epochs and one unsmoothed final value per row')
    x = np.arange(y.shape[1], dtype=np.float64)
    lin = np.polyfit(x, np.eye(len(x)), 1)
    quad = np.polyfit(x, np.eye(len(x)), 2)[0]
    f = np.empty((len(y), 5 if extended else 3), dtype=np.float64)
    f[:, 0] = final
    for i in range(0, len(y), batch):
        z = y[i:i + batch].astype(np.float64)
        b = z @ lin[0]
        f[i:i + len(z), 1] = b
        f[i:i + len(z), 2] = z @ quad
        if extended:
            intercept = z @ lin[1]
            residual = z - b[:, None] * x - intercept[:, None]
            f[i:i + len(z), 3] = residual.std(axis=1, ddof=0)
            f[i:i + len(z), 4] = np.abs(np.diff(z, axis=1)).max(axis=1)
    return f


def fit_projected(f, k=2, seed=42, contamination=.05, mask=None):
    if mask is None:
        mask = (np.ones(len(f), dtype=bool) if contamination == 0 else
                IsolationForest(contamination=contamination, random_state=seed,
                                n_jobs=1).fit_predict(f) == 1)
    if mask.sum() < k:
        raise ValueError('Fewer training inliers than requested clusters')
    scaler = RobustScaler().fit(f[mask])
    s = scaler.transform(f[mask])
    km = KMeans(n_clusters=k, init='k-means++', n_init=10,
                random_state=seed).fit(s)
    ri = pairwise_distances_argmin(km.cluster_centers_, s)
    return scaler, s[ri], np.asarray(mask), np.flatnonzero(mask)[ri]


def predict(f, model, batch=60000):
    scaler, reps = model[:2]
    ans = np.empty(len(f), dtype=np.int32)
    for i in range(0, len(f), batch):
        ans[i:i + batch] = pairwise_distances_argmin(scaler.transform(f[i:i + batch]), reps)
    return ans


def pcs(labels, final):
    return float(np.mean([max(np.mean(final[labels == k] > 0),
                              np.mean(final[labels == k] < 0))
                          for k in np.unique(labels)]))


def spatial_metrics(grid, labels, final, shape):
    if len(np.unique(grid)) != len(grid) or np.any(grid < 0) or np.any(grid >= np.prod(shape)):
        raise ValueError('grid_pos must be unique flattened grid indices')
    z = np.full(np.prod(shape), -1, dtype=np.int32)
    z[grid] = labels
    z = z.reshape(shape)
    n = same = 0
    for a, b in [(z[:, :-1], z[:, 1:]), (z[:-1], z[1:])]:
        valid = (a >= 0) & (b >= 0)
        n += int(valid.sum())
        same += int(((a == b) & valid).sum())
    ids = np.unique(labels)
    focus = int(ids[np.argmax([np.median(final[labels == k]) for k in ids])])
    m = labels == focus
    full = np.zeros(np.prod(shape), dtype=bool)
    full[grid[m]] = True
    cc, ncc = label(full.reshape(shape))  # SciPy default 4-neighbor connectivity
    counts = np.bincount(cc.ravel())[1:]
    return {'PCS': pcs(labels, final),
            'adjacent_label_agreement': same / n if n else None,
            'focus_label': focus, 'focus_fraction': float(m.mean()),
            'LCC_focus': float(counts.max() / m.sum()) if len(counts) else 0.,
            'focus_components': int(ncc)}


def dtw_distance(y, reference, radius=50):
    """Squared-error accumulation followed by sqrt, Sakoe-Chiba band."""
    from tslearn.metrics import cdist_dtw
    return cdist_dtw(y, np.asarray(reference)[None, :], n_jobs=1,
                    global_constraint='sakoe_chiba',
                    sakoe_chiba_radius=radius).ravel()


def load_input(config, root):
    path = Path(config['input'])
    path = path if path.is_absolute() else root / path
    if path.suffix.lower() == '.npz':
        with np.load(path, allow_pickle=False) as h:
            y, final, grid = h['y_mm'].copy(), h['final_mm'].copy(), h['grid_pos'].copy()
    elif path.suffix.lower() in ('.h5', '.hdf5'):
        import h5py
        keys = config.get('h5_keys', {'y_mm': 'y_ma', 'final_mm': 'cum_disp', 'grid_pos': 'coverage_idx'})
        with h5py.File(path, 'r') as h:
            y, final, grid = (h[keys[k]][:] for k in ('y_mm', 'final_mm', 'grid_pos'))
    else:
        raise ValueError('Input must be generic NPZ or already-preprocessed HDF5')
    if np.asarray(grid).ndim != 1 or not np.isfinite(grid).all() or not np.equal(grid, np.floor(grid)).all():
        raise ValueError('grid_pos must be a finite one-dimensional integer array')
    grid = grid.astype(np.int64)
    if np.asarray(final).shape != (len(y),):
        raise ValueError('final_mm must be one-dimensional')
    if y.ndim != 2 or len(y) != len(final) or len(y) != len(grid):
        raise ValueError('Input row dimensions do not agree')
    if not np.isfinite(y).all() or not np.isfinite(final).all():
        raise ValueError('Provide finite, already screened input; no silent gap filling')
    if config.get('input_stage') == 'decoded_referenced':
        y = smooth_decoded(y, config['window'])
    elif config.get('input_stage') != 'preprocessed':
        raise ValueError('input_stage must be preprocessed or decoded_referenced')
    shape = config['grid_shape']
    if len(shape) != 2 or any(int(v) != v or v < 1 for v in shape):
        raise ValueError('grid_shape must contain two positive integers')
    if len(np.unique(grid)) != len(grid) or np.any(grid < 0) or np.any(grid >= np.prod(shape)):
        raise ValueError('grid_pos must contain unique indices inside grid_shape')
    return y, final, grid


def run_main(config, y, final, grid, out):
    f = physical_features(y, final)
    sample = np.sort(np.random.RandomState(config['seed']).choice(
        len(y), min(config['sample_size'], len(y)), replace=False))
    model = fit_projected(f[sample], config['k'], config['seed'], config['contamination'])
    labels = predict(f, model)
    np.savez_compressed(out / 'partition.npz', grid_pos=grid, labels=labels,
                        sample_positions=sample, training_inlier_mask=model[2])
    save_json(out / 'model.json', {'scaler_center': model[0].center_.tolist(),
              'scaler_scale': model[0].scale_.tolist(), 'representatives': model[1].tolist(),
              'representative_sample_rows': model[3].tolist(), 'config': config})
    save_json(out / 'metrics.json', spatial_metrics(grid, labels, final, config['grid_shape']))
    return f, sample, model, labels


def augmentation(config, y, final, grid, out):
    sample = np.sort(np.random.RandomState(config['seed']).choice(
        len(y), min(config['sample_size'], len(y)), replace=False))
    z = y[sample].astype(np.float64)
    f5 = physical_features(z, final[sample], extended=True)
    yn = normalize(z)
    from tslearn.clustering import KShape
    ks = KShape(n_clusters=3, random_state=config['seed'], max_iter=10, n_init=1)
    ks.fit(yn[:min(5000, len(yn))])
    from tslearn.metrics import cdist_dtw
    best = cdist_dtw(yn, ks.cluster_centers_, n_jobs=1,
                    global_constraint='sakoe_chiba',
                    sakoe_chiba_radius=config['dtw_radius']).min(axis=1)
    rows, cols = config['grid_shape']
    angle = (grid[sample] // cols).astype(np.float32) / (rows - 1.)
    distance = (grid[sample] % cols).astype(np.float32) / (cols - 1.)
    f8 = np.column_stack([f5, angle, distance, best])
    sets = {'3D': [0, 1, 2], '+sigma_seas': [0, 1, 2, 3],
            '+v_max': [0, 1, 2, 4], '+ang_norm': [0, 1, 2, 5],
            '+rng_norm': [0, 1, 2, 6], '+best_dtw': [0, 1, 2, 7],
            '5D': [0, 1, 2, 3, 4], '8D': list(range(8))}
    base = fit_projected(f5[:, :3], config['k'], config['seed'], config['contamination'])
    mask = base[2]
    base_labels = predict(f5[mask, :3], base)
    records = []
    for name, columns in sets.items():
        f = f8[:, columns]
        model = fit_projected(f, config['k'], config['seed'], mask=mask)
        labels = predict(f[mask], model)
        counts = np.unique(labels, return_counts=True)[1]
        records.append({'feature_set': name, 'dimensions': len(columns),
            'common_inliers': int(mask.sum()),
            'ARI_vs_3D': float(adjusted_rand_score(base_labels, labels)),
            'PCS': pcs(labels, final[sample][mask]),
            'adjacent_label_agreement': spatial_metrics(grid[sample][mask], labels,
                final[sample][mask], config['grid_shape'])['adjacent_label_agreement'],
            'smaller_cluster_fraction': float(counts.min() / counts.sum())})
    save_csv(out / 'feature_augmentation.csv', records)


def comparison(config, y, final, grid, out):
    f, sample, base, labels = run_main(config, y, final, grid, out)
    yn = normalize(y)
    pca = PCA(n_components=.5, svd_solver='full').fit(yn[sample])
    method_features = {'physical_3D': f, 'PCA_50pct': pca.transform(yn),
        'single_reference_DTW': np.column_stack([final, dtw_distance(
            yn, yn[sample[0]], config['dtw_radius'])])}
    records = []
    for name, ff in method_features.items():
        model = fit_projected(ff[sample], config['k'], config['seed'], config['contamination'])
        ll = predict(ff, model)
        np.savez_compressed(out / (name + '_labels.npz'), labels=ll, grid_pos=grid)
        # PCS in the same method-specific training population as the original pipeline.
        sm = predict(ff[sample][model[2]], model)
        records.append({'method': name, 'training_inliers': int(model[2].sum()),
            'PCS_training_inliers': pcs(sm, final[sample][model[2]]),
            'ARI_full_vs_3D': float(adjusted_rand_score(labels, ll)),
            **spatial_metrics(grid, ll, final, config['grid_shape'])})
    if config.get('include_kshape', False):
        from tslearn.clustering import KShape
        np.random.seed(config['seed'])
        fit_idx = np.sort(np.random.RandomState(config['seed']).choice(
            len(sample), min(20000, len(sample)), replace=False))
        ks = KShape(n_clusters=config['k'], random_state=config['seed'], n_init=1, max_iter=10)
        ks.fit(yn[sample[fit_idx]])
        ll = np.concatenate([ks.predict(yn[i:i + 10000]) for i in range(0, len(yn), 10000)])
        records.append({'method': 'native_KShape', 'training_inliers': len(fit_idx),
            'PCS_training_inliers': pcs(ll[sample], final[sample]),
            'ARI_full_vs_3D': float(adjusted_rand_score(labels, ll)),
            **spatial_metrics(grid, ll, final, config['grid_shape'])})
        np.savez_compressed(out / 'native_KShape_labels.npz', labels=ll, grid_pos=grid)
    save_csv(out / 'method_comparison.csv', records)


def parameter_scan(config, y, final, grid, out):
    f = physical_features(y, final)
    sample = np.sort(np.random.RandomState(config['seed']).choice(
        len(y), min(config['sample_size'], len(y)), replace=False))
    base = fit_projected(f[sample], config['k'], config['seed'], config['contamination'])
    s = base[0].transform(f[sample][base[2]])
    sub = np.random.RandomState(0).choice(len(s), min(8000, len(s)), replace=False)
    records = []
    for seed in config['seeds']:
        for k in config['k_values']:
            ss = s[sub]
            km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(ss)
            reps = ss[pairwise_distances_argmin(km.cluster_centers_, ss)]
            labels = pairwise_distances_argmin(ss, reps)
            if len(np.unique(labels)) < 2:
                continue
            records.append({'seed': seed, 'k': k,
                'silhouette': float(silhouette_score(ss, labels)),
                'CH': float(calinski_harabasz_score(ss, labels)),
                'DB': float(davies_bouldin_score(ss, labels))})
    save_csv(out / 'k_scan.csv', records)
    seed_labels = [predict(f[sample][base[2]], fit_projected(
        f[sample], config['k'], seed, mask=base[2])) for seed in config['seeds']]
    save_csv(out / 'seed_stability.csv', [
        {'seed_a': config['seeds'][i], 'seed_b': config['seeds'][j],
         'ARI_common_inliers': float(adjusted_rand_score(seed_labels[i], seed_labels[j]))}
        for i in range(len(seed_labels)) for j in range(i + 1, len(seed_labels))])
    rates = []
    for rate in config.get('contamination_values', [0, .01, .03, .05, .10]):
        model = fit_projected(f[sample], config['k'], config['seed'], rate)
        ll = predict(f, model)
        rates.append({'contamination': rate, 'k_fixed': config['k'],
                      'training_inliers': int(model[2].sum()),
                      **spatial_metrics(grid, ll, final, config['grid_shape'])})
    save_csv(out / 'contamination_fixed_k.csv', rates)
    diagnostics = []
    for rate in config.get('contamination_values', [0, .01, .03, .05, .10]):
        model = fit_projected(f[sample], config['k'], config['seed'], rate)
        scaled = model[0].transform(f[sample][model[2]])
        take = np.random.RandomState(0).choice(len(scaled), min(8000, len(scaled)), replace=False)
        ss = scaled[take]
        for k in config['k_values']:
            if k < 2 or k >= len(ss):
                continue
            fitted = fit_projected(ss, k, config['seed'], 0)
            ll = predict(ss, fitted)
            if len(np.unique(ll)) > 1:
                diagnostics.append({'contamination': rate, 'k': k,
                    'diagnostic_rows': len(ss),
                    'silhouette': float(silhouette_score(ss, ll)),
                    'CH': float(calinski_harabasz_score(ss, ll)),
                    'DB': float(davies_bouldin_score(ss, ll))})
    save_csv(out / 'contamination_k_scan.csv', diagnostics)



def window_scan(config, root, out):
    if config['input_stage'] != 'decoded_referenced':
        raise ValueError('Window scan needs decoded_referenced input, not an already smoothed array')
    records = []
    partitions = {}
    for window in config.get('windows', [1, 3, 5, 7, 9]):
        c = dict(config, window=window)
        y, final, grid = load_input(c, root)
        f = physical_features(y, final)
        sample = np.sort(np.random.RandomState(c['seed']).choice(
            len(y), min(c['sample_size'], len(y)), replace=False))
        m = fit_projected(f[sample], c['k'], c['seed'], c['contamination'])
        partitions[window] = predict(f, m)
        ss = m[0].transform(f[sample][m[2]])
        take = np.random.RandomState(0).choice(len(ss), min(8000, len(ss)), replace=False)
        for k in c['k_values']:
            km = KMeans(n_clusters=k, n_init=10, random_state=c['seed']).fit(ss[take])
            reps = ss[take][pairwise_distances_argmin(km.cluster_centers_, ss[take])]
            ll = pairwise_distances_argmin(ss[take], reps)
            if len(np.unique(ll)) > 1:
                records.append({'window': window, 'epochs': y.shape[1], 'k': k,
                    'silhouette': float(silhouette_score(ss[take], ll))})
    save_csv(out / 'window_k_scan.csv', records)
    reference = config.get('window_reference', 9)
    if reference not in partitions:
        raise ValueError('window_reference must occur in windows')
    save_csv(out / 'window_stability.csv', [
        {'window': window, 'reference_window': reference,
         'k_fixed': config['k'], 'population': 'all eligible input pixels',
         'ARI_full_vs_reference': float(adjusted_rand_score(partitions[reference], ll))}
        for window, ll in partitions.items()])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['run', 'compare', 'augmentation', 'parameters', 'windows'])
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--input', type=Path, help='Overrides configuration input')
    parser.add_argument('--output', type=Path, help='Overrides configuration output')
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding='utf-8'))
    root = config_path.parent.parent
    if args.input:
        config['input'] = str(args.input.resolve())
    out = args.output.resolve() if args.output else root / config['output']
    out.mkdir(parents=True, exist_ok=True)
    with threadpool_limits(limits=1):
        if args.mode == 'windows':
            window_scan(config, root, out)
            print('Completed window scan')
            return
        y, final, grid = load_input(config, root)
        {'run': run_main, 'compare': comparison, 'augmentation': augmentation,
         'parameters': parameter_scan}[args.mode](config, y, final, grid, out)
    print('Completed:', args.mode, 'pixels:', len(y), 'epochs:', y.shape[1])


if __name__ == '__main__':
    main()
