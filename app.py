#!/usr/bin/python2.7
from flask import Flask, render_template, request, session, flash
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os
import logomaker
import uuid
import shutil
import sys
import subprocess

# this is the name of the flask app. This conventional in the flask frame-work
app = Flask(__name__)

app.secret_key = os.urandom(32)

# allowed input file extensions
ALLOWED_EXTENSIONS = set(['txt', 'fasta', 'fa'])
ALLOWED_PARAM_EXTENSIONS = set(['txt'])

# handler methods for checking file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_param_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_PARAM_EXTENSIONS


'''
This is the default route that is hit when the default URL is entered into the browser.
This handles data upload, logo draw, and parameter updates. Uploaded files are written to a
single temporary file; the same will be true of the parameters. This route returns results in
an HTTP get when the URL is entered and results in a POST when parameters are updated. One every
POST, the method re-renders the output page with the updated logo.
'''
@app.route('/', methods=['GET','POST'])
def index():

    # handle creation of temp files
    if 'uid' in session:
        tempFile = str(session['uid']) + ".fasta"
        tempStyleFile = str(session['uid']) + ".txt"
        logFile = str(session['uid']) + ".log"
        sys.stderr = WarningsLogger(logFile)
        print("Temp file already made")
    else:
        session['uid'] = uuid.uuid4()
        tempFile = str(session['uid'])+".fasta"
        shutil.copy('crp_sites.fasta',tempFile)
        tempStyleFile = str(session['uid']) + ".txt"
        logFile = str(session['uid']) + ".log"
        sys.stderr = WarningsLogger(logFile)
        print("New temp file created")


    #print("SECRET KEY: ",app.secret_key)
    # name of the file that gets passed onto make stylized logo
    # all parameter values are contained in this.
    #style_file = 'parameters_file.txt'
    style_file = tempStyleFile

    # default values of parameters
    default_parameters_text = """
colors : 'Blues'
logo_type : 'counts'
axes_type : 'classic'
font_family : 'sans-serif'
font_weight : 'heavy'
use_tightlayout : True
"""

    # access global variable, which will update if user uploads
    # new file
    #global dataFileName

    # this file name needs to be unique to the session, e.g. time stamp?
    #dataFileName = 'crp_sites.fasta'
    dataFileName = tempFile
    #print(" Beginning: ",dataFileName)

    if 'uid' in session:
        print("Session Indeks: ",session['uid'])
    else:
        session['uid'] = uuid.uuid4()
        print("Session Indeks after set: ",session['uid'])


    # process the post from html
    if request.method == 'POST':

        # if parameter button is hit, get updated values
        if str(request.form.get("parameterButton")) == 'Update logo':
            updatedParametes = request.form['paramsTextArea']
            print("Hitting parameter button ")
            with open(style_file, "w") as text_file:
                text_file.write(updatedParametes)

            print("in parameter update, filename:", dataFileName)

        # elif upload data button is hit, upload new data
        elif str(request.form.get("dataUploadButton")) == 'Upload Data':
            print("Hitting Upload button ")

            # get file name
            f = request.files['file']

            # display flash message if filetype not supported
            if not allowed_file(f.filename) and len(f.filename) is not 0:
                print(f.filename)
                flash(" File type not supported:  " + str(f.filename))
                # flash(" File type not supported ")

            # if button pressed without any uploaded
            elif len(f.filename) is 0:
                flash(" Please select a file to upload ")

            else:
                # secure filename cleans the name of the uploaded file
                f.save(secure_filename(f.filename))
                #dataFileName = f.filename
                #print("In upload, datafileName: ",dataFileName)
                # write the contents of the uploaded file in crp_sites.fasta.
                # write from
                with open(f.filename) as f1:
                    # write to
                    with open(dataFileName, "w") as f2:
                        for line in f1:
                            f2.write(line)

                # elif parameter button is pressed
        elif str(request.form.get("parameterUploadButton")) == 'Upload Parameters':
            print("Hitting parameter upload button ")

            # get file name
            f = request.files['file']

            # if button pressed without any uploaded
            if len(f.filename) is 0:
                flash(" Please select a parameters file to upload ")

            # if not right extension
            elif not allowed_param_file(f.filename) and len(f.filename) is not 0:
                print(f.filename)
                flash(" parameters must have .txt extension ")

            else:
                # secure filename cleans the name of the uploaded file
                f.save(secure_filename(f.filename))

                # the following puts uploaded data in the temp file
                # write from
                with open(f.filename) as f1:
                    # write to
                    with open(style_file, "w") as f2:
                        for line in f1:
                            f2.write(line)


    # show index page values on get
    elif request.method == 'GET':
        # on page load the first time, data file name is set to
        # the following file. This logo is displayed when the user
        # first arrives on the page
        #dataFileName = 'crp_sites.fasta'
        shutil.copy('crp_sites.fasta',tempFile)
        dataFileName = tempFile
        print("I am in get and updated the data file name: ",dataFileName)
        # write the default parameter values to a temporary style file
        # which gets passed onto make_stylized_logo
        with open(style_file, 'w') as f:
            f.write(default_parameters_text)

    # display parameter values in a textarea: 3 steps
    # Note: these steps could be combined into 1 step but
    # separated for clarity
    # 1) read raw text from style file
    with open(style_file, 'r') as p:
        rawParams = p.read()

    # 2) store length of raw params in variable which
    # will be used in html
    paramsLength = len(rawParams)

    # 3) append tab delimited values to list so they look
    # exactly like the raw data in the parameters file
    displayParams = []
    for index in range(paramsLength):
        displayParams.append(rawParams[index].split('    '))


    # display input data in input text area
    # Also in 3 steps (see comments above)

    # 1) read raw text from fasta file
    with open(dataFileName, 'r') as fileVar:
        rawInput = fileVar.readlines()

    # 2) store length of raw data in variable which
    # will be used in html
    inputDataLength = len(rawInput)

    # 3) append tab delimited values to list so they look
    # exactly like the raw data in the parameters file
    displayInput = []
    for x in range(inputDataLength):
        displayInput.append(rawInput[x].split('    '))

    # this clears the plot before re-rendering so old logos
    # aren't drawn on top of each other.
    plt.cla()

    # currently the default mat has the values of the pre-existing file.
    # this will be changed to uploaded mat when I implement the uploading functionality
    Mat = logomaker.load_alignment(dataFileName)

    # draw the logo
    logo = logomaker.make_styled_logo(style_file=style_file, matrix=Mat)
    fig, ax_list = plt.subplots(figsize=[8, 2])
    logo.draw(ax_list)

    # this saves the logo to disk. Although I'm not if we need this.
    plt.savefig('/home/kinneylab/Logomaker_python_anywhere/square_plot.png')

    #save the logo as a stream of bytes which can be passed into
    # html and decoded as an image.
    logoFigFile = BytesIO()
    plt.savefig(logoFigFile, format='png')
    logoFigFile.seek(0)

    # the following contains the actual data passed to the html template
    logoFigData = base64.b64encode(logoFigFile.getvalue())

    # show warnings
    #flash(str(subprocess.check_output(['tail', '-1', logFile])).strip())

    # Show warnings
    with open(logFile) as log:
        flash(log.read())

    cleanWarnings(logFile)

    # render the template with logo data
    return render_template('output.html', result=logoFigData, paramsLength=paramsLength, displayParams=displayParams,displayInput=displayInput, inputDataLength=inputDataLength)


