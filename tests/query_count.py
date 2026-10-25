"""Database calls per page with a realistic academy (60 players, 4 coaches).
On a remote database every call is a network round trip, so this is the speed budget.
Run: python tests/query_count.py"""
import os
import sys
import tempfile
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.pop("DATABASE_URL", None)
os.environ.pop("POSTGRES_URL", None)
import database as db  # noqa: E402

tmp = tempfile.mkdtemp()
db.DB_PATH = os.path.join(tmp, "q.db")
db.BACKUP_DIR = os.path.join(tmp, "b")
import app as appmod  # noqa: E402

appmod.EXPORTS_DIR = os.path.join(tmp, "x")
T = date.today()
iso = lambda n: (T + timedelta(days=n)).isoformat()  # noqa: E731

con = db.get_db()
for i in range(60):
    pid = con.execute("INSERT INTO players (full_name, first_name, last_name, school, birth_date, gender, group_id, "
                      "join_date, status, trial_used, guardian_phone) VALUES (?,?,?,?,?,?,?,?,'active',1,?)",
                      (f"Kid {i}", "Kid", str(i), f"School {i % 5}", f"201{i % 8}-05-1{i % 9}", "M", i % 4 + 1,
                       iso(-90), f"079{1000000 + i:07d}")).lastrowid
    db.create_subscription(con, pid, iso(-20 - i % 15), price=20, sessions_total=12, amount=20 if i % 4 else 10)
    for d in range(1, 15, 2):
        db.mark_attendance(con, pid, iso(-d), i % 4 + 1, "present" if (i + d) % 5 else "absent", "admin")
for n in range(4):
    con.execute("INSERT INTO coaches (name, phone, salary_type, salary_amount, active, join_date, code) "
                "VALUES (?,?,?,?,1,?,?)", (f"Coach {n}", "0790000000", "session", 10, iso(-90), f"90000{n}"))
    for d in range(1, 15, 2):
        db.coach_check_in(con, n + 1, iso(-d), "qr")
con.commit()
con.close()

COUNT = {"n": 0}
_orig = db.get_db


def counting_get_db():
    c = _orig()
    c.set_trace_callback(lambda s: COUNT.__setitem__("n", COUNT["n"] + 1))
    return c


db.get_db = counting_get_db
client = appmod.app.test_client()
pages = ["/dashboard", "/players", "/players/1", "/attendance", "/api/attendance?group_id=1&date=" + iso(-1),
         "/payments", "/finance", "/coaches", "/groups", "/analytics", "/events", "/settings",
         "/reports/weekly", "/reports/month", "/reports/trials", "/coaches/checkin"]
if __name__ == "__main__":
    for p in pages:
        COUNT["n"] = 0
        r = client.get(p)
        print(f"{COUNT['n']:6d}  {r.status_code}  {p}")
