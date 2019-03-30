print('priting from logomaker.py')

# Classes / functions imported with logomaker
from logomaker.logomaker.src.Logo import Logo
from logomaker.logomaker.src.Logo import Logo
from logomaker.logomaker.src.Glyph import Glyph
from logomaker.logomaker.src.Glyph import list_font_families
from logomaker.logomaker.src.matrix import transform_matrix
from logomaker.logomaker.src.matrix import sequence_to_matrix
from logomaker.logomaker.src.matrix import alignment_to_matrix
from logomaker.logomaker.src.matrix import saliency_to_matrix
from logomaker.logomaker.src.validate import validate_matrix

# TODO: fold these into validate_matrix
from logomaker.logomaker.src.validate import validate_probability_mat
from logomaker.logomaker.src.validate import validate_information_mat

# Useful variables for users to see
from logomaker.logomaker.src.colors import list_color_schemes
print('at the end of init file')