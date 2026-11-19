import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()                              
DATABASE_URL = os.environ["DATABASE_URL"]  

engine = create_engine(DATABASE_URL)       

if __name__ == "__main__":                 
    with engine.connect() as conn:         
        for row in conn.execute(text("SELECT id, email FROM users")):
            print(row)