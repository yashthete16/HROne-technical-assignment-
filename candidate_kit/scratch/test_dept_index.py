from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017')['attendance_db']
db.employees.create_index([("joined_on", 1)])

cmd_dept = {
    "aggregate": "employees",
    "pipeline": [
        {"$match": {"joined_on": {"$lte": "2026-07-31"}}}
    ],
    "cursor": {}
}
res_dept = db.command("explain", cmd_dept, verbosity="executionStats")
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

c5, i5 = [], []
check_stages(res_dept.get("stages", res_dept.get("queryPlanner", {})), c5, i5)
print("department_summary with joined_on index: IXSCAN count =", len(i5), "COLLSCAN count =", len(c5))
