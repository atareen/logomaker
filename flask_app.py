from flask import Flask, render_template, redirect, send_file, request,url_for,flash
import flask

from werkzeug.utils import secure_filename
import StringIO
import matrix
import pandas
import re
import sys
import os


import matplotlib.pyplot as plt
import logomaker

app = Flask(__name__)
# figure out what reasonable value for secret key should be
app.secret_key = 'some_secret'

'''
fig = plt.figure(figsize=[8,6])
ax = fig.add_subplot(3,1,1)
logomaker.Logo(mat=mat,mat_type='freq_mat',logo_type='freq_logo').draw()
#print(mat.head().to_html())
print(mat.head())
'''

#for index, row in mat.head().iterrows():
#    print row

#plt.show()


ALLOWED_EXTENSIONS = set(['txt', 'fasta'])


# global variable fix to unicode/panda conversion from python to template
# new globals
uploadData = ''
displayInput = []

inputDataLength = 0
displayParams = []
paramsLength = 0

userParametersUploaded = False

mat_type = 'freq_mat'
logo_type = 'weight_logo'
logo_style = 'classic'
color_scheme = 'classic'



# old globals, may get rid of them
uploadMatGlobal = pandas.DataFrame()
uploadedFileName = ''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# upload multiple files
# how to distinguish between params file and input data
@app.route('/uploadMultiple', methods=['GET', 'POST'])
def upload_file():

    # upload files in the post
    if request.method == 'POST':
        files = request.files.getlist('uploadedFile[]')
        print(len(files))
        for uploadFile in files:
            #upload(uploadFile.filename)
            uploadFile.save(secure_filename(uploadFile.filename))
            # status message for user, render on multiupload
            #message =str(uploadFile.filename)+"\n"
            #flash(message)

        print(files[1])

        # parse parameters file
        # parseParams returns a params dict
        params_dict = parseParams(files[1].filename)
        #convert params dict to pandas dataframe for displaying
        params = pandas.DataFrame(params_dict, index=[0])
        params_html = params.head().to_html()
        #print(params.head())


        with open(files[0].filename, 'r') as f:
            rawInput = f.readlines()

        displayInput = []
        inputDataLength = len(rawInput)

        for x in range(inputDataLength):
            #displayInput.append(rawInput[x].split(" "))
            displayInput.append(rawInput[x].split('    '))

        with open(files[1].filename, 'r') as p:
            rawParams = p.read()

        displayParams = []
        paramsLength = len(rawParams)

        for index in range(paramsLength):
            displayParams.append(rawParams[index].split('    '))


        # surround this with try catch also if the file is of the wrong format or bad data etc.
        uploadMat = logomaker.load_mat(files[0].filename, 'fasta', mat_type='freq_mat')
        uploaded_mat_html = matrix.validate_freq_mat(uploadMat)

        global uploadMatGlobal
        uploadMatGlobal = uploadMat

        global uploadedFileName
        uploadedFileName = files[0].filename

        # if one file uploaded
        # handle the case of more than 2 files uploaded
        if len(files) == 1:

            # status message displayed to the user
            #return redirect(url_for('index',showStatus=True))
            #message = 'Successfully Upload file: '+str(files[0].filename)
            #flash(message)

            #parse parameters file
            params = parseParams(files[0].filename)
            params_html = params.head().to_html(classes='mat')
            print(params.head())
            #return redirect(url_for('index'))
            return render_template('multiUpload.html',paramsTable =[params_html])
        else:
            #return render_template('multiUpload.html',paramsTable =[params_html])
            # fill parameters here ultimately with params file
            #return render_template('multiUpload.html', tables=[uploaded_mat_html.head().to_html(classes='mat')],params=params,paramsTable =[params_html],matPassedToUpload=uploadMat, matType='freq_mat', logoType='weight_logo')
            return render_template('multiUpload.html', logoType=params_dict['logo_type'],colorScheme=params_dict['color_scheme'],
                                   tables=[uploaded_mat_html.head().to_html(classes='mat')], params=params_dict,
                                   paramsTable=[params_html], matPassedToUpload=uploadMat, matType='freq_mat',
                                   inputDataLength=inputDataLength,displayInput=displayInput,
                                   paramsLength=paramsLength,displayParams=displayParams)

'''
<link rel=stylesheet type=text/css href="{{ url_for('static', filename='style.css') }}">
  <h2>Input Params</h2>
  {% for params in paramsTable %}
    {{ params|safe }}
  {% endfor %}
'''

