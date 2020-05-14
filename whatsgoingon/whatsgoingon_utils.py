import json
import pickle
import os
import sqlite3

def initial_setup(CONFIG_FILE='~/.whatsgoingon.config'):
    CONFIG_FILE = os.path.expanduser(CONFIG_FILE)
    # load config
    if not os.path.exists(CONFIG_FILE):
        config = {}
        config['main_dir'] = os.path.expanduser('~/.whatsgoingon/')
        json.dump(config, open(CONFIG_FILE, 'w'))
    else:
        config = json.load(open(CONFIG_FILE, 'r'))
        if 'main_dir' not in config:
            config['main_dir'] = os.path.expanduser('~/.whatsgoingon/')

    # ensure main dir exists
    main_dir = config['main_dir']
    if not os.path.isdir(main_dir):
        os.makedirs(main_dir)

def create_table(database):
    conn = sqlite3.connect(database)
    cmd = '''
    CREATE TABLE runs (nickname text PRIMARY KEY, notes text, status text, start text, end text, files text, filenames text)
    '''
    c = conn.cursor()
    c.execute(cmd)
    conn.commit()
    conn.close()
