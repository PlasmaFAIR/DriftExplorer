import numpy as np
from scipy.integrate import ode


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

    ax = (q / m) * (uy * Bz - uz * By) + (1 / m) * Fx
    ay = (q / m) * (uz * Bx - ux * Bz) + (1 / m) * Fy
    az = (q / m) * (ux * By - uy * Bx) + (1 / m) * Fz

    return np.array([ux, uy, uz, ax, ay, az])


r = ode(newton).set_integrator("dopri5")


def compute_motion(
    initial_conditions,
    t0,
    charge,
    mass,
    B,
    F=[0, 0, 0],
    num_periods=10,
    randomise=False,
    random_timestep=10,
    points_per_period=100
):
    r.set_initial_value(initial_conditions, t0).set_f_params(charge, mass, B, F)

    # Particle pusher
    x0, y0, z0 = initial_conditions[0], initial_conditions[1], initial_conditions[2]
    positions = [[x0, y0, z0]]

    if callable(B):
        wc = np.abs(charge) * norm(B([x0, y0, z0])) / mass
    else:
        wc = np.abs(charge) * norm(B) / mass

    # number of gyroperiods. dividing by m insures electrons go as far
    # as ions despite gyrating faster
    num_periods = num_periods / mass
    gyroperiod = 2 * np.pi / wc
    t1 = num_periods * gyroperiod
    dt = (1 / points_per_period) * gyroperiod
    timestep_num = 0
    while r.successful() and r.t < t1:
        r.integrate(r.t + dt)
        timestep_num += 1
        # Randomly jiggle velocities
        if randomise and (timestep_num % random_timestep == 0):
            r.y[3] += np.random.random() - 0.5
            r.y[4] += np.random.random() - 0.5
            r.y[5] += np.random.random() - 0.5

        positions.append(r.y[:3])  # keeping only position, not velocity

    positions = np.array(positions)

    return positions