@app.route('/updateParams', methods=['POST'])
def submit_textarea():
    updatedText = request.form['paramsText']
    print(updatedText)
    return updatedText
    #return format(request.form["paramsText"])

@app.context_processor
def displayUploadStatus(displayMessage=''):
    return dict(statusMessage=displayMessage)


@app.route("/")
def index():
    #return render_template("index.html",mat=mat)
    #mat_html = matrix.validate_freq_mat(mat)
    #mat_html = matrix.validate_freq_mat(logomaker.load_mat('crp_sites.fasta', 'fasta', mat_type='frequency'))
    #return render_template('index.html', tables=[mat_html.head().to_html(classes='mat')],mat=mat)
    return render_template('index.html')


'''
<!--
<img src="{{ url_for('fig') }}">

<p>{{ url_for('fig') }}</p>
-->


@app.route('/fig')
def fig():
    fig = plt.figure(figsize=[8, 6])
    ax = fig.add_subplot(3, 1, 1)
    logomaker.Logo(mat=matStatic, mat_type='freq_mat', logo_type='freq_logo').draw()

    img = StringIO.StringIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='image/png')
'''


# when I click submit, this funciton gets called. I should render the default parameters used to generate the plot in the parameter values window as a dict
# this dict should later be combined with the update function


# upload file at index.html and move to upload.html
# this method draws without the params file
@app.route('/', methods=['GET', 'POST'])
def uploaded_file():
    # surround with try catch if post fails, handle exception
    if request.method == 'POST':
    #if request.method == 'POST' and len(str(request.files))>1:


        f = request.files['file']
        if not allowed_file(f.filename):
            flash(" File type not supported: %s " % (f.filename))
            return render_template('index.html')

        # secure filename cleans the name of the uploaded file
        f.save(secure_filename(f.filename))

        #message = str(f.filename)
        #flash(message)

        #print("f: ",f)
        # surround this with try catch also if the file is of the wrong format or bad data etc.
        uploadMat = logomaker.load_mat(f.filename, 'fasta', mat_type='freq_mat')
        uploaded_mat_html = matrix.validate_freq_mat(uploadMat)

        global uploadMatGlobal
        uploadMatGlobal = uploadMat

        global uploadedFileName
        uploadedFileName = f.filename

        with open(f.filename, 'r') as fileVar:
            rawInput = fileVar.readlines()

        #displayInput = []

        global inputDataLength
        inputDataLength = len(rawInput)

        global displayInput
        for x in range(inputDataLength):
            # displayInput.append(rawInput[x].split(" "))
            displayInput.append(rawInput[x].split('    '))

        # keep uploaded data to display after logo updates
        global uploadData
        uploadData = displayInput

        global mat_type
        global logo_type
        global color_scheme

        if userParametersUploaded is False:
            status_upload_w_default_params = "Uploaded "+str(uploadedFileName) + " with Default parameters \n"
            flash(status_upload_w_default_params)

        # the mat variable in here gets passed onto returned template, e.g. upload.html in this instance
        return render_template('upload.html', matType=mat_type, logoType=logo_type,
                           colorScheme=color_scheme, inputDataLength=inputDataLength, displayInput=displayInput)


# method only for uploading parameters
@app.route('/uploadParams',methods=['GET','POST'])
def parametersUpload():

    # surround with try catch if post fails, handle exception
    if request.method == 'POST':

        # if request.method == 'POST' and len(str(request.files))>1:
        f = request.files['file']
        # secure filename cleans the name of the uploaded file
        f.save(secure_filename(f.filename))

        #message = str(f.filename)
        #flash(message)

        with open(f.filename, 'r') as p:
            rawParams = p.read()

        #displayParams = []
        global paramsLength
        paramsLength = len(rawParams)

        global displayParams
        for index in range(paramsLength):
            displayParams.append(rawParams[index].split('    '))


        #make params dictionary from uploaded file
        params = parseParams(f.filename)
        # Justin's method
        paramsTest = load_parameters(file_name=f.filename)


        # flag variable that tells server if user upload custom parameters
        global userParametersUploaded
        userParametersUploaded = True

        #return render_template('upload.html', matType=mat_type, logoType=logo_type,
        #                       colorScheme=color_scheme, inputDataLength=inputDataLength, displayInput=displayInput,
        #                       paramsLength=paramsLength,displayParams=displayParams)

        return render_template('upload.html', matType=mat_type, logoType=params['logo_type'],
                               colorScheme=color_scheme, inputDataLength=inputDataLength, displayInput=displayInput,
                               #paramsLength=paramsLength,displayParams=displayParams,paramsUploaded=params)
                               paramsLength=paramsLength, displayParams=displayParams, paramsUploaded=paramsTest)


