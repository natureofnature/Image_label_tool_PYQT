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
from PyQt5.Qt import QCursor
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
import datetime
from shutil import copy, move,rmtree
from Paint_window import popupwindow,my_QLabel_painter
from global_variable import set_screen_size,set_mouse_press_position

Image.MAX_IMAGE_PIXELS = 1000000000

class my_QScrollArea(QScrollArea):
    def __init__(self,widget=None,key_press_mode="Normal"):
        super(my_QScrollArea,self).__init__()
        self.registered_widget = widget 
        self.key_press_mode = key_press_mode
        #if key_press_mode == "Normal":
            #self.setFocusPolicy(Qt.StrongFocus)
    
    def get_size(self):
        return self.width(),self.height()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if self.registered_widget is not None:
            self.registered_widget.resize(self.width(),self.height())

    def wheelEvent(self,event):
        #override,do nothing
        pass
    def keyPressEvent(self,event):
        if self.key_press_mode== "Normal":
            super().keyPressEvent(event)
        else:
            pass
   

class my_QLabel(QLabel):
    def __init__(self,update_text_key):
        super(my_QLabel,self).__init__()
        self.setStyleSheet('QFrame {background-color:white;}')
        self.update_text_key = update_text_key
        self.coord = [0,0,0,0]
        self.history_all = []
        self.coord_list = []
        self.position_lists = []
        self.label_lists = [] #store labels
        self.window_status = []
        config_dic,_ = getConfig()
        self.bbx_color = config_dic['bbx_color']
        self.ruler_color=config_dic['ruler_color']
        self.color_dic={'green':QtCore.Qt.green,'red':QtCore.Qt.red,'yellow':QtCore.Qt.yellow,'white':QtCore.Qt.white,'blue':QtCore.Qt.blue}
        self.penRectangle = QtGui.QPen(self.color_dic[self.bbx_color])
        self.penRectangle_ruler = QtGui.QPen(self.color_dic[self.ruler_color],1,QtCore.Qt.DashDotLine)
        self.penRectangle.setWidth(1)
        self.released = True
        self.image_scale = 1
        self.label_dic = getLabelDic()
        self.num_class = config_dic['number_classes']
        self.wheel_x = 0
        self.wheel_y = 0
        self.x = 0
        self.y = 0
        self.setMouseTracking(True)

    def set_pen_width(self,value):
        pass
    def setNumClasses(self,value):
        self.num_class= value
        
    def set_bbx_color(self,value):
        self.bbx_color = value
        self.penRectangle = QtGui.QPen(self.color_dic[self.bbx_color])
    def set_ruler_color(self,value):
        self.ruler_color = value
        self.penRectangle_ruler = QtGui.QPen(self.color_dic[self.ruler_color],1,QtCore.Qt.DashDotLine)


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
        if self.released is False:
            qp.setPen(self.penRectangle)
            qp.drawRect(QtCore.QRect(self.coord[0],self.coord[1],self.coord[2]-self.coord[0],self.coord[3]-self.coord[1]))
        qp.setPen(self.penRectangle_ruler)
        qp.drawLine(int(self.coord[2]),0,int(self.coord[2]),20000)
        qp.drawLine(0,int(self.coord[3]),20000,int(self.coord[3]))

        index = 0
        for coord in self.coord_list:
            qp.setPen(self.penRectangle)
            qp.drawRect(QtCore.QRect(int(coord[0]),int(coord[1]),int(coord[2]-coord[0]),int(coord[3]-coord[1])))
            if index < len(self.label_lists):
                label = self.label_lists[index]
                qp.drawText(int(coord[0])-5,int(coord[1])-5,str(self.label_dic[str(label)]))
                index = index + 1



    def clear_labels(self):
        
        del(self.coord_list[:])
        del(self.position_lists[:])
        del(self.label_lists[:])
        self.update()

    def clear_all(self):
        del(self.coord_list[:])
        del(self.position_lists[:])
        del(self.label_lists[:])
        del(self.history_all[:])
    def get_wheel_ratio(self):
        width,height = self.pixmap().width(),self.pixmap().height()
        return self.wheel_x/width,self.wheel_y/height




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
        self.update_text_key('Mouse position',str(int(self.coord[2]/self.image_scale))+","+str(int(self.coord[3]/self.image_scale)))

    def mouseMoveEvent(self, event):
        #tracking mouse position for wheel change
        

        self.wheel_x = event.pos().x()/self.image_scale
        self.wheel_y = event.pos().y()/self.image_scale

        if len(self.label_lists) != len(self.coord_list):#no label is set
            return
        self.coord[2] = event.pos().x()
        self.coord[3] = event.pos().y()
        self.round_coord()
        self.update()
        self.update_text_key('Mouse position',str(int(self.coord[2]/self.image_scale))+","+str(int(self.coord[3]/self.image_scale)))


    def mouseReleaseEvent(self,event):
        self.x = QCursor.pos().x()
        self.y=  QCursor.pos().y()
        if len(self.label_lists) != len(self.coord_list):#no label is set
            return

        self.coord[2] = event.pos().x()
        self.coord[3] = event.pos().y()
        self.round_coord()
        self.update()
        x0,y0,x1,y1 = self.coord
        if x0>x1:
            tmp = x1
            x1 = x0
            x0 = tmp
        if y0>y1:
            tmp = y1
            y1 = y0
            y0 = tmp

        if x1!=x0 and y1!=y0:
            self.position_lists.append((x0,y0,x1,y1,self.image_scale,(self.pixmap().width(),self.pixmap().height())))
            self.coord_list.append([x0,y0,x1,y1])
            if int(self.num_class) > 1:
                self.window_status.append("opened")
                self.ppw = popupwindow(int(self.num_class),self.label_lists,self.window_status,int(self.x),int(self.y))
                self.ppw.show()
            else:
                self.label_lists.append(1)
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
        if len(self.window_status) > 0:
            #pop up window not closed 
            return
        if len(self.coord_list) > 0:
            del self.coord_list[-1]
            del self.position_lists[-1]
            del self.label_lists[-1]
           
            self.update()


    def get_bboxes(self):
        position_lists = self.position_lists.copy()
        label_lists = self.label_lists.copy()
       
        self.history_all.append((position_lists,label_lists))
        return self.position_lists,self.label_lists
    def previous(self):
   
        self.position_lists,self.label_lists= self.history_all[-1]
        for i in range(len(self.position_lists)):
        	x,y,z,w,scale,_ = self.position_lists[i]
        	self.coord_list.append([x/scale*self.image_scale,y/scale*self.image_scale,z/scale*self.image_scale,w/scale*self.image_scale]) 
        del(self.history_all[-1])
        self.update()
        #del(self.history_all[-1])




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
        self.verify_bounding_box = dic['verify_bounding_box']
        self.num_class = dic['number_classes']
        




        

        
    def __init__(self,screen):

        self.label_mode = "bounding_box_mode"
        self.log_file = "./log.txt"
        #self.label_mode = "painting_mode"
        self.last_wheel_pos = [0,0]

        screen_size = screen.size()
        set_screen_size(screen_size.width(),screen_size.height())
        self.get_attributes()
        QWidget.__init__(self)
        self.setWindowTitle('Label_tool_V2.1.0_by_LWZ')
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        menubar = QMenuBar()
        self.layout.addWidget(menubar, 0, 0,1,1)
        actionFile = menubar.addMenu("File")
        #(file_in_origin_folder,file_in_target)
        #if OK, file_in_target is path/name
        #if NG, file_in_target is path
        self.history= []


        self.key_to_display={}
        self.key_to_display['Folder'] = ""
        self.key_to_display['Total file'] = 0
        self.key_to_display['Index'] = 0
        self.key_to_display['Image name'] = ""
        self.key_to_display['Path saving labeled image'] = "Default path"
        self.key_to_display['Path saving unlabeled image'] = "Default path"
        self.key_to_display['Move_mode'] = 'Copy only' 
        self.key_to_display['Number of class'] = self.num_class
        self.key_to_display['Mouse position'] = "0,0"
        




        #Part 1
        actionFile.addAction("Select image folder").triggered.connect(self.open_folder)
        actionFile.addAction("Saving image to ...").triggered.connect(self.set_path_Root)
        #actionFile.addAction("Saving unlabeld image to...").triggered.connect(self.set_path_OK)
        actionFile.addSeparator()
        actionFile.addAction("Quit").triggered.connect(self.Quit)
        self.set_menu_style(actionFile)


        #Part 2
        self.next_action = menubar.addAction("Next (N)")
        self.next_action.triggered.connect(self.next_image)

        #Part 3
        menubar.addAction("Previous (P)").triggered.connect(self.previous)
        menubar.addAction("Undo (Z)").triggered.connect(self.undo)
        

        #menubar.addAction("Previous")
        #part 3
        option_menu = menubar.addMenu("Options")
        class_menu = option_menu.addMenu("Number of classes")
        for i in range(32):
            class_menu.addAction(str(i+1)).triggered.connect(lambda state,arg0=(i+1):self.setClassNumber(arg0))

        bbx_color_menu = option_menu.addMenu("BBx_color")
        ruler_color_menu = option_menu.addMenu("Ruler_color")
        for i in ["red","yellow","white","blue","green"]:
            bbx_color_menu.addAction(i).triggered.connect(lambda state,arg0=i:self.set_bbx_color(arg0))
            ruler_color_menu.addAction(i).triggered.connect(lambda state,arg0=i:self.set_ruler_color(arg0))
        pen_width_menu = option_menu.addMenu("Pen width")
        for i in [5,10,20,30,40,50,60,70,80,100]:
                pen_width_menu.addAction(str(i)).triggered.connect(lambda satte,arg0=i:self.imageLabel.set_pen_width(arg0))
        

        #option_menu.addAction("Move mode")
        #paint_mode_menu = menubar.addMenu("Label mode")
        #paint_mode_menu.addAction("Bounding box mode").triggered.connect(lambda:self.set_label_mode("bounding_box_mode"))
        #paint_mode_menu.addAction("Paint mode").triggered.connect(lambda:self.set_label_mode("painting_mode"))
        move_mode_menu = option_menu.addMenu("Move mode")
        move_mode_menu.addAction("Keep original images").triggered.connect(self.set_move_false)
        move_mode_menu.addAction("Move original images").triggered.connect(self.set_move_true)


        self.set_menu_style(option_menu)



        self.setGeometry(300,300,self.window_width,self.window_height)
        self.set_layout()
        self.imageLabel = None
        self.set_label_mode()
        #controller
        self.scale_rate = 1.25
        self.scale = 1
        self.image_lists = None
        self.image_name = None
        path_dic = getLastDialogue()
        self.NG_path = "Not specified"
        self.OK_path = "Not specified"
        self.last_root_dir = path_dic['last_save_folder_Root']
        self.move_mode = False
        self.last_image = "./configure_files/endbg.png"
        self.first_image="./configure_files/beginbg.png"
        self.wheel_angle = 0

    def set_bbx_color(self,value):
        self.imageLabel.set_bbx_color(value)
    def set_ruler_color(self,value):
        self.imageLabel.set_ruler_color(value)

    def setClassNumber(self,value):
        self.imageLabel.setNumClasses(value)
        self.update_text_key('Number of class',value)
        

    def set_label_mode(self):
        if self.label_mode == "painting_mode":
            self.imageLabel = my_QLabel_painter()
            #self.imageLabel.set_qpainter(self.qpixmap)
        else:
            self.imageLabel = my_QLabel(self.update_text_key)
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
        self.update_text_key('Move_mode','Copy only')
        #self.printf("Original files will not be removed")

    def set_move_true(self):
        self.move_mode = True
        self.update_text_key('Move_mode','Move original image')
        #self.printf("Original files will be removed")

        
    def open_folder(self):
        #reset background
        try:
            self.imageLabel.clear_all()
            del(self.history[:])
        except:
            self.printf("Warning: exception when clearing history")
            pass
        image = QImage(self.first_image)
        qpixmap = QPixmap.fromImage(image)
        self.imageLabel.setPixmap(qpixmap)

        path_dic = getLastDialogue()
        last_image_dir = path_dic['last_source_folder']
        if not os.path.exists(last_image_dir) or not os.path.isdir(last_image_dir):
            last_image_dir = "./"
        
        path = QFileDialog.getExistingDirectory(self, 'Select directory',directory = last_image_dir)
        while path is None or len(path) == 0:
            path = QFileDialog.getExistingDirectory(self, 'Select directory',directory = last_image_dir)
        setPath('last_source_folder',path)
        #self.printf("Selected folder ("+path+")")
        self.update_text_key('Folder', path)
        
        self.image_lists = [os.path.join(path,i) for i in os.listdir(path)]
        
        #self.printf("There are "+str(len(self.image_lists))+" files in the selected folder")
        self.update_text_key('Total file', len(self.image_lists))
        self.image_index = 0
        self.image_name = None
        self.next_action.setText("Display Image")

    def set_path_Root(self):
        path_dic = getLastDialogue()
        self.last_root_dir = path_dic['last_save_folder_Root']
        if not os.path.exists(self.last_root_dir) or not os.path.isdir(self.last_root_dir):
        	self.last_root_dir = "./"
        path = QFileDialog.getExistingDirectory(self, 'Select root directory',directory = self.last_root_dir)
        while path is None or len(path) == 0:
            path = QFileDialog.getExistingDirectory(self, 'Select root directory',directory = self.last_root_dir)
        setPath('last_save_folder_Root',path)
        now_time = datetime.datetime.now()
        time_string = str(now_time.year)+"-"+str(now_time.month)+"-"+str(now_time.day)+"-"+str(now_time.hour)

        self.NG_path = os.path.join(self.last_root_dir,"Labeled_image_"+time_string)
        self.OK_path = os.path.join(self.last_root_dir,"Unlabeld_image_"+time_string)
        if not os.path.exists(self.NG_path):
        	os.makedirs(self.NG_path)
        if not os.path.exists(self.OK_path):
        	os.makedirs(self.OK_path)
        self.update_text_key('Path saving labeled image',self.NG_path)
        self.update_text_key('Path saving unlabeled image',self.OK_path)

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
        #self.printf("NG path is set to: "+self.NG_path)
        self.update_text_key('Path saving labeled image',self.NG_path)
        
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
        #self.printf("OK path is set to: "+self.OK_path)
        self.update_text_key('Path saving unlabeled image',self.OK_path)
     

    
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
        #self.imageLabel.save_img("/dev/shm/m1/123.bmp")
        #print("--->",self.image_name)

        if self.label_mode == "painting_mode":
            im = Image.open(self.image_name)
            im_copy = im.copy()
            status = self.imageLabel.is_labeled()
            if status is True: #has mask
                if not os.path.exists(target_folder_NG):
                    os.makedirs(target_folder_NG)
                #print(os.path.join(target_folder_NG,base_name+".bmp"))
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
                    if self.verify_bounding_box == 'yes':
                        im = Image.open(self.image_name)
                        im = im.convert('RGB')
                       
                        draw = ImageDraw.Draw(im)
                    with open(os.path.join(target_folder_NG,base_name+".txt"),'w') as f:
                        line_index = 0
                        for box in bbxes:
                            x0,y0,x1,y1,ratio,(c_w,c_h) = box 
                            x0 = int(x0/ratio)
                            y0 = int(y0/ratio)
                            x1 = int(x1/ratio)
                            y1 = int(y1/ratio)
                            x0 = max(0,x0)
                            y0 = max(0,y0)
                            x1 = min(x1,c_w)
                            y1 = min(y1,c_h)
                            lab = label_lists[line_index]
                            if self.verify_bounding_box == 'yes':
                                draw.rectangle(((x0,y0),(x1,y1)),outline='yellow')
                            if line_index > 0:
                                f.write('\n')
                            f.write(str(x0)+","+str(y0)+","+str(x1)+","+str(y1)+","+str(lab))
                            line_index = line_index + 1
                            if self.verify_bounding_box == 'yes':
                                im_cropped = im.crop((x0,y0,x1,y1))
                                im_cropped.save(os.path.join(target_folder_NG,base_name+"_rect_"+str(line_index)+".jpg"))
                                

                except Exception as e:
                    self.printf(str(e))
                    print(e)
                if self.verify_bounding_box == 'yes':
                    im.save(os.path.join(target_folder_NG,base_name+"_rect_whole.jpg"))
                
                try:
                    if self.move_mode is False:
                        copy(self.image_name,os.path.join(target_folder_NG,os.path.basename(self.image_name)))
                    else:
                        move(self.image_name,os.path.join(target_folder_NG,os.path.basename(self.image_name)))

                    image_n,target_folder,target_n= self.image_name,target_folder_NG,os.path.join(target_folder_NG,os.path.basename(self.image_name))
                    #("type",index,original_name,new_name,new_folder)
                    self.history.append(('NG',self.image_index-1,image_n,target_n,target_folder))
                except Exception as e:
                    self.printf(str(e))

            else:
                #if not os.path.exists(target_folder_OK):
                #    os.makedirs(target_folder_OK)
                #print(self.image_name)
                try:
                    if self.move_mode is False:
                        copy(self.image_name,os.path.join(self.OK_path,os.path.basename(self.image_name)))
                    else:
                        move(self.image_name,os.path.join(self.OK_path,os.path.basename(self.image_name)))
                    image_n,target_folder,target_n= self.image_name,self.OK_path,os.path.join(self.OK_path,os.path.basename(self.image_name))
                    self.history.append(('OK',self.image_index-1,image_n,target_n,target_folder))
                except Exception as e:
                    self.printf(str(e))
                #OK images

            



    def next_image(self):
        self.scrollArea.setFocus()
        if self.image_lists is None:
            self.printf("Please select image folder first")
            return
        if self.imageLabel is None:
            self.printf("Please select labeling mode first")
            return 
        if not os.path.exists(self.last_root_dir):
        	self.printf("Please set root dir for saving")
        	return

        #-------------------------------------#
        # check and create forlder for saving

        now_time = datetime.datetime.now()
        time_string = str(now_time.year)+"-"+str(now_time.month)+"-"+str(now_time.day)+"-"+str(now_time.hour)
        self.NG_path = os.path.join(self.last_root_dir,"Labeled_image_"+time_string)
        if os.path.exists(self.NG_path): 
            pass
        else:
            os.makedirs(self.NG_path)

          
        now_time = datetime.datetime.now()
        time_string = str(now_time.year)+"-"+str(now_time.month)+"-"+str(now_time.day)+"-"+str(now_time.hour)
        self.OK_path = os.path.join(self.last_root_dir,"Unlabeld_image_"+time_string)
        if os.path.exists(self.OK_path):
        	pass  
        else:  
            os.makedirs(self.OK_path)
           
        self.update_text_key('Path saving labeled image',self.NG_path)
        self.update_text_key('Path saving unlabeled image',self.OK_path)
        #-------------------------------------#
        self.save_result()

        self.imageLabel.clear_labels()
        if len(self.image_lists) < 1 or self.image_index >=len(self.image_lists):
            self.printf("No remaining images to be labeled, current index: "+str(self.image_index))
            self.image_name = None
            image = QImage(self.last_image)
            qpixmap = QPixmap.fromImage(image)
            self.imageLabel.setPixmap(qpixmap)
            return 
        #skip files that are not images
        while self.image_index < len(self.image_lists):
            image_name = self.image_lists[self.image_index] 
            if os.path.isdir(image_name) or (not imghdr.what(image_name) in ['jpg','jpeg', 'bmp', 'png', 'tiff']):
                self.image_name = None
            else:
                break
            self.image_index = self.image_index + 1
            self.update_text_key('Index',self.image_index + 1)
        if self.image_index >=len(self.image_lists):
            self.image_name = None
            self.printf("No remaining images to be labeled, current index: "+str(self.image_index))
            image = QImage(self.last_image)
            qpixmap = QPixmap.fromImage(image)
            self.imageLabel.setPixmap(qpixmap)
            return
        #self.printf("Processing: [index = "+str(self.image_index+1)+"] "+image_name)
        self.update_text_key('Index',self.image_index + 1)
        self.update_text_key('Image name',image_name)

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
        self.next_action.setText("Next (N)")


        
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
        elif event.key()==(Qt.Key_N):
            self.printf("go to next")
            self.next_image() 
        elif event.key()==(Qt.Key_P):
            self.previous()

    def wheelEvent(self,event):
        if self.imageLabel is None or self.imageLabel.pixmap() is None:
            return
        super().wheelEvent(event)
        delta = event.angleDelta()
        #self.wheel_angle = self.wheel_angle + delta.y()
        hz_bar = self.scrollArea.horizontalScrollBar()
        vt_bar = self.scrollArea.verticalScrollBar()
        #print(hz_bar.value())
        #print(vt_bar.value())
        #print(event.x())
        #print(event.y())

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
        width = self.image_frame.frameGeometry().width()
        height = self.image_frame.frameGeometry().height()
        #ratio_x = event.x()/width
        #ratio_y = event.y()/height
        ratio_x,ratio_y = self.imageLabel.get_wheel_ratio()
        hz_bar.setValue(int(hz_bar.maximum()*ratio_x))
        vt_bar.setValue(int(vt_bar.maximum()*ratio_y))


        


        


       
    def set_layout(self):
        self.setStyleSheet("background-color: lightyellow;")
        self.splitter = QSplitter(Qt.Vertical)
        
        self.image_frame = QFrame(self)
        self.image_frame.setFrameShape(QFrame.StyledPanel)
        self.image_frame.setFrameShadow(QFrame.Raised)



        #--window(self.layout)
        #----imageframe(image_layout)
        #----infoframe(txt_laytout)
        #------scrollarea
        #--------text_box
        self.image_layout = QGridLayout() 
        self.image_frame.setLayout(self.image_layout)



        self.text_box= QTextEdit() 
        self.text_box.setReadOnly(True)
        #self.text_box.setMaximumSize(10000000,150)
        self.scrollArea_info = my_QScrollArea(self.text_box,"ignore_key")
        self.scrollArea_info.setBackgroundRole(QPalette.Dark)
        self.scrollArea_info.setWidget(self.text_box)

        self.info_frame = QFrame(self)
        self.info_frame.setFrameShape(QFrame.StyledPanel)
        self.info_frame.setFrameShadow(QFrame.Raised)
        #self.layout.addWidget(self.info_frame,91,0,10,1)
        txt_layout = QGridLayout()
        self.info_frame.setLayout(txt_layout)
        txt_layout.addWidget(self.scrollArea_info,0,0,1,1)
    
        self.splitter.addWidget(self.image_frame)
        self.splitter.addWidget(self.info_frame)
        self.splitter.setSizes([760,240])
        self.layout.addWidget(self.splitter,1,0,90,1)

 
    def printf(self,info):
        self.text_box.clear()
        self.text_box.append(info)
        with open(self.log_file,'a') as f:
            f.write(info+"\n")

    def update_displaying_text(self):
        info = ""
        for i,j in self.key_to_display.items():
            info = info+"["+str(i)+"]: "+str(j)+"\n"

        self.text_box.clear()
        self.text_box.append(info)

    def update_text_key(self,key,value):
        self.key_to_display[key] = value
        with open(self.log_file,'a') as f:
            if key != "Mouse position":
                f.write(str(key)+":->"+str(value)+"\n")
    
        self.update_displaying_text()

    def undo(self):
        self.imageLabel.undo()

    def previous(self):
        self.imageLabel.clear_labels()
        
        if len(self.history) <= 0:
            self.printf("This is already the begining")
            return
        
        image_type, index, image_name,target_name, target_folder = self.history[-1]
        self.image_index = index
        
        if image_name != self.image_lists[self.image_index]:
            self.printf("Inconsistent version")
        if image_type == "NG":
            if not os.path.exists(image_name):
                move(target_name,image_name)
            rmtree(target_folder)
        else:
            if not os.path.exists(image_name):
                move(target_name,image_name)
            else:
                os.remove(target_name)



             
        image = QImage(image_name)
        qpixmap = QPixmap.fromImage(image)
        self.imageLabel.setPixmap(qpixmap)
        self.imageLabel.set_qimage(image)
        self.image_name = image_name
        
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
        self.next_action.setText("Next (N)")



        del(self.history[-1])
        
        self.imageLabel.previous()

        self.update_text_key('Index',self.image_index)
        self.update_text_key('Image name',image_name)




#app = QApplication(sys.argv)
#scr = app.primaryScreen()
#screen = Window(scr)
#screen.show()
#sys.exit(app.exec_())
