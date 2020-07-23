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

class HtmlWriter(object):
    def __init__(self):
        
        part01 = '''<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Socket Nonblocking & Threading</title>
                <link href='http://fonts.googleapis.com/css?family=Roboto' rel='stylesheet' type='text/css'>
                <!-- BEGIN syntax highlighter -->
                <script type="text/javascript" src="sh/shCore.js"></script>
                <script type="text/javascript" src="sh/shBrushJScript.js"></script>
                <link type="text/css" rel="stylesheet" href="sh/shCore.css"/>
                <link type="text/css" rel="stylesheet" href="sh/shThemeDefault.css"/>
                <link href="https://fonts.googleapis.com/css?family=Gruppo" rel="stylesheet">
                <link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet">
                <script type="text/javascript">
                SyntaxHighlighter.all();
                </script>
                <!-- END syntax highlighter -->

                <link href='http://fonts.googleapis.com/css?family=Inconsolata:400,700' rel='stylesheet' type='text/css'>
                <link rel="stylesheet" href="linuxsetup.css">
            </head>
            <body>
            
            <div style="padding: 20px;font-size: 24px; line-height: 40px">'''
    

