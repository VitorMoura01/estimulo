import os
import psycopg2
import pandas as pd

def connect_to_db():
    conn = psycopg2.connect(host='localhost', database='videoknowledge', user='postgres', password='postgres', port='5432')
    return conn

def create_table(conn):
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transcripts (
            id SERIAL PRIMARY KEY,
            link VARCHAR(255),
            transcript VARCHAR
        )
    ''')
    conn.commit()
    cur.close()

def insert_into_table(conn, link, transcript):
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO transcripts (link, transcript) 
        VALUES (%s, %s)
    ''', (link, transcript))

    conn.commit()
    cur.close()

def select_all_and_create_txt(conn):
    df = pd.read_sql('SELECT * FROM transcripts', conn)
    txt_path = 'knowledgePrompt.txt'
    df.to_csv(txt_path, sep='\t', index=False)
    absolute_path = os.path.join(os.getcwd(), txt_path)

    return absolute_path

def close_connection(conn):
    conn.close()