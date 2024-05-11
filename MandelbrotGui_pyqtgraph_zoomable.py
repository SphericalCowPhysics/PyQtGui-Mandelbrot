# -*- coding: utf-8 -*-
"""
Created on Sun May  5 08:22:26 2024

@author: chris
"""

# -*- coding: utf-8 -*-
"""
Created on Sat May  4 14:59:35 2024

@author: chris
"""

import sys
import numpy as np

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout, QGridLayout, 
                             QTabWidget, QDoubleSpinBox , QLineEdit, QPushButton, QCheckBox, QLabel,
                             QSizePolicy
                             )
from PyQt6.QtGui import *
import pyqtgraph as pg

from timeit import default_timer as timer



x_min = -2
x_max = 1
y_min = -1
y_max = 1
x_pixels = 1536
y_pixels = 1024
max_iter = 50


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()   
        self.setWindowTitle('Mandelbrot Plotter: bitmapping')
        global x_min 
        global x_max 
        global y_min 
        global y_max 
        global x_pixels
        global y_pixels 
        global max_iter
        
        layout_h = QHBoxLayout()    #Holds plot widget left, and on right: layout_h containing button and timing labels
        layout_v = QVBoxLayout()    #Holds button and timing labels
        layout_v.setContentsMargins(0, 0, 0, 0)
        layout_v.setSpacing(1)
        layout_h.addLayout(layout_v)
        
        #Create a plot widget
        self.plt=pg.plot()
        self.plt.setTitle('Mandelbrot Set')
        self.plt.setLabel('top', f'max iterations={max_iter}')
        self.plt.setLabel('left', 'Imaginary axis')
        self.plt.setLabel('bottom', 'Real axis')
        self.plt.setBackground(background=pg.mkColor(200,200,200))
        self.plt.setGeometry(100, 100, x_pixels, y_pixels)  #Set size of plotting window
        self.plt.setRange(xRange = (x_min, x_max),      #Set default range. When changed by user, graphing will use the new ranges
                          yRange = (y_min, y_max),
                          padding = (0.01*(x_max-x_min)))
 
        self.img = pg.ImageItem()   #Create a widget that will hold mandelbrot bitmap image and colorbar
        self.cmap = pg.ColorMap(pos = None, color =      #a default custom colorbar. Can right click colorbar to choose from presets
                           [pg.mkColor([255, 255, 255]), pg.mkColor([255, 0, 0]), 
                            pg.mkColor([0, 255, 0]), pg.mkColor([0, 0, 255]), 
                            pg.mkColor([0, 0, 0]) ])
        self.img.setColorMap(self.cmap)
        self.color_bar = self.plt.addColorBar(self.img, colorMap=self.cmap, values=(0, max_iter)) 
        self.plt.showAxes(True)  # frame it with a full set of axes
        self.plt.invertY(False)   # vertical axis counts top to bottom
        
        layout_h.addWidget(self.plt)

        btn_plot=QPushButton("Plot Mandelbrot")
        btn_plot.clicked.connect(self.mandelbrot_generate_plotitem)
        layout_v.addWidget(btn_plot)
        
        self.lbl_status=QLabel('Status:\nWaiting...')
        self.lbl_status.adjustSize()
        layout_v.addWidget(self.lbl_status)
        
        self.lbl_calc_time=QLabel('Calculation took:\n...')  
        
        self.lbl_calc_time.adjustSize()
        layout_v.addWidget(self.lbl_calc_time)
        
        self.lbl_plot_time=QLabel('Plotting took:\n...')
        layout_v.addWidget(self.lbl_plot_time)
        self.lbl_plot_time.adjustSize()
        
        self.txtbox_max_iter=QLineEdit('New max iter')
        layout_v.addWidget(self.txtbox_max_iter)
        self.txtbox_max_iter.adjustSize()
        self.txtbox_max_iter.returnPressed.connect(self.max_iter_changed)
        
        
        for l in range(10):
            lbl=QLabel()
            layout_v.addWidget(lbl)

        
        widget_frame = QWidget()
        widget_frame.setLayout(layout_h)
        self.setCentralWidget(widget_frame)
        
    def max_iter_changed(self):
        '''
        Triggered when enter key is pressed on self.txtbox_max_iter. The text of the  

        '''
        global max_iter
        try:        #could probably use self.txtbox_max_iter.setInputMask() to eliminate need for try block
            max_iter = int(self.txtbox_max_iter.text())    #set max_iter to whatever user input 
            self.plt.setLabel('top', f'max iterations={max_iter}')
            self.color_bar.setLevels([0, max_iter])
            self.mandelbrot_generate_plotitem()
            self.txtbox_max_iter.setText('New max iter')
        except:
            self.txtbox_max_iter.setText("Must be an int")
        
        
    def mandelbrot_data_point(self, x, y, max_iteration):
        c = complex(x, y)
        z = 0. + 0.j
        for n in range(max_iteration+1):
            z = z*z + c         #mandelbrot algorithm
            if (abs(z) > 2):    #assume z will rapidly blow up toward inf if its magnitude ever exceeds 2. This is a very conservative value; with faster computation could raise this limit to 5 or 10
                return n
        return n

    def mandelbrot_generate_plotitem(self):
        global x_min, x_max, y_min, y_max, x_pixels, y_pixels, max_iter     #import global variables
        
        #calculations seem to get in the way of using this status label, so for now, print status to console
        self.lbl_status.setText('Status:\nCalculating...')
        print('Calculating...')
        
        time_start = timer()    #start timer to measure calculation and plotting time
 
        #Get current [x,y] range set by user zooming, and set the variables used to calulate mandelbrot min and max to this range
        graph_range = self.plt.viewRange()
        x_min, x_max, y_min, y_max = graph_range[0][0], graph_range[0][1], graph_range[1][0], graph_range[1][1]
        
        image_data = np.zeros(shape = (x_pixels, y_pixels))     #array will be used as image for bitmap. Element values are set to iteration reached by that x,y coordinate up to max_iter
        row, col  = 0, -1   #for indexing the correct element of image_data
        
        for x in np.linspace(x_min, x_max, int(x_pixels)):  
            row = 0
            col += 1
            for y in np.linspace(y_min, y_max, int(y_pixels)):
                #Each pixel gets number [0, max_iter] and colored depending on how many iterations that spot reached
                image_data[col, row] = self.mandelbrot_data_point(x, y, max_iter)      #returns number of iterations reached by c=x+iy between 0 and max_iter        
                row += 1

        time_calc = timer()   
        self.img.clear()
        self.img.setImage(image_data)   #apply bitmap to ImageItem
     
        tr = QTransform() #it should be possible to do this transform using keyword setRect[x, y, w, h] inside ImageItem()
        horiz_scale = ((x_max-x_min)/x_pixels)  #squash down from pixel units to mandelbrot 'c' units
        vert_scale = ((y_max-y_min)/y_pixels)
        tr.scale( horiz_scale, vert_scale)
        horiz_shift = x_pixels * (x_min - 0) / (x_max - x_min)  #pixel units always start at 0, so shift a number of pixels proportional to ratio of distance between 0 and minimum-c-value to c-range 
        vert_shift = y_pixels * (y_min - 0) / (y_max - y_min)
        tr.translate(horiz_shift, vert_shift)
        self.img.setTransform(tr)   #apply transformation to bitmap image
        
        self.plt.addItem( self.img )  # add ImageItem to PlotItem. PlotItem contains axis and colormap, ImageItem holds bitmap
    
        time_plot = timer()
        self.lbl_status.setText(('Status:\nDone!'))
        self.lbl_calc_time.setText(f'Calculation took:\n {(time_calc-time_start):.2f}s')
        self.lbl_plot_time.setText(f'Ploting took:\n {((time_plot-time_calc)*1000):.2f}ms')

