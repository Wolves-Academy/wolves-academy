"""Demo server on :8766 with a throwaway DB full of sample (synthetic) data.
Run:  python tests/serve_demo.py      (never touches academy.db)"""
import os
import sys
import tempfile
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import database as db  # noqa: E402

tmp = tempfile.mkdtemp()
db.DB_PATH = os.path.join(tmp, "demo.db")
db.BACKUP_DIR = os.path.join(tmp, "b")
import app as appmod  # noqa: E402

appmod.EXPORTS_DIR = os.path.join(tmp, "x")
T = date.today()


def iso(n):
    return (T + timedelta(days=n)).isoformat()


con = db.get_db()
schools = ["Al-Mafraq Secondary", "Jubilee School", "Al-Mafraq Secondary", "Modern Montessori", "", "Jubilee School"]
kids = [("Omar", "Khaled", "Haddad"), ("Leen", "Sami", "Abbadi"), ("Zaid", "Ali", "Masri"), ("Yousef", "", "Nasser"),
        ("Sara", "Ahmad", "Qudah"), ("Hamza", "Fadi", "Rawashdeh"), ("Tala", "", "Zoubi"), ("Kareem", "Basel", "Saleh")]
for i, (f, m, l) in enumerate(kids):
    full = db.compose_name(f, m, l)
    pid = con.execute(
        "INSERT INTO players (full_name, first_name, middle_name, last_name, school, birth_date, gender, group_id, "
        "join_date, status, trial_used, guardian_name, guardian_phone, parent2_name, parent2_phone) "
        "VALUES (?,?,?,?,?,?,?,?,?,'active',1,?,?,?,?)",
        (full, f, m, l, schools[i % len(schools)], f"201{i % 6 + 2}-0{i % 9 + 1}-1{i % 9}",
         "F" if f in ("Leen", "Sara", "Tala") else "M", i % 4 + 1, iso(-60 + i), f"{m or 'Fadi'} {l}",
         f"079{1000000 + i * 7311:07d}", f"Rana {l}", f"078{2000000 + i * 5311:07d}")).lastrowid
    db.create_subscription(con, pid, iso(-24 + i * 3), price=20, sessions_total=12, amount=20 if i % 3 else 10,
                           pay_date=iso(-24 + i * 3))
    for d in range(-10, 1):
        if db.is_training_day(iso(d)):
            db.mark_attendance(con, pid, iso(d), i % 4 + 1, "present" if (i + d) % 4 else "absent", "Coach Ahmad")
for code, name, kind, amt in (("482913", "Coach Ahmad", "monthly", 180), ("735102", "Coach Bashar", "session", 8)):
    cid = con.execute("INSERT INTO coaches (name, phone, salary_type, salary_amount, active, join_date, code) "
                      "VALUES (?,?,?,?,1,?,?)", (name, "0790000001", kind, amt, iso(-40), code)).lastrowid
    for d in (-6, -4, -2, 0):
        if db.is_training_day(iso(d)):
            db.coach_check_in(con, cid, iso(d))
    db.record_coach_login(con, cid, "10.0.0.7")
# trials: one joined, one waiting
for n, d, joined in (("Majd Haddadin", -9, True), ("Lana Khatib", -2, False)):
    p = con.execute("INSERT INTO players (full_name, first_name, last_name, school, group_id, join_date, status, trial_used) "
                    "VALUES (?,?,?,?,1,?, 'active',0)", (n, n.split()[0], n.split()[1], "Jubilee School", iso(d))).lastrowid
    con.commit()
    tday = next(iso(x) for x in range(d, d + 7) if db.is_training_day(iso(x)))
    db.mark_attendance(con, p, tday, 1, "present", "Coach Bashar")
    if joined:
        db.create_subscription(con, p, iso(d + 3), price=20, sessions_total=12)
con.execute("INSERT INTO events (title, kind, partner, location, date, start_time, end_time, amount, notes) "
            "VALUES ('Basketball day','school','Jubilee School','School yard',?, '10:00','12:30',NULL,'Bring 20 balls')",
            (iso(4),))
for d in (-6, -4, -2):
    if db.is_training_day(iso(d)):
        db.log_session_costs(con, iso(d), {"court_lights": 2, "water": 2})
con.commit()
con.close()
appmod.app.config["TEMPLATES_AUTO_RELOAD"] = True
appmod.app.jinja_env.auto_reload = True
print("demo on http://127.0.0.1:8766  (coach codes 482913 / 735102)")
appmod.app.run(host="127.0.0.1", port=8766, debug=False)
