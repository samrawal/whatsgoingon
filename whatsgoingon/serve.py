import json
import os
import pandas as pd
import sqlite3
from glob import glob
from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route("/", methods=['GET'])
def project_select():
    config_path = '~/.whatsgoingon.config'
    config = json.load(open(os.path.expanduser(config_path), 'r'))

    wgo_path = config['main_dir']
    print(wgo_path)
    projects = glob(f'{wgo_path}/*/')
    print(projects)


    to_html = '<h1>Choose a Project:</h1>'

    for p in projects:
        pname = p.split('/')[-2]
        to_html += f'<a href="projectviewer?projectname={p}">{pname}</a><br>'
    print(to_html)
    return to_html

    
@app.route("/projectviewer", methods=['GET'])
def project_viewer():
    projectname = request.args.get('projectname').strip()
    database = projectname + '/runs.db'
    to_html = '''
    <html><head> <meta http-equiv="refresh" content="30"></head>
    '''
    to_html += db2html(database)
    to_html += "</html>"
    return to_html

def db2html(db_path):
    conn = sqlite3.connect(db_path)
    pd.set_option('display.max_colwidth', -1)
    html = pd.read_sql_query("SELECT * FROM runs", conn).to_html(buf=None)
    html = html.replace(r'\n', r'<br>')
    return html
    
def run():
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    run()

