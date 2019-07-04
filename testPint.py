from pint import UnitRegistry
import numpy as np

ureg = UnitRegistry(autoconvert_offset_to_baseunit = True)

distance = 10 * ureg.meter
print(distance.to_tuple())