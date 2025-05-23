import json

"""
Structure:
{
    "reg_season": [
        {
            "week": 1,
            "games": [
                "tdb": bool,
                "date": str,
                "time": str,
                "channel": str,
                "home": str,
                "away": str
            ],
            "tbd_games": [
                "tdb": bool,
                "date": str,
                "time": str,
                "channel": str,
                "home": str,
                "away": str
            ],
            "byes": [
                {
                    "team": str
                }
            ]
        }
    ]
}
"""

class Schedule:
    def __init__(self):
        self.data = {
            "reg_season": []
        }

    def add_week(self, week_data):
        self.data["reg_season"].append(week_data)

    def write_data(self, file_name: str):
        with open(file_name, "w", encoding = "utf-8") as f:
            json.dump(self.data, f, indent = 4)
        
    