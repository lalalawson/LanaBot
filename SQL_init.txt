import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL, sslmode='allow')

cur = conn.cursor()

cur.execute("CREATE TABLE memories(id SERIAL PRIMARY KEY, author VARCHAR, content VARCHAR, photo VARCHAR, post_date DATE NOT NULL DEFAULT CURRENT_DATE);")
cur.execute("INSERT INTO memories(author, content, photo) VALUES('lawson', 'this is test content num 1', 'photoid1');") 
cur.execute("INSERT INTO memories(author, content, photo, post_date) VALUES('lina', 'wow test content num 2', 'photoid2', '2021-06-30');") 
cur.execute("INSERT INTO memories(author, content, photo, post_date) VALUES('lawson', 'hye hey 3', 'photoid3', '2021-05-30');") 
cur.execute("INSERT INTO memories(author, content, photo, post_date) VALUES('lawson', 'chicken 4', 'photoid4', '2021-06-02');") 
cur.execute("INSERT INTO memories(author, content, photo, post_date) VALUES('lawson', 'duck 5', 'photoid5', '2021-06-12');") 

conn.commit()

cur.execute("SELECT * FROM memories;")
q1 = cur.fetchall()
print(q1)

cur.close()
conn.close()