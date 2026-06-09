import os
import sys

#add to env the parent folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mf_api import APISession, RadarAPI
from dotenv import load_dotenv

load_dotenv()

APISession.set_auth_token(os.getenv("TOKEN"))

def test_get_stations():
    radarAPI = RadarAPI()
    stations = radarAPI.get_liste_stations()# return response, .text return str (csv if expected), .to_MClass() return dict or list[dict] like object (for json and csv)

    print(stations)
    
test_get_stations()