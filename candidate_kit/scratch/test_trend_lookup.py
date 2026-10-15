from pymongo import MongoClient
from datetime import datetime, timezone

db = MongoClient('mongodb://localhost:27017')['attendance_db']
coll = db['attendance_logs']

pipeline = [
    {
        '$match': {
            'date': {'$gte': '2026-07-06', '$lte': '2026-07-08'}
        }
    },
    {
        '$lookup': {
            'from': 'employees',
            'localField': 'emp_code',
            'foreignField': 'emp_code',
            'as': 'emp'
        }
    },
    {
        '$unwind': '$emp'
    },
    {
        '$match': {
            'emp.department': 'Engineering'
        }
    },
    {
        '$group': {
            '_id': '$date',
            'present_count': {
                '$sum': {
                    '$cond': [
                        {'$in': ['$status', ['PRESENT', 'WFH', 'ON_DUTY']]},
                        {'$cond': [{'$eq': ['$half_day', True]}, 0.5, 1.0]},
                        0
                    ]
                }
            },
            'late_count': {
                '$sum': {'$cond': [{'$gt': ['$late_minutes', 0]}, 1, 0]}
            }
        }
    },
    {
        '$project': {
            'date_val': {'$dateFromString': {'dateString': '$_id'}},
            'present_count': 1,
            'late_count': 1
        }
    },
    {
        '$densify': {
            'field': 'date_val',
            'range': {
                'step': 1,
                'unit': 'day',
                'bounds': [datetime(2026, 7, 5, tzinfo=timezone.utc), datetime(2026, 7, 9, tzinfo=timezone.utc)]
            }
        }
    },
    {
        '$project': {
            'date_str': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$date_val'}},
            'present_count': {'$ifNull': ['$present_count', 0]},
            'late_count': {'$ifNull': ['$late_count', 0]}
        }
    },
    {
        '$lookup': {
            'from': 'employees',
            'let': {'cur_date': '$date_str'},
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {'$eq': ['$department', 'Engineering']},
                                {'$lte': ['$joined_on', '$$cur_date']}
                            ]
                        }
                    }
                },
                {
                    '$count': 'count'
                }
            ],
            'as': 'hc'
        }
    },
    {
        '$project': {
            'date': '$date_str',
            'present_count': 1,
            'late_count': 1,
            'headcount': {'$ifNull': [{'$arrayElemAt': ['$hc.count', 0]}, 0]}
        }
    }
]

res = list(coll.aggregate(pipeline))
for r in res:
    print(r)
