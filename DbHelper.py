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

    def uploadMemory(self, author, content, file_id, post_date, file_type):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO memories(author, content, file_id, post_date, file_type) VALUES(%s, %s, %s, %s, %s);", (author, content, file_id, post_date, file_type))
        self.conn.commit()
        cur.close()

    def retrieveJoke(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM jokes OFFSET floor(random() * (SELECT COUNT(*) FROM jokes)) LIMIT 1;")
        joke = cur.fetchone()
        setup = joke[1]
        delivery = joke[2]
        return setup, delivery

    def uploadJoke(self, setup, delivery):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO jokes(setup, delivery) VALUES(%s, %s);", (setup, delivery))
        self.conn.commit()
        cur.close()