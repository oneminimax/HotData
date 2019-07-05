
from PyQt5.QtWidgets import QWidget,QApplication, QMainWindow,QLabel,QLineEdit, QPushButton, QCheckBox, QComboBox, QLayout, QHBoxLayout, QVBoxLayout, QGridLayout, QFileDialog, QColorDialog
from PyQt5.QtCore import QThreadPool, Qt
import sys

import numpy as np

import time

import pyqtgraph as pg

# from pint import UnitRegistry

# sys.path.append("/Users/oneminimax/Documents/Projets Programmation")

from AsciiDataFile.Readers import MDDataFileReader as Reader
from AsciiDataFile.HotReader import HotReader
from HotDataFollowerQt import DataFileFollower, DataPathFollower
import UnitModule as UM

# default_data_path = r'/Users/maximedion/Documents/Projets Physique/2019/PCCO Hall/Data Files/20180705A/isotherms'
default_data_path = r'/Users/maximedion/Documents/Projets Programmation/HotData/Data'

class DataHandle(object):

    def __init__(self,HDV,data_reader):

        self.HDV = HDV
        self.data_reader = data_reader

        self.column_names = self._get_column_names()
        self.column_units = self._get_column_units()
        
        self.follower = DataFileFollower(data_reader)
        self.follower.new_data_signal.connect(self.new_data)
        self.following = False

        self.pen = pg.mkPen()
        
        self.max_values = np.zeros((len(self.column_names),))
        self.data_plot = []
        self.data_item = []

        self.description = self.follower.get_description()
        self.visible = True

    def __del__(self):
        
        if self.data_plot:
            del(self.data_plot)
        if self.data_item:
            del(self.data_item)

    def _get_column_names(self):

        return self.data_reader.data_container.get_column_names()

    def _get_column_units(self):

        unitLabelList = self.data_reader.data_container.get_column_units()
        column_units = list()
        for unitLabel in unitLabelList:
            column_units.append(UM.make_unit(unitLabel))

        return column_units

    def setDataPlot(self,data_plot):

        self.data_plot = data_plot

    def setDataItem(self,data_item):

        self.data_item = data_item

    def setColor(self,color):

        self.pen.setColor(color)
        self.data_plot.setPen(self.pen)

    def follow(self):

        if not self.following:
            self.follower.start()
            self.following = True
        else:
            self.follower.unpause()

    def pause_follow(self):

        self.follower.pause()

    def stop_follow(self):

        if self.following:
            self.follower.stop()
            self.following = False

    def new_data(self):

        self.HDV.update_plot(self)

    def show(self):

        if not self.visible:
            self.HDV.axes.addItem(self.data_plot)
            self.visible = True

    def hide(self):

        if self.visible:
            self.HDV.axes.removeItem(self.data_plot)
            self.visible = False

    def get_xy(self,XFieldName,YFieldName):

        X = self.data_reader.data_container.get_column_by_name(XFieldName)
        Y = self.data_reader.data_container.get_column_by_name(YFieldName)
        
        return X,Y

    def remove(self):

        self.HDV.remove_data_handle(self)

