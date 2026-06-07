import os, json, smtplib, threading, time
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static')

# ── Konfigurim ──────────────────────────────────────────
SENDER_EMAIL   = "kalendaripunes1@gmail.com"
SENDER_PASS    = "indj btxr urou svtv"
RECEIVER_EMAIL = "orinesa24@gmail.com"
SEND_HOUR      = 21   # ora 21:00
DATA_FILE      = "data.json"
# ────────────────────────────────────────────────────────

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_base_url():
    return os.environ.get("BASE_URL", "http://localhost:5000")

def send_email():
    today = date.today().strftime("%Y-%m-%d")
    day_sq = ["E Hënë","E Martë","E Mërkurë","E Enjte","E Premte","E Shtunë","E Diel"]
    weekday = day_sq[date.today().weekday()]
    base = get_base_url()

    yes_link = f"{base}/pergjigje?data={today}&v=po"
    no_link  = f"{base}/pergjigje?data={today}&v=jo"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{ margin:0; padding:0; background:#04080f; font-family:'Courier New',monospace; }}
  .wrap {{ max-width:480px; margin:0 auto; padding:30px 20px; }}
  .card {{ background:#080f1a; border:1px solid #0e2030; border-radius:14px; overflow:hidden;
           box-shadow:0 0 30px #00d4ff15; }}
  .header {{ background:#060d18; padding:24px; text-align:center; border-bottom:1px solid #0e2030; }}
  .title {{ color:#00d4ff; font-size:22px; font-weight:900; letter-spacing:.2em;
            text-shadow:0 0 10px #00d4ff; text-transform:uppercase; margin-bottom:6px; }}
  .sub {{ color:#2a4a5a; font-size:11px; letter-spacing:.3em; }}
  .body {{ padding:28px 24px; text-align:center; }}
  .question {{ color:#8bb8cc; font-size:16px; margin-bottom:8px; }}
  .date-tag {{ color:#00ffcc; font-size:13px; letter-spacing:.15em;
               text-shadow:0 0 8px #00ffcc; margin-bottom:28px; }}
  .btns {{ display:flex; gap:14px; justify-content:center; }}
  .btn {{ display:inline-block; padding:14px 32px; border-radius:8px; text-decoration:none;
          font-size:16px; font-weight:900; letter-spacing:.15em; text-transform:uppercase;
          border:2px solid; transition:all .2s; }}
  .yes {{ color:#39ff14; border-color:#39ff14; background:#39ff1408;
          box-shadow:0 0 16px #39ff1444; }}
  .no  {{ color:#ff3860; border-color:#ff3860; background:#ff386008;
          box-shadow:0 0 16px #ff386044; }}
  .footer {{ padding:16px; text-align:center; border-top:1px solid #0e2030; }}
  .foot-text {{ color:#1a3a4a; font-size:10px; letter-spacing:.2em; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="card">
    <div class="header">
      <div class="title">◈ Kalendari i Punës ◈</div>
      <div class="sub">NJOFTIM DITOR · {weekday.upper()}</div>
    </div>
    <div class="body">
      <div class="question">A ka punuar babi sot?</div>
      <div class="date-tag">▸ {date.today().strftime("%d / %m / %Y")} ◂</div>
      <div class="btns">
        <a href="{yes_link}" class="btn yes">✓ PO</a>
        <a href="{no_link}"  class="btn no">✗ JO</a>
      </div>
    </div>
    <div class="footer">
      <div class="foot-text">◈ KALENDARI I BABAIT ◈</div>
    </div>
  </div>
</div>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📅 A ka punuar babi sot? · {date.today().strftime('%d/%m/%Y')}"
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(SENDER_EMAIL, SENDER_PASS)
            s.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print(f"[{datetime.now()}] Email dërguar!")
    except Exception as e:
        print(f"[{datetime.now()}] Gabim email: {e}")

# ── Scheduler ───────────────────────────────────────────
def scheduler():
    while True:
        now = datetime.now()
        if now.hour == SEND_HOUR and now.minute == 0:
            send_email()
            time.sleep(61)  # avoid double-send
        time.sleep(30)

# ── Routes ──────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/pergjigje")
def pergjigje():
    d = request.args.get("data")   # "2025-06-07"
    v = request.args.get("v")      # "po" ose "jo"
    if not d or not v:
        return "Parametra mungojnë", 400

    data = load_data()
    data[d] = 1 if v == "po" else -1
    save_data(data)

    emoj = "✅" if v == "po" else "❌"
    fjale = "PO — Babi ka punuar!" if v == "po" else "JO — Babi nuk ka punuar."
    ngjyra = "#39ff14" if v == "po" else "#ff3860"

    html = f"""<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="3;url=/">
<style>
  body{{margin:0;background:#04080f;display:flex;align-items:center;
       justify-content:center;min-height:100vh;font-family:'Courier New',monospace;}}
  .box{{background:#080f1a;border:1px solid #0e2030;border-radius:14px;
        padding:40px 32px;text-align:center;max-width:340px;
        box-shadow:0 0 30px {ngjyra}22;}}
  .emoj{{font-size:52px;margin-bottom:16px;}}
  .msg{{color:{ngjyra};font-size:18px;font-weight:900;letter-spacing:.1em;
        text-shadow:0 0 10px {ngjyra};margin-bottom:12px;}}
  .sub{{color:#2a4a5a;font-size:11px;letter-spacing:.2em;}}
</style>
</head>
<body>
<div class="box">
  <div class="emoj">{emoj}</div>
  <div class="msg">{fjale}</div>
  <div class="sub">PO KTHEHEM TE KALENDARI...</div>
</div>
</body></html>"""
    return html

@app.route("/api/data")
def api_data():
    return jsonify(load_data())

@app.route("/api/set", methods=["POST"])
def api_set():
    body = request.get_json()
    d, v = body.get("date"), body.get("value")
    if not d: return jsonify({"error":"no date"}), 400
    data = load_data()
    if v == 0:
        data.pop(d, None)
    else:
        data[d] = v
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/send-test", methods=["POST"])
def send_test():
    threading.Thread(target=send_email).start()
    return jsonify({"ok": True})

if __name__ == "__main__":
    threading.Thread(target=scheduler, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
