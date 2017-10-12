import argparse
import pandas as pd

"""
The class LoadMat is mean to work with LogoMaker.py.
LoadMat can be used by itself as follows:

standalone usage example:
python load_mat.py --input text.txt --filetype txt --parameters parameters.txt

the parameters file should have the following format:
# description of parameter 1
logo_type: info_logo
# description of parameter 2
logo_style: classic
# description of parameter 3
color_scheme: vividis
...

filetype can be fasta or csv, however I am uncertain where to implement the formatting for that
input is the file containing the actual input data (e.g. pwm) which will be used to make the logos

Expected output:
color_scheme fig_size logo_style  logo_type  resolution       ylabel   ylim
0      vividis    [8,2]    classic  info_logo      1080.0  Information  [0,2]


"""

#globally initalize params dict, this will be returned as a pandas
# which can be pass into logomaker.py
params = {}


class LoadMat:

    def get_commandline_arguments(self):
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

    def __init__(self):
        """
        This constructor sets up the logic for using loadmat as follows
        python load_mat.py --input text.txt --filetype txt --parameters parameters.txt
        """
        # get the parameters from the commandline
        args = LoadMat.get_commandline_arguments(self)
        # read parameters file name into a conveniently named variable
        parameterFileName = args.parameters_file

        # read the input file. This will have to be surrounded by try except
        # if input is in fact meant to be read this way
        inputFileName = args.input_file

        energy_mat = pd.read_csv(inputFileName, delim_whitespace=True)
        print(energy_mat.head())

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

        # to print parameters, arguments etc. un-comment the following
        #print(params)
        """
        print(params)
        print(args.parameters_file)
        print(args.file_type)
        print(args.input_file)
        """

# run the load matrix class
LoadMat()
parameters = pd.DataFrame(params, index=[0])
print(parameters)