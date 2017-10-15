from flask import Flask, render_template, make_response, send_file
import StringIO
import matrix

import matplotlib.pyplot as plt
import logomaker

app = Flask(__name__)

mat = logomaker.load_mat('crp_sites.fasta', 'fasta',mat_type='frequency')

fig = plt.figure(figsize=[8,6])
ax = fig.add_subplot(3,1,1)

logomaker.Logo(mat=mat,mat_type='freq_mat',logo_type='freq_logo').draw()

#print(mat.head().to_html())
print(mat.head())

#for index, row in mat.head().iterrows():
#    print row

#plt.show()

'''
@app.route('/')
def index():
    return render_template("index.html",mat=mat)
'''

@app.route("/")
def index():
    #return render_template("index.html",mat=mat)
    mat_html = matrix.validate_freq_mat(mat)
    return render_template('index.html', tables=[mat_html.head().to_html(classes='mat')],mat=mat)

@app.route('/fig')
def fig():
    fig = plt.figure(figsize=[8, 6])
    ax = fig.add_subplot(3, 1, 1)
    logomaker.Logo(mat=mat, mat_type='freq_mat', logo_type='freq_logo').draw()

    img = StringIO.StringIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='image/png')


@app.route("/tables")
def show_tables():
    #data = mat
    mat_html = matrix.validate_freq_mat(mat)
    #data.set_index(['Name'], inplace=True)
    return render_template('view.html',tables=[mat_html.head().to_html(classes='mat')])

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
