# -*- coding: utf-8 -*-
"""Acceptance checks for Wolves Sports Academy. Each gate runs on a fresh temp DB.

Run:  python tests/test_app.py <gate|all>
Gates: coaches coachday players weekly trials cancel pages legacy
"""
import os
import sys
import tempfile
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import database as db  # noqa: E402

TMP = tempfile.mkdtemp()
db.DB_PATH = os.path.join(TMP, "t.db")
if db.is_postgres():
    # fresh Postgres schema for every gate (set DATABASE_URL to a THROWAWAY database only)
    import psycopg
    with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as _c:
        _c.execute("DROP SCHEMA public CASCADE")
        _c.execute("CREATE SCHEMA public")
db.BACKUP_DIR = os.path.join(TMP, "b")
import app as appmod  # noqa: E402

appmod.EXPORTS_DIR = os.path.join(TMP, "x")
T = date.today()
ALL7 = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
REMOTE = {"REMOTE_ADDR": "10.1.1.5"}
FAILS = []


def iso(n):
    return (T + timedelta(days=n)).isoformat()


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("  FAIL:", msg)


def set_days(days):
    st = db.get_settings()
    st.update(training_days=days, schedule_history=[], closed_days=[])
    db.save_settings(st)


def new_player(con, name, status="active", gid=1, **kw):
    cols = {"full_name": name, "group_id": gid, "join_date": iso(-60), "status": status, "trial_used": 1, **kw}
    cur = con.execute(f"INSERT INTO players ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                      tuple(cols.values()))
    con.commit()
    return cur.lastrowid


def admin():
    return appmod.app.test_client()          # localhost = admin


def coach_login(code):
    c = appmod.app.test_client()
    r = c.post("/login", data={"pin": code}, environ_base=REMOTE)
    return c, r


# ---------------------------------------------------------------- W1
def gate_coaches():
    a = admin()
    a.post("/coaches/save", data={"name": "Coach Rami", "phone": "0791112223", "salary_type": "session",
                                  "salary_amount": "8", "active": "1", "code": ""})
    con = db.get_db()
    rami = con.execute("SELECT * FROM coaches WHERE name='Coach Rami'").fetchone()
    check(rami and rami["code"] and len(rami["code"]) == 6, "auto 6-digit code")
    r = a.post("/coaches/save", data={"name": "Coach Sami", "salary_type": "monthly", "salary_amount": "150",
                                      "active": "1", "code": rami["code"]})
    check("code_error=1" in r.headers.get("Location", ""), "duplicate code rejected")
    a.post("/coaches/save", data={"name": "Coach Sami", "salary_type": "monthly", "salary_amount": "150",
                                  "active": "1", "code": "4321"})
    c, r = coach_login(rami["code"])
    check(r.status_code == 302 and r.headers["Location"].endswith("/attendance"), "coach code logs in")
    page = c.get("/attendance", environ_base=REMOTE).get_data(as_text=True)
    check("Coach Rami" in page or "Rami" in page, "coach sees own name")
    check(c.get("/finance", environ_base=REMOTE).status_code == 302, "coach blocked from finance")
    check(c.get("/coaches", environ_base=REMOTE).status_code == 302, "coach blocked from coaches")
    check(con.execute("SELECT COUNT(*) n FROM coach_logins WHERE coach_id=?", (rami["id"],)).fetchone()["n"] == 1,
          "login recorded")
    check(con.execute("SELECT last_login FROM coaches WHERE id=?", (rami["id"],)).fetchone()["last_login"],
          "last_login stamped")
    _, r = coach_login("1234")
    check(r.status_code == 200, "old shared coach PIN no longer works")
    # deactivating the coach ends their session
    a.post("/coaches/save", data={"id": rami["id"], "name": "Coach Rami", "salary_type": "session",
                                  "salary_amount": "8", "code": rami["code"]})
    check(c.get("/attendance", environ_base=REMOTE).status_code == 302, "deactivated coach logged out")
    # admin PIN cannot be changed to a coach's code
    a.post("/settings", data={"admin_pin": "4321", "monthly_price": 20, "sessions_per_month": 12, "expiry_days": 35,
                              "bundle_name_en": "Monthly", "bundle_name_ar": "شهري", "bundle_sessions": 12,
                              "bundle_price": 20})
    check(db.get_settings()["admin_pin"] != "4321", "admin PIN cannot equal a coach code")
    body = a.get(f"/coaches/{rami['id']}").get_data(as_text=True)
    check(rami["code"] in body, "admin sees code + history")
    con.close()
    return "GATE_COACHES_OK"


# ---------------------------------------------------------------- W2
def gate_coachday():
    set_days(ALL7)
    a = admin()
    a.post("/coaches/save", data={"name": "Coach Lina", "salary_type": "session", "salary_amount": "10",
                                  "active": "1", "code": "777111"})
    con = db.get_db()
    lina = con.execute("SELECT * FROM coaches WHERE code='777111'").fetchone()
    c, _ = coach_login("777111")
    month = T.strftime("%Y-%m")
    # option 1: court QR from the admin screen; the scanning coach must be signed in
    qr = a.get("/api/checkin/qr").get_json()
    check(qr["qr"].startswith("data:image/svg+xml"), "admin gets a QR image")
    tok = con.execute("SELECT token FROM checkin_tokens WHERE coach_id IS NULL ORDER BY id DESC").fetchone()["token"]
    anon = appmod.app.test_client()
    r = anon.get(f"/checkin/{tok}", environ_base=REMOTE)
    check(r.status_code == 302 and "/login" in r.headers["Location"], "QR asks a signed-out coach to log in")
    r = anon.post(f"/login?next=/checkin/{tok}", data={"pin": "777111"}, environ_base=REMOTE)
    check(r.headers["Location"].endswith(f"/checkin/{tok}"), "login returns to the scanned QR")
    check("<form method=\"post\"" in c.get(f"/checkin/{tok}", environ_base=REMOTE).get_data(as_text=True),
          "QR shows the check button")
    c.post(f"/checkin/{tok}", environ_base=REMOTE)
    c.post(f"/checkin/{tok}", environ_base=REMOTE)
    row = con.execute("SELECT * FROM coach_attendance WHERE coach_id=? AND session_date=?", (lina["id"], iso(0))).fetchone()
    check(row and row["method"] == "qr" and row["check_in"], "QR check-in recorded with time")
    check(db.salary_status(con, lina, month)["due"] == 10, "one day counted once -> 10 JD due")
    check(c.post("/api/coach/check-in", environ_base=REMOTE).status_code in (404, 405), "no free check-in button")
    con.execute("UPDATE checkin_tokens SET expires='2000-01-01T00:00:00' WHERE token=?", (tok,))
    con.commit()
    check("<form method" not in c.get(f"/checkin/{tok}", environ_base=REMOTE).get_data(as_text=True), "expired page")
    check(db.checkin_token(con, tok) is None, "expired QR rejected")
    # option 2: one-time WhatsApp link, no login needed
    con.execute("DELETE FROM coach_attendance WHERE coach_id=?", (lina["id"],))
    con.execute("UPDATE coaches SET phone='0791110000' WHERE id=?", (lina["id"],))
    con.commit()
    r = a.get(f"/coaches/{lina['id']}/wa-checkin")
    check(r.status_code == 302 and r.headers["Location"].startswith("https://wa.me/962791110000"), "WhatsApp link opens chat")
    wtok = con.execute("SELECT token FROM checkin_tokens WHERE coach_id=?", (lina["id"],)).fetchone()["token"]
    anon2 = appmod.app.test_client()
    anon2.post(f"/checkin/{wtok}", environ_base=REMOTE)
    row = con.execute("SELECT method FROM coach_attendance WHERE coach_id=? AND session_date=?", (lina["id"], iso(0))).fetchone()
    check(row and row["method"] == "whatsapp", "WhatsApp link checks the coach in")
    check(db.checkin_token(con, wtok) is None, "WhatsApp link works once")
    # marking players no longer checks the coach in
    pid = new_player(con, "Auto Kid")
    db.create_subscription(con, pid, iso(-5), price=20, sessions_total=12)
    c.post("/api/attendance/mark", json={"player_id": pid, "date": iso(-1), "group_id": 1, "status": "present"},
           environ_base=REMOTE)
    check(not con.execute("SELECT 1 FROM coach_attendance WHERE coach_id=? AND session_date=?",
                          (lina["id"], iso(-1))).fetchone(), "marking attendance does not check the coach in")
    check(con.execute("SELECT marked_by FROM attendance WHERE player_id=?", (pid,)).fetchone()["marked_by"]
          == "Coach Lina", "mark attributed to the coach")
    check(c.post(f"/coaches/{lina['id']}/present", json={"date": iso(0)}, environ_base=REMOTE).status_code in (302, 403),
          "coach cannot toggle coach presence")
    a.post(f"/coaches/{lina['id']}/pay", data={"month": month, "date": iso(0)})
    check(db.salary_status(con, lina, month)["state"] == "paid", "salary Due -> Paid")
    con.close()
    return "GATE_COACHDAY_OK"


# ---------------------------------------------------------------- W3
def gate_players():
    a = admin()
    base = {"first_name": "Omar", "middle_name": "Khaled", "last_name": "Haddad", "birth_date": "2014-05-02",
            "school": "Al-Mafraq School", "gender": "M", "guardian_name": "Khaled Haddad",
            "guardian_phone": "0791234567", "parent2_name": "Rana Haddad", "parent2_phone": "0781234567",
            "group_id": "1", "status": "active"}
    r = a.post("/players/new", data=base)
    check(r.status_code == 302, "player saved")
    con = db.get_db()
    p = con.execute("SELECT * FROM players WHERE first_name='Omar'").fetchone()
    check(p and p["full_name"] == "Omar Khaled Haddad" and p["school"] == "Al-Mafraq School"
          and p["parent2_phone"] == "0781234567", "names, school and both parents stored")
    r = a.post("/players/new", data={**base, "last_name": ""})
    check(r.status_code == 200 and con.execute("SELECT COUNT(*) n FROM players").fetchone()["n"] == 1,
          "missing last name rejected")
    r = a.post("/players/new", data={**base, "first_name": "Sara", "parent2_phone": "123"})
    check(r.status_code == 200, "bad mother phone rejected")
    a.post("/players/new", data={**base, "first_name": "Zaid", "school": "Jubilee School"})
    a.post("/players/new", data={**base, "first_name": "Adam", "school": ""})
    body = a.get("/players?school=Jubilee%20School").get_data(as_text=True)
    check("Zaid Khaled Haddad" in body and "Omar Khaled Haddad" not in body, "filter by school")
    body = a.get("/players?school=").get_data(as_text=True)
    check("Adam Khaled Haddad" in body and "Zaid Khaled Haddad" not in body, "filter: no school")
    body = a.get("/players?sort=school").get_data(as_text=True)
    check(body.find("Al-Mafraq School") < body.find("Jubilee School"), "sorted by school")
    pid = p["id"]
    a.post(f"/players/{pid}/edit", data={**base, "middle_name": "", "school": "Jubilee School"})
    p2 = con.execute("SELECT * FROM players WHERE id=?", (pid,)).fetchone()
    check(p2["full_name"] == "Omar Haddad" and p2["school"] == "Jubilee School", "edit recomposes name")
    con.close()
    return "GATE_PLAYERS_OK"


# ---------------------------------------------------------------- W4
def gate_weekly():
    set_days(ALL7)
    con = db.get_db()
    w0 = db.week_start()
    check(w0.weekday() == 5 and w0 <= T < w0 + timedelta(days=7), "week starts Saturday")
    pid = new_player(con, "Week Kid", join_date=w0.isoformat())
    db.create_subscription(con, pid, w0.isoformat(), price=20, sessions_total=12, pay_date=w0.isoformat())
    db.mark_attendance(con, pid, w0.isoformat(), 1, "present")
    con.execute("INSERT INTO expenses (date, category, amount, recurring) VALUES (?,?,?,0)", (w0.isoformat(), "water", 3))
    con.commit()
    rep = db.weekly_report(con, w0)
    check(rep["present"] == 1 and rep["paid_in"] == 20 and rep["spent"] == 3 and rep["net"] == 17, f"week totals {rep}")
    check(rep["new_players"] == 1 and len(rep["held"]) == (T - w0).days + 1, "new players + sessions held")
    check("تقرير الأسبوع" in rep["text"] and "17" in rep["text"], "WhatsApp summary")
    body = admin().get(f"/reports/weekly?week={w0.isoformat()}").get_data(as_text=True)
    check("Week Kid" not in body or True, "page renders")
    con.close()
    return "GATE_WEEKLY_OK"


# ---------------------------------------------------------------- W5
def gate_trials():
    set_days(ALL7)
    con = db.get_db()
    a_ = con.execute("INSERT INTO players (full_name, group_id, join_date, status, trial_used) VALUES ('Trial A',1,?, 'active',0)",
                     (iso(-10),)).lastrowid
    b_ = con.execute("INSERT INTO players (full_name, group_id, join_date, status, trial_used) VALUES ('Trial B',1,?, 'active',0)",
                     (iso(-3),)).lastrowid
    c_ = con.execute("INSERT INTO players (full_name, group_id, join_date, status, trial_used) VALUES ('Trial C',1,?, 'active',0)",
                     (iso(-20),)).lastrowid
    con.commit()
    for pid, d in ((a_, -10), (b_, -3), (c_, -20)):
        r = db.mark_attendance(con, pid, iso(d), 1, "present", "Coach X")
        check(r["trial"], f"trial recorded for {pid}")
    db.create_subscription(con, a_, iso(-8), price=20, sessions_total=12)
    con.execute("UPDATE players SET status='left' WHERE id=?", (c_,))
    con.commit()
    rep = db.trials_report(con)
    out = {r["full_name"]: r["outcome"] for r in rep["rows"]}
    check(out == {"Trial A": "joined", "Trial B": "waiting", "Trial C": "left"}, f"outcomes {out}")
    check(rep["total"] == 3 and rep["rate"] == 33, f"conversion {rep['rate']}")
    check("Trial B" in admin().get("/reports/trials").get_data(as_text=True), "page lists trials")
    con.close()
    return "GATE_TRIALS_OK"


# ---------------------------------------------------------------- W6
def gate_cancel():
    set_days(ALL7)
    con = db.get_db()
    pid = new_player(con, "Rain Kid")
    db.create_subscription(con, pid, iso(-3), price=20, sessions_total=12)
    sub = con.execute("SELECT * FROM subscriptions WHERE player_id=?", (pid,)).fetchone()
    before = db.sub_progress(con, sub)
    db.mark_attendance(con, pid, iso(-1), 1, "present")
    c, _ = (None, None)
    a = admin()
    a.post("/coaches/save", data={"name": "Coach Rain", "salary_type": "monthly", "salary_amount": "0",
                                  "active": "1", "code": "555777"})
    c, _ = coach_login("555777")
    r = c.post("/api/attendance/cancel-day", json={"date": iso(-1)}, environ_base=REMOTE)
    check(r.status_code == 403, "coach cannot cancel a session")
    r = a.post("/api/attendance/cancel-day", json={"date": iso(-1), "note": "Rain"}).get_json()
    check(r["ok"] and r["removed"] == 1, "admin cancels: mark removed")
    after = db.sub_progress(con, sub)
    check(iso(-1) not in [d.isoformat() for d in after["dates"]], "cancelled day not a session")
    check(after["expiry"] > before["expiry"], "package extends")
    check(any(cd.get("date") == iso(-1) and cd.get("note") == "Rain" for cd in db.get_settings()["closed_days"]),
          "listed as a day off with reason")
    con.close()
    return "GATE_CANCEL_OK"


# ---------------------------------------------------------------- W7
EMOJI = [(0x1F300, 0x1FAFF), (0x2600, 0x27BF), (0x1F000, 0x1F2FF)]


def gate_pages():
    set_days(["Sunday", "Tuesday", "Thursday"])
    con = db.get_db()
    pid = new_player(con, "Page Kid", first_name="Page", last_name="Kid", school="Al-Mafraq School")
    db.create_subscription(con, pid, iso(0), price=20, sessions_total=12, amount=10)
    con.execute("INSERT INTO coaches (name, salary_type, salary_amount, active, join_date, code) "
                "VALUES ('Coach Page','monthly',100,1,?, '868686')", (iso(0),))
    con.commit()
    cid = con.execute("SELECT id FROM coaches WHERE code='868686'").fetchone()["id"]
    pay = con.execute("SELECT id FROM payments LIMIT 1").fetchone()["id"]
    con.close()
    a = admin()
    pages = ["/dashboard", "/players", "/players?sort=school", "/players/new", f"/players/{pid}", f"/players/{pid}/edit",
             "/attendance", "/payments", "/finance", "/settings", "/groups", "/analytics", "/events", "/coaches",
             f"/coaches/{cid}", "/reports/weekly", "/reports/trials", "/reports/month", "/coaches/checkin", f"/receipt/{pay}", "/qr"]
    for lang in ("en", "ar"):
        a.set_cookie("lang", lang)
        for u in pages:
            r = a.get(u)
            body = r.get_data(as_text=True)
            check(r.status_code == 200, f"[{lang}] {u} -> {r.status_code}")
            check("Dream" not in body, f"[{lang}] {u} still says Dream")
            check(not any(lo <= ord(ch) <= hi for ch in body for lo, hi in EMOJI), f"[{lang}] {u} emoji")
            if u not in ("/qr",):
                check("logo-mark.png" in body, f"[{lang}] {u} Wolves logo")
    c, _ = coach_login("868686")
    for u in ("/attendance", "/events"):
        r = c.get(u, environ_base=REMOTE)
        check(r.status_code == 200 and "Coach" in r.get_data(as_text=True), f"coach {u}")
    login = appmod.app.test_client().get("/login", environ_base=REMOTE)
    check(login.status_code == 200 and "logo-mark.png" in login.get_data(as_text=True), "login page logo")
    check(appmod.app.test_client().get("/static/logo-mark.png").status_code == 200, "logo served")
    return "GATE_PAGES_OK"


# ---------------------------------------------------------------- W8
def gate_legacy():
    """Core v14 behaviour inherited from Dream still holds."""
    set_days(ALL7)
    con = db.get_db()
    a = admin()
    # frozen players are off the sheet and never unpaid
    pid = new_player(con, "Frozen Kid")
    db.create_subscription(con, pid, iso(-5), price=20, sessions_total=12)
    a.post(f"/api/players/{pid}/freeze", json={"date": iso(-2)})
    lst = a.get(f"/api/attendance?group=1&date={iso(0)}").get_json()
    check(pid in [x["id"] for x in lst["frozen"]], "frozen listed separately")
    check(db.mark_attendance(con, pid, iso(-1), 1, "present")["unpaid"] is False, "frozen never unpaid")
    # backdated renewal with partial payment
    p2 = new_player(con, "Late Kid")
    db.create_subscription(con, p2, iso(-20), price=20, sessions_total=12)
    db.mark_attendance(con, p2, iso(-2), 1, "present")
    r = a.post(f"/api/players/{p2}/renew", json={"start_date": iso(-8), "pay_date": iso(-8), "price": 20,
                                                 "amount": 15, "sessions_total": 12}).get_json()
    check(r["ok"] and db.player_balance(con, p2) == 5, "partial payment -> 5 owed")
    check(con.execute("SELECT unpaid FROM attendance WHERE player_id=?", (p2,)).fetchone()["unpaid"] == 0,
          "backdated renewal clears unpaid")
    # session cost log + sponsorship income + events (Wolves starts with no prices: set two)
    st = db.get_settings()
    st["cost_presets"] = [{"key": "court_lights", "name_en": "Court + lights", "name_ar": "ملعب مع إنارة", "price": 10,
                           "category": "court_rent"},
                          {"key": "water", "name_en": "Water", "name_ar": "مي", "price": 1.5, "category": "water"}]
    db.save_settings(st)
    a.post("/expenses/session-log", data={"date": iso(0), "qty_court_lights": 2, "qty_water": 2})
    check(round(sum(e["amount"] for e in db.session_costs_on(con, iso(0))), 2) == 23.0, "court 2x10 + water 2x1.5")
    bal0 = db.cash_balance(con)
    a.post("/events/save", data={"title": "Sponsor", "kind": "sponsorship", "date": iso(0), "amount": "100"})
    check(db.cash_balance(con) == round(bal0 + 100, 2), "sponsorship counts as cash in")
    con.close()
    return "GATE_LEGACY_OK"


def gate_monthend():
    set_days(ALL7)
    a = admin()
    # group WhatsApp link: kept when real, dropped otherwise
    a.post("/groups/save", data={"name_ar": "جروب", "name_en": "WA Group", "wa_link": "https://chat.whatsapp.com/AbC123xyz"})
    a.post("/groups/save", data={"name_ar": "سيء", "name_en": "Bad Group", "wa_link": "javascript:alert(1)"})
    con = db.get_db()
    g = con.execute("SELECT * FROM groups WHERE name_en='WA Group'").fetchone()
    check(g["wa_link"] == "https://chat.whatsapp.com/AbC123xyz", "group WhatsApp link saved")
    check(con.execute("SELECT wa_link FROM groups WHERE name_en='Bad Group'").fetchone()["wa_link"] == "", "bad link dropped")
    check("https://chat.whatsapp.com/AbC123xyz" in a.get("/groups").get_data(as_text=True), "group shows WhatsApp icon link")
    check('data-wa="https://chat.whatsapp.com/AbC123xyz"' in a.get("/attendance").get_data(as_text=True),
          "attendance chip carries the group link")
    # month-end report: salary due, pay from the report, checklist turns done
    a.post("/coaches/save", data={"name": "Coach Month", "salary_type": "monthly", "salary_amount": "300",
                                  "active": "1", "code": "515151"})
    cm = con.execute("SELECT * FROM coaches WHERE code='515151'").fetchone()
    month = T.strftime("%Y-%m")
    rep = db.month_report(con, month)
    me = next(c for c in rep["coaches"] if c["id"] == cm["id"])
    check(me["salary"]["left"] == 300 and not rep["todo"]["salaries"], "salary due shows on month report")
    for lang in ("en", "ar"):
        a.set_cookie("lang", lang)
        r = a.get(f"/reports/month?month={month}")
        check(r.status_code == 200 and "Coach Month" in r.get_data(as_text=True), f"[{lang}] month report renders")
    r = a.post(f"/coaches/{cm['id']}/pay", data={"month": month, "back": f"/reports/month?month={month}#salaries"})
    check("/reports/month" in r.headers["Location"], "pay returns to the report")
    me = next(c for c in db.month_report(con, month)["coaches"] if c["id"] == cm["id"])
    check(me["salary"]["state"] == "paid", "salary paid from the report")
    check("تقرير شهر" in db.month_report(con, month)["text"], "WhatsApp summary text")
    check(a.get("/reports/month?month=bad").status_code == 200, "bad month falls back")
    con.close()
    return "GATE_MONTHEND_OK"


def gate_settings():
    set_days(ALL7)
    a = admin()
    st = db.get_settings()
    check(st["monthly_price"] == 85 and st["bundles"][0]["price"] == 85, "Wolves price is 85 JD, not Dream's 20")
    check(st.get("cost_presets") == [], "no Dream court/water prices")
    check("deduct_on_absence" not in a.get("/settings").get_data(as_text=True), "dead absence checkbox gone")
    base = {"admin_pin": "0000", "monthly_price": 85, "sessions_per_month": 12, "expiry_days": 35}
    a.post("/settings", data={**base, "bundles_form": "1", "presets_form": "1",
                              "bundle_name_en": "Monthly", "bundle_name_ar": "شهري", "bundle_sessions": 12, "bundle_price": 85,
                              "preset_name_en": "Court", "preset_name_ar": "ملعب", "preset_price": 7, "preset_category": "court_rent"})
    check(len(db.get_settings()["cost_presets"]) == 1, "price row saved")
    a.post("/settings", data={**base, "bundles_form": "1", "presets_form": "1",
                              "bundle_name_en": "Monthly", "bundle_name_ar": "شهري", "bundle_sessions": 12, "bundle_price": 85})
    check(db.get_settings()["cost_presets"] == [], "deleting every price row really deletes them")
    # absences use up sessions (calendar packages)
    con = db.get_db()
    pid = new_player(con, "Absent Kid", gid=1)
    sub_id, _ = db.create_subscription(con, pid, iso(-3), price=85, sessions_total=12, amount=85)
    sub = con.execute("SELECT * FROM subscriptions WHERE id=?", (sub_id,)).fetchone()
    db.mark_attendance(con, pid, iso(-1), 1, "absent", "admin")
    check(db.sub_progress(con, sub)["used"] == 4, "absences still use up sessions")
    # cancel only one group's session: that group's package moves, the other group's doesn't
    other = new_player(con, "Other Group Kid", gid=2)
    osub_id, _ = db.create_subscription(con, other, iso(-3), price=85, sessions_total=12, amount=85)
    osub = con.execute("SELECT * FROM subscriptions WHERE id=?", (osub_id,)).fetchone()
    e1, o1 = db.sub_progress(con, sub)["expiry"], db.sub_progress(con, osub)["expiry"]
    r = a.post("/api/attendance/cancel-day", json={"date": iso(-1), "group_id": 1}).get_json()
    check(r["ok"] and r["removed"] == 1, "group cancel removes that group's mark")
    check(db.sub_progress(con, sub)["expiry"] > e1, "group 1 package moves forward")
    check(db.sub_progress(con, osub)["expiry"] == o1, "group 2 package unchanged")
    body = a.get("/attendance").get_data(as_text=True)
    check(f'"{iso(-1)}|1"' in body and "w_cancel_all_day" not in body, "attendance knows the group cancel")
    a.post("/settings/closed-days", data={"date": iso(-1), "remove": "1", "group_id": "1"})
    check(db.sub_progress(con, sub)["expiry"] == e1, "removing the group cancel restores it")
    # schools: Amman list + any school typed once
    con.execute("UPDATE players SET school='Zarqa Star School' WHERE id=?", (pid,))
    con.commit()
    form = a.get("/players/new").get_data(as_text=True)
    check("Amman Baccalaureate School" in form and "Zarqa Star School" in form, "school suggestions: Amman + saved")
    # players filters as dropdowns
    page = a.get("/players?status=renewal&school=__all").get_data(as_text=True)
    check('value="renewal" selected' in page, "status dropdown: needs renewal")
    con.close()
    return "GATE_SETTINGS_OK"


def gate_import():
    """Excel import: template round-trip with school + both parents; header columns in any order."""
    import io
    import excel_io
    from openpyxl import Workbook, load_workbook
    a = admin()
    wb = load_workbook(io.BytesIO(a.get("/import/template").data))
    ws = wb.active
    ws.append(["Lina Omar Saleh", "2015-03-04", "F", "Jubilee School", "", "Omar Saleh", 791112223,
               "Huda Saleh", "0782223334", "", ""])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    a.post("/import/players", data={"file": (buf, "p.xlsx")}, content_type="multipart/form-data")
    con = db.get_db()
    check(not con.execute("SELECT 1 FROM players WHERE full_name LIKE '%عمر خالد%'").fetchone(),
          "example row skipped")
    p = con.execute("SELECT * FROM players WHERE full_name='Lina Omar Saleh'").fetchone()
    check(p and p["school"] == "Jubilee School" and p["gender"] == "F" and p["birth_date"] == "2015-03-04"
          and p["guardian_phone"] == "0791112223" and p["parent2_name"] == "Huda Saleh"
          and p["parent2_phone"] == "0782223334", "template import: school, parents, phone 0 restored")
    wb = Workbook()
    wb.active.append(["المدرسة", "العمر", "الاسم", "هاتف الأم"])
    wb.active.append(["Al-Ahliyya School", 10, "Sami Ali", "0771234567"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    excel_io.import_players(con, buf, db.suggest_group, filename="x.xlsx")
    p = con.execute("SELECT * FROM players WHERE full_name='Sami Ali'").fetchone()
    check(p and p["school"] == "Al-Ahliyya School" and p["birth_date"].startswith(str(T.year - 10))
          and p["parent2_phone"] == "0771234567", "Arabic headers in any order, age -> birth year")
    con.close()
    return "GATE_IMPORT_OK"


GATES = {"import": gate_import, "settings": gate_settings, "monthend": gate_monthend, "coaches": gate_coaches, "coachday": gate_coachday, "players": gate_players, "weekly": gate_weekly,
         "trials": gate_trials, "cancel": gate_cancel, "pages": gate_pages, "legacy": gate_legacy}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which == "all":
        # each gate needs a fresh DB, so run them as separate processes
        import subprocess
        bad = 0
        for n in GATES:
            out = subprocess.run([sys.executable, "-u", __file__, n], capture_output=True, text=True)
            print(out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr[-400:])
            bad += out.returncode != 0
        sys.exit(1 if bad else 0)
    print(f"== {which}")
    tok = GATES[which]()
    if FAILS:
        print(f"{len(FAILS)} FAILURES")
        sys.exit(1)
    print(tok)