import ast
# display the uploaded figure at upload.html after file has been uploaded
@app.route('/uploadedFig/<matType>/<logoType>/<argColorScheme>')
@app.route('/uploadedFig/<matType>/<logoType>/<argColorScheme>/<paramsDict>')
def uploadedFig(matType,logoType,argColorScheme,paramsDict={}):

    #logomaker.Logo(mat=uploadMatGlobal,mat_type='freq_mat',logo_type='info_logo').draw()



    # if no parameters file uploaded
    if bool(paramsDict) is False:

        fig = plt.figure(figsize=[8, 6])
        ax = fig.add_subplot(3, 1, 1)

        logomaker.Logo(mat=uploadMatGlobal, mat_type=matType, logo_type=logoType,color_scheme=str(argColorScheme)).draw()

    #otherwise if parameters file uploaded
    elif bool(paramsDict) is True:

        # need to do this to convert params to dict
        # flask returns params as unicode instead of dict
        paramsDict = ast.literal_eval(paramsDict)

        fig = plt.figure(figsize=paramsDict['fig_size'])
        ax = fig.add_subplot(3, 1, 1)

        logomaker.Logo(mat=uploadMatGlobal, mat_type=matType, logo_type=str(paramsDict['logo_type']),
                      color_scheme=paramsDict['color_scheme'],logo_style=paramsDict['logo_style']).draw()


    img = StringIO.StringIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='image/png')

# if I edit the default values of parameters, hit redraw, and then upload new parameters, the
# default parameters don't get erased. I am right now returning early if userParametersUploaded
# is false but that's not the best of of doing this. Handle the case where default values are
# edited, redrawn, and then new paramter file is upload; make sure old values are overwritten

# press button on upload.html to update logo type
@app.route('/updateLogo', methods=['GET', 'POST'])
def updateLogo():

    updatedText = request.form['paramsText']

    # make updates to the params box
    tempParamFileName = "tempParams.txt"
    with open(tempParamFileName, "w") as text_file:
        text_file.write(updatedText)

    #updatedParamsTest = parseParams(tempParamFileName)
    updatedParamsTest = load_parameters(tempParamFileName)

    if userParametersUploaded is False:
        # keep the value of logo type updated
        # so it doesn't change when parameters
        # are uploaded
        global logo_type
        logo_type = updatedParamsTest['logo_type']

        global color_scheme
        color_scheme = updatedParamsTest['color_scheme']
        os.remove(tempParamFileName)
        return render_template('upload.html', matType=mat_type, logoType=logo_type, colorScheme=color_scheme,
                               inputDataLength=inputDataLength, displayInput=displayInput)

    updatedParams = load_parameters(tempParamFileName)
    #print("logo_type: ",updatedParams['logo_type'])


    with open(tempParamFileName, 'r') as p:
        rawParams = p.read()

    global paramsLength
    paramsLength = len(rawParams)

    global displayParams
    for index in range(paramsLength):
        displayParams.append(rawParams[index].split('    '))

    '''
    # keep the value of logo type updated
    # so it doesn't change when parameters
    # are uploaded
    global logo_type
    logo_type = updatedParamsTest['logo_type']

    global color_scheme
    color_scheme = updatedParamsTest['color_scheme']
    '''
    os.remove(tempParamFileName)

    #print("printing1: ", userParametersUploaded)
    #print("printing2: ", updatedParamsTest)

    if request.method == 'POST':

        # if params not uploaded by user, then don't pass to upload.html
        # this is not robust at all, check if user has uploaded some parameters
        # via a variable that's true when upload parameters button is hit and
        # false other wise
        #if paramsLength <= 68:
        if userParametersUploaded is False:
            return render_template('upload.html', matType=mat_type, logoType=logo_type, colorScheme=color_scheme,
                           inputDataLength=inputDataLength, displayInput=displayInput)
        else:
            return render_template('upload.html', matType=mat_type, logoType=updatedParams['logo_type'], colorScheme=updatedParams['color_scheme'],
                                   inputDataLength=inputDataLength, displayInput=displayInput,
                                   paramsLength=paramsLength, displayParams=displayParams)



