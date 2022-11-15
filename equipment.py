
from labequipment.laser import Laser, ventus_commands
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import pandas as pd
import matplotlib.pyplot as plt


class DLSLaser(Laser):
    def __init__(self):
        super(Laser,self).__init__(laser=ventus_commands)
        self.set_power(5)



# Step 1: Create a worker class
class APD_Task(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def measure(self, apd):
        self.apd = apd
        """Long-running task."""
        self.times, self.channelA = self.apd.start(collect_time=5)
        self.finished.emit()

