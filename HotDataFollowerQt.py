import time
import os
import sys
from PyQt5.QtCore import QCoreApplication, QThread, QObject, pyqtSignal

from AsciiDataFile.HotReader import HotReader

class Follower(QThread):
    lapse = 0.1
    def __init__(self):
        QThread.__init__(self)

        self.keep_running = True
        self.on_pause = False
        self.iterations = 0

    def stop(self):

        self.keep_running = False

    def pause(self):

        self.on_pause = True

    def unpause(self):

        self.on_pause = False

    def run(self):

        while self.keep_running:
            if self.on_pause:
                time.sleep(self.lapse)
                continue
            
            self._iteration()

            time.sleep(self.lapse)
            # print('following {0:d}'.format(self.iterations))
            self.iterations += 1

    def _iteration(self):
        pass

class DataPathFollower(Follower):
    
    lapse = 1
    new_file_signal = pyqtSignal()

    def __init__(self,data_path):
        
        super().__init__()

        self.extension = '.txt'
        self.data_path = data_path
        self.data_files = list()
        self.data_file_followers = list()
    
    def _iteration(self):
        
        wanted_files = self._wanted_files()
        for file_name in wanted_files:
            if not file_name in self.data_files:
                self.data_files.append(file_name)
                self.last_new_file = file_name
                self.new_file_signal.emit()
                break # prevent treating new files while one is being added

    def _wanted_files(self):

        all_files = os.listdir(self.data_path)
        wanted_files = list()
        for file in all_files:
            if os.path.splitext(file)[1] == self.extension:
                wanted_files.append(file)

        return wanted_files

    def get_last_new_file(self):

        return os.path.join(self.data_path,self.last_new_file)

class DataFileFollower(Follower):

    lapse = 0.1
    new_data_signal = pyqtSignal()

    def __init__(self,data_reader):
        
        super().__init__()

        self.data_reader = data_reader
        self.nb_new_line = 0

    def _iteration(self):

        new_line = self.data_reader.read_data_line()
        if new_line:
            self.nb_new_line += 1
        else:
            if self.nb_new_line > 0:
                self.nb_new_line = 0
                self.new_data_signal.emit()
            time.sleep(self.lapse)

    def get_description(self):

        return os.path.basename(self.data_reader.get_file_path())