def parseParams(parameterFileName):

    """
    helper function that will parse the upload parameters file
    so that the parameters can be displayed on screen

    parameters
    ----------
    :parameter parameters_filename (str): name of file containing parameters

    """
    params = {}
    # try read parameters file
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

            if "logo_type" in params:
                params["logo_type"] = str(params["logo_type"])
            if "logo_style" in params:
                params["logo_style"] = str(params["logo_style"])
            if "color_scheme" in params:
                params["color_scheme"] = str(params["color_scheme"])
            if "ylabel" in params:
                params["ylabel"] = str(params["ylabel"])
            if "resolution" in params:
                params["resolution"] = float(params["resolution"])
            # need additional care for conversion to lists
            # params["fig_size"] = list(params["fig_size"])
            # params["ylim"] = list(params["ylim"])
        except (RuntimeError,ValueError) as pe:
            print('some went wrong parsing the parameters file',pe.message)

    except IOError as e:
        print("Something went wrong reading the parameters file: ",e.strerror, e.filename)

    # the following will change your dict to a pandas df
    #param_df = pandas.DataFrame(params, index=[0])
    return params


'''
@app.route("/plot")
def show_plot():

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    fig = plt.figure(figsize=[8, 6])
    ax = fig.add_subplot(3, 1, 1)

    logomaker.Logo(mat=mat, mat_type='freq_mat', logo_type='freq_logo').draw()

    ax = fig.add_subplot(3, 1, 2)
    logomaker.Logo(mat=mat, mat_type='energy_mat', font_name='Arial Bold', logo_type='freq_logo',
                   color_scheme='random', logo_style='rails', stack_order='small_on_top').draw()

    # Plot energy logo
    ax = fig.add_subplot(3, 1, 3)
    logomaker.Logo(mat=mat, mat_type='energy_mat', logo_type='energy_logo', neg_flip=True,
                   logo_style='everything', font_name='Comic Sans MS Bold', color_scheme='gray').draw()

    canvas=FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)

    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response
'''


def load_parameters(file_name, print_params=False, print_warnings=False):
    """
    Fills a dictionary with parameters parsed from specified file.
    Arg:
        file_name (str): Name of file containing parameter assignments
    Return:
        params_dict (dict): Dictionary containing parameter assignments
            parsed from parameters file
    """

    # Create dictionary to hold results
    params_dict = {}

    # Create regular expression for parsing parameter file lines
    pattern = re.compile('^\s*(?P<param_name>[\w]+)\s*:\s*(?P<param_value>.*)$')

    # Quit if file_name is not specified
    if file_name is None:
        return params_dict

    # Open parameters file
    try:
        file_obj = open(file_name, 'r')
    except IOError:
        print('Error: could not open file %s for reading.' % file_name)
        raise IOError

    # Process each line of file and store resulting parameter values
    # in params_dict
    params_dict = {}
    prefix = '' # This is needed to parse multi-line files
    for line in file_obj:

        # removing leading and trailing whitespace
        line = prefix + line.strip()

        # Ignore lines that are empty or start with comment
        if (len(line) == 0) or line.startswith('#'):
            continue

        # Record current line plus a space in prefix, then continue to next
        # if line ends in a "\"
        if line[-1] == '\\':
            prefix += line[:-1] + ' '
            continue

        # Otherwise, clean prefix and continue with this parsing
        else:
            prefix = ''

        # Parse line using pattern
        match = re.match(pattern, line)

        # If line matches, record parameter name and value
        if match:
            param_name = match.group('param_name')
            param_value_str = match.group('param_value')

            # Evaluate parameter value as Python literal
            try:
                params_dict[param_name] = ast.literal_eval(param_value_str)
                if print_params:
                    print('[set] %s = %s' % (param_name, param_value_str))

            except ValueError:
                if print_warnings:
                    print(('Warning: could not set parameter "%s" because ' +
                          'could not interpret "%s" as literal.') %
                          (param_name, param_value_str))
            except SyntaxError:
                if print_warnings:
                    print(('Warning: could not set parameter "%s" because ' +
                          'of a syntax error in "%s".') %
                          (param_name, param_value_str))


        elif print_warnings:
            print('Warning: could not parse line "%s".' % line)

    return params_dict

if __name__ == "__main__":
    #other option
    #app.run(port=8080, debug=True)
    app.run(debug=True,use_reloader=True)
