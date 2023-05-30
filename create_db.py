import sqlite3

if __name__=="__main__":

    # Create a local DB to prevent duplicate alerts by slack bot
    con = sqlite3.connect("04_alerts.db")
    cur = con.cursor()
    
    # Create the table inside the db
    cur.execute("CREATE TABLE alerts (superevent_id, type, event_time)")

