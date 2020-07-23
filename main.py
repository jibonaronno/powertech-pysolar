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
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

#from pymodbus.client.asynchronous import Modbus

_UI = join(dirname(abspath(__file__)), 'main.ui')

'''
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
'''

UNIT = 0x1

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.widget = uic.loadUi(_UI, self)
        self.devices = DetectDevices()
        self.devices.listUsbPorts()
        self.devices.printUsbPorts()
        self.comports = self.devices.ports
        #pprint.pprint(self.devices.ports[0][0])
        self.outPort = ''
        self.inPort = ''
        self.inSerial = ''
        self.outSerial = ''
        self.rightStackIndex = 0

        #self.menuInPort = QMenu()
        
        '''if len(self.devices.ports) > 0:
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
            self.outSerial = serial.Serial(self.comports[0][0], baudrate=9600, timeout=0)
            self.rxthread = RxThread(self.outSerial, self.write_info)'''

        if len(self.devices.ports) > 0:
            self.menuPort.clear()
            for port in self.comports:
                self.menuPort.addAction(QAction(str(port[0]), self))

        if len(self.menuPort.actions()) > 0:
            print(' Out ................. ')
            for act in self.menuPort.actions():
                self.outPort = act.text()
                act.setCheckable(True)
                act.triggered.connect(self.common_outport_ation_trigger)

        if len(self.devices.ports) > 0:
            self.menuInPort.clear()
            for port in self.comports:
                self.menuInPort.addAction(QAction(str(port[0]), self))
        
        if len(self.menuInPort.actions()) > 0:
            print(' In ................. ')
            for act in self.menuInPort.actions():
                self.inPort = act.text()
                act.setCheckable(True)
                act.triggered.connect(self.common_inport_ation_trigger)

        self.connectAction = QAction('Connect', self)
        self.menuOps.addAction(self.connectAction)
        self.connectAction.setObjectName('connectAction')
        self.connectAction.triggered.connect(self.on_connectAction_triggered)

        self.rightStack.setCurrentIndex(0)

        ##self.connectModbus()

        '''try:
            self.client = ModbusClient(method='rtu', port='COM10', timeout=0.5, baudrate=9600, parity='N')
            self.client.connect()
        except Exception as e:
            print('Exc: ModbusClient : ' + str(e))

        try:
            self.rr = self.client.read_holding_registers(32016, 1, unit=1)
        except Exception as e:
            print('Exc readHoldingReg : ' + str(e))
        finally:
            print('Data : ')
            try:
                pprint.pprint(self.rr.registers)
            except:
                print('ERR')'''

    def connectModbus(self):
        self.mbSerial = serial.Serial('COM10', baudrate=9600, timeout=0)
        self.mbusThread = RxThread(self.mbSerial, self.receiveModbus)
        self.mbusThread.Start()
        
    invVoltage01 = 0

    def receiveModbus(self, data_stream):
        idx = 0
        txt = ''
        hexd = []
        hexstr = ''
        if len(data_stream) < 1:
            return
        for ttx in data_stream:
            for itx in ttx:
                txt += '{:02X} '.format(int(itx))
                if idx == 3 or idx == 4:
                    hexd.append(itx)
                    hexstr += str(itx)
                idx += 1
        try:
            self.invVoltage01 = int(hexstr, 16)
        except:
            print('0x000000000000000000000000000000000000000')
        print('Modbus : ' + txt)
        self.lcdinvvolt01.display(self.invVoltage01)

    def write_info(self, data_stream):
        if len(data_stream) < 1:
            return
        if len(data_stream[0]) > 40:
            return
        rcount = self.rxtable.rowCount()
        ####pprint.pprint(data_stream)
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
            try:
                self.lcddcout.display(str(int(str_int_digits[5])))
                self.lcddcin.display(str(int(str_int_digits[6])))
                str_ampere = str_hex_digits[3][-1] + '.' + str_hex_digits[2][-1] + str_hex_digits[1][-1]
                self.lcddcamp.display(float(str_ampere))
            except:
                print('exc - lcddcamp')

        self.rxtable.insertRow(rcount)
        self.rxtable.setItem(rcount,0, QTableWidgetItem(txt))
        self.rxtable.setItem(rcount,1, QTableWidgetItem(intstr))
        if self.isAutoScroll:
            self.rxtable.scrollToBottom()
        self.rxtable.resizeColumnsToContents()
        self.rxtable.resizeRowsToContents()
        ####pprint.pprint(data_stream)


    def on_connectAction_triggered(self):

        #self.inSerial = serial.Serial(self.inPort, baudrate=9600, timeout=0, parity=serial.PARITY_SPACE, bytesize=serial.SEVENBITS, stopbits=serial.STOPBITS_ONE)
        self.inSerial = serial.Serial(self.inPort, baudrate=9600, timeout=0)
        self.rxthread = RxThread(self.inSerial, self.write_info)
        self.rxthread.Start()
        #self.rxthread.thread.start()
        print('Connect Triggered')

    def on_portaction_triggered(self):
        self.portname = self.portAction.text()
        print(str(self.portname))

    def common_inport_ation_trigger(self):
        sender = self.sender()
        #print('sender : ' + sender.text())
        self.inPort = sender.text()
        print('IN : ' + self.inPort)
        self.inSerial = self.inPort

    def common_outport_ation_trigger(self):
        sender = self.sender()
        #print('sender : ' + sender.text())
        self.outPort = sender.text()
        print('OUT : ' + self.outPort)
        self.outSerial = self.outPort

    isAutoScroll = True
    @Slot()
    def on_btnScroll_clicked(self):
        if self.isAutoScroll:
            self.isAutoScroll = False
            self.btnScroll.setText('X')
        else:
            self.isAutoScroll = True
            self.btnScroll.setText('S')

    @Slot()
    def on_btnSnd_clicked(self):
        msg1 = [0x00, 0x04, 0x00, 0x01, 0x00, 0xFF, 0x01, 0x04]
        msg2 = [0x00, 0x03, 0x01, 0xC9, 0x00, 0x83, 0x01, 0x50 ]
        self.rxthread.sendGlitch(msg1, msg2)

    @Slot()
    def on_btnSnd2_clicked(self):
        msg1 = [0x00, 0x04, 0x00, 0x01, 0x00, 0xFF, 0x01, 0x04, 0x00, 0x03, 0x01, 0xC9, 0x00, 0x83, 0x01, 0x50]
        self.rxthread.sendCatch(msg1)

    @Slot()
    def on_btnPage2_clicked(self):
        if self.rightStackIndex == 0:
            self.rightStack.setCurrentIndex(1)

    @Slot()
    def on_btnClrtbl_clicked(self):
        if self.rxtable.rowCount() > 5:
            self.rxtable.setRowCount(5)

    @Slot()
    def on_btnMbus_clicked(self):
        self.mbusThread.sendModbusMsg([0x01, 0x03, 0x7D, 0x10, 0x00, 0x01, 0x9D, 0xA3])
        '''try:
            self.rr = self.client.read_holding_registers(32016, 1, unit=1)
        except Exception as e:
            print('Exc : modbus read holding' + str(e))
        finally:
            print('----------DATA : ')
            try:
                pprint.pprint(self.rr.registers)
            except:
                print('ERR 2')'''
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)
    #qtmodern.styles.light(app)

    mw_class_instance = MainWindow()
    mw = qtmodern.windows.ModernWindow(mw_class_instance)
    #mw.showFullScreen()
    mw.show()
    sys.exit(app.exec_())
