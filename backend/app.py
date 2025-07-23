from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import cgi
import os
from io import BytesIO
from email_draft import DraftCreator

UPLOAD_DIR = 'uploads'
LOG = []

def log(msg):
    LOG.append(msg)
    print(msg)

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if self.path == '/log':
            self._set_headers()
            self.wfile.write(json.dumps(LOG).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'not found'}).encode())

    def do_POST(self):
        if self.path == '/upload':
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype != 'multipart/form-data':
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'invalid'}).encode())
                return
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'}, keep_blank_values=True)
            file_field = form['file']
            if not file_field.filename:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'no file'}).encode())
                return
            if not os.path.exists(UPLOAD_DIR):
                os.makedirs(UPLOAD_DIR)
            path = os.path.join(UPLOAD_DIR, os.path.basename(file_field.filename))
            with open(path, 'wb') as f:
                f.write(file_field.file.read())
            log(f'Uploaded {path}')
            self._set_headers()
            self.wfile.write(json.dumps({'path': path}).encode())
        elif self.path == '/create':
            length = int(self.headers.get('content-length', 0))
            body = json.loads(self.rfile.read(length))
            csv_path = body.get('csv')
            imap = body.get('imap')
            smtp = body.get('smtp')
            user = body.get('user')
            password = body.get('password')
            if not all([csv_path, imap, user, password]):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'missing params'}).encode())
                return
            creator = DraftCreator(imap, user, password)
            try:
                count = creator.create_drafts(csv_path)
                log(f'Created {count} drafts from {csv_path}')
                self._set_headers()
                self.wfile.write(json.dumps({'created': count}).encode())
            except Exception as e:
                log(f'Error: {e}')
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        elif self.path == '/send':
            length = int(self.headers.get('content-length', 0))
            body = json.loads(self.rfile.read(length))
            csv_path = body.get('csv')
            smtp = body.get('smtp')
            user = body.get('user')
            password = body.get('password')
            if not all([csv_path, smtp, user, password]):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'missing params'}).encode())
                return
            creator = DraftCreator('', user, password)
            try:
                count = creator.send_emails(csv_path, smtp)
                log(f'Sent {count} emails from {csv_path}')
                self._set_headers()
                self.wfile.write(json.dumps({'sent': count}).encode())
            except Exception as e:
                log(f'Error: {e}')
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'not found'}).encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), Handler)
    print('Listening on port 8000')
    server.serve_forever()
