#import site
#site.addsitedir("C:/Users/jobo/Documents/maya/2022/venvs/cg3/Lib/site-packages")

import gspread
from oauth2client.service_account import ServiceAccountCredentials


auth_json = "C:/Users/jobo/Documents/maya/2022/gspread_key.json"
sheet_name = "joboproject"

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(auth_json, scope)
client = gspread.authorize(creds)

sheet = client.open(sheet_name).sheet1

result = sheet.get_all_records()
print(result)


#### ALTERNATIVE:
import json
from gspread import Client
from authlib.integrations.requests_client import AssertionSession

def create_assertion_session(conf_file, scopes, subject=None):
    with open(conf_file, 'r') as f:
        conf = json.load(f)

    key_id = conf.get('private_key_id')
    header = {'alg': 'RS256'}
    if key_id:
        header['kid'] = key_id

    # Google puts scope in payload
    claims = {'scope': ' '.join(scopes)}
    return AssertionSession(
        token_endpoint=conf['token_uri'],
        grant_type=AssertionSession.JWT_BEARER_GRANT_TYPE,
        issuer=conf['client_email'],
        audience=conf['token_uri'],
        claims=claims,
        subject=subject,
        key=conf['private_key'],
        header=header,
    )

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]
session = create_assertion_session("C:/Users/jobo/Documents/maya/2022/gspread_key.json", scopes)
client = Client(None, session)

sheet_name = "joboproject"
sheet = client.open(sheet_name).sheet1

# examples
# query
result = sheet.get_all_records()
print(result)
print(len(result))
result = sheet.row_values(2)
print(result)
result = sheet.col_values(2)
print(result)
result = sheet.cell(4, 2).value
print(result)
sheet.update_cell(4,2,"Review")
