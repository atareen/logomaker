from __future__ import division
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl

# Import LogoMaker
import sys
sys.path.append('../')
import logomaker
import inspect
import make_logo


param_dict = logomaker.documentation_parser.parse_documentation_file('make_logo_arguments.txt')
#print(param_dict)

default_values = inspect.getargspec(logomaker.make_logo)
doc_dict = dict(zip(default_values[0], list(default_values[3])))

#print(doc_dict['font_family'])
#print(doc_dict['matrix'])

doc_dict_2 = {}
param_pairs = [(val.param_num, val.section, val.name,val.description) for val in param_dict.values()]
for num, section, name, description in sorted(param_pairs):
    #print '%d: %s, %s, %s '%(num, section, name,description)
    doc_dict_2[name] = (doc_dict[name],description)
    #print(num,section,name,description)
    #print(num, name, description)

#print(doc_dict_2)

print(doc_dict_2['font_weight'][1])



