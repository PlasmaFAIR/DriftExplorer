from drift_explorer import compute_motion

import numpy as np


def test_basic():
    q, m = 1, 1
    t0 = 0
    x0 = np.array([0, 1, 0])
    v0 = np.array([1, 0, 0.1])
    initial_conditions = np.concatenate((x0, v0))

    B = (0, 0, 1)

    ions = compute_motion(initial_conditions, t0, q, m, B)

    x_min = ions[:, 0].min()
    x_max = ions[:, 0].max()
    y_min = ions[:, 1].min()
    y_max = ions[:, 1].max()
    z_min = ions[:, 2].min()
    z_max = ions[:, 2].max()

    assert np.isclose(x_min, -1.0)
    assert np.isclose(x_max, 1.0)
    assert np.isclose(y_min, -1.0)
    assert np.isclose(y_max, 1.0)
    assert np.isclose(z_min, 0.0)
    assert np.isclose(z_max, 2 * np.pi)
