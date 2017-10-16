from __future__ import division
import numpy as np
import pandas
import argparse
import matplotlib.pyplot as plt

from Bio import SeqIO
from utils import Box, SMALL
import color
from character import Character, DEFAULT_FONT
import matrix
import pdb

#globally initalize params dict, this will be returned as a pandas
# which can be pass into logomaker.py
params = {}


# Logo base class
class Logo:

    def __init__(self,
                 mat,
                 mat_type=None,
                 logo_type=None,
                 wtseq=None,
                 color_scheme='classic',
                 logo_style='classic',
                 font_name=DEFAULT_FONT,
                 stack_order='big_on_top',
                 use_transparency=False,
                 max_alpha_val=None,
                 neg_shade=.5,
                 neg_flip=False,
                 floor_line_width=.5,
                 background=None,
                 xlabel='position',
                 ylabel=None,
                 xlim=None,
                 ylim=None,
                 xticks=None,
                 yticks=None,
                 xticklabels=None,
                 yticklabels=None):


        # Validate df
        mat = matrix.validate_mat(mat)

        # Get background mat
        bg_mat = matrix.set_bg_mat(background, mat)

        if logo_type == 'freq_logo':
            # Transform input mat to freq_mat
            mat = matrix.transform_mat(mat, from_type=mat_type, to_type='freq_mat', background=bg_mat)

            # Change default plot settings
            if ylim is None:
                ylim = [0, 1]
            if ylabel is None:
                ylabel = 'frequency'

        elif logo_type == 'info_logo':
            # Transform input mat to info_mat
            mat = matrix.transform_mat(mat, from_type=mat_type, to_type='info_mat', background=bg_mat)

            # Get max info value
            self.max_info = max(mat.values.sum(axis=1))

            # Change default plot settings
            if ylim  is None and (background is None):
                ylim = [0, np.log2(mat.shape[1])]
            if ylabel is None:
                ylabel = 'information\n(bits)'

        elif logo_type == 'weight_logo':
            # Transform input mat to weight_mat
            mat = matrix.transform_mat(mat, from_type=mat_type, to_type='weight_mat', background=bg_mat)

            # Change default plot settings
            if ylabel is None:
                ylabel = 'score'

        elif logo_type == 'energy_logo':
            # Transform input mat to weight_mat
            mat = matrix.transform_mat(mat, from_type=mat_type, to_type='energy_mat', background=background)

            # Change default plot settings
            if ylabel is None:
                ylabel = '- energy\n($k_B T$)'

        elif logo_type is None:
            mat = matrix.validate_mat(mat)

        else:
            assert False, 'Error! logo_type %s is invalid'%logo_type

        # Set matrix
        self.df = mat.copy()
        self.poss = mat.index.copy()
        self.chars = mat.columns.copy()
        self.wtseq = wtseq

        # Set colors
        self.color_scheme = color_scheme
        self.color_dict = color.get_color_dict(color_scheme=self.color_scheme, chars=self.chars)

        # Set character style
        self.font_name = font_name
        self.logo_style = logo_style
        self.stack_order = stack_order
        self.use_transparency = use_transparency
        self.neg_shade = neg_shade
        self.neg_flip = neg_flip
        self.max_alpha_val = max_alpha_val
        self.use_transparency = use_transparency

        # Compute characters and box
        self.compute_characters()

        # Set x axis params
        self.xlim = [self.box.xlb, self.box.xub]\
            if xlim is None else xlim
        self.xticks = self.poss \
            if xticks is None else xticks
        self.xticklabels = ['%d' % x for x in self.xticks] \
            if xticklabels is None else xticklabels
        self.xlabel = xlabel

        # Set y axis params
        self.ylim = [self.box.ylb, self.box.yub]\
            if ylim is None else ylim
        self.yticks = range(
            int(np.ceil(self.ylim[0])),
            int(np.floor(self.ylim[1])) + 1) \
            if yticks is None else yticks
        self.yticklabels = ['%d' % y for y in self.yticks]\
            if yticklabels is None else yticklabels
        self.ylabel = ylabel

        # Set other formatting parameters
        self.floor_line_width=floor_line_width


    def draw(self, ax=None):
        if ax is None:
            ax = plt.gca()

        # Draw characters
        for char in self.char_list:
            char.draw(ax)

        # Draw floor line
        ax.axhline(0,color='k',linewidth=self.floor_line_width)

        # Logo-specific formatting
        ax.set_xlim(self.xlim)
        ax.set_ylim(self.ylim)

        if self.logo_style == 'classic':

            # x axis
            ax.set_xticks(self.xticks)
            ax.xaxis.set_tick_params(length=0)
            ax.set_xticklabels(self.xticklabels, rotation=90)

            # y axis
            ax.set_yticks(self.yticks)
            ax.set_yticklabels(self.yticklabels)
            ax.set_ylabel(self.ylabel)

            # box
            ax.spines['left'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        elif self.logo_style == 'naked':

            # Turn everything off
            ax.axis('off')

        elif self.logo_style == 'rails':
            ax.set_xticks([])
            ax.set_yticks(self.ylim)
            ax.set_ylabel(self.ylabel)
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)


        elif self.logo_style == 'light_rails':
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
            [i.set_linewidth(0.5) for i in ax.spines.itervalues()]


        elif self.logo_style == 'everything':

            # x axis
            ax.set_xticks(self.xticks)
            ax.set_xticklabels(self.xticklabels)
            ax.set_xlabel(self.xlabel)

            # y axis
            ax.set_yticks(self.yticks)
            ax.set_yticklabels(self.yticklabels)
            ax.set_ylabel(self.ylabel)

            # box
            ax.axis('on')

        else:
            assert False, 'Error! Undefined logo_style=%s' % self.logo_style

    def compute_characters(self):

        # Get largest value for computing transparency
        if self.max_alpha_val is None:
            self.max_alpha_val = abs(self.df.values).max()

        char_list = []
        for i, pos in enumerate(self.poss):

            vals = self.df.loc[pos, :].values
            ymin = (vals * (vals < 0)).sum()

            # Reorder columns
            if self.stack_order == 'big_on_top':
                indices = np.argsort(vals)
            elif self.stack_order == 'small_on_top':
                indices = np.argsort(vals)[::-1]
            else:
                indices = range(len(vals))
            ordered_chars = self.chars[indices]

            # This is the same for every character
            x = pos - .5
            w = 1.0

            # Initialize y
            y = ymin

            for n, char in enumerate(ordered_chars):

                # Get value
                val = self.df.loc[pos, char]

                # Get height
                h = abs(val)
                if h < SMALL:
                    continue

                # Get color
                color = self.color_dict[char]

                # Get flip, alpha, and shade
                if val >= 0.0:
                    alpha = 1.0
                    flip = False
                    shade = 1.0
                else:
                    alpha = self.neg_shade
                    flip = self.neg_flip
                    shade = self.neg_shade

                if self.use_transparency:
                    alpha *= h / self.max_alpha_val
                    if alpha > 1:
                        alpha = 1.0

                assert alpha <= 1.0, \
                    'Error: alpha=%f must be in [0,1]' % alpha

                # Create and store character
                char = Character(
                    c=char, x=x, y=y, w=w, h=h,
                    alpha=alpha, color=color, flip=flip,
                    shade=shade, font_name=self.font_name, edgecolor='none')
                char_list.append(char)

                # Increment y
                y += h

        # Get box
        xlb = min([c.box.xlb for c in char_list])
        xub = max([c.box.xub for c in char_list])
        ylb = min([c.box.ylb for c in char_list])
        yub = max([c.box.yub for c in char_list])
        box = Box(xlb, xub, ylb, yub)

        # Set char_list and box
        self.char_list = char_list
        self.box = box

