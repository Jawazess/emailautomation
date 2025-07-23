import csv
import os
import time
import imaplib
import mimetypes
from email.message import EmailMessage
import base64
import json
from urllib import request as urlrequest

class DraftCreator:
    """Utility to read a CSV file of recipients and create Gmail drafts."""

    def __init__(self, imap_server: str, username: str, password: str):
        self.imap_server = imap_server
        self.username = username
        self.password = password

    def _connect(self):
        imap = imaplib.IMAP4_SSL(self.imap_server)
        imap.login(self.username, self.password)
        return imap

    def _build_message(self, row: dict) -> EmailMessage:
        msg = EmailMessage()
        msg['To'] = row['email']
        msg['From'] = self.username
        msg['Subject'] = row.get('subject', '')
        msg.set_content(row.get('message', ''))
        attachments = row.get('attachments', '')
        for path in filter(None, [p.strip() for p in attachments.split(';')]):
            if not os.path.exists(path):
                continue
            ctype, encoding = mimetypes.guess_type(path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            with open(path, 'rb') as f:
                msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(path))
        return msg

    def create_drafts(self, csv_path: str) -> int:
        """Create drafts from a csv file. Returns number of drafts created."""
        count = 0
        with self._connect() as imap, open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                msg = self._build_message(row)
                imap.append('Drafts', '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
                count += 1
        return count

    def send_emails(self, csv_path: str, smtp_server: str, smtp_port: int = 587) -> int:
        """Send emails from a csv file using SMTP. Returns number of emails sent."""
        import smtplib

        count = 0
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(self.username, self.password)
            with open(csv_path, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    msg = self._build_message(row)
                    smtp.send_message(msg)
                    count += 1
        return count

    # --- Gmail API helpers using OAuth token ---
    def _gmail_request(self, url: str, token: str, data: dict) -> dict:
        req = urlrequest.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            data=json.dumps(data).encode(),
        )
        with urlrequest.urlopen(req) as resp:
            return json.loads(resp.read())

    def create_drafts_api(self, csv_path: str, token: str) -> int:
        count = 0
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                msg = self._build_message(row)
                b64 = base64.urlsafe_b64encode(msg.as_bytes()).decode()
                data = {"message": {"raw": b64}}
                self._gmail_request(
                    "https://gmail.googleapis.com/gmail/v1/users/me/drafts",
                    token,
                    data,
                )
                count += 1
        return count

    def send_emails_api(self, csv_path: str, token: str) -> int:
        count = 0
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                msg = self._build_message(row)
                b64 = base64.urlsafe_b64encode(msg.as_bytes()).decode()
                data = {"raw": b64}
                self._gmail_request(
                    "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
                    token,
                    data,
                )
                count += 1
        return count
