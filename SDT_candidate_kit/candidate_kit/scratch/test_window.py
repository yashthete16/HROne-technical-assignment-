from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017')['attendance_db']
coll = db['_test_moving_avg']
coll.drop()

# Insert dummy sequence
data = [
    {"date": "2026-07-05", "is_working_day": False, "rate": None},
    {"date": "2026-07-06", "is_working_day": True, "rate": 0.8},
    {"date": "2026-07-07", "is_working_day": True, "rate": 1.0},
    {"date": "2026-07-08", "is_working_day": True, "rate": 0.9},
    {"date": "2026-07-09", "is_working_day": True, "rate": 0.5},
    {"date": "2026-07-10", "is_working_day": True, "rate": 0.7},
    {"date": "2026-07-11", "is_working_day": False, "rate": None},
    {"date": "2026-07-12", "is_working_day": False, "rate": None},
    {"date": "2026-07-13", "is_working_day": True, "rate": 1.0},
]
coll.insert_many(data)

pipeline = [
    {
        "$setWindowFields": {
            "sortBy": {"date": 1},
            "output": {
                "moving_avg_7d": {
                    "$avg": "$rate",
                    "window": {
                        "documents": [-6, 0]
                    }
                }
            }
        }
    }
]

res = list(coll.aggregate(pipeline))
for r in res:
    print(r["date"], "rate:", r["rate"], "moving_avg:", r["moving_avg_7d"])
coll.drop()
