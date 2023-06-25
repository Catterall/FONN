import pyodbc
import typing
from dotenv import dotenv_values


class FONNDB:
    def __init__(self):
        config = dotenv_values(".env")
        self.conn = pyodbc.connect(
            f"Driver={config['DRIVER']};"
            f"Server={config['SERVER']};"
            f"Database={config['DATABASE']};"
            f"Trusted_Connection={config['TRUSTED_CONNECTION']};"
        )
        self.cursor = self.conn.cursor()
    
    def select(self, query, *args) -> typing.List[typing.Tuple]:
        self.cursor.execute(query, args)
        return self.cursor.fetchall()
    
    def nonselect(self, query, *args) -> None:
        self.cursor.execute(query, args)
        self.conn.commit()

    def session_key_exists(self, session_key: str) -> bool:
        return self.select("SELECT COUNT(*) FROM Session WHERE SessionKey = ?", session_key)[0][0]
    
    def session_key_expired(self, session_key: str) -> bool:
        return self.select("SELECT COUNT(*) FROM Session WHERE SessionKey = ? AND ExpiryDate < GETDATE()", session_key)[0][0]
