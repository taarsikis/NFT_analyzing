from datetime import datetime

import gspread
import pygsheets
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from httplib2 import Http
import pandas as pd

json_path = 'google_key.json'
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
client = gspread.authorize(creds)

folderId = '1yRCt8awRYCksWLlYVjBUd77vGPkiZJI6'

def get_list_files_from_folder():
    drive = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    files_in_folder = drive.files().list(q=f"mimeType='application/vnd.google-apps.spreadsheet' and trashed = false and parents in '{folderId}'",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()

    return [x['name'] for x in files_in_folder['files']]

def create_spreadsheet(name):
    workbook = client.create(name, folder_id=folderId)


def overwrite_file_with_dataframe(file_name, df):
    gc = pygsheets.authorize(service_file='google_key.json')

    sh = gc.open(file_name)

    #select the first sheet
    wks = sh[0]

    #update the first sheet with df, starting at cell B2.
    wks.set_dataframe(df,(1,1),fit=False)

def read_spreadsheet_as_df(name) -> pd.DataFrame:
    sh = client.open(name)

    ws = sh.get_worksheet(0)
    df = pd.DataFrame(ws.get_values())

    header = df.iloc[0]
    df = df[1:]
    df.columns = header

    return df

def delete_duplicates_from_file(name):
    df = read_spreadsheet_as_df(name).drop_duplicates()

    overwrite_file_with_dataframe(name,df)

def get_last_timestamp_in(name):
    df = read_spreadsheet_as_df(name)
    # print(df.sort_values(by = 'Date'))
    # max_date = df['Date'].max()
    # return int(datetime.strptime(max_date, "%Y-%m-%d %H:%M:%S").timestamp())
    df = df[df['Date'].apply(lambda x : len(x.split('.'))) != 2]
    return df['Date'].apply(lambda x : datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp()).max()

if __name__ == '__main__':
    print(get_list_files_from_folder())
    print(get_last_timestamp_in('halo-official'))
    # print(read_spreadsheet_as_df('slowturtles'))
    # delete_duplicates_from_file('slowturtles')
