import re
import numpy as np

def make_unit(label):

    if SIGenericUnit.valid_label(label):
        return SIGenericUnit(label)
    else:
        return Unit(label)

def rescale(data,old_unit):

    max_value = np.amax(np.abs(data))
    new_unit = old_unit.rescaled_unit(max_value)
    
    return express_in(data,old_unit,new_unit)

def express_in(data,old_unit,new_unit):

    relative_scale = new_unit.base_scale/old_unit.base_scale

    return data/relative_scale


class Unit(object):
    def __init__(self,label):
       self.label = label

    def __str__(self):
        return 'Unit : {0:s}'.format(self.label)

    @classmethod
    def valid_label(cls,label):

        return True

    def get_scaled_label(self,scale):

        return self.label

    def get_label(self):

        return self.label

    def get_all_scale_labels(self):

        return [self.label]

    def relative_scale(self,otherUnit):

        return 1

class SIGenericUnit(Unit):

    supported_labels = ['K','s','V','A','T','Gauss','m','Hz']
    prefix = ['T','G','M','k','','m','u','n','p']
    prefixScale = [1e12,1e9,1e6,1e3,1,1e-3,1e-6,1e-9,1e-12]

    def __init__(self,label):
        Unit.__init__(self,label)

        self.match = self._match_label(self.label)
        self.base_scale = self._base_scale()
        self.baseLabel = self._base_label()
        self.all_scale_labels = self._all_scale_labels()

    def __str__(self):
        return 'SIGenericUnit : {0:s} = {1:1.0e} {2:s}'.format(self.label,self.base_scale,self.baseLabel)

    @classmethod
    def valid_label(cls,label):
        return bool(cls._match_label(label))

    @classmethod
    def _generate_match_str(cls):
        return '^\s*([' + '|'.join(cls.prefix) + ']?)(' + '|'.join(cls.supported_labels) + ')\s*$'

    @classmethod
    def _match_label(cls,label):
        return re.match(cls._generate_match_str(),label)

    @classmethod
    def _get_scale(cls,base_value):
        if base_value >= np.amax(cls.prefixScale):
            scale = np.amax(cls.prefixScale)
        elif base_value <= np.amin(cls.prefixScale):
            scale = np.amin(cls.prefixScale)
        else:
            scale = cls._floor_scale(base_value)

        return scale

    @classmethod
    def _floor_scale(cls,base_value):
        
        return 10**(3*(int(np.log10(base_value)/3+1)-1))

    def _base_scale(self):
        
        return self.prefixScale[self.prefix.index(self.match.group(1))]

    def _base_label(self):
        
        return self.match.group(2)

    def _all_scale_labels(self):

        labels = list()
        for prefix in self.prefix:
            labels.append(prefix + self.baseLabel)

        return labels

    def get_scaled_label(self,scale):

        base_scale = self.base_scale
        new_base_scale = self._get_scale(base_scale*scale)

        new_prefix = self.prefix[self.prefixScale.index(new_base_scale)]

        return new_prefix + self._base_label()

    def rescaled_unit(self,max_value):
        if max_value == 0:
            return self
        else:
            return SIGenericUnit(self.get_scaled_label(max_value))

    def get_all_scale_labels(self):

        return self.all_scale_labels

    def relative_scale(self,otherUnit):

        if isinstance(otherUnit,SIGenericUnit):
            ratio = otherUnit.base_scale/self.base_scale
        elif isinstance(otherUnit,str):
            labels = self.get_all_scale_labels()
            ratio = self.prefixScale[labels.index(otherUnit)]/self.base_scale

        return ratio


class TimeUnit(Unit):
    supported_labels = ['s','min']


def main():
    
    new_label = 'mV'
    unit = make_unit(new_label)

    # print(unit)

    # data = 1e3
    # newData, new_unit = rescale(data,unit)

    # print(np.amax(data),unit)
    # print(np.amax(newData),new_unit)

if __name__ == '__main__':
    main()