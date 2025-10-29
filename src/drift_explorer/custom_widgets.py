#
# Initial code taken from  http://stackoverflow.com/questions/6723527/getting-pyside-to-work-with-matplotlib
# Additional bits from https://gist.github.com/jfburkhart/2423179
#

import matplotlib

matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

from matplotlib.figure import Figure
import numpy as np

from PyQt6.QtWidgets import QVBoxLayout, QDoubleSpinBox
from PyQt6.QtGui import QValidator

import warnings

from .animation import animate_particles


class ScientificDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDecimals(8)
        self.setMinimum(1e-16)
        self.setMaximum(1e17)

    def textFromValue(self, val):
        return f"{val:5.3e}"

    def valueFromText(self, text):
        return float(text)

    def validate(self, input, pos):
        try:
            float(input)
            valid = QValidator.State.Acceptable
        except ValueError:
            valid = QValidator.State.Invalid

        return (valid, input, pos)

    def stepBy(self, step):
        try:
            old_exponent = int(np.log10(self.value()))
        except OverflowError:
            old_exponent = 0
        new_exponent = old_exponent + step
        self.setValue(float(f"1e{new_exponent}"))


class MatplotlibWidget:
    def __init__(self, parent):
        self.figure = Figure(constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(parent)
        self.mpl_toolbar = NavigationToolbar(self.canvas, parent)
        self._make_axes()
        self.animation = None

        self.grid_layout = QVBoxLayout()
        self.grid_layout.addWidget(self.canvas)
        self.grid_layout.addWidget(self.mpl_toolbar)
        parent.setLayout(self.grid_layout)

        self.callback_id = None

        warnings.filterwarnings(
            "ignore", "Attempting to set identical left == right.*", UserWarning
        )

    def _make_axes(self):
        self.axes = self.figure.add_subplot(111, projection="3d")
        self.axes.set_xlabel("x [m]")
        self.axes.set_ylabel("y [m]")
        self.axes.set_zlabel("z [m]")

    def _clean_axes(self):
        """
        Make sure the figure is in a nice state
        """
        # Get rid of any extra axes
        if isinstance(self.axes, list):
            for axes in self.axes:
                del axes
            self._make_axes()
        else:
            self.axes.clear()

        self.figure.clear()
        self.axes.grid(True)

        # Remove any event callbacks
        if self.callback_id:
            try:
                self.figure.canvas.mpl_disconnect(self.callback_id)
            except TypeError:
                for callback_id in self.callback_id:
                    self.figure.canvas.mpl_disconnect(callback_id)
                self.callback_id = None

    def clear_fig(self):
        """
        Reset the plot widget
        """
        self._clean_axes()
        self._make_axes()
        self.canvas.draw()

    def animate(self, positions):
        self.animation = animate_particles(positions, ax=self.axes)
        self.canvas.draw()

    def plot_field(self, X, Y, Z, U, V, W, colour="black"):
        self.axes.quiver(X, Y, Z, U, V, W, alpha=0.5, color=colour, normalize=True)

    def plot_all(self, positions):
        self.axes.plot3D(positions[:, 0], positions[:, 1], positions[:, 2])
        self.canvas.draw()

    def set_view_xy(self):
        self.axes.view_init(90, -90, 0)
        self.canvas.draw()

    def set_view_xz(self):
        self.axes.view_init(0, -90, 0)
        self.canvas.draw()

    def set_view_yz(self):
        self.axes.view_init(0, 0, 0)
        self.canvas.draw()

    def set_perspective(self):
        self.axes.set_proj_type("persp")
        self.canvas.draw()

    def set_orthographic(self):
        self.axes.set_proj_type("ortho")
        self.canvas.draw()

    def adjust_axis(self, limits):
        self.axes.axis(limits)
        self.canvas.draw()

    def get_axis(self):
        return self.axes.axis()

    def reset_axis(self):
        self.axes.axis("tight")
        self.axes.axis("auto")
        self.canvas.draw()
