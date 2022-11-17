
import pyqtgraph as pg





class Plot:
    def __init__(self, params):
        pen = pg.mkPen(color=params['line_colour'])
        self.graph=pg.PlotWidget()
        
        self.graph.setLabel('left', params['ylabel'])
        self.graph.setLabel('bottom', params['xlabel'])
        self.graph.setTitle(params['title'], color="w", size="30pt")
        self.line=self.graph.plot([0,1], [0,0], pen=pen)