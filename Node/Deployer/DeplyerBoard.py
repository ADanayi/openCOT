#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 15:12:18 2018

@author: root
"""

import sys
import docker
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi


class DeployerBoard(QDialog):
    def __init__(self, *args):
        super(DeployerBoard, self).__init__(*args)
        loadUi('DeployerBoard.ui', self)


app = QApplication(sys.argv)
widget = DeployerBoard()
widget.show()
sys.exit(app.exec_())