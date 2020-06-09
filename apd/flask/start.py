import os
from flask import Flask, request, render_template, url_for
from werkzeug.utils import secure_filename
from apd import apd2pdf

dir_path = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = os.path.join(dir_path, 'static')


@app.route('/')
def upload_file():
    return render_template('upload.html')


@app.route('/getpdf', methods=['GET', 'POST'])
def getpdf():
    if request.method == 'POST':
        f = request.files['file']
        secure_name = secure_filename(f.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        print(file_path)
        f.save(file_path)
        outfile = apd2pdf.run(file_path)
        fout = f'../static/{os.path.basename(outfile)}'
        return render_template('uploader.html', file_path=fout)


if __name__ == '__main__':
    app.run(host='192.168.1.106')
