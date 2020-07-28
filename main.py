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
import struct

import requests as req

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

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.widget = uic.loadUi(_UI, self)
        self.port_outback = 'NA'
        self.port_sun2000 = 'NA'
        self.devices = DetectDevices()
        self.devices.listUsbPorts()
        #self.devices.printUsbPorts()
        self.comports = self.devices.ports
        for port in self.devices.ports:
            if 'USB' in port[2]:
                print(port[2])
                if 'LOCATION=1-1.3' in port[2]:
                    print(' : PORT OUTBACK : ' + port[0])
                    self.port_outback = port[0]
                if 'LOCATION=1-1.2' in port[2]:
                    print(' : PORT SUN2000 : ' + port[0])
                    self.port_sun2000 = port[0]

            for prt in port:
                pass
                #pprint.pprint(prt)
                #print(str(prt))
        self.outPort = ''
        self.inPort = ''
        self.inSerial = ''
        self.outSerial = ''
        self.rightStackIndex = 0

        self.modbustimer = QTimer(self)
        self.modbustimer.timeout.connect(self.modbustimer_tout)

        self.sched_timer = QTimer(self)
        self.sched_timer.timeout.connect(self.sched_timeout)

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

    def sched_timeout(self):
        res = req.get('http://nervoustech.com:8090/gateway/pinlog.php?dckwhout='+ self.outback_kwh +'&dcinob='+ self.outback_dcin +'&dcoutob=' + self.outback_dcout + '&ackwhsun=0.0' + '&alarmsun=0x00' + '&pv1volt=' + self.PV1volt)
        if 'ok' in res:
            print('Uploaded')
        else:
            print(res)

    def modbustimer_tout(self):
        self.on_btnMbus_clicked()

    def connectModbus(self, modbusPort):
        self.mbSerial = serial.Serial(modbusPort, baudrate=9600, timeout=0)
        self.mbusThread = RxThread(self.mbSerial, self.receiveModbus)
        self.mbusThread.Start()
        
    invVoltage01 = 0.0

    def receiveModbus(self, data_stream):
        idx = 0
        txt = ''
        hexd = []
        hexstr = ''
        hstr = ''
        ttr = []
        if len(data_stream) < 1:
            return
        for ttx in data_stream:
            for itx in ttx:
                txt += '{:02X} '.format(int(itx))
                hexd.append(itx)
                if idx == 3 or idx == 4:
                    hexstr += str(itx)
                idx += 1
        ttr = txt.split(' ')
        try:
            #hstr = '0x' + '{:02X}{:02X}'.format(int(hexd[3]), int(hexd[4]))
            print(ttr[3] + ttr[4] + ttr[5] + ttr[6])
            ######print(ttr[3] + ttr[4])
            #print(str(int(hexstr, 16)))
            #self.invVoltage01 = float('0x' + (ttr[3] + ttr[4] + ttr[5] + ttr[6]))
            #self.lcdinvvolt01.display(self.invVoltage01)
            
            print(str(struct.unpack('!i', bytes.fromhex(ttr[3] + ttr[4]))[0]))

            #Read 4 byte into 32 bits integer value
            #print(str(struct.unpack('!i', bytes.fromhex(ttr[3] + ttr[4] + ttr[5] + ttr[6]))[0]))
            
            #self.lcdkwhinv.display(struct.unpack('!i', bytes.fromhex(ttr[3] + ttr[4] + ttr[5] + ttr[6]))[0])

            self.PV1volt = str(struct.unpack('!i', bytes.fromhex(ttr[3] + ttr[4]))[0])
            
            #Read 16bit integer
            self.lcdkwhinvout.display(struct.unpack('!i', bytes.fromhex(ttr[3] + ttr[4]))[0])

            #Read 32Bit integer
            #self.lcdkwhinvout.display(struct.unpack('!i', bytes.fromhex(ttr[3] + ttr[4] + ttr[5] + ttr[6]))[0])
        
        except Exception as e:
            #pass
            print('0x0000 ' + str(e))
        print('Modbus : ' + txt)
        
    outback_dcin = ''
    outback_dcout = ''
    outback_current = ''
    outback_kwh = ''
    PV1volt = ''

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
                #pprint.pprint(str_int_digits)

                self.lcddcout.display(str(int(str_int_digits[5])))
                self.lcddcin.display(str(int(str_int_digits[6])))
                str_ampere = str(int(str_hex_digits[3][-2:], 16) - 128) # + '.' + str_hex_digits[2][-1] + str_hex_digits[1][-1]
                print('Amp : '+str_hex_digits[3][-2:])
                self.lcddcamp.display(float(str_ampere))
                #pprint.pprint(str_hex_digits)
                print('KWh : ' +  str_hex_digits[9][-2:]) #+ str(int(str_hex_digits[5][-2:], 16)))
                self.lcdkwhob.display(int(str_hex_digits[9][-2:], 16))

                self.outback_dcout = str(int(str_int_digits[5]))
                self.outback_dcin = str(int(str_int_digits[6]))
                self.outback_current = str(int(str_hex_digits[3][-2:], 16) - 128)
                self.outback_kwh = str(int(str_hex_digits[9][-2:], 16))
            except Exception as e:
                print('exc - lcddcamp : ' + str_hex_digits[3] + ' : ' + str(e))

        self.rxtable.insertRow(rcount)
        self.rxtable.setItem(rcount,0, QTableWidgetItem(txt))
        self.rxtable.setItem(rcount,1, QTableWidgetItem(intstr))
        if self.isAutoScroll:
            self.rxtable.scrollToBottom()
        self.rxtable.resizeColumnsToContents()
        self.rxtable.resizeRowsToContents()
        ####pprint.pprint(data_stream)


    def on_connectAction_triggered(self):
        self.inPort = self.port_outback
        self.outPort = self.port_sun2000

        #self.inSerial = serial.Serial(self.inPort, baudrate=9600, timeout=0, parity=serial.PARITY_SPACE, bytesize=serial.SEVENBITS, stopbits=serial.STOPBITS_ONE)
        self.inSerial = serial.Serial(self.inPort, baudrate=9600, timeout=0)
        self.rxthread = RxThread(self.inSerial, self.write_info)
        self.rxthread.Start()

        self.connectModbus(self.outPort)

        time.sleep(3)
        self.modbustimer.start(5000)
        self.sched_timer.start(10000)

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
        #Read KWh
        #self.mbusThread.sendModbusMsg([0x01, 0x03, 0x7D, 0x50, 0x00, 0x02, 0xDC, 0x76])

        #Read PV1 Volt
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