"""

the following can be run in this way from the command line:
python logomaker.py --input text.txt --filetype txt --parameters parameters.txt

"""

def get_commandline_arguments():
    """
    this method uses argparse to parse command line arguments for the parameters file,
    and also the input file and input file type. I am uncertain whether it should have
    any logic for handling input file or filetype.
    parameters
    ----------
    None
    """
    parser = argparse.ArgumentParser()

    #input file argument
    parser.add_argument('-i', '--input', dest='input_file', default='stdin', type=str,
                        help='File containing input data. Default: standard input')

    #parameters.txt file argument
    parser.add_argument('--parameters', dest='parameters_file', default="parameters.txt", type=str,
                        help='File containing input parameters. Default: standard input')

    #file_type argument: e.g. fasta,csv
    parser.add_argument('--filetype', dest='file_type', default='fa', type=str,
                        help='input data-file format. Default: standard input')

    # Parse arguments
    args = parser.parse_args()

    # Return arguments
    return args

import sys
def load_mat(inputdata_filename, inputdata_filetype, mat_type='counts', parameters_filename='none'):


    """
    This class method sets up the logic for using loadmat as follows
    python load_mat.py --input text.txt --filetype txt --parameters parameters.txt

    parameters
    ----------
    :parameter inputdata_filename  (str): name of file containing input data
    :parameter inputdata_filetype  (str): file type of file containing input data
    :parameter parameters_filename (str): name of file containing parameters

    """
    # get the parameters from the commandline
    args = get_commandline_arguments()
    # read parameters file name into a conveniently named variable
    parameterFileName = args.parameters_file

    # read the input data file:

    # if no command line input_data file provided
    if (args.input_file == 'stdin'):
        try:
            if(inputdata_filetype=='fasta'):
                mat = load_fasta(inputdata_filename,mat_type=mat_type)

            #print(mat)
        except IOError as e:
            print(" Something went wrong with the input file ",e)
            raise e

    # if command line input_data file provided, try to read that
    else:
        try:
            mat = pandas.read_csv(args.input_file, delim_whitespace=True)
        except IOError as e:
            print(" Something went wrong with the input file ",e)
            raise e

    # read parameters file
    try:
        # try opening file
        fileObj = open(parameterFileName)

        """ the following snippet tries to read parameters from file into a dict called params """
        try:
            for line in fileObj:
                # removing leading and trailing whitespace
                line = line.strip()
                # ignore comments in the parameters file
                if not line.startswith("#"):
                    # split lines by colon separator
                    key_value = line.split(":")
                    # print lists only of format key-value, i.e. ignore inputs \
                    # with multiple values for the same key:{value_1,value_2}
                    if len(key_value) == 2:
                        params[key_value[0].strip()] = key_value[1].strip()

            """ 
            parse read-in parameters correctly, i.e. change the value of the appropriate 
            key to the appropriate type
            """
            params["logo_type"] = str(params["logo_type"])
            params["logo_style"] = str(params["logo_style"])
            params["color_scheme"] = str(params["color_scheme"])
            params["ylabel"] = str(params["ylabel"])
            params["resolution"] = float(params["resolution"])
            # need additional care for conversion to lists
            # params["fig_size"] = list(params["fig_size"])
            # params["ylim"] = list(params["ylim"])
        except (RuntimeError,ValueError) as pe:
            print('some went wrong parsing the parameters file',pe.message)

    except IOError as e:
        print("Something went wrong reading the parameters file: ",e.strerror, e.filename)

    param_df = pandas.DataFrame(params, index=[0])
    return mat


