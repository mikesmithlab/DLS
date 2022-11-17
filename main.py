#Graphs https://www.pythonguis.com/tutorials/plotting-pyqtgraph/
#https://stackoverflow.com/questions/52716273/python-pyqt-restarting-a-thread-which-is-finished

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from time import sleep
import pyqtgraph as pg
import numpy as np


from qtwidgets.sliders import QCustomSlider
from equipment import DLSLaser, APD, Detector
from settings import *
from plots import Plot




        


class Window(QMainWindow):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_apd()
        self.setup_laser()
        self.setupUi()
        self.monitor_intensity()
    
    def setup_apd(self):
        self.apd_obj=APD()
        self.worker = Detector(self.apd_obj)
        self.worker.signal.signal.connect(self.plot_intensity)
        self.threadpool = QThreadPool()   
    
    def setup_laser(self):
        self.laser=DLSLaser()
  
    def setupUi(self):

        self.setWindowTitle("DLS")
      
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.measurement_btn = QPushButton("Start Measurement", self)
        self.measurement_btn.clicked.connect(self.measure_intensity)
        self.intensity_title_lbl = QLabel("Mean Intensity")
        self.intensity_title_lbl.setFont(QFont('Arial', 20))
        self.intensity_title_lbl.setAlignment(Qt.AlignCenter)
        self.intensity_lbl = QLabel("0")
        self.intensity_lbl.setFont(QFont('Arial', 20))
        self.intensity_lbl.setAlignment(Qt.AlignCenter)
        self.laser_power_sld = QCustomSlider(title='Laser Power (mW)', min_=1, max_=500, step_= 1, spinbox=True, label=True)
        self.laser_power_sld.title_label.setFont(QFont('Arial', 16))
        
        #Graph windows
        self.intensity_plot = Plot(intensity_plot)
        self.correlation_plot = Plot(correlation_plot)
        self.size_plot = Plot(size_plot)
        

        layout = QGridLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.addWidget(self.intensity_plot.graph, 0, 0, 2, 3)
        layout.addWidget(self.correlation_plot.graph, 2, 0, 2, 3)
        layout.addWidget(self.size_plot.graph, 4, 0, 2, 3)

        intensity_layout = QVBoxLayout()
        intensity_layout.addWidget(self.intensity_title_lbl)
        intensity_layout.addWidget(self.intensity_lbl)
        intensity_layout.addWidget(self.laser_power_sld)
        layout.addLayout(intensity_layout, 0, 3, 2, 1)
        

        layout.addWidget(self.measurement_btn, 2, 3)
        self.centralWidget.setLayout(layout)

    def measure_intensity(self):
        """ Stops monitoring and starts a measurement. """
        self.worker.measure()   

    def monitor_intensity(self):
        """ Sets up a continuous low resolution measurement of scattered intensity. """
        self.threadpool.start(self.worker)



        


    @pyqtSlot(bool, np.ndarray, np.ndarray)
    def plot_intensity(self,measurement, time, intensity_data):
        """This plot receives signals sent by the picoscope_daq which is running in a separate thread"""
        self.intensity_plot.line.setData(time, intensity_data)
        self.mean_intensity = np.mean(intensity_data)
        self.intensity_lbl.setText(str(self.mean_intensity))










def launch():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())

launch()