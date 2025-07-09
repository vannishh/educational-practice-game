import json
import os
from config import HIGHSCORE_FILE

def load_high_score():
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as file:
                data = json.load(file)
                return data.get("high_score", 0)
        return 0
    except:
        return 0

def save_high_score(score):
    try:
        with open(HIGHSCORE_FILE, "w") as file:
            json.dump({"high_score": score}, file)
    except:
        print("Не удалось сохранить рекорд")
