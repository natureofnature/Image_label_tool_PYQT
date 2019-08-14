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
from Configure import getConfig,setConfig,getLastDialogue,setPath,getLabelDic
import imghdr
import threading
import numpy as np
from PIL import Image
import os
from PyQt5.QtWidgets import *
import sys
import time
from shutil import copy, move
from Paint_window import popupwindow,my_QLabel_painter
from global_variable import set_screen_size,set_mouse_press_position

Image.MAX_IMAGE_PIXELS = 1000000000

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

   

class my_QLabel(QLabel):
    def __init__(self):
        super(my_QLabel,self).__init__()
        self.setStyleSheet('QFrame {background-color:white;}')
        self.coord = [0,0,0,0]
        self.coord_list = []
        self.position_lists = []
        self.label_lists = [] #store labels
        self.penRectangle = QtGui.QPen(QtCore.Qt.green)
        self.penRectangle.setWidth(1)
        self.released = False
        self.image_scale = 1
        self.label_dic = getLabelDic()
        config_dic,_ = getConfig()
        self.num_class = config_dic['number_classes']
        
    
    #def wheelEvent(self,event):
    #    super().wheelEvent(event)
    #    delta = event.angleDelta()
    #   print(delta)

    def round_coord(self):
        for i in range(len(self.coord)):
            self.coord[i] = int(self.coord[i])

    def set_qimage(self,qimage):
        pass

    def paintEvent(self, event):
        super().paintEvent(event)
        qp = QtGui.QPainter(self)
        br = QtGui.QBrush(QtGui.QColor(100, 10, 10, 40))  
        #qp.setBrush(br)   
        qp.setPen(self.penRectangle)
        if self.released is False:
            qp.drawRect(QtCore.QRect(self.coord[0],self.coord[1],self.coord[2]-self.coord[0],self.coord[3]-self.coord[1]))
        index = 0
        for coord in self.coord_list:
            qp.drawRect(QtCore.QRect(int(coord[0]),int(coord[1]),int(coord[2]-coord[0]),int(coord[3]-coord[1])))
            if index < len(self.label_lists):
                label = self.label_lists[index]
                qp.drawText(int(coord[0])-5,int(coord[1])-5,str(self.label_dic[str(label)]))
                index = index + 1



    def clear_labels(self):
        del(self.coord_list[:])
        del(self.position_lists[:])
        del(self.label_lists[:])


    def mousePressEvent(self, event):
        if len(self.label_lists) != len(self.coord_list):#no label is set
            print(len(self.label_lists))
            return
        self.coord[0] = event.pos().x()
        self.coord[1] = event.pos().y()
        self.coord[2] = event.pos().x()
        self.coord[3] = event.pos().y()
        self.round_coord()
        self.update()
        self.released = False

    def mouseMoveEvent(self, event):
        if len(self.label_lists) != len(self.coord_list):#no label is set
            return
        self.coord[2] = event.pos().x()
        self.coord[3] = event.pos().y()
        self.round_coord()
        self.update()

    def mouseReleaseEvent(self,event):
        if len(self.label_lists) != len(self.coord_list):#no label is set
            return
        self.coord[2] = event.pos().x()
        self.coord[3] = event.pos().y()
        self.round_coord()
        self.update()
        x0,y0,x1,y1 = self.coord
        if x1!=x0 and y1!=y0:
            self.position_lists.append((x0,y0,x1,y1,self.image_scale))
            self.coord_list.append([x0,y0,x1,y1])
            self.ppw = popupwindow(int(self.num_class),self.label_lists)
            self.ppw.show()
        set_mouse_press_position(event.pos().x(),event.pos().y())
        #print(event.pos().x(),event.pos().y())
        self.released = True 


    def setImageScale(self,scale):
        #recover real bounding boxes
        self.image_scale = scale


    def scale(self,scale_rate):
        for coord in self.coord_list: 
            for i in range(4):
                coord[i] =coord[i]*scale_rate

            
    def undo(self):
        if len(self.coord_list) > 0:
            del self.coord_list[-1]
            del self.position_lists[-1]
            del self.label_lists[-1]
           
            self.update()


    def get_bboxes(self):
        return self.position_lists,self.label_lists


