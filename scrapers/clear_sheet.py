import gspread
from google.oauth2.service_account import Credentials

creds = Credentials.from_service_account_file(
    "scrapers/credentials.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)
gc = gspread.authorize(creds)
sh = gc.open_by_key("1P7i1J9hC1uWS4zvxLOlL2RtFNBw-wj9VzNIU5edspUw").worksheet("SMBkits Lead DB")
sh.delete_rows(2, sh.row_count)
print("삭제 완료")
