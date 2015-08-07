# stdlib
import sys
import logging

# external
from PyQt4 import QtGui

# internal
from cutiestix import window


# Module-level logger
LOG = logging.getLogger(__name__)


def init_logging():
    fmt = "[%(asctime)s] [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=fmt)


def main():
    init_logging()

    LOG.debug("Launching ui")

    app = QtGui.QApplication(sys.argv)
    mainwindow = window.MainWindow()
    mainwindow.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()