@app.before_first_request
def before_first_request():
    session['uid'] = uuid.uuid4()

    tempFile = str(session['uid']) + ".fasta"
    shutil.copy('crp_sites.fasta', tempFile)

    #session['uid'] = uuid.uuid4()
    #print("First request TIMESTAMP1111: ",datetime.now())
    #print("User agent: ",request.user_agent)
    #print("IP: ",request.environ['REMOTE_ADDR'])
    #print("Headers: ", request.headers)
    #print("Session: ",session)

@app.before_request
def before_request():
    # here we can do something before every
    # request is made e.g:

    #print("First request TIMESTAMP: ",datetime.now())
    #print("User agent: ",request.user_agent)
    #print("IP: ",request.environ['REMOTE_ADDR'])
    #print("Headers: ", request.headers)
    #print("Session: ",session)
    #print("Session: ",session['uid'])
    # this doesn't always get set :(
    #print("Cookies: ",request.cookies.get('session'))
    pass

def cleanWarnings(logFile):
    # erase warnings file before request
    if len(logFile)!=0 :
        open(logFile,'w').close()

class WarningsLogger(object):

    def __init__(self, logFileName):
        self.terminal = sys.stdout
        #self.log = open("warnings.log", "a")
        self.log = open(logFileName, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        # why flush, see following:
        # https://stackoverflow.com/questions/24011117/logging-realtime-stdout-to-a-file-in-python
        self.terminal.flush()
        self.log.flush()

'''
if __name__ == "__main__":
    app.run()
'''
