'''
    Copyright (C) <2019>  <natureofnature>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''
from PyQt5.QtCore import *
from PIL import Image,ImageDraw
from PyQt5 import QtCore,QtGui
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from Configure import getConfig,setConfig,getLastDialogue,setPath
import imghdr
import threading
import os
from PyQt5.QtWidgets import *
import sys
import time
from shutil import copy, move
from global_variable import get_screen_size,get_mouse_press_position

class my_QScrollArea(QScrollArea):
    def __init__(self,widget=None):
        super(my_QScrollArea,self).__init__()
        self.registered_widget = widget 
    
    def get_size(self):
        return self.width(),self.height()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if self.registered_widget is not None:
            self.registered_widget.resize(self.width(),self.height())

    def wheelEvent(self,event):
        #do nothing
        pass

   



class my_QLabel_painter(QLabel):
    def __init__(self):
        super(my_QLabel_painter,self).__init__()
        self.setStyleSheet('QFrame {background-color:white;}')
        self.coord = [0,0,0,0]
        self.coord_list = []
        self.position_lists = []
        self.penRectangle = QtGui.QPen(QtCore.Qt.green)
        self.penRectangle.setWidth(20)
        self.released = False
        self.image_scale = 1
        self.qpoints = []
        self.last_pos = None
        self.current_pos = None
        self.lines = []
        self.qimage = None
        self.qimage_list = []
        self.counter = 0
        self.is_painting = True

    def set_qimage(self,qimage):
        del(self.qimage_list[:])
        self.qimage = qimage.copy()
        self.qimage_list.append(qimage)

    def get_qimage(self):
        return self.qimage
    def save_img(self,path,img_format="bmp"):
        self.pixmap().save(path,img_format)                #self.update()

    
    #def wheelEvent(self,event):
    #    super().wheelEvent(event)
    #    delta = event.angleDelta()
    #   print(delta)

    def round_coord(self):
        for i in range(len(self.coord)):
            self.coord[i] = int(self.coord[i])

    def paintEvent(self, event):
        super().paintEvent(event)
        '''
        try:
            if self.pixmap() is not None:
                qp.begin(self.pixmap())
        except Exception as e:
            print(e)
            return
        '''
        '''
        if self.released is False:
            qp.drawRect(QtCore.QRect(self.coord[0],self.coord[1],self.coord[2]-self.coord[0],self.coord[3]-self.coord[1]))
        for coord in self.coord_list:
            qp.drawRect(QtCore.QRect(int(coord[0]),int(coord[1]),int(coord[2]-coord[0]),int(coord[3]-coord[1])))
        '''
        if self.qimage is not None:
            qp = QtGui.QPainter(self.qimage)
            #qp.begin(current_pix_map)
            br = QtGui.QBrush(QtGui.QColor(100, 10, 10, 40))  
            #qp.setBrush(br)   
            qp.setPen(self.penRectangle)
            #for qpoint in self.qpoints:
            #    qp.drawPoints(qpoint)
            for line in self.lines:
                qp.drawLine(line[0]/self.image_scale,line[1]/self.image_scale)
            #qp.drawLine(self.last_pos/self.image_scale,self.current_pos/self.image_scale)
            self.counter = self.counter + 1

            if len(self.lines)  > 0  and (self.is_painting is True) :
                current_pix_map = QPixmap.fromImage(self.qimage) 
                self.setPixmap(current_pix_map)
                #self.update()
        del(self.lines[:])
        

        '''
        for line in self.lines:
            qp.drawLine(line[0],line[1])
        '''
        '''
        if self.released is False:
            qp.drawLine(self.last_pos,self.current_pos)
            self.update()
        '''

    def clear_labels(self):
        del(self.coord_list[:])
        del(self.position_lists[:])


    def mousePressEvent(self, event):
        self.is_painting = True
        self.coord[0] = event.pos().x()
        self.coord[1] = event.pos().y()
        self.coord[2] = event.pos().x()
        self.coord[3] = event.pos().y()
        self.round_coord()
        self.qpoints.append(QPoint(event.pos().x(),event.pos().y()))
        self.last_pos = event.pos() 
        self.current_pos = event.pos()
        #self.lines.append((self.last_pos,self.current_pos))
        
        self.update()
        self.released = False

    def mouseMoveEvent(self, event):
        self.last_pos = self.current_pos
        self.coord[2] = event.pos().x()
        self.coord[3] = event.pos().y()
        self.current_pos = event.pos()
        self.round_coord()
        self.qpoints.append(QPoint(event.pos().x(),event.pos().y()))
        self.lines.append((self.last_pos,self.current_pos))
        self.update()
        if self.qimage is not None:
            qp = QtGui.QPainter(self.qimage)
            #qp.begin(current_pix_map)
            br = QtGui.QBrush(QtGui.QColor(100, 10, 10, 40))  
            #qp.setBrush(br)   
            qp.setPen(self.penRectangle)
            #for qpoint in self.qpoints:
            #    qp.drawPoints(qpoint)
            for line in self.lines:
                qp.drawLine(line[0]/self.image_scale,line[1]/self.image_scale)
            self.counter = self.counter + 1

        


    def mouseReleaseEvent(self,event):
        self.coord[2] = event.pos().x()
        self.coord[3] = event.pos().y()
        self.round_coord()
        self.update()
        x0,y0,x1,y1 = self.coord
        if x1!=x0 and y1!=y0:
            self.position_lists.append((x0,y0,x1,y1,self.image_scale))
            self.coord_list.append([x0,y0,x1,y1])
        self.released = True 
        
        if self.qimage is not None:
            #only save copy when mouse is released to undo
            qimage = self.qimage.copy()
            self.qimage_list.append(qimage)

    def setImageScale(self,scale):
        #recover real bounding boxes
        self.image_scale = scale



    def scale(self,scale_rate):
        for coord in self.coord_list: 
            for i in range(4):
                coord[i] =coord[i]*scale_rate

        '''
        for line in self.lines:
            point0,point1 = line
            point0.setX(point0.x()*scale_rate)
            point0.setY(point0.y()*scale_rate)
            point1.setX(point1.x()*scale_rate)
            point1.setY(point1.y()*scale_rate)
       '''
            
    def undo(self):
        self.is_painting = False
        if len(self.coord_list) > 0:
            del(self.coord_list[-1])
            self.update()
        if len(self.qimage_list) > 1:
            #print(len(self.qimage_list))
            del(self.qimage_list[-1])
            self.qimage = self.qimage_list[-1].copy()
            current_pix_map = QPixmap.fromImage(self.qimage) 
            self.setPixmap(current_pix_map)
            #self.update()

    def is_labeled(self):
        return len(self.qimage_list) > 1

    def get_bboxes(self):
        return self.position_lists


class popupwindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        w_w,w_h = get_screen_size()
        self.setWindowTitle('Paint on the target')
        x,y = get_mouse_press_position()
        #print(x,y)
        self.setGeometry(x,y,500,500)
        #self.setGeometry(int(w_w/2),int(w_h/2),500,500)
        self.raise_()
        self.set_layout()

    def set_layout(self):
        self.setStyleSheet("background-color: lightyellow;")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        menubar = QMenuBar()
        actionFile = menubar.addMenu("File")
        self.layout.addWidget(menubar, 0, 0,1,1)
        actionFile.addAction("Select image folder")
        self.button_frame = QFrame(self)
        self.button_frame.setFrameShape(QFrame.StyledPanel)
        self.button_frame.setFrameShadow(QFrame.Raised)
        self.layout.addWidget(self.button_frame,1,0,30,1)


        self.imageLabel = my_QLabel_painter()
        #self.imageLabel.set_qpainter(self.qpixmap)
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.scrollArea = my_QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)


        self.layout.addWidget(self.scrollArea,31,0,60,1)

 


    
