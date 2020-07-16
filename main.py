#!/usr/bin/python3
import sys
import enum
from os.path import join, dirname, abspath
import math
import os
import numpy as np
import random
import qtmodern.styles
import qtmodern.windows
import time
import json
import pprint
import queue
import serial
import serial.tools.list_ports as port_list
from qtpy import uic
from qtpy.QtCore import Slot, QTimer, QThread, Signal, QObject, Qt
from qtpy.QtWidgets import QApplication, QMainWindow, QMessageBox, QAction, QDialog, QTableWidgetItem, QLabel
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from collections import deque
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QMenu
from portdetection import DetectDevices
from dispatcher import RxThread

_UI = join(dirname(abspath(__file__)), 'main.ui')

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.widget = uic.loadUi(_UI, self)
        self.devices = DetectDevices()
        self.devices.listUsbPorts()
        self.devices.printUsbPorts()
        #pprint.pprint(self.devices.ports[0][0])
        self.inPort = ''
        self.inSerial = ''

        #self.menuInPort = QMenu()
        
        if len(self.devices.ports) > 0:
            self.comports = self.devices.ports
            self.portAction = QAction(str(self.comports[0][0]), self)
            self.portAction.setCheckable(True)
            self.menuPort.clear()
            self.menuPort.addAction(self.portAction)
            self.portAction.triggered.connect(self.on_portaction_triggered)

            self.connectAction = QAction('Connect', self)
            self.menuOps.addAction(self.connectAction)
            self.connectAction.setObjectName('connectAction')
            self.connectAction.triggered.connect(self.on_connectAction_triggered)
            self.Serial = serial.Serial(self.comports[0][0], baudrate=9600, timeout=0)
            self.rxthread = RxThread(self.Serial, self.write_info)

        if len(self.devices.ports) > 1:
            self.menuInPort.clear()
            for port in self.comports:
                self.menuInPort.addAction(QAction(str(port[0]), self))
        
        if len(self.menuInPort.actions()) > 0:
            print(' ................. ')
            for act in self.menuInPort.actions():
                self.inPort = act.text()
                act.triggered.connect(self.common_ation_trigger)
                print(self.inPort)

    def write_info(self, data_stream):
        if len(data_stream[0]) > 30:
            return
        rcount = self.rxtable.rowCount()
        pprint.pprint(data_stream)
        cntr = 0
        hexstr = ''
        intstr = ''
        txt = ''
        decimals = ''
        str_int_digits = []
        str_hex_digits = []
        str_ampere = ''
        for ttx in data_stream:
            for itx in ttx:
                txt += '{:02X} '.format(int(itx))
                cntr += 1
                if cntr > 2:
                    intstr += '{:04d} '.format(int(hexstr, 16))
                    str_int_digits.append('{:04d}'.format(int(hexstr, 16)))
                    hexstr = ''
                    cntr = 1

                hexstr += '{:02X}'.format(int(itx))
                str_hex_digits.append(hexstr)
                

        if len(str_int_digits) > 7:
            self.lcddcout.display(str(int(str_int_digits[5])))
            self.lcddcin.display(str(int(str_int_digits[6])))
            str_ampere = str_hex_digits[3][-1] + '.' + str_hex_digits[2][-1] + str_hex_digits[1][-1]
            self.lcddcamp.display(float(str_ampere))

        self.rxtable.insertRow(rcount)
        self.rxtable.setItem(rcount,0, QTableWidgetItem(txt))
        self.rxtable.setItem(rcount,1, QTableWidgetItem(intstr))
        if self.isAutoScroll:
            self.rxtable.scrollToBottom()
        self.rxtable.resizeColumnsToContents()
        self.rxtable.resizeRowsToContents()
        pprint.pprint(data_stream)


    def on_connectAction_triggered(self):
        self.rxthread.Start()
        #self.rxthread.thread.start()
        print('Connect Triggered')

    def on_portaction_triggered(self):
        self.portname = self.portAction.text()
        print(str(self.portname))

    def common_ation_trigger(self):
        sender = self.sender()
        print('sender : ' + sender.text())
        self.inPort = sender.text()
        self.inSerial = self.inPort

    isAutoScroll = True
    @Slot()
    def on_btnScroll_clicked(self):
        if self.isAutoScroll:
            self.isAutoScroll = False
            self.btnScroll.setText('X')
        else:
            self.isAutoScroll = True
            self.btnScroll.setText('S')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)
    #qtmodern.styles.light(app)

    mw_class_instance = MainWindow()
    mw = qtmodern.windows.ModernWindow(mw_class_instance)
    #mw.showFullScreen()
    mw.show()
    sys.exit(app.exec_())
