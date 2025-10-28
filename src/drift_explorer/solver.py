import numpy as np
from scipy.integrate import ode, solve_ivp


def norm(A):
    Ax, Ay, Az = A
    return np.sqrt(Ax**2 + Ay**2 + Az**2)


def newton(t, Y, q, m, B, F):
    """Computes the derivative of the state vector y according to the equation of motion:
    Y is the state vector (x, y, z, u, v, w) === (position, velocity).
    returns dY/dt.
    """
    x, y, z = Y[0], Y[1], Y[2]
    ux, uy, uz = Y[3], Y[4], Y[5]

    if callable(B):
        B_ = B([x, y, z])  # avoids evaluating B(x, y, z) three times
        Bx, By, Bz = B_[0], B_[1], B_[2]
    else:
        Bx, By, Bz = B

    Fx, Fy, Fz = F

    inverse_mass = 1 / m
    charge_mass_ratio = q * inverse_mass

    ax = charge_mass_ratio * (uy * Bz - uz * By) + inverse_mass * Fx
    ay = charge_mass_ratio * (uz * Bx - ux * Bz) + inverse_mass * Fy
    az = charge_mass_ratio * (ux * By - uy * Bx) + inverse_mass * Fz

    return np.array([ux, uy, uz, ax, ay, az])


def compute_motion(
    initial_conditions,
    t0,
    charge,
    mass,
    B,
    F=[0, 0, 0],
    num_periods=10,
    points_per_period=100,
    method="RK45",
    rtol=None,
    atol=None,
):
    # Particle pusher
    x0, y0, z0 = initial_conditions[:3]

    if callable(B):
        wc = np.abs(charge) * norm(B([x0, y0, z0])) / mass
    else:
        wc = np.abs(charge) * norm(B) / mass

    # number of gyroperiods. dividing by m insures electrons go as far
    # as ions despite gyrating faster
    num_periods = num_periods / mass
    gyroperiod = 2 * np.pi / wc
    t1 = num_periods * gyroperiod

    # Only pass these arguments if set
    kwargs = {}
    if rtol is not None:
        kwargs["rtol"] = rtol
    if atol is not None:
        kwargs["atol"] = atol

    solution = solve_ivp(
        newton,
        [0, t1],
        initial_conditions,
        args=(charge, mass, B, F),
        t_eval=np.linspace(0, t1, int(num_periods) * points_per_period),
        method=method,
        **kwargs,
    )

    return solution.y[:3].T
