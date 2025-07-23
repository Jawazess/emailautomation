import os
import sys
from flask import Flask, request, jsonify

# Ensure backend module is importable
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from email_draft import DraftCreator
from log_store import log, get_logs

app = Flask(__name__)
UPLOAD_DIR = '/tmp/uploads'

@app.post('/upload')
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'no file'}), 400
    file = request.files['file']
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(path)
    log(f'Uploaded {path}')
    return jsonify({'path': path})

@app.post('/create')
def create():
    data = request.get_json() or {}
    csv_path = data.get('csv')
    imap = data.get('imap')
    user = data.get('user')
    password = data.get('password')
    if not all([csv_path, imap, user, password]):
        return jsonify({'error': 'missing params'}), 400
    creator = DraftCreator(imap, user, password)
    try:
        count = creator.create_drafts(csv_path)
        log(f'Created {count} drafts from {csv_path}')
        return jsonify({'created': count})
    except Exception as e:
        log(f'Error: {e}')
        return jsonify({'error': str(e)}), 500

@app.post('/send')
def send():
    data = request.get_json() or {}
    csv_path = data.get('csv')
    smtp = data.get('smtp')
    user = data.get('user')
    password = data.get('password')
    if not all([csv_path, smtp, user, password]):
        return jsonify({'error': 'missing params'}), 400
    creator = DraftCreator('', user, password)
    try:
        count = creator.send_emails(csv_path, smtp)
        log(f'Sent {count} emails from {csv_path}')
        return jsonify({'sent': count})
    except Exception as e:
        log(f'Error: {e}')
        return jsonify({'error': str(e)}), 500

@app.get('/log')
def get_log():
    return jsonify(get_logs())

# For local development
if __name__ == '__main__':
    app.run(port=8000)
