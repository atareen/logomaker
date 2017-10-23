from flask import Flask, render_template, redirect, send_file, request,url_for,flash

import flask

from werkzeug.utils import secure_filename
import StringIO
import pandas
import re
import sys
import os


import matplotlib.pyplot as plt
import logomaker

app = Flask(__name__)
# session key. Use random key to invalidate old sessions
app.secret_key = os.urandom(32)


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


@app.route("/")
def index():
    return render_template('index.html')


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
    #if request.method == 'POST' and len(str(request.files))>1:

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
        uploadMat.to_csv('crp_counts.txt', sep='\t', float_format='%d')
        # END ADDITION (i)

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
        # clear list for new input uploads
        del displayInput[:]
        for x in range(inputDataLength):
            # displayInput.append(rawInput[x].split(" "))
            displayInput.append(rawInput[x].split('    '))

        # keep uploaded data to display after logo updates
        global uploadData
        uploadData = displayInput

        global mat_type
        global logo_type
        global color_scheme

        global userParametersUploaded
        userParametersUploaded = False

        if userParametersUploaded is False:
            status_upload_w_default_params = "Uploaded "+str(uploadedFileName) + " with Default parameters \n"
            flash(status_upload_w_default_params)

        # the mat variable in here gets passed onto returned template, e.g. upload.html in this instance
    return render_template('upload.html', matType=mat_type, logoType=logo_type,
                           colorScheme=color_scheme, inputDataLength=inputDataLength, displayInput=displayInput,
                           uploadMat=uploadMat)


import ast
# display the uploaded figure at upload.html after file has been uploaded
@app.route('/uploadedFig')
@app.route('/uploadedFig/<argMat>')
def uploadedFig(argMat=None):

    global userParametersUploaded
    print("uploaded fig, paramsUpload: ",userParametersUploaded)
    print("argMat: ",argMat)

    # if no parameters file uploaded
    if userParametersUploaded is False:

        print(" I have not uploaded parameters")
        # ADDITION (iia)
        # if no params uploaded, empty style file
        style_fileTemp = 'parameters_file.txt'
        with open(style_fileTemp, 'w') as f:
            f.write("")

        # Make frequency logo
        # logo2 = logomaker.make_logo(counts_mat)
        logo = logomaker.make_styled_logo(style_file=style_fileTemp, matrix=uploadMatGlobal)
        # END ADDITION (iia)

        # Draw logos
        fig, ax_list = plt.subplots(figsize=[8, 2])
        # logo1.draw(ax_list[0])

        logo.draw(ax_list)

        #fig = plt.figure(figsize=[8, 6])
        #ax = fig.add_subplot(3, 1, 1)

        #logomaker.Logo(mat=uploadMatGlobal, mat_type=matType, logo_type=logoType,color_scheme=str(argColorScheme)).draw()

    # otherwise if parameters file uploaded
    elif userParametersUploaded is True:

        # ADDITION (iib)
        global style_file
        print(" I have not uploaded parameters ",style_file)



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

        #return render_template('upload.html', matType=mat_type, logoType=logo_type,
        #                       colorScheme=color_scheme, inputDataLength=inputDataLength, displayInput=displayInput,
        #                       paramsLength=paramsLength,displayParams=displayParams)
        flash(" Logo redrawn with uploaded parameters")
        print('just hit upload parameters with filename ',style_file)
        return render_template('upload.html', matType=mat_type,
                               inputDataLength=inputDataLength, displayInput=displayInput,
                               paramsLength=paramsLength, displayParams=displayParams,
                               uploadMat=uploadMatGlobal,userParamsUploaded=userParametersUploaded)






if __name__ == "__main__":
    #other option
    #app.run(port=8080, debug=True)
    #app.run(debug=True,use_reloader=True)
    app.run()

