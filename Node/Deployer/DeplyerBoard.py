#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 15:12:18 2018

@author: root
"""

import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
import Deployer
import os
import zmq

class DeployerBoard(QDialog):
    def __init__(self, buildPath, basePath):
        super(DeployerBoard, self).__init__()
        loadUi('DeployerBoard.ui', self)
        self.buildPath = buildPath
        self.basePath = basePath
        self.dpl = Deployer.Deployer(buildPath, basePath)
        
        self.on_pushButton_refresh_pressed()
        self.progressBar.setValue(0)
        
    def on_pushButton_refresh_pressed(self):
        self.list = self.dpl.getListOfAllImages()
        self.listWidget.clear()
        for item in self.list:
            self.listWidget.addItem(item)
                        
    def on_pushButton_removeAll_pressed(self):
        self.pr('Removing all images...')
        self.dpl.removeAllImages()
        self.pr('Removed all images.')
        self.on_pushButton_refresh_pressed()
            
    def on_pushButton_download_pressed(self):
        self._cIP = self.lineEdit_IP.text()
        self._controllerClerkPort = self.lineEdit_port.text()
        fname = self.lineEdit_fname.text()
        self.progressBar.setValue(0)
        ret = self.__req_clerk_function(fname)
        self.progressBar.setValue(25)
        if ret is None:
            self.pr('Error in getting the function data from Clerk server!')
            self.progressBar.setValue(0)
        self.pr('Function source downloaded. Deploying. This might take a while.')
        self.dpl.deployNewImage(ret['func'], ret['req'], fname)
        self.progressBar.setValue(100)
        self.pr('Completely deployed {}'.format(fname))
        self.on_pushButton_refresh_pressed()
    
    def __req_clerk_function(self, fname):
        ret = self.__req_clerk({'msg':'function?', 'func':fname})
        if ret['msg'] != 'function.':
            return False
        else:
            return ret    
    
    def pr(self, txt):
        self.label_pr.setText(txt)
        QApplication.processEvents()
    
    def __req_clerk(self, req):
        context = zmq.Context()
        self.pr("\tConnecting to Clerk server...")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://{}:{}".format(self._cIP, self._controllerClerkPort))
        socket.send_json(req)
        self.pr("\t\tWaiting for response")
        resp = socket.recv_json()
        return resp
        
app = QApplication(sys.argv)

cwd = os.getcwd()
Node_dir = os.path.dirname(cwd)

buildPath = os.path.join(Node_dir, 'ImagesBuild')
basePath = os.path.join(Node_dir, 'Base')
                         
widget = DeployerBoard(buildPath, basePath)
widget.show()
sys.exit(app.exec_())
