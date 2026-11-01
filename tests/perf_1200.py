"""Page time + database calls with a real-size academy (1,200 players, each with a package).
On Supabase each call is one round trip (~6 ms in-region), so calls x 6 ms + time = the server cost.
Run: python tests/perf_1200.py"""
import os
import sys
import tempfile
import time
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.pop("DATABASE_URL", None)
os.environ.pop("POSTGRES_URL", None)
import database as db  # noqa: E402

tmp = tempfile.mkdtemp()
db.DB_PATH = os.path.join(tmp, "p.db")
db.BACKUP_DIR = os.path.join(tmp, "b")
import app as appmod  # noqa: E402

appmod.EXPORTS_DIR = os.path.join(tmp, "x")
T = date.today()
iso = lambda n: (T + timedelta(days=n)).isoformat()  # noqa: E731
N = int(os.environ.get("PERF_N", 1200))

con = db.get_db()
for gid in range(1, 5):
    con.execute("UPDATE groups SET slots=? WHERE id=?",
                ('[{"day":"Saturday","time":"5:00"},{"day":"Monday","time":"5:00"},{"day":"Wednesday","time":"5:00"}]', gid))
for i in range(N):
    pid = con.execute("INSERT INTO players (full_name, first_name, last_name, birth_date, gender, group_id, join_date, "
                      "status, trial_used, phone) VALUES (?,?,?,?,?,?,?,'active',1,?)",
                      (f"Kid {i}", "Kid", str(i), f"201{i % 8}-05-1{i % 9}", "M", i % 4 + 1, iso(-90),
                       f"079{1000000 + i:07d}")).lastrowid
    con.execute("INSERT INTO subscriptions (player_id, start_date, sessions_total, sessions_used, price, expiry_date, status) "
                "VALUES (?,?,12,0,0,?,'active')", (pid, iso(-(i % 30)), iso(30)))
    if i % 10 == 0:
        db.mark_attendance(con, pid, iso(-1), i % 4 + 1, "present", "admin")
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
pages = ["/dashboard", "/players", "/players?q=Kid%201", "/players/1", "/attendance",
         "/api/attendance?group=1&date=" + iso(0), "/finance", "/analytics", "/reports/weekly",
         "/reports/month", "/players/setup"]
if __name__ == "__main__":
    for warm in (True, False):
        for p in pages:
            COUNT["n"] = 0
            t0 = time.perf_counter()
            r = client.get(p)
            ms = (time.perf_counter() - t0) * 1000
            if not warm:
                print(f"{COUNT['n']:6d} calls {ms:8.0f} ms  {len(r.data) // 1024:5d} KB  {r.status_code}  {p}")
