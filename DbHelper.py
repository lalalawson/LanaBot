import psycopg2
from dotenv import load_dotenv

load_dotenv()

class DbHelper():

    def __init__(self, url):
        self.url = url
        self.conn = psycopg2.connect(url, sslmode='allow')

    def retrieveMemory(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM memories OFFSET floor(random() * (SELECT COUNT(*) FROM memories)) LIMIT 1;")
        memory = cur.fetchone()
        cur.close()
        return memory