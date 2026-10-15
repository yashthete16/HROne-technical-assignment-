from pymongo import MongoClient
from datetime import datetime, timezone

db = MongoClient('mongodb://localhost:27017')['attendance_db']
coll = db['_test_densify']
coll.drop()

pipeline = [
    {
        '$densify': {
            'field': 'date',
            'range': {
                'step': 1,
                'unit': 'day',
                'bounds': [datetime(2026, 7, 5, tzinfo=timezone.utc), datetime(2026, 7, 11, tzinfo=timezone.utc)]
            }
        }
    }
]
res = list(coll.aggregate(pipeline))
print("Results with empty coll:", len(res))
