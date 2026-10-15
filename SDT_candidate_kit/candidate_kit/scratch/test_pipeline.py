from pymongo import MongoClient
from datetime import datetime, timezone

db = MongoClient('mongodb://localhost:27017')['attendance_db']
coll = db['_test_densify']
coll.drop()
coll.insert_one({'date': datetime(2026, 7, 6, tzinfo=timezone.utc), 'val': 1})
coll.insert_one({'date': datetime(2026, 7, 9, tzinfo=timezone.utc), 'val': 2})

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
for r in res:
    print(r['date'].strftime('%Y-%m-%d'), r.get('val'))
coll.drop()
