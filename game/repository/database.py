from time import strftime

import mysql.connector

scores_table = "metro2d"

class Database:
    def __init__(self, address, db_name, db_user, db_pass):
        self.top_scores = []

        self.db = mysql.connector.connect(
            host=address,
            database=db_name,
            user=db_user,
            password=db_pass
        )

        print("[DB] Connecting to the database...")
        self.cursor = self.db.cursor()

        print("[DB] Creating the table if absent...")
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {scores_table} (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, score INT NOT NULL, time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)")

        print("[DB] Initializing leaderboard...")
        self.refresh_leaderboard()

    def add_score(self, name, score):
        print(f"[DB] Saving score for {name}...")

        self.cursor.execute(f"INSERT INTO {scores_table} (name,score) VALUES (%s,%s)", (name, score))
        self.db.commit()

        if self.cursor.rowcount == 0:
            print("[DB] Score failed to save!")
        else:
            print("[DB] Score saved.")

    def refresh_leaderboard(self):
        self.top_scores = self.get_top_scores()

    def get_top_scores(self):
        print("[DB] Loading top scores...")

        self.cursor.execute(f"SELECT name, MAX(score) AS high_score, time FROM {scores_table} GROUP BY name ORDER BY high_score DESC LIMIT 10")
        return self.cursor.fetchall()