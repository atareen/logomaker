print('priting from logomaker.py')

# Classes / functions imported with logomaker
from src.Logo import Logo
from src.Glyph import Glyph
from src.Glyph import list_font_families
from src.matrix import transform_matrix
from src.matrix import sequence_to_matrix
from src.matrix import alignment_to_matrix
from src.matrix import saliency_to_matrix
from src.validate import validate_matrix

# TODO: fold these into validate_matrix
from src.validate import validate_probability_mat
from src.validate import validate_information_mat

# Useful variables for users to see
from src.colors import list_color_schemes
print('at the end of init file')