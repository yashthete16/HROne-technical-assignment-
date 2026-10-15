from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017')['attendance_db']

# Create indexes
db.employees.create_index([("emp_code", 1)], unique=True)
db.employees.create_index([("department", 1), ("emp_code", 1)])
db.employees.create_index([("department", 1), ("joined_on", 1)])

db.attendance_logs.create_index([("emp_code", 1), ("date", 1)], unique=True)
db.attendance_logs.create_index([("emp_code", 1), ("punch_in", -1)])
db.attendance_logs.create_index([("date", -1), ("emp_code", 1)])
db.attendance_logs.create_index([("date", 1), ("late_minutes", 1)])

def check_stages(stage, collscans, ixscans):
    if not isinstance(stage, dict):
        return
    s = stage.get("stage")
    if s == "COLLSCAN":
        collscans.append(stage)
    if s == "IXSCAN":
        ixscans.append(stage)
    for v in stage.values():
        if isinstance(v, dict):
            check_stages(v, collscans, ixscans)
        elif isinstance(v, list):
            for item in v:
                check_stages(item, collscans, ixscans)

# 1. attendance_list explain
cmd_list = {
    "find": "attendance_logs",
    "filter": {"date": {"$gte": "2026-07-01", "$lte": "2026-07-31"}},
    "sort": {"date": -1, "emp_code": 1},
    "skip": 0,
    "limit": 20
}
res_list = db.command("explain", cmd_list, verbosity="executionStats")
c1, i1 = [], []
check_stages(res_list.get("queryPlanner", {}), c1, i1)
print("attendance_list: IXSCAN count =", len(i1), "COLLSCAN count =", len(c1))

# 2. employee_monthly explain
cmd_monthly = {
    "aggregate": "attendance_logs",
    "pipeline": [
        {"$match": {"emp_code": "EMP0001", "date": {"$gte": "2026-07-01", "$lte": "2026-07-31"}}}
    ],
    "cursor": {}
}
res_monthly = db.command("explain", cmd_monthly, verbosity="executionStats")
c2, i2 = [], []
check_stages(res_monthly.get("stages", res_monthly.get("queryPlanner", {})), c2, i2)
print("employee_monthly: IXSCAN count =", len(i2), "COLLSCAN count =", len(c2))

# 3. late_leaderboard explain
cmd_lead = {
    "aggregate": "attendance_logs",
    "pipeline": [
        {"$match": {"date": {"$gte": "2026-07-01", "$lte": "2026-07-31"}, "late_minutes": {"$gt": 0}}}
    ],
    "cursor": {}
}
res_lead = db.command("explain", cmd_lead, verbosity="executionStats")
c3, i3 = [], []
check_stages(res_lead.get("stages", res_lead.get("queryPlanner", {})), c3, i3)
print("late_leaderboard: IXSCAN count =", len(i3), "COLLSCAN count =", len(c3))

# 4. department_trend explain
cmd_trend = {
    "aggregate": "attendance_logs",
    "pipeline": [
        {"$match": {"date": {"$gte": "2026-07-01", "$lte": "2026-07-31"}}}
    ],
    "cursor": {}
}
res_trend = db.command("explain", cmd_trend, verbosity="executionStats")
c4, i4 = [], []
check_stages(res_trend.get("stages", res_trend.get("queryPlanner", {})), c4, i4)
print("department_trend: IXSCAN count =", len(i4), "COLLSCAN count =", len(c4))

# 5. department_summary explain
cmd_dept = {
    "aggregate": "employees",
    "pipeline": [
        {"$match": {"joined_on": {"$lte": "2026-07-31"}}}
    ],
    "cursor": {}
}
res_dept = db.command("explain", cmd_dept, verbosity="executionStats")
c5, i5 = [], []
check_stages(res_dept.get("stages", res_dept.get("queryPlanner", {})), c5, i5)
print("department_summary: IXSCAN count =", len(i5), "COLLSCAN count =", len(c5))
