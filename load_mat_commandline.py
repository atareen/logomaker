import sys
import argparse


def get_commandline_arguments():
    parser = argparse.ArgumentParser()

    #parameters.txt file argument
    parser.add_argument('-i', '--input', dest='parameters_file', default='stdin', type=str,
                        help='File containing input parameters. Default: standard input')
    # Parse arguments
    args = parser.parse_args()

    # Return arguments
    return args

args = get_commandline_arguments()

# read parameters from file into a dict called params
#fileName = "parameters.txt"
if len(sys.argv)==1:
    fileName = "parameters.txt"
else:
    fileName = args.parameters_file
fileObj = open(fileName)
params = {}     # initalize dictionary
for line in fileObj:
    line = line.strip()  # removing leading and trailing whitespace
    if not line.startswith("#"):    # ignore comments in the parameters file
        key_value = line.split(":")     # split lines by colon separator
        if len(key_value) == 2:     # print lists only of format key-value
            params[key_value[0].strip()] = key_value[1].strip()

#surround by try/except to handle bad input
fileObj.close()

# parse read-in parameters correctly, i.e. change the value of the appropriate \
# key to the appropriate type
params["logo_type"] = str(params["logo_type"])
params["logo_style"] = str(params["logo_style"])
params["color_scheme"] = str(params["color_scheme"])
#params["ylim"] = list(params["ylim"])
params["ylabel"] = str(params["ylabel"])
params["resolution"] = float(params["resolution"])
#params["fig_size"] = list(params["fig_size"])

print(params)
