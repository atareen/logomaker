#!/usr/bin/python2.7
from flask import Flask, render_template, request,session, flash
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os
import sys
sys.path.append('../')
import Logomaker_python_anywhere_CSV as logomaker
import uuid
import shutil
import sys
from numpydoc.docscrape import NumpyDocString
from make_logo import make_logo



# this is the name of the flask app. This conventional in the flask frame-work
app = Flask(__name__)

# this key decrypts the cookie on the client's browser
app.secret_key = os.urandom(32)

# allowed input file extensions
ALLOWED_EXTENSIONS = set(['txt', 'fasta', 'fa','input'])
ALLOWED_PARAM_EXTENSIONS = set(['txt'])

# handler methods for checking file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_param_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_PARAM_EXTENSIONS

# global variable gotten from radio button. Run this by Justin
# update: tis will be replaced by the functionality via metadata

'''
This is the default route that is hit when the default URL is entered into the browser.
This handles data upload, logo draw, and parameter updates. Uploaded files are written to a
single temporary file; the same will be true of the parameters. This route returns results in
an HTTP get when the URL is entered and results in a POST when parameters are updated. One every
POST, the method re-renders the output page with the updated logo.
'''
@app.route('/', methods=['GET','POST'])
def index():

    # radio button state and file format
    radioState = ''
    fileFormat = ''

    # handle creation of temp files
    if 'uid' in session:
        print("Temp file already created")
        tempFile = str(session['uid']) + ".input"
        tempStyleFile = str(session['uid']) + ".txt"
        logFile = str(session['uid']) + ".log"
        metaDataFile = str(session['uid']) + ".meta"
        sys.stderr = WarningsLogger(logFile)
    else:
        session['uid'] = uuid.uuid4()
        tempFile = str(session['uid'])+".input"
        shutil.copy('crp_sites.fasta',tempFile)
        tempStyleFile = str(session['uid']) + ".txt"
        metaDataFile = str(session['uid']) + ".meta"
        logFile = str(session['uid']) + ".log"
        print("New temp file created")
        sys.stderr = WarningsLogger(logFile)


    #if my_file.is_file():
    # read meta data file if not empty
    #print("Metadata File Size: ",os.path.getsize(metaDataFile))

    # give the data file the temp name
    dataFileName = tempFile

    # name of the style file that gets passed onto make stylized logo
    # all parameter values are contained in this.
    #style_file = 'parameters_file.txt'
    style_file = tempStyleFile

    # default values of parameters
    default_parameters_text = """
colors : 'Blues'
logo_type : 'probability'
axes_type : 'classic'
font_family : 'Dejavu Sans'
font_weight : 'heavy'
use_tightlayout : True
"""

    # this value will received from radio button choice
    #fileFormat = 'fasta'
    # process the post from html
    if request.method == 'POST':

        # if update parameter button is hit, get updated values
        if str(request.form.get("parameterButton")) == 'Update logo':

            print("Request: ",request.data)

            updatedParametes = request.form['paramsTextArea']
            print("Hitting parameter button ")
            with open(style_file, "w") as text_file:
                text_file.write(updatedParametes)

        # elif upload data button is hit, upload new data
        # but put new data in temp file
        elif str(request.form.get("dataUploadButton")) == 'Upload Data':
            print("Hitting Upload button ")

            # read radio button value
            if request.form.getlist('fileformat'):
                fileFormat = str(request.form['fileformat'])

                # write state to file
                with open(metaDataFile,'w') as md:
                    md.write(fileFormat)
                #print(fileFormat)


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

            elif len(fileFormat) is 0:
                flash("Please choose a radio button")

            else:
                # secure filename cleans the name of the uploaded file
                f.save(secure_filename(f.filename))

                # the following puts uploaded data in the temp file
                # write from
                with open(f.filename) as f1:
                    # write to
                    with open(dataFileName, "w") as f2:
                        for line in f1:
                            f2.write(line)

        # elif parameter upload button is pressed
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
        print("In get ")
        # on page load the first time, data file name is set to
        # the following file. This logo is displayed when the user
        # first arrives on the page

        # the following resets things
        # reset if get
        shutil.copy('crp_sites.fasta', tempFile)

        radioState=''
        if len(metaDataFile)!=0 :
            open(metaDataFile,'w').close()

        dataFileName = tempFile

        # write the default parameter values to a temporary style file
        # which gets passed onto make_stylized_logo
        with open(style_file, 'w') as f:
            f.write(default_parameters_text)


    # read state from the metadata file
    try:
        with open(metaDataFile) as file:
            radioState = file.read()
    except IOError as e:
        print "Unable to open file"
        # need to do more here in case can't open file


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

    #if str(fileFormat)=='fasta':
    if radioState == 'fasta':
        print("Calling logomaker from fasta", dataFileName)
        logomaker.make_styled_logo(style_file=style_file,fasta_file=dataFileName)
    #elif str(fileFormat) == 'meme':
    elif radioState == 'meme':
        print("Calling logomaker from meme",dataFileName)
        logomaker.make_styled_logo(style_file=style_file,meme_file=dataFileName)
    #elif str(fileFormat) == 'csv':
    elif radioState == 'csv':
        logomaker.make_styled_logo(style_file=style_file, csv_file=dataFileName)
    else:
        print("Calling logomaker from default", dataFileName, " radiostate: ",radioState)
        logomaker.make_styled_logo(style_file=style_file, fasta_file=dataFileName)


    #save the logo as a stream of bytes which can be passed into
    logoFigFile = BytesIO()
    plt.savefig(logoFigFile, format='png')
    logoFigFile.seek(0)

    # the following contains the actual data passed to the html template
    logoFigData = base64.b64encode(logoFigFile.getvalue())

    # Show warnings
    with open(logFile) as log:
        flash(log.read())
    cleanWarnings(logFile)

    # populate documentation dictionary
    # this is currently sub-optimal; should only be run once
    doc = NumpyDocString(make_logo.__doc__)
    doc_dict = {}
    valueString = ''
    for i in range(len(doc.get('Extended Summary'))):

        if len(doc.get('Extended Summary')[i]) != 0:
            valueString += doc.get('Extended Summary')[i]
        else:
            key = valueString.partition(' ')[0]
            value = " ".join(valueString.split())
            # print key ,":",value
            doc_dict[key] = value
            valueString = ''
    # the following to avoid overflows
    plt.close('All')
    # render the template with logo data
    return render_template('output.html', result=logoFigData, paramsLength=paramsLength, displayParams=displayParams,
                           displayInput=displayInput, inputDataLength=inputDataLength,doc_dict=doc_dict,radioState=radioState)


@app.before_first_request
def before_first_request():
    '''
    # attempt to create unique session id
    # and make temp file
    # if it's not made here, for some weird server issue, make again in index
    session['uid'] = uuid.uuid4()
    tempFile = str(session['uid']) + ".input"
    shutil.copy('crp_sites.fasta', tempFile)
    '''
    pass


@app.before_request
def before_request():
    # here we can do something before every
    # request is made
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

if __name__ == "__main__":
    app.run(debug=True)
