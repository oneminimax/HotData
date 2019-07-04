# import threading
import time
import os
import sys
from PyQt5.QtCore import QCoreApplication, QThread, QObject, pyqtSignal

sys.path.append("/Users/oneminimax/Documents/Projets Programmation")

from AsciiDataFile.Readers import MDDataFileReader as Reader
from AsciiDataFile.HotReader import HotReader

class Follower(QThread):
    lapse = 1
    def __init__(self):
        QThread.__init__(self)

        self.keepRunning = True
        self.onPause = False
        self.iterations = 0

    def stop(self):

        self.keepRunning = False

    def pause(self):

        self.onPause = True

    def unpause(self):

        self.onPause = False

    def run(self):

        while self.keepRunning:
            if self.onPause:
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
    newFileSignal = pyqtSignal()

    def __init__(self,dataPath):
        
        Follower.__init__(self)

        self.extension = '.txt'
        self.dataPath = dataPath
        self.dataFileList = list()
        self.dataFileFollowerList = list()
    
    def _iteration(self):
        
        wantedFiles = self._listWantedFiles()
        for file in wantedFiles:
            if not file in self.dataFileList:
                self.dataFileList.append(file)
                self.lastNewFile = file
                self.newFileSignal.emit()
                time.sleep(0.1)

    def _listWantedFiles(self):

        allFile = os.listdir(self.dataPath)
        wantedFiles = list()
        for file in allFile:
            if os.path.splitext(file)[1] == self.extension:
                wantedFiles.append(file)

        return wantedFiles

    def getLastNewFilePath(self):

        return os.path.join(self.dataPath,self.lastNewFile)

class DataFileFollower(Follower):

    lapse = 0.1
    newDataSignal = pyqtSignal()

    def __init__(self,dataReader):
        
        Follower.__init__(self)

        self.dataReader = dataReader
        self.nbNewLine = 0

    def _iteration(self):

        newLine = self.dataReader.read_data_line()
        if newLine:
            self.nbNewLine += 1
        else:
            if self.nbNewLine > 0:
                self.nbNewLine = 0
                self.newDataSignal.emit()
            time.sleep(self.lapse)

    def getDescription(self):

        return os.path.basename(self.dataReader.get_file_path())
            
def testDataPathFollower():

    dataPath = '/Users/oneminimax/Documents/Projets Programmation/HotData/'

    app = QCoreApplication([])
    thread = QThread()

    pathFollower = DataPathFollower(dataPath)
    pathFollower.moveToThread(thread)
    thread.start()
    pathFollower.follow()
    sys.exit(app.exec_())
    time.sleep(4)

def testDataFileFollower():

    filePath = '/Users/oneminimax/Documents/Projets Programmation/HotData/Data/workfile0_011.txt'

    reader = Reader()

    dataReader = HotReader(reader,filePath)

    app = QCoreApplication([])
    thread = QThread()

    fileFollower = DataFileFollower(dataReader)
    fileFollower.moveToThread(thread)
    thread.start()
    fileFollower.run()
    print('en retard')
    sys.exit(app.exec_())




if __name__ == '__main__':
    testDataFileFollower()