def load_fasta(file_name, mat_type='counts_mat'):

    """
    This methods loads sequences from a fasta file and returns a matrix
    based on the mat type parameter

    :param file_name: fasta file name containing input data
    :param mat_type: type of matrix to be returned
    :return: counts matrix is the default return type
    """
    # Read in sequences from FASTA file into a pandas dataframe
    df = pandas.io.parsers.read_csv(file_name, comment='>', names=['seq'])

    # Get sequence length
    seqLength = len(df.loc[0, 'seq'])

    # Remove whitespace and ensure that sequence length doesn't vary
    for i in range(len(df)):
        seq = df.loc[i, 'seq'].strip()
        assert len(seq) == seqLength
        df.loc[i, 'seq'] = seq


    # Get set of unique characters
    seq_list = list(df['seq'])
    # join all sequences in a one long string
    # might be a bad idea for longer files
    seq_concat = ''.join(seq_list)
    # get unique characters
    unique_chars = list(set(seq_concat))

    # Create counts matrix and fill with zeros initially
    # label columns with unique seq chars via unique_chars
    counts_mat = pandas.DataFrame(index=range(seqLength), columns=unique_chars).fillna(0)

    # Create array of characters at each position as an np array
    char_array = np.array([np.array(list(seq)) for seq in seq_list])



    # Sum of the number of occurrences of each character at each position
    for c in unique_chars:
        counts_mat.loc[:, c] = (char_array == c).sum(axis=0).ravel()

    # temporary addition, add val_ to unique chars
    # so validate matrix behaves normally
    counts_mat = counts_mat.rename(columns=lambda colName: 'val_'+colName)

    # Name index
    #counts_mat.index.name = 'pos'

    if mat_type=='freq_mat' or mat_type=='frequency':
        #print(" printing frequency matrix: \n")
        return counts_mat_to_freq_mat(counts_mat)

    #print(" printing counts matrix: \n")
    return counts_mat

# Load counts matrix from fasta file
#counts_mat = load_fasta('crp_sites.fasta')

# Convert to frequency matrix
def counts_mat_to_freq_mat(counts_mat):
    freq_mat = counts_mat.copy()
    pseudocount = 1
    tmp_mat = counts_mat + pseudocount
    freq_mat.loc[:,:] = tmp_mat.values/tmp_mat.values.sum(axis=1)[:,np.newaxis]
    return freq_mat

#freq_mat = counts_mat_to_freq_mat(counts_mat)
#freq_mat.head()
#freq_mat.to_csv('crp_freq_mat.txt', sep='\t')
