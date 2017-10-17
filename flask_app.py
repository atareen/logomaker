from flask import Flask, render_template, make_response, send_file, request
import flask

from werkzeug.utils import secure_filename
import StringIO
import matrix
import sys
import pandas


import matplotlib.pyplot as plt
import logomaker

app = Flask(__name__)


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

@app.route('/foo', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('uploadedFile[]')
        for uploadedFile in files:
            upload(uploadedFile.filename)
            uploadedFile.save(secure_filename(uploadedFile.filename))
        return 'It worked'

def upload(filename):
    filename = 'https://localhost/' + filename


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


@app.context_processor
def example():
    return dict(myexample="This is an example")

# global variable fix to unicode/panda conversion from python to template
uploadMatGlobal = pandas.DataFrame()
uploadedFileName = ''



# upload file at index.html and move to upload.html
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


@app.route('/uploadedFig/<matType>/<logoType>')
def uploadedFig(matType,logoType):
    fig = plt.figure(figsize=[8, 6])
    ax = fig.add_subplot(3, 1, 1)
    #logomaker.Logo(mat=uploadMatGlobal,mat_type='freq_mat',logo_type='info_logo').draw()
    logomaker.Logo(mat=uploadMatGlobal, mat_type=matType, logo_type=logoType).draw()

    img = StringIO.StringIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='image/png')

@app.route('/updateLogo', methods=['GET', 'POST'])
def foo():
    if request.method == 'POST':
        uploadMat = logomaker.load_mat(uploadedFileName, 'fasta', mat_type='freq_mat')
        uploaded_mat_html = matrix.validate_freq_mat(uploadMat)
        return render_template('upload.html', tables=[uploaded_mat_html.head().to_html(classes='mat')],matPassedToUpload=uploadMat, matType='freq_mat', logoType='info_logo')



'''
@app.route("/tables")
def show_tables():
    #data = mat
    mat_html = matrix.validate_freq_mat(mat)
    #data.set_index(['Name'], inplace=True)
    return render_template('view.html',tables=[mat_html.head().to_html(classes='mat')])
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

if __name__ == "__main__":
    app.run()
