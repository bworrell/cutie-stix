#!/usr/bin/env python

# stdlib
import sys
import logging
import argparse

# external
from PyQt4 import QtGui

# internal
from cutiestix import version
from cutiestix import window


# Module-level logger
LOG = logging.getLogger(__name__)


def init_logging(lvl=logging.DEBUG):
    fmt = "[%(asctime)s] [%(levelname)s] %(message)s"
    logging.basicConfig(level=lvl, format=fmt)


def _get_argparser():
    desc = "cutiestix v%s" % (version.__version__)
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument(
        "--log-level",
        default="INFO",
        help="The logging output level.",
        choices=["DEBUG", "INFO", "WARN", "ERROR"]
    )

    return parser


def main():
    # Parse the commandline args
    parser = _get_argparser()
    args = parser.parse_args()

    # Initialize logging
    init_logging(args.log_level)

    # Launch the UI
    LOG.debug("Launching ui")
    app = QtGui.QApplication(sys.argv)
    mainwindow = window.MainWindow()
    mainwindow.show()

    # Wait for it to exit.
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()