class Window(QWidget):

    def set_menu_style(self,menu):
        menu.setStyleSheet("""
        QMenu {
            background-color: rgb(49,49,49);
            color: rgb(255,255,255);
            border: 1px solid ;
        }

        QMenu::item::selected {
            background-color: rgb(30,30,30);

        }
        """)

    def get_attributes(self):
        dic,_ = getConfig()
        self.window_width = int(dic['width'])
        self.window_height= int(dic['height'])
        self.label_mode = dic['label_mode']
        

        
    def __init__(self,screen):

        self.label_mode = "bounding_box_mode"
        #self.label_mode = "painting_mode"

        screen_size = screen.size()
        set_screen_size(screen_size.width(),screen_size.height())
        self.get_attributes()
        QWidget.__init__(self)
        self.setWindowTitle('Label_tool_V2.0.0_by_LWZ')
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        menubar = QMenuBar()
        self.layout.addWidget(menubar, 0, 0,1,1)
        actionFile = menubar.addMenu("File")

        #Part 1
        actionFile.addAction("Select image folder").triggered.connect(self.open_folder)
        actionFile.addAction("Save NG image to ...").triggered.connect(self.set_path_NG)
        actionFile.addAction("Save OK images to ...").triggered.connect(self.set_path_OK)
        actionFile.addSeparator()
        actionFile.addAction("Quit").triggered.connect(self.Quit)
        self.set_menu_style(actionFile)


        #Part 2
        menubar.addAction("Next").triggered.connect(self.next_image)
        

        #menubar.addAction("Previous")
        #part 3
        option_menu = menubar.addMenu("Options")
        option_menu.addAction("Number of classes")
        #option_menu.addAction("Move mode")
        #paint_mode_menu = menubar.addMenu("Label mode")
        #paint_mode_menu.addAction("Bounding box mode").triggered.connect(lambda:self.set_label_mode("bounding_box_mode"))
        #paint_mode_menu.addAction("Paint mode").triggered.connect(lambda:self.set_label_mode("painting_mode"))
        move_mode_menu = option_menu.addMenu("Move mode")
        move_mode_menu.addAction("Keep original images").triggered.connect(self.set_move_false)
        move_mode_menu.addAction("Move original images").triggered.connect(self.set_move_true)
        self.set_menu_style(option_menu)



        self.setGeometry(0,0,self.window_width,self.window_height)
        self.set_layout()
        self.imageLabel = None
        self.set_label_mode()
        #controller
        self.scale_rate = 1.25
        self.scale = 1
        self.image_lists = None
        self.image_name = None
        path_dic = getLastDialogue()
        self.NG_path = path_dic['last_save_folder_NG']
        self.OK_path = path_dic['last_save_folder_OK']
        self.move_mode = False
        self.last_image = "./configure_files/endbg.png"
        self.wheel_angle = 0


    def set_label_mode(self):
        if self.label_mode == "painting_mode":
            self.imageLabel = my_QLabel_painter()
            #self.imageLabel.set_qpainter(self.qpixmap)
        else:
            self.imageLabel = my_QLabel()
        print("Using mode:",self.label_mode)
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.scrollArea = my_QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.image_layout.addWidget(self.scrollArea,0,0,1,1)



    def set_move_false(self):
        self.move_mode = False
        self.printf("Original files will not be removed")

    def set_move_true(self):
        self.move_mode = True
        self.printf("Original files will be removed")

        
    def open_folder(self):
        path_dic = getLastDialogue()
        last_image_dir = path_dic['last_source_folder']
        if not os.path.exists(last_image_dir) or not os.path.isdir(last_image_dir):
            last_image_dir = "./"
        
        path = QFileDialog.getExistingDirectory(self, 'Select directory',directory = last_image_dir)
        while path is None or len(path) == 0:
            path = QFileDialog.getExistingDirectory(self, 'Select directory',directory = last_image_dir)
        setPath('last_source_folder',path)
        self.printf("Selected folder ("+path+")")
        
        self.image_lists = [os.path.join(path,i) for i in os.listdir(path)]
        self.printf("There are "+str(len(self.image_lists))+" files in the selected folder")
        self.image_index = 0

    def set_path_NG(self):
        path_dic = getLastDialogue()
        last_image_dir = path_dic['last_save_folder_NG']
        if not os.path.exists(last_image_dir) or not os.path.isdir(last_image_dir):
            last_image_dir = "./"
        
        path = QFileDialog.getExistingDirectory(self, 'Select directory',directory = last_image_dir)
        while path is None or len(path) == 0:
            path = QFileDialog.getExistingDirectory(self, 'Select directory',directory = last_image_dir)
        setPath('last_save_folder_NG',path)
        self.NG_path = path
        self.printf("NG path is set to: "+self.NG_path)
        
    def set_path_OK(self):
        path_dic = getLastDialogue()
        last_image_dir = path_dic['last_save_folder_OK']
        if not os.path.exists(last_image_dir) or not os.path.isdir(last_image_dir):
            last_image_dir = "./"
        
        path = QFileDialog.getExistingDirectory(self, 'Select directory',directory = last_image_dir)
        while path is None or len(path) == 0:
            path = QFileDialog.getExistingDirectory(self, 'Select directory',directory = last_image_dir)
        setPath('last_save_folder_OK',path)
        self.OK_path = path
        self.printf("OK path is set to: "+self.OK_path)
     

    
    def save_result(self):
        if self.image_name is None:
            return
        if self.OK_path is None or self.NG_path is None:
            self.printf("Please select OK/NG paths first")
        base_name = os.path.basename(self.image_name)
        base_name,_ = os.path.splitext(base_name) 

        target_folder_NG = os.path.join(self.NG_path,base_name)
        target_folder_OK = os.path.join(self.OK_path,base_name)

        
        bbxes,label_lists = self.imageLabel.get_bboxes()
        im = Image.open(self.image_name)
        im_copy = im.copy()
        #self.imageLabel.save_img("/dev/shm/m1/123.bmp")
        print("--->",self.image_name)

        if self.label_mode == "painting_mode":
            status = self.imageLabel.is_labeled()
            print(status)
            if status is True: #has mask
                if not os.path.exists(target_folder_NG):
                    os.makedirs(target_folder_NG)
                print(os.path.join(target_folder_NG,base_name+".bmp"))
                self.imageLabel.save_img(os.path.join(target_folder_NG,base_name+"_labeled.bmp"))
                if self.move_mode is False:
                    copy(self.image_name,os.path.join(target_folder_NG,os.path.basename(self.image_name)))
                else:
                    move(self.image_name,os.path.join(target_folder_NG,os.path.basename(self.image_name)))
                im1 = Image.open(os.path.join(target_folder_NG,base_name+"_labeled.bmp"))
                im2 = Image.open(os.path.join(target_folder_NG,os.path.basename(self.image_name)))
                array1 = np.array(im1)
                array2 = np.array(im2)
                array3 = array1-array2
                im3 = Image.fromarray(array3)
                im3.save(os.path.join(target_folder_NG,base_name+"_mask.bmp"))
            else:
                if self.move_mode is False:
                    copy(self.image_name,os.path.join(self.OK_path,os.path.basename(self.image_name)))
                else:
                    move(self.image_name,os.path.join(self.OK_path,os.path.basename(self.image_name)))





        else:
            if len(bbxes) > 0:
                if not os.path.exists(target_folder_NG):
                    os.makedirs(target_folder_NG)
                #NG images
                try:
                    draw = ImageDraw.Draw(im)
                    with open(os.path.join(target_folder_NG,base_name+".txt"),'w') as f:
                        line_index = 0
                        for box in bbxes:
                            x0,y0,x1,y1,ratio = box 
                            x0 = int(x0/ratio)
                            y0 = int(y0/ratio)
                            x1 = int(x1/ratio)
                            y1 = int(y1/ratio)
                            x0 = min(x0,x1)
                            x1 = max(x0,x1)
                            y0 = min(y0,y1)
                            y1 = max(y0,y1)
                            lab = label_lists[line_index]
                            draw.rectangle(((x0,y0),(x1,y1)),outline='yellow')
                            if line_index > 0:
                                f.write('\n')
                            f.write(str(x0)+","+str(y0)+","+str(x1)+","+str(y1)+","+str(lab))
                            line_index = line_index + 1
                            im_cropped = im_copy.crop((x0,y0,x1,y1))
                            im_cropped.save(os.path.join(target_folder_NG,base_name+"_rect_"+str(line_index)+".jpg"))

                except Exception as e:
                    self.printf(str(e))
                    print(e)
                im.save(os.path.join(target_folder_NG,base_name+"_rect_whole.jpg"))
                if self.move_mode is False:
                    copy(self.image_name,os.path.join(target_folder_NG,os.path.basename(self.image_name)))
                else:
                    move(self.image_name,os.path.join(target_folder_NG,os.path.basename(self.image_name)))

            else:
                #if not os.path.exists(target_folder_OK):
                #    os.makedirs(target_folder_OK)
                print(self.image_name)
                if self.move_mode is False:
                    copy(self.image_name,os.path.join(self.OK_path,os.path.basename(self.image_name)))
                else:
                    move(self.image_name,os.path.join(self.OK_path,os.path.basename(self.image_name)))
                #OK images

            



    def next_image(self):
        if self.image_lists is None:
            self.printf("Please select image folder first")
            return
        if self.imageLabel is None:
            self.printf("Please select labeling mode first")
            return 
        self.save_result()
        if len(self.image_lists) < 1 or self.image_index >=len(self.image_lists):
            self.printf("No remaining images to be labeled, current index: "+str(self.image_index))
            image = QImage(self.last_image)
            qpixmap = QPixmap.fromImage(image)
            self.imageLabel.setPixmap(qpixmap)
            return 
        self.imageLabel.clear_labels()
        while self.image_index < len(self.image_lists):
            image_name = self.image_lists[self.image_index] 
            if os.path.isdir(image_name) or (not imghdr.what(image_name) in ['jpg','jpeg', 'bmp', 'png', 'tiff']):
                self.image_name = None
            else:
                break
            self.image_index = self.image_index + 1
        if self.image_index >=len(self.image_lists):
            self.image_name = None
            return
        self.printf("Processing: [index = "+str(self.image_index+1)+"] "+image_name)

        image = QImage(image_name)
        qpixmap = QPixmap.fromImage(image)
        self.imageLabel.setPixmap(qpixmap)
        self.imageLabel.set_qimage(image)

        scroll_width, scroll_height = self.scrollArea.get_size()
        image_width, image_height = qpixmap.width(),qpixmap.height()
        if image_width == 0 or image_height == 0:
            return
        ratio = min(scroll_width/image_width,scroll_height/image_height)
        self.scale = ratio
        self.imageLabel.setImageScale(self.scale)
        image_width = int(image_width*ratio)
        image_height = int(image_height*ratio)
        self.imageLabel.resize(image_width,image_height)
        self.image_name = image_name
        self.image_index = self.image_index + 1


        
    def Quit(sel):
        sys.exit(0)

    def keyPressEvent(self, event):
        if self.imageLabel is None or self.imageLabel.pixmap() is None:
            return
        if event.key() == QtCore.Qt.Key_Equal:
            self.scale = self.scale * self.scale_rate
            self.imageLabel.setImageScale(self.scale)
            self.imageLabel.resize(self.imageLabel.pixmap().size()*self.scale)
            #set coord
            self.imageLabel.scale(self.scale_rate)
        elif event.key() == QtCore.Qt.Key_Minus:
            self.scale = self.scale / self.scale_rate
            self.imageLabel.setImageScale(self.scale)
            self.imageLabel.resize(self.imageLabel.pixmap().size()*self.scale)
            self.imageLabel.scale(1/self.scale_rate)
        elif event.key()==(Qt.Key_Control and Qt.Key_Z):
            self.imageLabel.undo()

    def wheelEvent(self,event):
        if self.imageLabel is None or self.imageLabel.pixmap() is None:
            return
        super().wheelEvent(event)
        delta = event.angleDelta()
        #self.wheel_angle = self.wheel_angle + delta.y()

        if delta.y() > 0:
            self.scale = self.scale * self.scale_rate
            self.imageLabel.setImageScale(self.scale)
            self.imageLabel.resize(self.imageLabel.pixmap().size()*self.scale)
            #set coord
            self.imageLabel.scale(self.scale_rate)
        else:
            self.scale = self.scale / self.scale_rate
            self.imageLabel.setImageScale(self.scale)
            self.imageLabel.resize(self.imageLabel.pixmap().size()*self.scale)
            self.imageLabel.scale(1/self.scale_rate)


        


        


       
    def set_layout(self):
        self.setStyleSheet("background-color: lightyellow;")
        
        self.image_frame = QFrame(self)
        self.image_frame.setFrameShape(QFrame.StyledPanel)
        self.image_frame.setFrameShadow(QFrame.Raised)
        self.layout.addWidget(self.image_frame,1,0,90,1)
        self.image_layout = QGridLayout() 
        self.image_frame.setLayout(self.image_layout)



        self.text_box= QTextEdit() 
        self.scrollArea_info = my_QScrollArea(self.text_box)
        self.scrollArea_info.setBackgroundRole(QPalette.Dark)
        self.scrollArea_info.setWidget(self.text_box)

        self.info_frame = QFrame(self)
        self.info_frame.setFrameShape(QFrame.StyledPanel)
        self.info_frame.setFrameShadow(QFrame.Raised)
        self.layout.addWidget(self.info_frame,91,0,9,1)
        txt_layout = QGridLayout()
        self.info_frame.setLayout(txt_layout)
        txt_layout.addWidget(self.scrollArea_info,0,0,1,1)


 
    def printf(self,info):
        self.text_box.append(info)





#app = QApplication(sys.argv)
#scr = app.primaryScreen()
#screen = Window(scr)
#screen.show()
#sys.exit(app.exec_())
