import sys

from PyQt5.QtWidgets import QApplication

from predictionapp.ui import AllView


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ga_view = AllView()
    sys.exit(app.exec_())
