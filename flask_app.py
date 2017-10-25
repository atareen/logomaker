from flask import Flask, render_template, redirect, send_file, request,url_for,flash

import flask

from werkzeug.utils import secure_filename
import StringIO
import pandas
import inspect
import sys
import os



import matplotlib.pyplot as plt
import logomaker

app = Flask(__name__)
# session key. Use random key to invalidate old sessions
app.secret_key = os.urandom(64)


ALLOWED_EXTENSIONS = set(['txt', 'fasta'])

ALLOWED_PARAM_EXTENSIONS = set(['txt'])

# global variable fix to unicode/panda conversion from python to template
# new globals
uploadData = ''
displayInput = []

inputDataLength = 0
displayParams = []
paramsLength = 0

userParametersUploaded = False
paramsTest = {}

# part of ADDITION (iib)
style_file = ''
updatedParams = False


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

def allowed_param_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_PARAM_EXTENSIONS


@app.route('/updateParams', methods=['POST'])
def submit_textarea():
    updatedText = request.form['paramsText']
    print(updatedText)
    return updatedText
    #return format(request.form["paramsText"])

@app.context_processor
def displayUploadStatus(displayMessage=''):
    return dict(statusMessage=displayMessage)


# homepage global variables
default_parameters_text = """
colors : 'Blues'
logo_type : 'counts'
axes_style : 'vlines'
font_family : 'sans-serif'
font_weight : 'heavy'
"""

defaultMat = logomaker.load_alignment('data/crp_sites.fasta')
defaultMat.to_csv('crp_counts.txt', sep='\t', float_format='%d')
# flag that checks whether default parameters have been modified
#if this is set to default, copy default matrices to uploaded matrices
# upon parameter modification
updatedDefaultParams = ''
defaultDisplayInput = []
defaultInputDataLength = 0
defaultParamsLength = 0
defaultDisplayParams = []
default_style_file = 'parameters_file.txt'

# end homepage global variables

@app.route("/")
def index():

    # this snippet cannot be different than the default snippet
    # in uploadedFig

    global defaultMat
    global default_parameters_text

    with open(default_style_file, 'w') as f:
        f.write(default_parameters_text)

    defaultFileName = 'crp_sites.fasta'

    with open('data/'+defaultFileName, 'r') as fileVar:
        defaultRawInput = fileVar.readlines()

    global defaultInputDataLength
    defaultInputDataLength = len(defaultRawInput)

    global defaultDisplayInput
    for x in range(defaultInputDataLength):
        # displayInput.append(rawInput[x].split(" "))
        defaultDisplayInput.append(defaultRawInput[x].split('    '))


    with open(default_style_file, 'r') as p:
        defaultRawParams = p.read()

    global defaultParamsLength
    defaultParamsLength = len(defaultRawParams)

    global defaultDisplayParams
    for index in range(defaultParamsLength):
        defaultDisplayParams.append(defaultRawParams[index].split('    '))

    print("Index: drawing default logo")

    return render_template('index.html',defaultMat=defaultMat,defaultInputDataLength=defaultInputDataLength,
                           defaultDisplayInput=defaultDisplayInput,defaultParamsLength=defaultParamsLength,
                           defaultDisplayParams=defaultDisplayParams)


