from os import environ as env, getcwd, path, makedirs
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, send_file, render_template
from api.pychromepdf import ChromePDF

BASE_DIR = getcwd()
# CHROME_PATH = "/app/.apt/usr/bin/google-chrome-stable"
CHROME_PATH = env.get('CHROME_PATH', '{}/bin/google-chrome-stable'.format(BASE_DIR))
UPLOAD_FOLDER = 'media/uploads/'

if not path.exists(path.join(BASE_DIR, UPLOAD_FOLDER)):
    makedirs(path.join(BASE_DIR, UPLOAD_FOLDER))
    makedirs(path.join(BASE_DIR, 'pdf'))

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def generate_pdf(filepath):
    cpdf = ChromePDF(CHROME_PATH, sandbox=False)
    file_name = path.basename(filepath).split('.')[0]
    pdf_name = f'{BASE_DIR}/pdf/{file_name}.pdf'
    with open(pdf_name, 'wb') as output_file:
        if cpdf.page_to_pdf(f'file://{BASE_DIR}/{filepath}', output_file):
            return pdf_name

    return False


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            saved_file = path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(saved_file)
            print("saved file successfully")
            pdf = generate_pdf(saved_file)
            if pdf:
                print(pdf)
                filename = pdf
            else:
                return {
                    "result": False,
                    "object": [],
                    "message": "Erro ao gerar pdf."
                }
            return redirect('/downloadfile/' + filename)

    return render_template('upload.html')


@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    return render_template('download.html', value=filename)


@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
