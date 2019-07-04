import re
import numpy as np

def makeUnit(label):

    if SIGenericUnit.validLabel(label):
        return SIGenericUnit(label)
    else:
        return Unit(label)

def rescale(data,oldUnit):

    maxValue = np.amax(np.abs(data))
    newUnit = oldUnit.rescaledUnit(maxValue)
    
    return expressIn(data,oldUnit,newUnit)

def expressIn(data,oldUnit,newUnit):

    relativeScale = newUnit.baseScale/oldUnit.baseScale

    return data/relativeScale


class Unit(object):
    def __init__(self,label):
       self.label = label

    def __str__(self):
        return 'Unit : {0:s}'.format(self.label)

    @classmethod
    def validLabel(cls,label):

        return True

    def getScaledLabel(self,scale):

        return self.label

    def getLabel(self):

        return self.label

    def getAllScaleLabelList(self):

        return [self.label]

    def relativeScale(self,otherUnit):

        return 1

class SIGenericUnit(Unit):

    supportedLabels = ['K','s','V','A','T','Gauss','m','Hz']
    prefix = ['T','G','M','k','','m','u','n','p']
    prefixScale = [1e12,1e9,1e6,1e3,1,1e-3,1e-6,1e-9,1e-12]

    def __init__(self,label):
        Unit.__init__(self,label)

        self.match = self._matchLabel(self.label)
        self.baseScale = self._baseScale()
        self.baseLabel = self._baseLabel()
        self.allScaleLabelList = self._allScaleLabelList()

    def __str__(self):
        return 'SIGenericUnit : {0:s} = {1:1.0e} {2:s}'.format(self.label,self.baseScale,self.baseLabel)

    @classmethod
    def validLabel(cls,label):
        return bool(cls._matchLabel(label))

    @classmethod
    def _generateMatchStr(cls):
        return '^\s*([' + '|'.join(cls.prefix) + ']?)(' + '|'.join(cls.supportedLabels) + ')\s*$'

    @classmethod
    def _matchLabel(cls,label):
        return re.match(cls._generateMatchStr(),label)

    @classmethod
    def _getScale(cls,baseValue):
        if baseValue >= np.amax(cls.prefixScale):
            scale = np.amax(cls.prefixScale)
        elif baseValue <= np.amin(cls.prefixScale):
            scale = np.amin(cls.prefixScale)
        else:
            scale = cls._floorScale(baseValue)

        return scale

    @classmethod
    def _floorScale(cls,baseValue):
        
        return 10**(3*(int(np.log10(baseValue)/3+1)-1))

    def _baseScale(self):
        
        return self.prefixScale[self.prefix.index(self.match.group(1))]

    def _baseLabel(self):
        
        return self.match.group(2)

    def _allScaleLabelList(self):

        labelList = list()
        for prefix in self.prefix:
            labelList.append(prefix + self.baseLabel)

        return labelList

    def getScaledLabel(self,scale):

        baseScale = self.baseScale
        newBaseScale = self._getScale(baseScale*scale)

        newPrefix = self.prefix[self.prefixScale.index(newBaseScale)]

        return newPrefix + self._baseLabel()

    def rescaledUnit(self,maxValue):
        if maxValue == 0:
            return self
        else:
            return SIGenericUnit(self.getScaledLabel(maxValue))

    def getAllScaleLabelList(self):

        return self.allScaleLabelList

    def relativeScale(self,otherUnit):

        if isinstance(otherUnit,SIGenericUnit):
            ratio = otherUnit.baseScale/self.baseScale
        elif isinstance(otherUnit,str):
            labelList = self.getAllScaleLabelList()
            ratio = self.prefixScale[labelList.index(otherUnit)]/self.baseScale

        return ratio


class TimeUnit(Unit):
    supportedLabels = ['s','min']


def main():
    
    newLabel = 'mV'
    unit = makeUnit(newLabel)

    print(unit)

    # data = 1e3
    # newData, newUnit = rescale(data,unit)

    # print(np.amax(data),unit)
    # print(np.amax(newData),newUnit)

if __name__ == '__main__':
    main()