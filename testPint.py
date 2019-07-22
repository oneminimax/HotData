from pint import UnitRegistry
import numpy as np

ureg = UnitRegistry(autoconvert_offset_to_baseunit = True)

distance = 10e6 * ureg.meter
distance2 = ureg.Quantity(1,distance.units)

distance.to_compact()

print(distance.to_compact())
# print(distance2)