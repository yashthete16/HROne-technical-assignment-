from pymongo import MongoClient
from datetime import datetime, timezone

db = MongoClient('mongodb://localhost:27017')['attendance_db']
coll = db['attendance_logs']

pipeline = [
    {
        '$match': {
            'emp_code': 'NON_EXISTENT_EMP'
        }
    },
    {
        '$group': {
            '_id': '$date',
            'count': {'$sum': 1}
        }
    },
    {
        '$project': {
            'date_val': {'$dateFromString': {'dateString': '$_id'}},
            'count': 1
        }
    },
    {
        '$densify': {
            'field': 'date_val',
            'range': {
                'step': 1,
                'unit': 'day',
                'bounds': [datetime(2026, 7, 5, tzinfo=timezone.utc), datetime(2026, 7, 11, tzinfo=timezone.utc)]
            }
        }
    }
]
res = list(coll.aggregate(pipeline))
print("Results with 0 matched docs before densify:", len(res))
for r in res:
    print(r)
