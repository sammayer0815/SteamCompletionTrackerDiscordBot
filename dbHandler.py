import sqlite3
import os
from steam_web_api import Steam
from dotenv import load_dotenv

load_dotenv()

con = sqlite3.connect('steamCompletionTracker.db')

cur = con.cursor()

steam = Steam(os.getenv("STEAM_APIKEY"))
    
def registerAccount(discord_uid, steam_uid):
    cur.execute("""
        INSERT INTO user_connections (discord_uid, steam_uid)
        VALUES (?, ?)
    """, (discord_uid, steam_uid))
    con.commit()
    return

def steamUidCheck(steam_uid: str):

    steam_id = steam_uid.rstrip('/')

    steam_id = steam_id.split('/')[-1]

    # First, try searching for the user
    profile_data = steam.users.search_user(steam_id)
    
    if profile_data != "No match":
        return profile_data['player']
    
    # Fallback to getting user details directly
    user_details = steam.users.get_user_details(steam_id)
    player_data = user_details.get("player")

    if player_data is None:
        return "No data found"
    
    return player_data
