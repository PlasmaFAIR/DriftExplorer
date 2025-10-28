from PyQt6.QtWidgets import QMainWindow

from .mainwindow import Ui_MainWindow
from .solver import compute_motion
from .matplotlib_widget import MatplotlibWidget


class DriftExplorer(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.plot = MatplotlibWidget(self.plot_widget)
        self.positions = None

        self.reset()

        self.reset_button.clicked.connect(self.reset)
        self.run_button.clicked.connect(self.run)
        self.stop_button.clicked.connect(self.stop)

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

        self.plot.clear_fig()

    def run(self):
        initial_conditions = [
            self.x_spin_box.value(),
            self.y_spin_box.value(),
            self.z_spin_box.value(),
            self.v_x_spin_box.value(),
            self.v_y_spin_box.value(),
            self.v_z_spin_box.value(),
        ]
        magnetic_field = [
            self.b_x_spin_box.value(),
            self.b_y_spin_box.value(),
            self.b_z_spin_box.value(),
        ]
        force = [
            self.f_x_spin_box.value(),
            self.f_y_spin_box.value(),
            self.f_z_spin_box.value(),
        ]

        self.positions = compute_motion(
            initial_conditions,
            0.0,
            self.charge_spin_box.value(),
            self.mass_spin_box.value(),
            magnetic_field,
            force,
        )

        self.plot.plot_field(magnetic_field, self.positions.max())
        self.plot.animate([self.positions])

    def stop(self):
        if self.plot.animation is not None:
            self.plot.animation.pause()
        
