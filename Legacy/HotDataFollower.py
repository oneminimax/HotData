# import threading
import time
import os
import threading

# class HotDataHandler(object):

    # self.dataFileList = list()
    # self.dataPlotList = list()
    # self.dataFollowerList = list()

class Follower(threading.Thread):
    lapse = 1
    def __init__(self):
        threading.Thread.__init__(self)

        self.keepRunning = True
        self.onPause = False

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

    def _iteration(self):
        pass


class DataPathFollower(Follower):
    lapse = 1
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
                print(len(self.dataFileList))

    def follow(self):

        while self.keepRunning:
            if self.onPause:
                time.sleep(self.lapse)
                continue
            self._iteration()
            time.sleep(self.lapse)

    def _listWantedFiles(self):

        allFile = os.listdir(self.dataPath)
        wantedFiles = list()
        for file in allFile:
            if os.path.isfile(file) and os.path.splitext(file)[1] == self.extension:
                wantedFiles.append(file)

        return wantedFiles

class DataFileFollower(Follower):
    lapse = 0.1
    def __init__(self,dataFile,dataPlot,hdvframe):
        
        Follower.__init__(self)

        self.dataFile = dataFile
        self.dataPlot = dataPlot
        self.hdvframe = hdvframe

    def follow(self):

        nbNewLine = 0
        while self.keepRunning:
            if self.onPause:
                time.sleep(self.lapse)
                continue
            newLine = self.dataFile._readADataLine()
            if newLine:
                nbNewLine += 1
            else:
                if nbNewLine > 0:
                    wx.CallAfter(self.hdvframe.updatePlot,self.dataPlot,self.dataFile)
                    nbNewLine = 0
                time.sleep(self.lapse)
                continue

def testDataPathFollower():

    dataPath = '/Users/oneminimax/Documents/Projets Programmation/HotData/'
    dataPathFollower = DataPathFollower(dataPath)
    dataPathFollower.start()



if __name__ == '__main__':
    testDataPathFollower()




