from labequipment.picoscope_daq import PicoScopeDAQ
from equipment import DLSLaser, APD_Task
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
import sys
import numpy as np
import matplotlib.pyplot as plt



type={'channel':'A',
        'samples':3000,
        'sample_rate':2000,
        'coupling':'DC',
        'voltage_range':1,
        'oversampling':10
        }

#laser=DLSLaser()
apd_obj=PicoScopeDAQ()
apd_obj.setup_channel()
time, data, _ = apd_obj.start(mode='stream')

plt.figure()
plt.plot(time,data)
plt.show()


