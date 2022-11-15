#Graphs https://www.pythonguis.com/tutorials/plotting-pyqtgraph/
#https://stackoverflow.com/questions/52716273/python-pyqt-restarting-a-thread-which-is-finished

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from qtwidgets.sliders import QCustomSlider

import sys
from time import sleep
from labequipment.picoscope_daq import PicoScopeDAQ
from equipment import DLSLaser, APD_Task

import pyqtgraph as pg
import numpy as np

type={'channel':'A',
        'samples':3000,
        'sample_rate':2000,
        'coupling':'DC',
        'voltage_range':1,
        'oversampling':10
        }


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
        """Long-running task."""
        
        if self.make_measurement:
            self.apd_obj.setup_channel(samples=1000)
            for i in range(3):
                time, data, _ = self.apd_obj.start(mode='block')
                self.signal.signal.emit(self.make_measurement, time, data)
            self.make_measurement=False

        self.apd_obj.setup_channel()
        self.is_running=True
        while self.is_running:
            time, data, _ = self.apd_obj.start(mode='stream',collect_time=2)
            self.signal.signal.emit(self.make_measurement, time, data)
        self.run()
        
    
    def measure(self):
        self.is_running = False
        self.make_measurement = True
        

        


class Window(QMainWindow):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_apd()
        self.setupUi()
        self.monitor_intensity()
    
    def setup_apd(self):
        self.apd_obj=PicoScopeDAQ()
        self.worker = Detector(self.apd_obj)
        self.worker.signal.signal.connect(self.plot_intensity)
        self.threadpool = QThreadPool()   
       
  
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
        #Graph window
        self.intensity_plot_setup()
        self.correlation_plot_setup()
        self.size_plot_setup()
        

        layout = QGridLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.addWidget(self.intensity_graph, 0, 0, 2, 3)
        layout.addWidget(self.correlation_graph, 2, 0, 2, 3)
        layout.addWidget(self.size_graph, 4, 0, 2, 3)

        intensity_layout = QVBoxLayout()
        intensity_layout.addWidget(self.intensity_title_lbl)
        intensity_layout.addWidget(self.intensity_lbl)
        intensity_layout.addWidget(self.laser_power_sld)
        layout.addLayout(intensity_layout, 0, 3, 2, 1)
        

        layout.addWidget(self.measurement_btn, 2, 3)



        self.centralWidget.setLayout(layout)

    """
    --------------------------------------------------------------------------------------
        Plot setup
    --------------------------------------------------------------------------------------
    """
    

    def intensity_plot_setup(self):
        self.intensity_graph = pg.PlotWidget()
        pen = pg.mkPen(color=(255, 0, 0))
        self.intensity_graph.setLabel('left', 'Intensity')
        self.intensity_graph.setLabel('bottom', 'Time (s)')
        self.intensity_graph.setTitle("Scattering Intensity", color="w", size="30pt")
        self.intensity_line=self.intensity_graph.plot([0,1], [0,0], pen=pen)
    
    def correlation_plot_setup(self):
        self.correlation_graph = pg.PlotWidget()
        pen = pg.mkPen(color=(255, 0, 0))
        self.correlation_graph.setLabel('left', '<I(0)I(t)>')
        self.correlation_graph.setLabel('bottom', 'lag time (s)')
        self.correlation_graph.setTitle("Autocorrelation", color="w", size="30pt")
        self.correlation_line=self.correlation_graph.plot([0,1], [0,0], pen=pen)

    def size_plot_setup(self):
        self.size_graph = pg.PlotWidget()
        pen = pg.mkPen(color=(255, 0, 0))
        self.size_graph.setLabel('left', 'p(x)')
        self.size_graph.setLabel('bottom', 'size nm)')
        self.size_graph.setTitle("Size Distribution", color="w", size="30pt")
        self.size_line=self.size_graph.plot([0,1], [0,0], pen=pen)
        
    def measure_intensity(self):
        """
        Stops monitoring and starts a measurement.
        """
        self.worker.measure()   

    def monitor_intensity(self):
        """
        Sets up a continuous low resolution measurement of scattered intensity.
        """
        self.threadpool.start(self.worker)

    @pyqtSlot(bool, np.ndarray, np.ndarray)
    def plot_intensity(self,measurement, time, intensity_data):
        self.intensity_line.setData(time, intensity_data)
        self.mean_intensity = np.mean(intensity_data)
        self.intensity_lbl.setText(str(self.mean_intensity))












app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec())