from __future__ import division
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pandas as pd

# Import LogoMaker
import logomaker

# Load counts matrix from fasta file
counts_mat = logomaker.load_alignment('data/crp_sites.fasta')
counts_mat.to_csv('crp_counts.txt', sep='\t', float_format='%d')

import matplotlib as mpl
mpl.rcParams['lines.linewidth'] = .5
mpl.rcParams['font.size'] = 5
mpl.rcParams['axes.labelsize'] = 8

# Make information logo
'''
logo1 = logomaker.make_logo(counts_mat,
                       font_family='sans-serif',
                       font_weight='bold',
                       logo_type='information',
                       axes_style='classic',
                       ylim=[0,1])
                                           
'''

# highlight_sequence : 'AATTAATGTGAGTTAGCTCACTCATTAGGCACCCCAGGCTTTACACTTTATGCTTCCGGCTCGTATGTTGTGTGG'

parameters_text = """
colors : 'deepskyblue'
logo_type : 'probability'
axes_style : 'vlines'
font_family : 'sans-serif'
font_weight : 'heavy'
"""

style_file = 'parameters_file.txt'
with open(style_file,'w') as f:
    f.write(parameters_text)


# Make frequency logo
#logo2 = logomaker.make_logo(counts_mat)
logo2 = logomaker.make_styled_logo(style_file=style_file,matrix=counts_mat)


# Draw logos
fig, ax_list = plt.subplots(figsize=[8,2])
#logo1.draw(ax_list[0])

logo2.draw(ax_list)
#logo2.draw(ax_list[1])

fig.tight_layout(h_pad=2)
#fig.savefig('logos.pdf')
plt.show()