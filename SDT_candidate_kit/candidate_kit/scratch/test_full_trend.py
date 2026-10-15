from pymongo import MongoClient
from datetime import datetime, timedelta, timezone

db = MongoClient('mongodb://localhost:27017')['attendance_db']
department = "Engineering"
from_str = "2026-07-05"
to_str = "2026-07-10"

bounds = [
    datetime.fromisoformat(f"{from_str}T00:00:00+00:00"),
    datetime.fromisoformat(f"{to_str}T00:00:00+00:00") + timedelta(days=1)
]

pipeline = [
    {
        "$match": {
            "date": {"$gte": from_str, "$lte": to_str}
        }
    },
    {
        "$lookup": {
            "from": "employees",
            "localField": "emp_code",
            "foreignField": "emp_code",
            "as": "emp"
        }
    },
    {
        "$unwind": "$emp"
    },
    {
        "$match": {
            "emp.department": department
        }
    },
    {
        "$group": {
            "_id": "$date",
            "present_count": {
                "$sum": {
                    "$cond": [
                        {"$in": ["$status", ["PRESENT", "WFH", "ON_DUTY"]]},
                        {"$cond": [{"$eq": ["$half_day", True]}, 0.5, 1.0]},
                        0.0
                    ]
                }
            },
            "late_count": {
                "$sum": {"$cond": [{"$gt": ["$late_minutes", 0]}, 1, 0]}
            }
        }
    },
    {
        "$project": {
            "date_val": {"$dateFromString": {"dateString": "$_id"}},
            "present_count": 1,
            "late_count": 1
        }
    },
    {
        "$densify": {
            "field": "date_val",
            "range": {
                "step": 1,
                "unit": "day",
                "bounds": bounds
            }
        }
    },
    {
        "$project": {
            "date_str": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date_val"}},
            "present_count": {"$ifNull": ["$present_count", 0.0]},
            "late_count": {"$ifNull": ["$late_count", 0]}
        }
    },
    {
        "$lookup": {
            "from": "employees",
            "let": {"cur_date": "$date_str"},
            "pipeline": [
                {
                    "$match": {
                        "$expr": {
                            "$and": [
                                {"$eq": ["$department", department]},
                                {"$lte": ["$joined_on", "$$cur_date"]}
                            ]
                        }
                    }
                },
                {
                    "$count": "count"
                }
            ],
            "as": "hc"
        }
    },
    {
        "$project": {
            "date": "$date_str",
            "present_count": 1,
            "late_count": 1,
            "headcount": {"$ifNull": [{"$arrayElemAt": ["$hc.count", 0]}, 0]},
            "is_working_day": {
                "$lte": [
                    {"$isoDayOfWeek": {"$dateFromString": {"dateString": "$date_str"}}},
                    5
                ]
            }
        }
    },
    {
        "$project": {
            "date": 1,
            "is_working_day": 1,
            "headcount": 1,
            "present_count": 1,
            "late_count": 1,
            "attendance_rate": {
                "$cond": [
                    {
                        "$and": [
                            {"$eq": ["$is_working_day", True]},
                            {"$gt": ["$headcount", 0]}
                        ]
                    },
                    {"$divide": ["$present_count", "$headcount"]},
                    None
                ]
            }
        }
    },
    {
        "$setWindowFields": {
            "sortBy": {"date": 1},
            "output": {
                "moving_avg_7d": {
                    "$avg": "$attendance_rate",
                    "window": {
                        "documents": [-6, 0]
                    }
                }
            }
        }
    },
    {
        "$sort": {"date": 1}
    }
]

res = list(db.attendance_logs.aggregate(pipeline))
for r in res:
    print(r)