# when I click submit, this funciton gets called. I should render
# the default parameters used to generate the plot in the parameter
# values window as a dict this dict should later be combined with
# the update function. TLDR:
# upload file at index.html
# and draws without params file
@app.route('/', methods=['GET', 'POST'])
def uploaded_file():
    # surround with try catch if post fails, handle exception
    if request.method == 'POST':

        # if not editing default params, set back to default value
        global updatedDefaultParams
        updatedDefaultParams = ''

        f = request.files['file']

        # display flash message if filetype not supported
        if not allowed_file(f.filename) and len(f.filename) is not 0:
            print(f.filename)
            flash(" File type not supported:  "+str(f.filename))
            #flash(" File type not supported ")
            return render_template('index.html')


        #if button pressed without any uploaded
        if len(f.filename) is 0:
            flash(" Please select a file to upload ")
            return render_template('index.html')


        print(f.filename)

        # secure filename cleans the name of the uploaded file
        f.save(secure_filename(f.filename))

        # surround this with try catch also if the file is of the wrong format or bad data etc.
        # upload matrix contains input data
        # ADDITION (i):         # Load counts matrix from fasta file
        # uploadMat = logomaker.load_mat(f.filename, 'fasta', mat_type='freq_mat')

        uploadMat = logomaker.load_alignment(f.filename)
        # why do the following? ask Justin:
        #uploadMat.to_csv('crp_counts.txt', sep='\t', float_format='%d')
        # END ADDITION (i)

        global uploadMatGlobal
        uploadMatGlobal = uploadMat

        global uploadedFileName
        uploadedFileName = f.filename

        with open(f.filename, 'r') as fileVar:
            rawInput = fileVar.readlines()

        global inputDataLength
        inputDataLength = len(rawInput)

        global displayInput
        # clear list for new input uploads
        del displayInput[:]
        for x in range(inputDataLength):
            # displayInput.append(rawInput[x].split(" "))
            displayInput.append(rawInput[x].split('    '))

        # keep uploaded data to display after logo updates
        global uploadData
        uploadData = displayInput

        global userParametersUploaded
        userParametersUploaded = False

        if userParametersUploaded is False:
            status_upload_w_default_params = "Uploaded "+str(uploadedFileName) + " with Default parameters \n"
            flash(status_upload_w_default_params)

        # the mat variable in here gets passed onto returned template, e.g. upload.html in this instance
    return render_template('upload.html', inputDataLength=inputDataLength, displayInput=displayInput,
                           uploadMat=uploadMat)


# display the uploaded figure at upload.html after file has been uploaded
@app.route('/uploadedFig')
@app.route('/uploadedFig/<argMat>')
@app.route('/uploadedFig/<argMat>/<refresh>')
def uploadedFig(argMat=None,refresh=None):

    global userParametersUploaded
    print("Uploaded fig, paramsUpload: ",userParametersUploaded)

    # flag for default logo drawing
    strArgMat = str(argMat)
    strArgMat.encode('ascii')

    strRefresh = str(refresh)
    strRefresh.encode('ascii')

    print("argMat: ",strArgMat)

    # for drawing the homepage logo
    if(strArgMat=='default'):

        print("In the default part of UploadedFig")
        global updatedDefaultParams
        updatedDefaultParams = strArgMat

        # get default parameters for printing
        global defaultMat
        global default_parameters_text

        style_fileTemp = 'parameters_file.txt'
        with open(style_fileTemp, 'w') as f:
            f.write(default_parameters_text)

        if(strRefresh=='editDefault'):
            print("Uploaded Fig strRefresh: ",strRefresh)
            logo = logomaker.make_styled_logo(style_file=style_file, matrix=defaultMat)
        else:
            print("Uploaded Fig strRefresh: ", strRefresh)
            logo = logomaker.make_styled_logo(style_file=style_fileTemp, matrix=defaultMat)

        # Draw logos
        fig, ax_list = plt.subplots(figsize=[8, 2])
        # logo1.draw(ax_list[0])

        logo.draw(ax_list)

        img = StringIO.StringIO()
        fig.savefig(img)
        img.seek(0)
        return send_file(img, mimetype='image/png')

    # if no parameters file uploaded
    if userParametersUploaded is False:

        print(" Draw Fig: I have not uploaded parameters")
        # ADDITION (iia)
        # if no params uploaded, empty style file
        style_fileTemp = 'parameters_file.txt'
        with open(style_fileTemp, 'w') as f:
            f.write("")

        logo = logomaker.make_styled_logo(style_file=style_fileTemp, matrix=uploadMatGlobal)
        # END ADDITION (iia)

        # Draw logos
        fig, ax_list = plt.subplots(figsize=[8, 2])

        logo.draw(ax_list)

    # otherwise if parameters file uploaded
    elif userParametersUploaded is True:

        # ADDITION (iib)
        #global style_file
        print(" Draw Fig: I have uploaded parameters ",style_file)

        logo = logomaker.make_styled_logo(style_file=style_file, matrix=uploadMatGlobal)
        # Draw logos
        fig, ax_list = plt.subplots(figsize=[8, 2])
        logo.draw(ax_list)
        # END ADDITION (iib)

    img = StringIO.StringIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='image/png')


