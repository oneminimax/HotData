
import wx

import matplotlib as mpl
mpl.use('WXAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigureCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar

class APP(wx.App):
    
    def OnInit(self):
        self.mainFrame = Interface()

        self.mainFrame.Show()

        return True

    def setHotDataHandler(self,HDH):

        self.mainFrame.HDH = HDH

    def start(self):

        print("Starting Hot Data Viewer")
        
        self.MainLoop()

class Interface(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,"Hot Data Viewer",size=(700,600))

        self.plotConfigFrame = PlotConfigFrame(self)

        self._makeWidget()
        self._makeSizer()
        self._makeBinding()

    def _makeWidget(self):

        self.figure = Figure(facecolor=(0.9,0.9,0.9,1))
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.axes = self.figure.add_axes((0.1,0.1,0.8,0.8))

        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        self.toolbar.update()

        self.OpenFileButton = wx.Button(self, -1, "Open File", size = (100,20))
        self.PlotConfigButton = wx.Button(self, -1, "Plot Config", size = (100,20))
        
    def _makeSizer(self):

        topSizer = wx.BoxSizer(wx.HORIZONTAL)

        middleSizer = wx.BoxSizer(wx.HORIZONTAL)
        middleSizer = wx.BoxSizer(wx.HORIZONTAL)
        middleSizer.Add(self.canvas, 1, wx.EXPAND|wx.ALL, 0)

        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        bottomSizer.Add(self.OpenFileButton, 0, wx.ALL|wx.EXPAND, 0)
        bottomSizer.Add(self.PlotConfigButton, 0, wx.EXPAND|wx.ALL, 0)
        bottomSizer.AddStretchSpacer(1) 
        bottomSizer.Add(self.toolbar, 0, wx.ALL|wx.EXPAND , 0)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(topSizer, 0, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(middleSizer, 1, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(bottomSizer, 0, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(mainSizer)

    def _makeBinding(self):

        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.OpenFileButton.Bind(wx.EVT_BUTTON, self.onOpenFile)
        self.PlotConfigButton.Bind(wx.EVT_BUTTON, self.onPlotConfig)

    def onClose(self,event):
        self.Destroy()
        for dataFollower in self.dataFollowerList:
            dataFollower.stop()

        print("Hot Data Viewer Closed!")

    def onOpenFile(self,event):

        with wx.FileDialog(self, "Open data file", wildcard="Data files (*.txt)|*.txt",style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathName = fileDialog.GetPath()
            try:
                self.openDataFile(pathName)
                self.lastDataFileDir, dump = os.path.split(pathName)
            except IOError:
                wx.LogError("Cannot open file.")


    def onPlotConfig(self,event):

        self.plotConfigFrame.Show()

class PlotConfigFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY,"Hot Data Viewer",size=(200,200))

        self.HDV = parent

        self._makeWidget()
        self._makeSizer()
        self._makeBinding()

    def _makeWidget(self):

        self.controlPanel = wx.StaticBox(self, -1, "Axes control")
        
        self.FieldLabel = wx.StaticText(self.controlPanel, -1, "Field",size = (40,20))
        
        self.AutoLimLabel = wx.StaticText(self.controlPanel, -1, "Auto",size = (40,20),style = wx.TE_CENTRE)

        self.XAxisLabel = wx.StaticText(self.controlPanel, -1, "X : ",size = (30,20))
        self.XAxisChoice = wx.Choice(self.controlPanel, -1,size = (100,20))
        self.XAutoLimCheckBox = wx.CheckBox(self.controlPanel, -1,size = (20,20))
        self.XAutoLimCheckBox.SetValue(1)

        self.YAxisLabel = wx.StaticText(self.controlPanel, -1, "Y :",size = (30,20))
        self.YAxisChoice = wx.Choice(self.controlPanel, -1,size = (100,20))
        self.YAutoLimCheckBox = wx.CheckBox(self.controlPanel, -1,size = (20,20))
        self.YAutoLimCheckBox.SetValue(1)
        
    def _makeSizer(self):

        controlSizer = wx.StaticBoxSizer(self.controlPanel,wx.HORIZONTAL)

        axisLabelSizer = wx.BoxSizer(wx.VERTICAL)
        axisLabelSizer.Add((20,20),0,wx.ALL,1)
        axisLabelSizer.Add(self.XAxisLabel,0,wx.ALL,1)
        axisLabelSizer.Add(self.YAxisLabel,0,wx.ALL,1)

        axisChoiceSizer = wx.BoxSizer(wx.VERTICAL)
        axisChoiceSizer.Add(self.FieldLabel,0,wx.ALL,1)
        axisChoiceSizer.Add(self.XAxisChoice,0,wx.ALL,1)
        axisChoiceSizer.Add(self.YAxisChoice,0,wx.ALL,1)

        axisAutoLimSizer = wx.BoxSizer(wx.VERTICAL)
        axisAutoLimSizer.Add(self.AutoLimLabel,0,wx.CENTER | wx.ALL,1)
        axisAutoLimSizer.Add(self.XAutoLimCheckBox,0,wx.CENTER | wx.ALL,1)
        axisAutoLimSizer.Add(self.YAutoLimCheckBox,0,wx.CENTER | wx.ALL,1)

        controlSizer.Add(axisLabelSizer,0)
        controlSizer.Add(axisChoiceSizer,0)
        controlSizer.Add(axisAutoLimSizer,0)
        
        self.SetSizer(controlSizer)

    def _makeBinding(self):

        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.XAxisChoice.Bind(wx.EVT_CHOICE, self.onSelectAxis)
        self.YAxisChoice.Bind(wx.EVT_CHOICE, self.onSelectAxis)

        self.XAutoLimCheckBox.Bind(wx.EVT_CHECKBOX, self.onAutoLimCheckBox)
        self.YAutoLimCheckBox.Bind(wx.EVT_CHECKBOX, self.onAutoLimCheckBox)

    def onClose(self,event):

        self.Hide()

    def onAutoLimCheckBox(self,event):

        if event.GetEventObject() == self.XAutoLimCheckBox:
            self.HDV.setXAutoLim(event.GetEventObject().IsChecked())

        if event.GetEventObject() == self.YAutoLimCheckBox:
            self.HDV.setYAutoLim(event.GetEventObject().IsChecked())


    def onSelectAxis(self,event):

        if event.GetEventObject() == self.XAxisChoice:
            self.HDV.selectXAxis(event.GetEventObject().GetSelection())

        if event.GetEventObject() == self.YAxisChoice:
            self.HDV.selectYAxis(event.GetEventObject().GetSelection())
