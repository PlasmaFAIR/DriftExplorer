from PyQt6.QtWidgets import QMainWindow

from .mainwindow import Ui_MainWindow
from .solver import compute_motion
from .custom_widgets import MatplotlibWidget


class DriftExplorer(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.plot = MatplotlibWidget(self.plot_widget)
        self.positions = None

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

    def run(self):
        self.run_sim()
        self.plot.plot_field(self.magnetic_field, self.positions[-1, :])
        self.plot.plot_force(self.force, self.positions[-1, :])
        self.plot.animate([self.positions])

    def stop(self):
        if self.plot.animation is not None:
            self.plot.animation.pause()

    def run_to_end(self):
        self.run_sim()
        self.plot.plot_field(self.magnetic_field, self.positions[-1, :])
        self.plot.plot_force(self.force, self.positions[-1, :])
        self.plot.plot_all(self.positions)