# method only for uploading parameters
@app.route('/uploadParams',methods=['GET','POST'])
def parametersUpload():

    # surround with try catch if post fails, handle exception
    if request.method == 'POST':

        # if request.method == 'POST' and len(str(request.files))>1:
        f = request.files['file']

        # if button pressed without any uploaded
        if len(f.filename) is 0:
            flash(" Please select a parameters file to upload ")
            return render_template('upload.html', matType=mat_type, logoType=logo_type,
                               colorScheme=color_scheme, inputDataLength=inputDataLength, displayInput=displayInput)

        # if not right extension
        if not allowed_param_file(f.filename) and len(f.filename) is not 0:
            print(f.filename)
            flash(" parameters must have .txt extension ")
            return render_template('upload.html', matType=mat_type, logoType=logo_type,
                               colorScheme=color_scheme, inputDataLength=inputDataLength, displayInput=displayInput)

        # secure filename cleans the name of the uploaded file
        f.save(secure_filename(f.filename))

        with open(f.filename, 'r') as p:
            rawParams = p.read()

        global paramsLength
        paramsLength = len(rawParams)

        global displayParams
        for index in range(paramsLength):
            displayParams.append(rawParams[index].split('    '))


        # ADDITION (iib)
        # this uploaded file will go into the makestyled logo method
        global style_file
        style_file = f.filename
        # END ADDITION (iib)


        # flag variable that tells server if user upload custom parameters
        global userParametersUploaded
        userParametersUploaded = True

        print('Upload params: ',userParametersUploaded)

        flash(" Logo redrawn with uploaded parameters")
        print('Upload Params: Just hit upload parameters with filename ',style_file)
        return render_template('upload.html',
                               inputDataLength=inputDataLength, displayInput=displayInput,
                               paramsLength=paramsLength, displayParams=displayParams,
                               uploadMat=uploadMatGlobal,userParamsUploaded=userParametersUploaded)


# press button on upload.html to update logo type
#@app.route('/updateLogo', methods=['GET', 'POST'])
@app.route('/updateLogo', methods=['POST'])
def updateLogo():

    if request.method == 'POST':

        if updatedDefaultParams == 'default':
            print('getting data from default textarea')
            updatedText = request.form['defaultParamsText']
        else:
            updatedText = request.form['paramsText']

        # make updates to the params box
        tempParamFileName = "updatedParams.txt"
        with open(tempParamFileName, "w") as text_file:
            text_file.write(updatedText)

        global style_file
        style_file = tempParamFileName

        with open(tempParamFileName, 'r') as p:
            rawParams = p.read()

        global paramsLength
        paramsLength = len(rawParams)

        global displayParams
        del displayParams[:]

        for index in range(paramsLength):
            displayParams.append(rawParams[index].split('    '))

        flash(" Logo redrawn with updated parameters")

        global updatedParams
        updatedParams = True

        print('Update Params: Just hit update parameters with filename ', style_file, " Updated default params: ",updatedDefaultParams)

        if updatedDefaultParams == 'default':
            print("Update: editing default parameteres")

            '''
                return render_template('index.html',defaultMat=defaultMat,defaultInputDataLength=defaultInputDataLength,
                           defaultDisplayInput=defaultDisplayInput,defaultParamsLength=defaultParamsLength,
                           defaultDisplayParams=defaultDisplayParams)
            
            '''

            return render_template('index.html', uploadMat=defaultMat, defaultInputDataLength=defaultInputDataLength,
                                   defaultDisplayInput=defaultDisplayInput, paramsLength=paramsLength,
                                   displayParams=displayParams,userParamsUploaded=userParametersUploaded,
                                   style_file=style_file, updatedParams=updatedParams,updatedDefaultParams=updatedDefaultParams)
        else:

            # if not editing default parameters,
            # updatedDefaultParams is set to default
            # value in upload file

            return render_template('upload.html',
                                   inputDataLength=inputDataLength, displayInput=displayInput,
                                   paramsLength=paramsLength, displayParams=displayParams,
                                   uploadMat=uploadMatGlobal,userParamsUploaded=userParametersUploaded,
                                   style_file=style_file,updatedParams=updatedParams)





if __name__ == "__main__":

    #other option
    #app.run(port=8080, debug=True)
    #app.run(debug=True,use_reloader=True)
    #app.jinja_env.auto_reload = True
    #app.config['TEMPLATES_AUTO_RELOAD'] = True
    #https://stackoverflow.com/questions/41144565/flask-does-not-see-change-in-js-file
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # avoids loading cached image on send_url
    app.run()


