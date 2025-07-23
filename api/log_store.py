import os
LOG_PATH = '/tmp/emailautomation.log'

def log(message: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'a') as f:
        f.write(message + '\n')


def get_logs():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, 'r') as f:
        return [line.strip() for line in f.readlines()]
