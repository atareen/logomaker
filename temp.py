import logomaker


style_file = 'parameters_file.txt'

with open(style_file, 'w') as f:
            f.write("")

uploadMat = logomaker.load_alignment('data/crp_sites.fasta')
logo = logomaker.make_styled_logo(style_file=style_file, matrix=uploadMat)


#print logomaker.make_styled_logo.func_code.co_varnames[:logomaker.make_styled_logo.func_code.co_argcount]
#print logomaker.make_logo.func_code.co_varnames[:logomaker.make_logo.func_code.co_argcount]

import inspect


for member in inspect.getmembers(logo):
    if member[1] is not None and \
       str(member[0]) is not 'bg_mat' and\
       str(member[0]) is not 'df' and\
       str(member[0]) is not 'in_df' and\
       str(member[1]) is not 'none' and\
       callable(member[1]) is False and\
       str(member[0]) is not 'char_list' and\
       str(member[0]) is not 'font_properties' and\
       str(member[0]) is not '__module__' and\
       len(str(member[1])) < 100:


        print member[0],":",member[1],len(str(member[1]))