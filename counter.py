import time
import re
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import rethinkdb as r

DB = 'phd'
TABLE = 'words'
PATH = '/Users/helge/projects/phdthesis'

files = [
    'concept.tex',
    'conclusion.tex',
    'implementation.tex',
    'introduction.tex',
    'outlook.tex',
    'requirements.tex',
    'state.tex',
    'validation.tex',
    ]
reg = re.compile(r'(^\s+[0-9]+\+[0-9]+\+[0-9]+)(.*)(\s[a-z]+\.tex$)')
db = r.db(DB).table(TABLE)

class Handler(PatternMatchingEventHandler):
    patterns = ['*.tex']
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
    def on_modified(self, event):
        counts = get_wordcounts()
        if db.count().run(conn) > 0:
            previous = db.nth(-1).run(conn)
            previous.pop('id')
            previous.pop('date')
            if counts != previous:
                counts.update({"date": r.now()})
                db.insert(counts).run(conn)
        else:
            counts.update({"date": r.now()})
            db.insert(counts).run(conn)

def get_wordcount():
    command = ['texcount', '-utf8', '-brief', '-total']
    command.extend(files)
    count = subprocess.check_output(command).split(b'+')[0]
    return int(count)

def get_wordcounts():
    command = ['texcount', '-utf8', '-total']
    command.extend(files)
    lines = subprocess.check_output(command).decode('utf8').split('\n')
    counts = {}
    for l in lines:
        m = reg.match(l)
        if m:
            count = int(m.groups()[0].strip().split('+')[0])
            tex = m.groups()[2].strip().split('.')[0]
            counts.update({tex: count})
        if l.startswith('Words in text'):
            counts.update({'total': int(l.split()[-1])})
    return counts

if __name__ == '__main__':
    conn = r.connect('localhost', 28015)
    dbs = r.db_list().run(conn)
    if DB not in dbs:
        r.db_create(DB).run(conn)
    tables = r.db(DB).table_list().run(conn)
    if TABLE not in tables:
        r.db(DB).table_create(TABLE).run(conn)
    observer = Observer()
    observer.schedule(Handler(conn), path=PATH)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
