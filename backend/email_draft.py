import csv
import os
import time
import imaplib
import mimetypes
from email.message import EmailMessage

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
