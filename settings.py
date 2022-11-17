
"""
APD setup
"""

monitor={'channel':'A',
        'samples':3000,
        'sample_rate':2000,
        'coupling':'DC',
        'voltage_range':1,
        'oversampling':10,
        'trigger':None
        }

measure={'channel':'A',
        'samples':3000,
        'sample_rate':2000,
        'coupling':'DC',
        'voltage_range':1,
        'oversampling':10,
        'trigger':None
        }



"""
Plot setup
"""

intensity_plot = {
                'ylabel':'Intensity',
                'xlabel':'Time (s)',
                'title' : "Scattering Intensity",
                'line_colour' : (255, 0, 0)
            }

correlation_plot = {
                'ylabel':'<I(0)I(t)>',
                'xlabel':'Lag Time (s)',
                'title' : "Autocorrelation Plot",
                'line_colour' : (255, 0, 0)
            }

size_plot = {
                'ylabel':'<I(0)I(t)>',
                'xlabel':'Lag Time (s)',
                'title' : "Autocorrelation Plot",
                'line_colour' : (255, 0, 0)
            }
