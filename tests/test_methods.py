"""Scientific checks; no field data needed. Run from the package root."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
import unittest
import tempfile
import json
import numpy as np
from scipy.ndimage import uniform_filter1d
from sklearn.metrics import adjusted_rand_score
from radar_zoning import (physical_features, smooth_decoded, fit_projected,
                          predict, spatial_metrics, dtw_distance, load_input)
from public_data import read_rain, rainfall_response


class ScientificChecks(unittest.TestCase):
    def test_polynomial_units_and_curvature(self):
        x = np.arange(15.)
        y = np.array([2 + 3*x, 1 - 2*x + .125*x*x])
        f = physical_features(y, np.array([100., 200.]), extended=True)
        self.assertEqual(f[0, 0], 100.)  # unsmoothed final is a separate input
        self.assertAlmostEqual(f[0, 1], 3.)
        self.assertAlmostEqual(f[1, 2], .125)  # coefficient, not 2*a2
        self.assertAlmostEqual(f[0, 3], 0., places=10)

    def test_smoothing_endpoint_and_crop(self):
        y = np.array([[0., 3., 6., 9., 12., 15., 18.]])
        expected = np.array([[1., 3., 6., 9., 12.]])
        np.testing.assert_allclose(smooth_decoded(y, 3), expected)

    def test_projection_and_full_assignment(self):
        rng = np.random.RandomState(9)
        f = np.r_[rng.normal(-3, .1, (100, 3)), rng.normal(3, .1, (100, 3))]
        m = fit_projected(f, 2)
        self.assertEqual(len(predict(f, m)), 200)
        scaled = m[0].transform(f[m[2]])
        self.assertTrue(all(np.any(np.all(scaled == r, axis=1)) for r in m[1]))
        self.assertEqual(adjusted_rand_score(np.r_[np.zeros(100), np.ones(100)], predict(f, m)), 1.)

    def test_grid_gaps_not_neighboring(self):
        m = spatial_metrics(np.array([0, 2]), np.array([0, 1]), np.array([1., -1.]), [1, 3])
        self.assertIsNone(m['adjacent_label_agreement'])

    def test_dtw_against_independent_recurrence(self):
        a, b = np.array([0., 1., 2., 3.]), np.array([0., 0., 1., 3.])
        d = np.full((5, 5), np.inf);d[0, 0] = 0
        for i in range(1, 5):
            for j in range(1, 5):
                d[i, j] = (a[i-1] - b[j-1])**2 + min(d[i-1,j],d[i,j-1],d[i-1,j-1])
        got = dtw_distance(a[None], b, 50)[0]
        self.assertAlmostEqual(got, np.sqrt(d[-1,-1]))
        self.assertEqual(dtw_distance(a[None], a)[0], 0.)

    def test_input_rejects_fractional_grid_and_matrix_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = {'input': 'a.npz', 'input_stage': 'preprocessed', 'grid_shape': [1, 2]}
            y = np.zeros((2, 4))
            np.savez(root/'a.npz', y_mm=y, final_mm=np.zeros(2), grid_pos=np.array([0., .5]))
            with self.assertRaisesRegex(ValueError, 'integer array'):
                load_input(config, root)
            np.savez(root/'a.npz', y_mm=y, final_mm=np.zeros((2, 1)), grid_pos=np.array([0, 1]))
            with self.assertRaisesRegex(ValueError, 'one-dimensional'):
                load_input(config, root)

    def test_rain_lag_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p/'rain.csv').write_text('date,precip_mm\n2020-01-01,1\n2020-01-03,2\n2020-01-04,0\n')
            (p/'series.csv').write_text('date,cumulative_LOS_mm\n2020-01-01,0\n2020-01-03,5\n2020-01-04,6\n')
            rows, stat = rainfall_response(p/'rain.csv', p/'series.csv', 1)
            self.assertEqual(rows[0]['rain_lag_days'], 2)
            self.assertEqual(rows[0]['increment_mm'], 5.)
            self.assertEqual(rows[0]['rain_mm'], 1.)


if __name__ == '__main__':
    unittest.main()
