import gspread
from oauth2client.service_account import ServiceAccountCredentials


json_path = 'google_key.json'

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
client = gspread.authorize(creds)

folderId = '1yRCt8awRYCksWLlYVjBUd77vGPkiZJI6'
#
name = 'NFT_index'
#
def delete_spreadheet(name):
    sh = client.open(name)

    client.del_spreadsheet(sh.id)

    print('deleted' , "id - " ,sh.id, '. Name - ', name)


if __name__ == '__main__':
    delete_spreadheet(name)