class HotDataViewer(QMainWindow):

    colorList = [
        'red',
        'blue',
        'green',
        'orange',
        'pink',
        'plum']

    def __init__(self,app):
        super().__init__()

        self.app = app

        self.data_handles = list()
        self.number_of_data = 0

        self.axis_column_names = list()
        self.axis_column_units = list()
        self.x_axis_column_name = None
        self.y_axis_column_name = None

        self.x_data_lim = [0,1]
        self.y_data_lim = [0,1]

        self.x_scale = 1
        self.y_scale = 1

        self.folder_followers = list()

        self._initUI()

    def __del__(self):

        print('close')

    def _initUI(self):

        self.setGeometry(300, 300, 700, 500)
        self.setWindowTitle('Hot Data Viewer')
        self.setStyleSheet("background-color: black;")

        self._make_widgets()
        self._make_layout()
        self._make_connect()

    def _make_widgets(self):

        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)
        
        self.button_open_file = QPushButton("Open File",self.cw)
        self.button_follow_file = QPushButton("Follow File",self.cw)
        self.button_follow_folder = QPushButton("Follow Folder",self.cw)

        self.button_select_data = QPushButton("Select Data")
        self.button_select_axis = QPushButton("Select Axis")

        self.button_open_file.setStyleSheet("background-color: gray;")
        self.button_follow_file.setStyleSheet("background-color: gray;")
        self.button_follow_folder.setStyleSheet("background-color: gray;")
        self.button_select_data.setStyleSheet("background-color: gray;")
        self.button_select_axis.setStyleSheet("background-color: gray;")

        self.axes = pg.PlotWidget()

        self.axis_config_window = SelectAxis(self)
        self.data_config_window = SelectData(self)

    def _make_layout(self):

        hbox = QHBoxLayout()
        hbox.addWidget(self.button_open_file)
        hbox.addWidget(self.button_follow_file)
        hbox.addWidget(self.button_follow_folder)
        hbox.addStretch(1)
        hbox.addWidget(self.button_select_data)
        hbox.addWidget(self.button_select_axis)

        vbox = QVBoxLayout(self.cw)
        vbox.addWidget(self.axes)
        vbox.addLayout(hbox)

    def _make_connect(self):

        self.button_open_file.clicked.connect(self.onButtonOpenFile)
        self.button_follow_file.clicked.connect(self.onButtonFollowFile)
        self.button_follow_folder.clicked.connect(self.onButtonFollowFolder)
        self.button_select_data.clicked.connect(self.onButtonSelectData)
        self.button_select_axis.clicked.connect(self.onButtonSelectAxis)

    def onButtonOpenFile(self):

        file_path = QFileDialog.getOpenFileName(self, 'Open File',default_data_path)[0]

        if file_path:
            self.new_data_handle(file_path)

    def onButtonFollowFile(self):

        file_path = QFileDialog.getOpenFileName(self, 'Open File',default_data_path)[0]

        if file_path:
            self.new_data_handle(file_path,follow = True)

    def onButtonFollowFolder(self):

        data_path = QFileDialog.getExistingDirectory(self, 'Select a directory',default_data_path)

        if data_path:
            new_folder_follower = DataPathFollower(data_path)
            new_folder_follower.new_file_signal.connect(lambda: self.detect_new_file(new_folder_follower,follow = True))
            new_folder_follower.start()
            self.folder_followers.append(new_folder_follower)

    def onButtonSelectData(self):

        self.data_config_window.show()
        self.data_config_window.raise_()
        self.data_config_window.activateWindow()

    def onButtonSelectAxis(self):

        self.axis_config_window.show()
        self.axis_config_window.raise_()
        self.axis_config_window.activateWindow()

    def detect_new_file(self,folderFollower,follow = False):

        self.new_data_handle(folderFollower.getLastNewFilePath(),follow)
                
    def new_data_handle(self,file_path,follow = False):

        reader = Reader()
        data_reader = HotReader(reader,file_path)

        new_data_handle = DataHandle(self,data_reader)
        if self.add_data_handle(new_data_handle):
            if follow:
                new_data_handle.follow()
            self.data_config_window.add_data_handle(new_data_handle)

    def add_data_handle(self,new_data_handle):

        if len(self.data_handles) == 0:
            self.axis_column_names = new_data_handle.column_names
            self.axis_column_units = new_data_handle.column_units

            # for unit in self.axis_column_units:
            #     print(unit)

            self.x_axis_column_name = self.axis_column_names[0]
            self.y_axis_column_name = self.axis_column_names[1]
            self.update_x_axis_choice()
            self.update_y_axis_choice()
            self.change_x_axis_choice()
            self.change_y_axis_choice()
            self.update_x_label()
            self.update_y_label()

            add_it = True
        else:
            duplicate = False
            for data_handle in self.data_handles:
                if data_handle.data_reader.file_path == new_data_handle.data_reader.file_path:
                    duplicate = True
                    break
            
            if duplicate:
                add_it = False
                print('File already opened')
            # If the datafile contains the same field name
            elif set(self.axis_column_names) == set(new_data_handle.column_names):
                add_it = True
            else:
                add_it = False

        if add_it:
            self.data_handles.append(new_data_handle)
            self.new_plot(new_data_handle)
            
            self.number_of_data += 1

        return add_it

    def remove_data_handle(self,data_handle):

        self.axes.removeItem(data_handle.data_plot)
        self.data_config_window.remove_data_handle(data_handle)
        self.data_handles.remove(data_handle)
        del(data_handle)

    def new_plot(self,data_handle):

        data_handle.pen = pg.mkPen(self.number_of_data,width = 2)
        X,Y = data_handle.get_xy(self.x_axis_column_name,self.y_axis_column_name)
        data_plot = self.axes.plot(X, Y, pen = data_handle.pen)
        # self.axes.removeItem(data_plot) #Need to remove it so it can be added when the visible checkbox is automatically checked at creation
        data_handle.setDataPlot(data_plot)

    def update_all_plot(self):

        for data_handle in self.data_handles:
            self.update_plot(data_handle)

    def update_plot(self,data_handle):

        X,Y = data_handle.get_xy(self.x_axis_column_name,self.y_axis_column_name)

        data_handle.data_plot.setData(X/self.x_scale,Y/self.y_scale)

    def getXYDataLimit(self):

        x_mins = list()
        x_maxs = list()
        y_mins = list()
        y_maxs = list()

        for data_handle in self.data_handles:
            X,Y = data_handle.get_xy(self.x_axis_column_name,self.y_axis_column_name)
            x_mins.append(X.min())
            x_maxs.append(X.max())
            y_mins.append(Y.min())
            y_maxs.append(Y.max())

        x_data_lim = [np.array(x_mins).min(),np.array(x_maxs).max()]
        y_data_lim = [np.array(y_mins).min(),np.array(y_maxs).max()]

        return x_data_lim, y_data_lim

    def update_x_label(self):

        index_x = self.axis_column_names.index(self.x_axis_column_name)
        x_axis_unit = self.axis_column_units[index_x]
        
        x_label = '{0:s} ({1:s})'.format(self.x_axis_column_name,x_axis_unit.get_scaled_label(self.x_scale))
        self.axes.setLabel('bottom', text = x_label)
        
    def update_y_label(self):

        index_y = self.axis_column_names.index(self.y_axis_column_name)
        y_axis_unit = self.axis_column_units[index_y]

        y_label = '{0:s} ({1:s})'.format(self.y_axis_column_name,y_axis_unit.get_scaled_label(self.y_scale))
        self.axes.setLabel('left', text = y_label)

    def update_x_axis_choice(self):

        index_x = self.axis_column_names.index(self.x_axis_column_name)

        self.axis_config_window.x_axis_combo_box.clear()
        self.axis_config_window.x_axis_combo_box.addItems(self.axis_column_names)
        self.axis_config_window.x_axis_combo_box.setCurrentIndex(index_x)

    def update_y_axis_choice(self):

        index_y = self.axis_column_names.index(self.y_axis_column_name)

        self.axis_config_window.y_axis_combo_box.clear()
        self.axis_config_window.y_axis_combo_box.addItems(self.axis_column_names)
        self.axis_config_window.y_axis_combo_box.setCurrentIndex(index_y)

    def change_x_axis_choice(self):

        index_x = self.axis_config_window.x_axis_combo_box.currentIndex()
        
        self.x_axis_column_name = self.axis_column_names[index_x]
        x_axis_unit = self.axis_column_units[index_x]
        
        self.axis_config_window.x_unit_combo_box.clear()
        self.axis_config_window.x_unit_combo_box.addItems(x_axis_unit.get_all_scale_labels())

        self.x_scale = 1
        
        x_unit_index = self.axis_config_window.x_unit_combo_box.findText(x_axis_unit.get_scaled_label(self.x_scale))
        if x_unit_index > -1:
            self.axis_config_window.x_unit_combo_box.setCurrentIndex(x_unit_index)

        self.update_x_label()
        self.update_all_plot()

    def change_y_axis_choice(self):

        index_y = self.axis_config_window.y_axis_combo_box.currentIndex()
        
        self.y_axis_column_name = self.axis_column_names[index_y]
        y_axis_unit = self.axis_column_units[index_y]

        self.axis_config_window.y_unit_combo_box.clear()
        self.axis_config_window.y_unit_combo_box.addItems(y_axis_unit.get_all_scale_labels())

        self.y_scale = 1

        YUnitIndex = self.axis_config_window.y_unit_combo_box.findText(y_axis_unit.get_scaled_label(self.y_scale))
        if YUnitIndex > -1:
            self.axis_config_window.y_unit_combo_box.setCurrentIndex(YUnitIndex)

        self.update_y_label()
        self.update_all_plot()

    def update_x_scale(self):

        index_x = self.axis_config_window.x_axis_combo_box.currentIndex()
        
        x_axis_unit = self.axis_column_units[index_x]
        index_unit_x = self.axis_config_window.x_unit_combo_box.currentIndex()
        if index_unit_x > -1:
            currentXUnitLabel = x_axis_unit.get_all_scale_labels()[index_unit_x]
            self.x_scale = x_axis_unit.relative_scale(currentXUnitLabel)
            
        self.update_x_label()
        self.update_all_plot()
            
    def update_y_scale(self):

        index_y = self.axis_config_window.y_axis_combo_box.currentIndex()

        y_axis_unit = self.axis_column_units[index_y]
        index_unit_y = self.axis_config_window.y_unit_combo_box.currentIndex()
        if index_unit_y > -1:
            current_y_unit_label = y_axis_unit.get_all_scale_labels()[index_unit_y]
            self.y_scale = y_axis_unit.relative_scale(current_y_unit_label)
            
        self.update_y_label()
        self.update_all_plot()

            