"""#Obsolete methods
    def viewRangeChanged(self, view, rang):
        #refresh graph, the hour changes to keep x-axis consistent no matter the scale     
        xMin=rang[0][0]
        xMax=rang[0][1]
        yMin=rang[1][0]
        yMax=rang[1][1]
        print(f"xMin={xMin}, xMax={xMax},\nyMin={yMin}, yMax={yMax}")
    
    
    def mousePressEvent(self, e):
        self.lbl.setText("mousePressEvent")
        #print(plt.viewPixelSize())
        print('x=', e.pos().x())
        print('y=', e.pos().y())
        
    def mouseReleaseEvent(self, e):
        rang = self.plt.viewRange()
        pix_rang = self.plt.viewPixelSize()
        #self.lbl.setText('range=',str(rang))
        #self.lbl.setText('pixel range=',str(pixel_rang))
    
    def create_colormap_brush(self, iterations, num_of_colors = 50, final_color = 0xFFFFFF):
        '''
        converts the number of iterations reached into a color of the format "#000000-#FFFFFF"
        '''
        global max_iter
        hex_color = hex( int ( final_color-(final_color * iterations / max_iter ) ) )[2:]
            
        while len(hex_color) < 6:   #Ensure all hex_colors have exactly 6 characters.
            hex_color = '0' + hex_color

        return ('#' + hex_color + 'FF')  #fill the list with colors in desired forma
    
    def iter_to_rgb(self, iterations, final_color = 0xFFFFFF):
        
        global max_iter
        hex_color = int ( final_color-(final_color * iterations / max_iter) )
        red = hex_color >> 16
        green = (hex_color % 0x10000) >> 8
        blue = hex_color % 0x100
        return [red, green, blue]
"""


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()