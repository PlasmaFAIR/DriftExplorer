from PyQt6.QtWidgets import QApplication

import sys

from .gui import DriftExplorer

def main():
    app = QApplication(sys.argv)
    window = DriftExplorer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