class SelectAxis(QWidget):
    def __init__(self,HDV):
        QWidget.__init__(self)
        
        self.HDV = HDV
        self._initUI()

        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

    def _initUI(self):

        self.setGeometry(350, 350, 300, 150)
        self.setWindowTitle('Select Axis')
        self.setStyleSheet("background-color: gray;")

        self._make_widgets()
        self._make_layout()
        self._make_connect()

    def closeEvent(self,event):

        print('closing select axis')

    def _make_widgets(self):

        self.x_axis_label = QLabel('X axis')
        self.y_axis_label = QLabel('Y axis')

        self.x_axis_combo_box = QComboBox()
        self.y_axis_combo_box = QComboBox()

        self.x_unit_combo_box = QComboBox()
        self.y_unit_combo_box = QComboBox()

    def _make_layout(self):

        grid = QGridLayout()
        grid.addWidget(self.x_axis_label,1,1)
        grid.addWidget(self.y_axis_label,2,1)
        grid.addWidget(self.x_axis_combo_box,1,2)
        grid.addWidget(self.y_axis_combo_box,2,2)
        grid.addWidget(self.x_unit_combo_box,1,3)
        grid.addWidget(self.y_unit_combo_box,2,3)

        vbox = QVBoxLayout(self)
        vbox.addLayout(grid)
        vbox.addStretch(1)

    def _make_connect(self):
        
        self.x_axis_combo_box.currentIndexChanged.connect(self.HDV.change_x_axis_choice)
        self.y_axis_combo_box.currentIndexChanged.connect(self.HDV.change_y_axis_choice)

        self.x_unit_combo_box.currentIndexChanged.connect(self.HDV.update_x_scale)
        self.y_unit_combo_box.currentIndexChanged.connect(self.HDV.update_y_scale)

