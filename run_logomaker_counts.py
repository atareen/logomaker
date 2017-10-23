from __future__ import division
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pandas as pd

# Import LogoMaker
import logomaker

# Read in sortseq data
wtseq = 'AATTAATGTGAGTTAGCTCACTCATTAGGCACCCCAGGCTTTACACTTTATGCTTCCGGCTCGTATGTTGTGTGG'
L = len(wtseq)
poss = range(-L,0)
df_wt = pd.read_csv('data/full-wt-formatted.txt', delim_whitespace=True)
df_0 = pd.read_csv('data/full-0-formatted.txt', delim_whitespace=True)

parameters_text = """
colors : 'deepskyblue'
logo_type : 'enrichment'
axes_style : 'vlines'
highlight_sequence : 'AATTAATGTGAGTTAGCTCACTCATTAGGCACCCCAGGCTTTACACTTTATGCTTCCGGCTCGTATGTTGTGTGG'
vline_color : 'gray'
xtick_spacing : 10
xtick_anchor : 5
vline_width : .5
highlight_colors : 'tomato'
font_family : 'sans-serif'
font_weight : 'heavy'
width : .9
vpad : .1
use_position_range : [-45,0]
"""
style_file = 'parameters_file.txt'
with open(style_file,'w') as f:
    f.write(parameters_text)

# Load counts matrix from files
counts_wt_mat = logomaker.load_alignment(sequences=df_wt['seq'], sequence_counts=df_wt['ct_9'])
bg_mat = logomaker.load_alignment(sequences=df_wt['seq'], sequence_counts=df_wt['ct_0'])

# Make logos
logo1 = logomaker.make_styled_logo(style_file=style_file, print_params=False,
                                   matrix=counts_wt_mat, background=bg_mat, positions=poss)

fig, axs = plt.subplots(2, figsize=[10,4])
logo1.draw(axs[0])
axs[0].set_title('+ cAMP')


fig.tight_layout()

plt.show()

