from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017')['attendance_db']
month = "2026-07"
first_day = f"{month}-01"
last_day = f"{month}-31"

pipeline = [
    {
        "$match": {
            "joined_on": {"$lte": last_day}
        }
    },
    {
        "$group": {
            "_id": "$department",
            "headcount": {"$sum": 1},
            "emp_codes": {"$push": "$emp_code"}
        }
    },
    {
        "$lookup": {
            "from": "attendance_logs",
            "let": {"dept_emps": "$emp_codes"},
            "pipeline": [
                {
                    "$match": {
                        "$expr": {
                            "$and": [
                                {"$in": ["$emp_code", "$$dept_emps"]},
                                {"$gte": ["$date", first_day]},
                                {"$lte": ["$date", last_day]}
                            ]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "present_days": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$and": [
                                            {"$in": ["$status", ["PRESENT", "WFH", "ON_DUTY"]]},
                                            {"$lte": [{"$isoDayOfWeek": {"$dateFromString": {"dateString": "$date"}}}, 5]}
                                        ]
                                    },
                                    {"$cond": [{"$eq": ["$half_day", True]}, 0.5, 1.0]},
                                    0.0
                                ]
                            }
                        },
                        "late_count": {
                            "$sum": {"$cond": [{"$gt": ["$late_minutes", 0]}, 1, 0]}
                        },
                        "total_late_minutes": {
                            "$sum": {"$ifNull": ["$late_minutes", 0]}
                        },
                        "leave_count": {
                            "$sum": {"$cond": [{"$eq": ["$status", "LEAVE"] }, 1, 0]}
                        },
                        "on_duty_count": {
                            "$sum": {"$cond": [{"$eq": ["$status", "ON_DUTY"]}, 1, 0]}
                        },
                        "work_hours_sum": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$and": [
                                            {"$in": ["$status", ["PRESENT", "WFH", "ON_DUTY"]]},
                                            {"$ne": ["$work_hours", None]}
                                        ]
                                    },
                                    "$work_hours",
                                    0.0
                                ]
                            }
                        },
                        "work_hours_count": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$and": [
                                            {"$in": ["$status", ["PRESENT", "WFH", "ON_DUTY"]]},
                                            {"$ne": ["$work_hours", None]}
                                        ]
                                    },
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                }
            ],
            "as": "stats"
        }
    },
    {
        "$sort": {"_id": 1}
    }
]

res = list(db.employees.aggregate(pipeline))
print("Department summary results:")
for r in res:
    print(r)