class SelectData(QWidget):
    def __init__(self,HDV):
        QWidget.__init__(self)
        
        self.HDV = HDV
        self.data_items = list()

        self._initUI()

        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

    def _initUI(self):

        self.setGeometry(350, 350, 400, 300)
        self.setWindowTitle('Select Data')
        # self.setStyleSheet("background-color: gray;")

        self._make_widgets()
        self._make_layout()
        self._make_connect()

    def closeEvent(self,event):

        print('closing select data')

    def _make_widgets(self):

        pass

    def _make_layout(self):

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addStretch()

    def _make_connect(self):
        
        pass
        # self.dataTree.itemChanged.connect(self.onChangeHandler)

    def addFolder(self,folder):

        pass

    def add_data_handle(self,data_handle):

        self.data_items.append(DataListItem(data_handle,parent=self))
        data_handle.setDataItem(self.data_items[-1])
        self.layout.insertWidget(self.layout.count()-1,self.data_items[-1])

    def remove_data_handle(self,data_handle):

        self.layout.removeWidget(data_handle.data_item)
        self.data_items.remove(data_handle.data_item)
        data_handle.data_item.deleteLater()

class DataListItem(QWidget):

    def __init__(self,data_handle, parent = None):

        super(DataListItem, self).__init__(parent)

        self.data_handle = data_handle

        self._make_widgets()
        self._make_layout()
        self._make_connect()

    def _make_widgets(self):
        
        self.description_edit = QLineEdit(self.data_handle.description,parent = self)

        self.visible_checkbox = QCheckBox('Visible',parent = self)
        if self.data_handle.visible:
            self.visible_checkbox.setCheckState(2)

        self.follow_checkbox = QCheckBox('Follow',parent = self)
        if self.data_handle.following:
            self.follow_checkbox.setCheckState(2)

        self.button_color_pick = QPushButton("",parent = self)
        self.button_color_pick.setMaximumWidth(32)
        self.setButtonColor(self.data_handle.pen.color())

        self.button_remove = QPushButton("Remove",parent = self)

    def _make_layout(self):

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        self.layout.addWidget(self.description_edit)
        self.layout.addWidget(self.visible_checkbox)
        self.layout.addWidget(self.follow_checkbox)
        self.layout.addWidget(self.button_color_pick)
        self.layout.addWidget(self.button_remove)
        
    def _make_connect(self):

        self.visible_checkbox.stateChanged.connect(self.on_change_visible)
        self.follow_checkbox.stateChanged.connect(self.on_change_follow)
        self.description_edit.editingFinished.connect(self.onChangeDescription)
        self.button_color_pick.clicked.connect(self.onColorPick)
        self.button_remove.clicked.connect(self.onRemoveHandle)

    def setButtonColor(self,color):

        self.button_color_pick.setStyleSheet("background-color: {0:s};".format(color.name()))

    def on_change_visible(self):

        if self.visible_checkbox.isChecked():
            self.data_handle.show()
        else:
            self.data_handle.hide()

    def on_change_follow(self):

        if self.follow_checkbox.isChecked():
            self.data_handle.follow()
        else:
            self.data_handle.pause_follow()

    def onChangeDescription(self):

        self.data_handle.description = self.description_edit.text()

    def onColorPick(self):

        dlg = QColorDialog(self)
        # if self._color:
            # dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            new_color = dlg.currentColor()
            self.setButtonColor(new_color)
            self.data_handle.setColor(new_color)


            # self.setColor(dlg.currentColor().name())

    def onRemoveHandle(self):

        self.data_handle.remove()



def main():
    app = QApplication(sys.argv)
    HDV = HotDataViewer(app)
    HDV.show()
    sys.exit(app.exec_())






if __name__ == '__main__':
    main()

