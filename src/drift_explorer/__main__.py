from PyQt6.QtWidgets import QApplication

import sys
import signal

from .gui import DriftExplorer

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    window = DriftExplorer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
