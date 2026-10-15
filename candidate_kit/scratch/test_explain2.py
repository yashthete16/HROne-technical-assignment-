from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017')['attendance_db']

# Test find explain via command
find_cmd = {
    "find": "attendance_logs",
    "filter": {"date": "2026-07-06"},
    "sort": {"date": -1, "emp_code": 1},
    "skip": 0,
    "limit": 20
}
explain_find = db.command("explain", find_cmd, verbosity="executionStats")
print("Find explain ok:", "executionStats" in explain_find or "queryPlanner" in explain_find)

# Test aggregate explain via command
agg_cmd = {
    "aggregate": "attendance_logs",
    "pipeline": [{"$match": {"date": "2026-07-06"}}],
    "cursor": {}
}
explain_agg = db.command("explain", agg_cmd, verbosity="executionStats")
print("Agg explain ok:", "executionStats" in explain_agg or "queryPlanner" in explain_agg)
