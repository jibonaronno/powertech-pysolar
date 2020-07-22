import sys
import serial
import pprint
import time
import enum
import queue
from queue import Queue
from os.path import join, dirname, abspath
from qtpy.QtCore import Slot, QTimer, QThread, Signal, QObject, Qt, QMutex
import threading


class RxThread(QObject):
    signal = Signal(list)

    def __init__(self, serialport, callback):
        super().__init__()
        self.signal.connect(callback)
        self.serialport = serialport
        self.thread = QThread()
        #self.timer = QTimer()
        #self.timer.setSingleShot(True)
        self.timerStopped = True
        self.thread.started.connect(self.run)
        self.moveToThread(self.thread)

        self.msg1 = []
        self.msg2 = []
        self.flagGlitch = False
        self.flagCatch = False
        self.flagModbus = False

    def Start(self):
        self.thread.start()

    def sendGlitch(self, msg1, msg2):
        self.msg1 = msg1
        self.msg2 = msg2
        self.flagGlitch = True

    def sendCatch(self, msg1):
        self.msg1 = msg1
        self.flagCatch = True

    def sendModbusMsg(self, msg1):
        self.msg1 = msg1
        self.flagModbus = True


    itm = []
    def timeout(self):
        self.timerStopped = True
        self.signal.emit(self.itm)
        self.itm.clear()

    
    @Slot()
    def run(self):
        in_waiting = 0
        unit = b''
        time.sleep(3)
        print('Beep')
        timer = threading.Timer(0.05, self.timeout)
        #timer.start()
        while 1:
            try:
                in_waiting = self.serialport.in_waiting
            except Exception as e:
                print('Ex:0X07 : ' + str(e))
                
            while in_waiting == 0:
                time.sleep(0.001)
                
                if self.flagGlitch:
                    self.flagGlitch = False
                    #self.serialport.write(self.msg)
                    for mms in self.msg1:
                        self.serialport.write([mms])
                    time.sleep(0.075)
                    for mms in self.msg1:
                        self.serialport.write([mms])
                    time.sleep(0.075)
                    for mms in self.msg2:
                        self.serialport.write([mms])
                    time.sleep(0.075)
                    for mms in self.msg2:
                        self.serialport.write([mms])

                if self.flagCatch:
                    self.flagCatch = False
                    for mms in self.msg1:
                        self.serialport.write([mms])

                if self.flagModbus:
                    self.flagModbus = False
                    for mms in self.msg1:
                        self.serialport.write([mms])
                
                try:
                    in_waiting = self.serialport.in_waiting
                except Exception as e:
                    print('Ex:0x08 : ' + str(e))
            try:
                unit = self.serialport.read(in_waiting)
                self.itm.append(unit)
                #pprint.pprint(self.itm)
                if self.timerStopped:
                    del timer
                    timer = threading.Timer(0.05, self.timeout)
                    #timer.cancel()
                    timer.start()
                    self.timerStopped = False
                else:
                    #timer.cancel()
                    timer.interval = 0.1
                    
            except Exception as e:
                print('Ex in sensor Thread readline() 527 : ' + str(e))


