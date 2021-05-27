import os
import re
import requests

BASE_URL = 'http://localhost:5000/api/v1'


def get_filename(content_disposition):
    if not content_disposition:
        return None
    fname = re.findall('filename=(.+)', content_disposition)
    if len(fname) == 0:
        return None
    return fname[0]


def make_pdf(content, output=None):
    path_to_save = "../downloads"
    if output:
        path_to_save = output
    filename = get_filename(content.headers['Content-Disposition'])
    with open(os.path.join(f"{path_to_save}", filename), "wb") as pdf:
        for chunk in content.iter_content(1024):
            pdf.write(chunk)


class Browser(object):

    def __init__(self):
        self.response = None
        self.headers = self.get_headers()
        self.session = requests.Session()

    def get_headers(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          " AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.88 Safari/537.36"
        }
        return self.headers

    def send_request(self, method, url, **kwargs):
        response = self.session.request(method, url, **kwargs)
        if response.status_code == 200:
            return response
        return None


class Html2PdfAPI(Browser):

    def __init__(self):
        super().__init__()

    def generate_pdf(self, filepath):
        files = {'file': open(filepath, 'rb')}
        self.response = self.send_request('POST', f"{BASE_URL}/upload", files=files, headers=self.headers)
        if self.response:
            return self.response
        return False


if __name__ == '__main__':
    api = Html2PdfAPI()
    get_pdf = api.generate_pdf('../file.html')
    if get_pdf.status_code == 200:
        make_pdf(get_pdf, output='')
