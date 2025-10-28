import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D # noqa: F401


def animate_particles(
    array_of_positions: list[np.ndarray],
    title: str | None = None,
    nframes: int = 50,
    ax: plt.Axes | None = None,
):
    """Animate particle traces.

    Parameters
    ----------
    array_of_positions : list[np.ndarray]
        List of 3D arrays of particle positions
    B : tuple[int]
        Magnetic field vector
    F : tuple[int]
        Force vector
    nframes : int
        Number of frames

    Examples
    --------
    >>> anim = animate_particles([ion, electron], B, F)

    """
    if not isinstance(array_of_positions, (list, tuple)):
        raise ValueError(
            f"`array_of_positions` must be a sequence of arrays (got {type(array_of_positions)})"
        )

    if len(array_of_positions) == 0:
        raise ValueError("Expected at least one array in `array_of_positions`!")

    positions = array_of_positions
    _step = positions[0].shape[0] // nframes

    if ax is None:
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    else:
        fig = ax.get_figure()

    if title is not None:
        ax.set_title(title, size="xx-large")

    ax.axis(
        (
            min(positions[0][:, 0]),
            max(positions[0][:, 0]),
            min(positions[0][:, 1]),
            max(positions[0][:, 1]),
            min(positions[0][:, 2]),
            max(positions[0][:, 2]),
        )
    )

    artists = [
        ax.plot3D(positions[:0, 0], positions[:0, 1], positions[:0, 2])[0]
        for positions in positions
    ]
    ratios = [int(round(len(p) / len(positions[0]))) for p in positions]

    def update(frame):
        index = _step * frame
        for artist, position, ratio in zip(artists, positions, ratios):
            artist.set_data_3d(
                position[: index * ratio, 0],
                position[: index * ratio, 1],
                position[: index * ratio, 2],
            )
        return artist

    return animation.FuncAnimation(fig, update, frames=nframes, interval=100)
