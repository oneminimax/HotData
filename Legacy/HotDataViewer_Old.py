import os
import sys
import numpy as np

from HotDataFollower import DataFileFollower
import WX_Interface as Interface

sys.path.append("/Users/oneminimax/Documents/Projets Programmation/Slave")
sys.path.append("/Users/oneminimax/Documents/Projets Programmation/DataFileIO")

import DataFileIO as DFIO


class HotDataHandler(object):

    colorList = [
        'red',
        'blue',
        'green',
        'orange',
        'pink',
        'plum']

    def __init__(self):

        self.dataFileList = list()
        self.dataPlotList = list()
        self.dataFollowerList = list()

        self.lastDataFileDir = ''

        self.XAxisIndex = 0
        self.YAxisIndex = 1

        self.XAutoLim = True
        self.YAutoLim = True

        self.xplotlim = [0,1]
        self.yplotlim = [0,1]

    def openDataFile(self,dataFileName):

        dataFile = DFIO.DataFileReader(dataFileName)

        self.dataFileList = [dataFile]
        self.currentDataFileIndex = 0
        self.updateAxisChoice()

        dataPlot = self.newPlot(dataFile)
        dataFollower = DataFileFollower(dataFile,dataPlot,self)
        dataFollower.start()

        # self.dataPlotList.append(dataPlot)
        # self.dataFollowerList.append(dataFollower)

        self.dataPlotList = [dataPlot]
        self.dataFollowerList = [dataFollower]

    def getXY(self,dataFile):

        X = dataFile.getDataByIndex(self.XAxisIndex)
        Y = dataFile.getDataByIndex(self.YAxisIndex)
        
        return X,Y

    def getXYDataLimit(self):

        minXList = list()
        maxXList = list()
        minYList = list()
        maxYList = list()

        for dataFile in self.dataFileList:
            X = dataFile.getDataByIndex(self.XAxisIndex)
            Y = dataFile.getDataByIndex(self.YAxisIndex)
            minXList.append(X.min())
            maxXList.append(X.max())
            minYList.append(Y.min())
            maxYList.append(Y.max())

        xplotlim = [np.array(minXList).min(),np.array(maxXList).max()]
        yplotlim = [np.array(minYList).min(),np.array(maxYList).max()]

        return xplotlim, yplotlim

    def newPlot(self,dataFile):

        X,Y = self.getXY(dataFile)

        dataPlot = self.axes.plot(X, Y, color = self.colorList[0], linestyle = "solid", marker = "o")[0]

        self.updatePlotLim()
        self.updateAxesLabel()
        self.canvas.draw()

        return dataPlot

    def updatePlot(self,plot,dataFile):

        X,Y = self.getXY(dataFile)

        plot.set_xdata(X)
        plot.set_ydata(Y)

        self.updatePlotLim()
        self.updateAxesLabel()
        self.canvas.draw()

    def updatePlotLim(self):

        xplotlim, yplotlim = self.getXYDataLimit()

        if self.XAutoLim:
            self.xplotlim = xplotlim
            xmargin = 0.02 * (self.xplotlim[1] - self.xplotlim[0])
            self.axes.set_xlim((self.xplotlim[0] - xmargin,self.xplotlim[1] + xmargin))
        else:
            pass

        if self.YAutoLim:
            self.yplotlim = yplotlim
            ymargin = 0.02 * (self.yplotlim[1] - self.yplotlim[0])
            self.axes.set_ylim((self.yplotlim[0] - ymargin,self.yplotlim[1] + ymargin))
        else:
            pass

    def updateAxisChoice(self):

        dataFile =  self.dataFileList[self.currentDataFileIndex]
        fieldNameList = dataFile.nameList

        if len(fieldNameList) >= 2:

            self.plotConfigFrame.XAxisChoice.SetItems(fieldNameList)
            self.plotConfigFrame.YAxisChoice.SetItems(fieldNameList)

            self.plotConfigFrame.XAxisChoice.SetSelection(self.XAxisIndex)
            self.plotConfigFrame.YAxisChoice.SetSelection(self.YAxisIndex)

    def updateAxesLabel(self):

        dataFile =  self.dataFileList[self.currentDataFileIndex]
        fieldNameList = dataFile.nameList
        unitNameList = dataFile.unitList

        XLabel = '{0:s} ({1:s})'.format(fieldNameList[self.XAxisIndex],unitNameList[self.XAxisIndex])
        YLabel = '{0:s} ({1:s})'.format(fieldNameList[self.YAxisIndex],unitNameList[self.YAxisIndex])

        self.axes.set_xlabel(XLabel)
        self.axes.set_ylabel(YLabel)

    def selectXAxis(self,selection):

        self.XAxisIndex = selection

        self.updatePlot(self.dataPlotList[self.currentDataFileIndex],self.dataFileList[self.currentDataFileIndex])
        self.updatePlotLim()
        self.updateAxesLabel()

    def selectYAxis(self,selection):

        self.YAxisIndex = selection

        self.updatePlot(self.dataPlotList[self.currentDataFileIndex],self.dataFileList[self.currentDataFileIndex])
        self.updatePlotLim()
        self.updateAxesLabel()

    def setXAutoLim(self,autoBool):

        self.XAutoLim = autoBool

    def setYAutoLim(self,autoBool):

        self.YAutoLim = autoBool

def main():

    hdv = Interface.APP()
    hdv.setHotDataHandler(HotDataHandler())
    hdv.start()

    
    


if __name__ == '__main__':
    main()