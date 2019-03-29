# Classes / functions imported with logomaker

print('printing from logomaker.py in directory latest')

# import paths for local install
try:

    print('importing from the try clause')
    from logomaker.src.Logo import Logo
    from logomaker.src.Glyph import Glyph
    from logomaker.src.Glyph import list_font_families
    from logomaker.src.matrix import transform_matrix
    from logomaker.src.matrix import sequence_to_matrix
    from logomaker.src.matrix import alignment_to_matrix
    from logomaker.src.matrix import saliency_to_matrix
    from logomaker.src.validate import validate_matrix

    # TODO: fold these into validate_matrix
    from logomaker.src.validate import validate_probability_mat
    from logomaker.src.validate import validate_information_mat

    # Useful variables for users to see
    from logomaker.src.colors import list_color_schemes

# import paths for read the docs
except:

    print('importing from the except clause')
    from Logo import Logo
    from Glyph import Glyph
    from Glyph import list_font_families
    from matrix import transform_matrix
    from matrix import sequence_to_matrix
    from matrix import alignment_to_matrix
    from matrix import saliency_to_matrix
    from validate import validate_matrix

    # TODO: fold these into validate_matrix
    from validate import validate_probability_mat
    from validate import validate_information_mat

    # Useful variables for users to see
    from colors import list_color_schemes