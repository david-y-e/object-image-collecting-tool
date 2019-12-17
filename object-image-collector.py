import sys
import cv2
import time
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import rospy
import os
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
# import image_segmentation_black_background
from image_segmentation_black_background import Background_Removal_Black
from image_segmentation_white_background import Background_Removal_White
from image_segmentation_green_background import Background_Removal_Green
from image_segmentation_blue_background import Background_Removal_Blue
from image_segmentation_canny import Background_Removal_Canny
import json


class Capture_UI(QDialog):

	def __init__(self):

		super(Capture_UI,self).__init__()
		loadUi('Capture.ui',self)
		self.setWindowTitle('Capture')

		config_file = open("config.json",'r')
		config = json.load(config_file)

		self.frame = None
		self.class_num = None
		self.sec_per_rev = None
		self.images_per_rev = None
		self.removed_img = None
		self.background = None
		self.threshold = None
		self.folder_path = None
		self.outliner = None
		self.offset_x = 0
		self.offset_y = 0
		self.synthesis_background_folder_path = None
		self.synthesis_save_folder_path = None
		self.preview_state = False
		self.guideline = (255,0,0)
		self.interval = 1
		self.guide_xmin = config["CONFIG"]["GUIDE_XMIN"]
		self.guide_xmax = config["CONFIG"]["GUIDE_YMIN"]
		self.guide_ymin = config["CONFIG"]["GUIDE_XMAX"]
		self.guide_ymax = config["CONFIG"]["GUIDE_YMAX"]
		self.horizontal, self.vertical = 0, 0

		self.guide_offset_scale = config["CONFIG"]["GUIDE_OFFSET_SCALE"]
		self.guide_control_scale = config["CONFIG"]["GUIDE_CONTROL_SCALE"]
		
		self.class_id = config["CONFIG"]["CLASSES"]
		# print(self.class_id)
		
		############## Class_Selector #############
		Class_Selector = self.Class_Selector
		for i in self.class_id:
			Class_Selector.addItem("%s"%i)
		Class_Selector.activated[str].connect(self.class_choice)
		###########################################

		########### Background_Selector ###########
		Background_Selector = self.Background_Selector
		Background_Selector.addItem("Black")
		Background_Selector.addItem("White")
		Background_Selector.addItem("Green")
		Background_Selector.addItem("Blue")
		Background_Selector.addItem("Canny")
		Background_Selector.activated[str].connect(self.background_choice)
		###########################################

		############ Guideline_Selector ###########
		Guideline_Selector = self.Guideline_Selector
		Guideline_Selector.addItem("Red")
		Guideline_Selector.addItem("Green")
		Guideline_Selector.addItem("Blue")
		Guideline_Selector.activated[str].connect(self.guideline_choice)
		###########################################

		############ Button Connection ############
		self.Capture_Btn.clicked.connect(self.capture_screen)
		self.Sec_Per_Rev_Btn.clicked.connect(self.second_per_revolution)
		self.Folder_Browse_Btn.clicked.connect(self.folder_browse)
		self.Number_Of_Images_Btn.clicked.connect(self.number_of_images)
		self.Threshold_Btn.clicked.connect(self.threshold_setup)
		self.Streaming_Start_Btn.clicked.connect(self.start)
		self.Preview_Btn.clicked.connect(self.preview)
		###########################################

		############ Slider Connection ############
		self.horizontal_value = self.Horizontal_Slider
		self.horizontal_value.valueChanged.connect(self.horizontal_change)
		self.vertical_value = self.Vertical_Slider
		self.vertical_value.valueChanged.connect(self.vertical_change)
		self.offset_value_x = self.Offset_Slider_X
		self.offset_value_x.valueChanged.connect(self.offset_change)
		self.offset_value_y = self.Offset_Slider_Y
		self.offset_value_y.valueChanged.connect(self.offset_change)
		###########################################
		###########################################

		############### Calibrating ###############
		self.count = [1]*len(self.class_id)
		self.bridge = CvBridge()
		# Change 'self.image_sub' to your camera topic
		self.image_sub = rospy.Subscriber("%s"%config["CONFIG"]["CAMERA_TOPIC"], Image, self.callback, queue_size=1)
		###########################################

	def callback(self, data):
		try:
			self.frame = self.bridge.imgmsg_to_cv2(data, "rgb8")
		except CvBridgeError as e:
			print(e)

	def calibration(self,class_num):
		if self.folder_path == None:
			print("Problem occurs, check the folder or change the path.")
		else:
			try:
				l = os.listdir(self.folder_path)
				file_names = [x for x in l]
				self.count[class_num] = 1

				for i in file_names:
					if int(i[0:2]) == self.class_num + 1:
						self.count[class_num] = self.count[class_num] + 1
				self.count[class_num] = self.count[class_num] + 1
			except ValueError:
				self.Notice_Status.setText("Check the folder or change the path.")


	def folder_browse(self):
		dialog = QFileDialog()
		self.folder_path = dialog.getExistingDirectory(None,"Select Folder")
		self.Notice_Folder.setText(self.folder_path)

	def preview(self):
		self.preview_state = True
		self.capture_screen()

	def start(self):
		self.timer = QTimer()
		self.timer.timeout.connect(self.streaming_start)
		self.timer.start(1000/60)

	def streaming_start(self):        
		self.guide_xmin = 200 - int(self.horizontal) + self.offset_x
		self.guide_xmax = 440 + int(self.horizontal) + self.offset_x
		self.guide_ymin = 140 - int(self.vertical) + self.offset_y
		self.guide_ymax = 340 + int(self.vertical) + self.offset_y
		self.frame[self.guide_ymin-3:self.guide_ymin,self.guide_xmin:self.guide_xmax] = self.guideline
		self.frame[self.guide_ymax:self.guide_ymax+3,self.guide_xmin:self.guide_xmax] = self.guideline
		self.frame[self.guide_ymin:self.guide_ymax,self.guide_xmin-3:self.guide_xmin] = self.guideline
		self.frame[self.guide_ymin:self.guide_ymax,self.guide_xmax:self.guide_xmax+3] = self.guideline
		self.image = QtGui.QImage(self.frame, self.frame.shape[1], self.frame.shape[0], QImage.Format_RGB888)
		self.pixmapImage = QtGui.QPixmap.fromImage(self.image)
		self.Video_Streaming.setPixmap(self.pixmapImage)

	def threshold_setup(self):
		self.threshold = self.Threshold.text()
		self.Notice_Threshold.setText(self.threshold)

	def removal_result(self):
		label = self.Removal_Result
		if self.preview_state == False:
			label.setPixmap(QPixmap('%s/%.2i_%.4i.png'%(self.folder_path,self.class_num + 1,self.count[self.class_num]-1)))
		else:
			try:
				preview_result = cv2.imread('%s/preview_temp.png'%self.folder_path,cv2.IMREAD_UNCHANGED)
				tempy, tempx, channel = preview_result.shape
				if tempy > tempx:					
					preview_result = cv2.resize(preview_result, (int(round(250*(float(tempx)/float(tempy)))),250), interpolation=cv2.INTER_CUBIC)
				else:
					preview_result = cv2.resize(preview_result, (250,int(round(250*(float(tempy)/float(tempx))))), interpolation=cv2.INTER_CUBIC)
				cv2.imwrite('%s/preview_temp.png'%self.folder_path,preview_result)
				label.setPixmap(QPixmap('%s/preview_temp.png'%self.folder_path))
				self.Notice_Status.setText("Check the preview")
			except AttributeError:
				self.Notice_Status.setText("No object")
			os.remove('%s/preview_temp.png'%self.folder_path)
	def class_choice(self,text):
		self.class_num = self.class_id.index(text)
		self.calibration(self.class_num)
		self.Notice_Status.setText("Starting Number : %d"%self.count[self.class_num])

	def background_choice(self,text):
		self.background = text
		self.Notice_Background.setText(text)

	def guideline_choice(self,text):
		guideline_text = text
		if text == 'Red':
			self.guideline = (255,0,0)
		elif text == 'Blue':
			self.guideline = (0,0,255)
		if text == 'Green':
			self.guideline = (0,255,0)

	def horizontal_change(self):
		self.horizontal = self.horizontal_value.value() * self.guide_control_scale

	def vertical_change(self):
		self.vertical = self.vertical_value.value() * self.guide_control_scale

	def offset_change(self):
		self.offset_x = self.offset_value_x.value() * self.guide_offset_scale
		self.offset_y = self.offset_value_y.value() * self.guide_offset_scale

	def capture_screen(self):
		if self.sec_per_rev==None or self.images_per_rev==None or self.class_num==None or self.threshold==None or self.background==None or self.folder_path==None:
			self.Notice_Status.setText("Please set options")
		else:
			z = 0
			det = 1
			while True:
				if det == 0:
					break
				t = 0
				temp_img = cv2.cvtColor(self.frame,cv2.COLOR_RGB2BGR)
				temp_img = temp_img[self.guide_ymin+2:self.guide_ymax-2,self.guide_xmin+2:self.guide_xmax-2]
				if self.background == 'Black':
					self.removed_img, img_check = Background_Removal_Black(temp_img,int(self.threshold))
				elif self.background == 'White':
					self.removed_img, img_check = Background_Removal_White(temp_img,int(self.threshold))
				elif self.background == 'Green':
					self.removed_img, img_check = Background_Removal_Green(temp_img,int(self.threshold))
				elif self.background == 'Blue':
					self.removed_img, img_check = Background_Removal_Blue(temp_img,int(self.threshold))
				elif self.background == 'Canny':
					self.removed_img, img_check = Background_Removal_Canny(temp_img,int(self.threshold))
				if self.preview_state == False:
					cv2.imwrite('%s/%.2i_%.4i.png'%(self.folder_path, self.class_num + 1, self.count[self.class_num]), self.removed_img)
					self.Notice_Status.setText("Images were saved successfully")
					self.count[self.class_num] = self.count[self.class_num] + 1
					interval = int(self.sec_per_rev) / int(self.images_per_rev)
					rospy.sleep(interval)
					t = t + 100/int(self.images_per_rev)
					self.Progress.setValue(t)
					z = z + 1
					if z > int(self.images_per_rev)-1:
						self.Progress.setValue(100)
						break
				else :
					cv2.imwrite('%s/preview_temp.png'%self.folder_path,self.removed_img)
					det = 0

				self.removal_result()
				self.preview_state = False

	def second_per_revolution(self):
		self.sec_per_rev = self.Sec_Per_Rev.text()
		self.Notice_Sec.setText(self.sec_per_rev)

	def number_of_images(self):
		self.images_per_rev = self.Number_Of_Images.text()
		self.Notice_Images.setText(self.images_per_rev)


def main(args):
	rospy.init_node('Capture_UI', anonymous=True)

if __name__=='__main__':
	main(sys.argv)
	app = QApplication(sys.argv)
	widget = Capture_UI()
	widget.show()
	sys.exit(app.exec_())
