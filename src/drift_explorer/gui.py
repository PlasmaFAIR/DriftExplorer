from PyQt6.QtWidgets import QMainWindow

import numpy as np

from .mainwindow import Ui_MainWindow
from .solver import compute_motion
from .custom_widgets import MatplotlibWidget


class DriftExplorer(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.plot = MatplotlibWidget(self.plot_widget)
        self.positions = None
        self.field_plot = None
        self.force_plot = None

        self.method_box.addItems(["RK45", "RK23", "DOP853", "Radau", "BDF", "LSODA"])

        self.reset()

        self.clear_fig_button.clicked.connect(self.plot.clear_fig)
        self.reset_button.clicked.connect(self.reset)
        self.run_button.clicked.connect(self.run)
        self.stop_button.clicked.connect(self.stop)
        self.end_button.clicked.connect(self.run_to_end)

        self.actionExit.triggered.connect(self.close)
        self.action_Run.triggered.connect(self.run)
        self.action_Reset.triggered.connect(self.reset)

        self.xy_axis_view_button.clicked.connect(self.plot.set_view_xy)
        self.xz_axis_view_button.clicked.connect(self.plot.set_view_xz)
        self.yz_axis_view_button.clicked.connect(self.plot.set_view_yz)

        self.perspective_view_button.clicked.connect(self.plot.set_perspective)
        self.orthographic_view_button.clicked.connect(self.plot.set_orthographic)

        self.x_axis_min_box.valueChanged.connect(self.adjust_axis)
        self.x_axis_max_box.valueChanged.connect(self.adjust_axis)
        self.y_axis_min_box.valueChanged.connect(self.adjust_axis)
        self.y_axis_max_box.valueChanged.connect(self.adjust_axis)
        self.z_axis_min_box.valueChanged.connect(self.adjust_axis)
        self.z_axis_max_box.valueChanged.connect(self.adjust_axis)

        self.reset_axis_view_button.clicked.connect(self.reset_axis)
        self.equal_axis_view_button.clicked.connect(self.equal_axis)

    def reset(self):
        self.mass_spin_box.setValue(1.0)
        self.charge_spin_box.setValue(1.0)

        self.x_spin_box.setValue(0.0)
        self.y_spin_box.setValue(1.0)
        self.z_spin_box.setValue(0.0)

        self.v_x_spin_box.setValue(1.0)
        self.v_y_spin_box.setValue(0.0)
        self.v_z_spin_box.setValue(0.1)

        self.f_x_spin_box.setValue(0.0)
        self.f_y_spin_box.setValue(0.0)
        self.f_z_spin_box.setValue(0.0)

        self.b_x_spin_box.setValue(0.0)
        self.b_y_spin_box.setValue(0.0)
        self.b_z_spin_box.setValue(1.0)

        self.method_box.setCurrentIndex(0)
        self.rtol_box.setValue(1.0e-3)
        self.atol_box.setValue(1.0e-6)

        self.plot.clear_fig()

        self.update_axis_boxes()

    @property
    def magnetic_field(self):
        return [
            self.b_x_spin_box.value(),
            self.b_y_spin_box.value(),
            self.b_z_spin_box.value(),
        ]

    @property
    def force(self):
        return [
            self.f_x_spin_box.value(),
            self.f_y_spin_box.value(),
            self.f_z_spin_box.value(),
        ]

    def run_sim(self):
        initial_conditions = [
            self.x_spin_box.value(),
            self.y_spin_box.value(),
            self.z_spin_box.value(),
            self.v_x_spin_box.value(),
            self.v_y_spin_box.value(),
            self.v_z_spin_box.value(),
        ]

        self.positions = compute_motion(
            initial_conditions,
            0.0,
            self.charge_spin_box.value(),
            self.mass_spin_box.value(),
            self.magnetic_field,
            self.force,
            num_periods=self.num_gyroperiods_spinbox.value(),
            points_per_period=self.points_per_period_spinbox.value(),
            method=self.method_box.currentText(),
            rtol=self.rtol_box.value(),
            atol=self.atol_box.value(),
        )

    def single_vector_as_field(self, vector):
        x_min, x_max, y_min, y_max, z_min, z_max = self.plot.get_axis()

        x = np.linspace(x_min, x_max, 5)
        y = np.linspace(y_min, y_max, 5)
        z = np.linspace(z_min, z_max, 5)

        X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
        U = np.ones_like(X) * vector[0]
        V = np.ones_like(Y) * vector[1]
        W = np.ones_like(Z) * vector[2]

        return (X, Y, Z, U, V, W)

    def run(self):
        self.run_sim()

        self.plot.animate([self.positions])
        self.plot_field_and_force()
        self.update_axis_boxes()

    def stop(self):
        if self.plot.animation is not None:
            self.plot.animation.pause()

    def run_to_end(self):
        self.run_sim()

        self.plot.plot_all(self.positions)
        self.plot_field_and_force()
        self.update_axis_boxes()

    def plot_field_and_force(self):
        if self.plot_field_box.isChecked():
            self.field_plot = self.plot.plot_field(
                *self.single_vector_as_field(self.magnetic_field)
            )

        if self.plot_force_box.isChecked():
            self.force_plot = self.plot.plot_field(
                *self.single_vector_as_field(self.force), colour="red"
            )

    def adjust_axis(self):
        limits = (
            self.x_axis_min_box.value(),
            self.x_axis_max_box.value(),
            self.y_axis_min_box.value(),
            self.y_axis_max_box.value(),
            self.z_axis_min_box.value(),
            self.z_axis_max_box.value(),
        )

        self.plot.adjust_axis(limits)

    def equal_axis(self):
        self.plot.adjust_axis("equal")
        self.update_axis_boxes()

    def update_axis_boxes(self):
        x_min, x_max, y_min, y_max, z_min, z_max = self.plot.get_axis()

        self.x_axis_min_box.setValue(x_min)
        self.x_axis_max_box.setValue(x_max)
        self.y_axis_min_box.setValue(y_min)
        self.y_axis_max_box.setValue(y_max)
        self.z_axis_min_box.setValue(z_min)
        self.z_axis_max_box.setValue(z_max)

    def reset_axis(self):
        self.plot.reset_axis()
        self.update_axis_boxes()
