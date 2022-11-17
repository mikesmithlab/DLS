from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


from labequipment.laser import Laser, ventus_commands
from labequipment.picoscope_daq import PicoScopeDAQ
from settings import *



class DLSLaser(Laser):
    def __init__(self):
        super(DLSLaser,self).__init__(laser=ventus_commands)
        self.set_power(5)

class APD(PicoScopeDAQ):
    def __init__(self):
        super(APD, self).__init__()



class WorkerSignals(QObject):
    signal = pyqtSignal( bool, np.ndarray, np.ndarray)

# Step 1: Create a worker class
class Detector(QRunnable):

    def __init__(self, apd_obj):
        super(Detector, self).__init__()
        self.apd_obj = apd_obj
        self.is_running = False
        self.make_measurement = False
        self.signal = WorkerSignals()
     

    def run(self):
        """Detector Data Collection."""
        if self.make_measurement:
            self.apd_obj.quick_setup(measure)
            for i in range(3):
                time, data, _ = self.apd_obj.start(mode='block')
                self.signal.signal.emit(self.make_measurement, time, data)
            self.make_measurement=False

        self.apd_obj.quick_setup(monitor)
        self.is_running=True
        while self.is_running:
            time, data, _ = self.apd_obj.start(mode='stream',collect_time=2)
            self.signal.signal.emit(self.make_measurement, time, data)
        self.run()    
    
    def measure(self):
        self.is_running = False
        self.make_measurement = True
        

