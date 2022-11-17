#Graphs https://www.pythonguis.com/tutorials/plotting-pyqtgraph/
#https://stackoverflow.com/questions/52716273/python-pyqt-restarting-a-thread-which-is-finished

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from time import sleep
import pyqtgraph as pg
import numpy as np
import os

from qtwidgets.sliders import QCustomSlider
from equipment import DLSLaser, APD, Detector
from settings import *
from plots import Plot


class Window(QMainWindow):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_apd()
        #self.setup_laser()
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

        #Create File Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('&File')
        self.data_menu = self.menu.addMenu('&Data')

        new_project = QAction(QIcon(os.path.join('icons','folder-open-film.png')),'New Project', self)
        close = QAction(QIcon(os.path.join('icons','cross-button.png')),'Close', self)
        view_corr_data = QAction(QIcon(os.path.join('icons','excel.png')),'View Correlation Data', self)
        view_size_data = QAction(QIcon(os.path.join('icons','view_pandas.png')),'View Size Data', self)

        new_project.triggered.connect(self.new_project)
        close.triggered.connect(self.close)


        self.file_menu.addAction(new_project)
        self.file_menu.addAction(close)

        self.data_menu.addAction(view_corr_data)
        self.data_menu.addAction(view_size_data)

        
        



        #Intensity controls
        self.intensity_title_lbl = QLabel("Mean Intensity")
        self.intensity_title_lbl.setFont(QFont('Arial', 20))
        self.intensity_title_lbl.setAlignment(Qt.AlignCenter)
        self.intensity_lbl = QLabel("0")
        self.intensity_lbl.setFont(QFont('Arial', 18))
        self.intensity_lbl.setAlignment(Qt.AlignCenter)
        self.laser_power_sld = QCustomSlider(title='Laser Power (mW)', min_=1, max_=500, step_= 1, spinbox=True, label=True, settings=False)
        self.laser_power_sld.title_label.setFont(QFont('Arial', 16))
        self.laser_power_sld.valueChanged.connect(self.change_laser_power)

        #Measurement contols
        self.num_repeats = QLabel("Num Repeats")
        self.worker.repeat=3
        self.num_measurements =  QSpinBox(self)
        self.num_measurements.setValue(self.worker.repeat)
        self.num_measurements.value=self.worker.repeat
        self.num_measurements.setRange(0,20)
        

        self.num_measurements.valueChanged.connect(lambda x: setattr(self.worker, 'repeat',x))
        self.measurement_btn = QPushButton("Start Measurement", self)
        self.measurement_btn.clicked.connect(self.measure_intensity)

        #Size analysis controls
        self.analyse_btn = QPushButton("Find Size Distribution", self)
        self.analyse_btn.clicked.connect(self.analyse_size)

        #Graph windows
        self.intensity_plot = Plot(intensity_plot)
        self.correlation_plot = Plot(correlation_plot)
        self.size_plot = Plot(size_plot)


        #Put everything into layout
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

        correlation_layout = QVBoxLayout()
        correlation_layout.addWidget(self.num_measurements)
        correlation_layout.addWidget(self.measurement_btn)

        layout.addLayout(correlation_layout, 2, 3)

        layout.addWidget(self.analyse_btn, 4, 3)
        self.centralWidget.setLayout(layout)

    def measure_intensity(self):
        """ Stops monitoring and starts a measurement. """
        self.worker.measure()

    def monitor_intensity(self):
        """ Sets up a continuous low resolution measurement of scattered intensity. """
        self.threadpool.start(self.worker)

    def analyse_size(self):
        pass

    
    def new_project(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        
        self.project_dir_name, ok = QFileDialog.getSaveFileName(self, "Navigate to desired folder and type project name", QDir.homePath(),
                                                            "", options=options)
        os.mkdir(self.project_dir_name)
        self.filename_base = os.path.basename(self.project_dir_name)                                                           
        print(self.filename_base)

    def close(self):
        #self.laser.close()
        #self.apd_obj.close_scope()
        sys.exit()




    @pyqtSlot(bool, np.ndarray, np.ndarray)
    def plot_intensity(self,measurement, time, intensity_data):
        """This plot receives signals sent by the picoscope_daq which is running in a separate thread"""
        self.intensity_plot.line.setData(time, intensity_data)
        self.mean_intensity = np.mean(intensity_data)
        self.intensity_lbl.setText(str(self.mean_intensity))

    @pyqtSlot(int)
    def change_laser_power(self, power):
        """power is integer value in mw between 0 and 500"""
        if (power >=0) & (power <= 500):
            print(power)
            #self.laser.set_power(power)

    










def launch():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    screen_size = app.primaryScreen().size()

    window = Window()
    window.show()
    #Start event loop
    app.exec_()

    

launch()