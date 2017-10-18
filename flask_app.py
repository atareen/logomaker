from flask import Flask, render_template, redirect, send_file, request,url_for,flash
import flask

from werkzeug.utils import secure_filename
import StringIO
import matrix
import pandas
import re


import matplotlib.pyplot as plt
import logomaker

app = Flask(__name__)
# figure out what reasonable value for secret key should be
app.secret_key = 'some_secret'

matStatic = logomaker.load_mat('crp_sites.fasta', 'fasta',mat_type='frequency')
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

'''
@app.route('/')
def index():
    return render_template("index.html",mat=mat)
'''

allowed_file = set(['txt', 'fasta'])

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
            message =str(uploadFile.filename)+"\n"
            flash(message)

        print(files[1])

        # parse parameters file
        # parseParams returns a params dict
        params_dict = parseParams(files[1].filename)
        #convert params dict to pandas dataframe for displaying
        params = pandas.DataFrame(params_dict, index=[0])
        params_html = params.head().to_html()
        #print(params.head())


        with open(files[0].filename, 'r') as f:
            #rawInput = [line.split("\t") for line in f]
            rawInput = f.readlines()

        displayInput = []
        inputDataLength = len(rawInput)

        for x in range(inputDataLength):
            displayInput.append(rawInput[x].split(" "))
            #displayInput.append(rawInput[x])

        print(displayInput)

        # print("f: ",f)
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
            message = 'Successfully Upload file: '+str(files[0].filename)
            flash(message)

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
                                   inputDataLength=inputDataLength,displayInput=displayInput)

'''
<link rel=stylesheet type=text/css href="{{ url_for('static', filename='style.css') }}">
  <h2>Input Params</h2>
  {% for params in paramsTable %}
    {{ params|safe }}
  {% endfor %}
'''

@app.context_processor
def displayUploadStatus(displayMessage=''):
    return dict(statusMessage=displayMessage)


@app.route("/")
def index():
    #return render_template("index.html",mat=mat)
    #mat_html = matrix.validate_freq_mat(mat)
    mat_html = matrix.validate_freq_mat(logomaker.load_mat('crp_sites.fasta', 'fasta', mat_type='frequency'))
    #return render_template('index.html', tables=[mat_html.head().to_html(classes='mat')],mat=mat)
    return render_template('index.html', tables=[mat_html.head().to_html(classes='mat')], mat=logomaker.load_mat('crp_sites.fasta', 'fasta',mat_type='frequency'))


'''
<!--
<img src="{{ url_for('fig') }}">

<p>{{ url_for('fig') }}</p>
-->
'''

@app.route('/fig')
def fig():
    fig = plt.figure(figsize=[8, 6])
    ax = fig.add_subplot(3, 1, 1)
    logomaker.Logo(mat=matStatic, mat_type='freq_mat', logo_type='freq_logo').draw()

    img = StringIO.StringIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='image/png')


# global variable fix to unicode/panda conversion from python to template
uploadMatGlobal = pandas.DataFrame()
uploadedFileName = ''



# upload file at index.html and move to upload.html
# this method draws without the params file
@app.route('/', methods=['GET', 'POST'])
def uploaded_file():
    # surround with try catch if post fails, handle exception
    if request.method == 'POST':
    #if request.method == 'POST' and len(str(request.files))>1:
        f = request.files['file']
        # secure filename cleans the name of the uploaded file
        f.save(secure_filename(f.filename))

        #print("f: ",f)
        # surround this with try catch also if the file is of the wrong format or bad data etc.
        uploadMat = logomaker.load_mat(f.filename, 'fasta', mat_type='freq_mat')
        uploaded_mat_html = matrix.validate_freq_mat(uploadMat)

        global uploadMatGlobal
        uploadMatGlobal = uploadMat

        global uploadedFileName
        uploadedFileName = f.filename

        # the mat variable in here gets passed onto returned template, e.g. upload.html in this instance
        return render_template('upload.html',tables=[uploaded_mat_html.head().to_html(classes='mat')],matPassedToUpload=uploadMat,matType='freq_mat',logoType='weight_logo')


# display the uploaded figure at upload.html after file has been uploaded
@app.route('/uploadedFig/<matType>/<logoType>/<argColorScheme>')
def uploadedFig(matType,logoType,argColorScheme):
    fig = plt.figure(figsize=[8, 6])
    ax = fig.add_subplot(3, 1, 1)
    #logomaker.Logo(mat=uploadMatGlobal,mat_type='freq_mat',logo_type='info_logo').draw()
    logomaker.Logo(mat=uploadMatGlobal, mat_type=matType, logo_type=logoType,color_scheme=str(argColorScheme)).draw()

    img = StringIO.StringIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='image/png')

# press button on upload.html to update logo type
@app.route('/updateLogo', methods=['GET', 'POST'])
def updateLogo():
    if request.method == 'POST':
        uploadMat = logomaker.load_mat(uploadedFileName, 'fasta', mat_type='freq_mat')
        uploaded_mat_html = matrix.validate_freq_mat(uploadMat)
        #return render_template('upload.html', tables=[uploaded_mat_html.head().to_html(classes='mat')],matPassedToUpload=uploadMat, matType='freq_mat', logoType='info_logo')
        return render_template('multiUpload.html', tables=[uploaded_mat_html.head().to_html(classes='mat')],matPassedToUpload=uploadMat, matType='freq_mat', logoType='info_logo',colorScheme='classic')


# press button on upload.html to update logo type
@app.route('/editParam', methods=['GET', 'POST'])
def editParam():
    if request.method == 'POST':
        return "Edit param under dev"

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

    #param_df = pandas.DataFrame(params, index=[0])
    return params
    #return param_df


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

if __name__ == "__main__":
    #other option
    #app.run(port=8080, debug=True)
    app.run()
