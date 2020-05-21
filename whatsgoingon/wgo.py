from whatsgoingon import whatsgoingon_utils as wgo_util
from whatsgoingon import serve
import sqlite3
import json
import os
from datetime import datetime
from shutil import copyfile
import pickle

class logger():
    def __init__(self, project, nickname=None, notes=' ', config='~/.whatsgoingon.config'):
        if nickname is None:
            nickname = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        
        # load config or create new one if doesn't exist
        config = os.path.expanduser(config)
        if not os.path.exists(config):
            wgo_util.initial_setup(config)
        self.config = json.load(open(config, 'r'))

        # make project dir if doesn't exist
        self.project_path = os.path.expanduser(f'{self.config["main_dir"]}/{project}/')
        if not os.path.isdir(self.project_path):
            os.makedirs(self.project_path)

        # load project database
        self.database = f'{self.project_path}/runs.db'
        if not os.path.exists(self.database):
            wgo_util.create_table(self.database)

        # make nickname dir if doesn't exist
        self.nickname_path = os.path.expanduser(
            f'{self.config["main_dir"]}/{project}/{nickname}/'
        )
        self.nickname = nickname
        if not os.path.isdir(self.nickname_path):
            os.makedirs(self.nickname_path)

        self.notes = notes
        self.files = []


    '''
    Create new row and add nickname (Primary Key), notes, starttime
    '''
    def start(self):
        starttime = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        cmd = f"""
        INSERT INTO runs (nickname, start, notes) VALUES ('{self.nickname}', '{starttime}', '{self.notes}')
        """
        self._database_command(self.database, cmd)

    def end(self):
        endtime = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        cmd = f"""
        UPDATE runs SET end = '{endtime}' WHERE nickname = '{self.nickname}'
        """
        self._database_command(self.database, cmd)

    def add_notes(self, notetext):
        self.notes += "\n" + notetext
        cmd = f"""
        UPDATE runs SET notes = '{self.notes}' WHERE nickname = '{self.nickname}'
        """
        self._database_command(self.database, cmd)

    def status(self, statustext_):
        statustext = str(statustext_)
        cmd = f"""
        UPDATE runs SET status = '{statustext}' WHERE nickname = '{self.nickname}'
        """
        self._database_command(self.database, cmd)


    def file_softlink(self, filepath):
        self.files.append(filepath)
        self._update_files()

    def file_hardcopy(self, filepath):
        file_basename = os.path.basename(filepath)
        new_file_path = f'{self.nickname_path}/{file_basename}'
        copyfile(filepath, new_file_path)
        self.files.append(new_file_path)
        self._update_files()

    def file_hardcopy_pickle(self, dataobject, filename):
        new_file_path = f'{self.nickname_path}/{filename}'
        with open(new_file_path, 'wb') as pf:
            pickle.dump(dataobject, pf)
        self.files.append(new_file_path)
        self._update_files()

    def _update_files(self):
        files_str = str(self.files).replace("'", '"')
        cmd = f"""
        UPDATE runs SET files = '{files_str}' WHERE nickname = '{self.nickname}'
        """
        self._database_command(self.database, cmd)
        self._update_filenames()

    def _update_filenames(self):
        filenames = [os.path.basename(x) for x in self.files]
        filenames_str = str(filenames).replace("'", '"')
        cmd = f"""
        UPDATE runs SET filenames = '{filenames_str}' WHERE nickname = '{self.nickname}'
        """
        self._database_command(self.database, cmd)

        
    def _database_command(self, database, cmd):
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute(cmd)
        conn.commit()
        conn.close()
        
    def _to_pandas(self):
        import pandas as pd
        conn = sqlite3.connect(self.database)
        df = pd.read_sql_query("SELECT * FROM runs", conn)
        return df

def dashboard():
    serve.run()
