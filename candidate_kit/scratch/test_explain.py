from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017')['attendance_db']

# Test find explain
cursor = db.attendance_logs.find({"date": "2026-07-06"}).sort([("date", -1), ("emp_code", 1)])
explain_find = cursor.explain("executionStats")
print("Find explain ok:", "executionStats" in explain_find)

# Test aggregate explain
cmd = {"aggregate": "attendance_logs", "pipeline": [{"$match": {"date": "2026-07-06"}}], "cursor": {}}
explain_agg = db.command("explain", cmd, verbosity="executionStats")
print("Agg explain ok:", "executionStats" in explain_agg)
