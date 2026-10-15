from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017')['attendance_db']
month = "2026-07"
first_day = f"{month}-01"
last_day = f"{month}-31"
limit = 10

pipeline = [
    {
        "$match": {
            "date": {"$gte": first_day, "$lte": last_day},
            "late_minutes": {"$gt": 0}
        }
    },
    {
        "$group": {
            "_id": "$emp_code",
            "total_late_minutes": {"$sum": "$late_minutes"},
            "late_count": {"$sum": 1}
        }
    },
    {
        "$lookup": {
            "from": "employees",
            "localField": "_id",
            "foreignField": "emp_code",
            "as": "emp"
        }
    },
    {
        "$unwind": "$emp"
    },
    {
        "$setWindowFields": {
            "sortBy": {"total_late_minutes": -1},
            "output": {
                "rank": {"$rank": {}}
            }
        }
    },
    {
        "$match": {
            "rank": {"$lte": limit}
        }
    },
    {
        "$sort": {
            "total_late_minutes": -1,
            "_id": 1
        }
    },
    {
        "$project": {
            "_id": 0,
            "rank": 1,
            "emp_code": "$_id",
            "name": "$emp.name",
            "department": "$emp.department",
            "total_late_minutes": 1,
            "late_count": 1
        }
    }
]

res = list(db.attendance_logs.aggregate(pipeline))
print("Leaderboard results:")
for r in res:
    print(r)
