from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-me-to-a-random-secret-string-later"
import os
DB = "/tmp/orders.db" if os.environ.get("VERCEL") else "orders.db"

# ---------- Business config ----------
WHATSAPP_NUMBER = "254790801646"   
ADMIN_PASSWORD = "souls2025"       

# ---------- Pricing ----------
BOXES = {
    "6":  {"price": 80,  "label": "Box of 6"},
    "12": {"price": 150, "label": "Box of 12"},
    "18": {"price": 200, "label": "Box of 18"},
}

ZONES = {
    "roysambu":   {"name": "Roysambu",        "fee": 100},
    "kasarani":   {"name": "Kasarani",        "fee": 150},
    "zimmerman":  {"name": "Zimmerman",       "fee": 150},
    "kahawa":     {"name": "Kahawa Wendani",  "fee": 200},
    "thika-road": {"name": "Thika Road",      "fee": 200},
    "eastleigh":  {"name": "Eastleigh",       "fee": 250},
    "westlands":  {"name": "Westlands",       "fee": 300},
    "cbd":        {"name": "Nairobi CBD",     "fee": 300},
    "parklands":  {"name": "Parklands",       "fee": 300},
    "kilimani":   {"name": "Kilimani",        "fee": 350},
    "other":      {"name": "Other (call us)", "fee": 0},
}

# ---------- Database ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()


    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            box_size TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            zone TEXT NOT NULL,
            address TEXT,
            notes TEXT,
            total INTEGER NOT NULL,
            status TEXT DEFAULT 'new',
            created_at TEXT NOT NULL
        )
    """)

    # Check if 'status' column exists; if not, add it
    c.execute("PRAGMA table_info(orders)")
    columns = [row[1] for row in c.fetchall()]
    if "status" not in columns:
        c.execute("ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'new'")
        # Set existing orders to 'new'
        c.execute("UPDATE orders SET status = 'new' WHERE status IS NULL")

    conn.commit()
    conn.close()


init_db()

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("index.html", boxes=BOXES, zones=ZONES)

@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        name    = request.form["name"].strip()
        phone   = request.form["phone"].strip()
        box     = request.form["box"]
        qty     = int(request.form.get("quantity", 1))
        zone    = request.form["zone"]
        address = request.form.get("address", "").strip()
        notes   = request.form.get("notes", "").strip()

        if box not in BOXES or zone not in ZONES:
            return "Invalid order", 400

        subtotal = BOXES[box]["price"] * qty
        delivery = ZONES[zone]["fee"]
        total    = subtotal + delivery

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("""
            INSERT INTO orders
              (name, phone, box_size, quantity, zone, address, notes, total, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, phone, box, qty, zone, address, notes, total,
              datetime.now().isoformat()))
        order_id = c.lastrowid
        conn.commit()
        conn.close()

        return redirect(url_for("success", order_id=order_id))

    return render_template("order.html", boxes=BOXES, zones=ZONES)

@app.route("/success/<int:order_id>")
def success(order_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return "Order not found", 404

    order = {
        "id": row[0], "name": row[1], "phone": row[2],
        "box": BOXES[row[3]]["label"], "quantity": row[4],
        "zone": ZONES[row[5]]["name"],
        "address": row[6], "notes": row[7], "total": row[8],
    }

    msg = (
        f"Hi Soul's Treat! I just placed order #{order['id']}%0A"
        f"Name: {order['name']}%0A"
        f"Box: {order['box']} x{order['quantity']}%0A"
        f"Zone: {order['zone']}%0A"
        f"Address: {order['address']}%0A"
        f"Total: KSH {order['total']}"
    )
    whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={msg}"

    return render_template("success.html", order=order, whatsapp_url=whatsapp_url)

# ---------- Admin ----------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        pw = request.form.get("password", "")
        if pw == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        return render_template("admin_login.html", error="Wrong password")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    # Search + filter params
    search = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "all")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    query = "SELECT * FROM orders WHERE 1=1"
    params = []

    if status_filter in ("new", "delivered", "cancelled"):
        query += " AND status = ?"
        params.append(status_filter)

    if search:
        query += " AND (name LIKE ? OR phone LIKE ? OR address LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like])

    query += " ORDER BY id DESC"
    c.execute(query, params)
    rows = c.fetchall()

    # Stats (across ALL orders, not filtered)
    c.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM orders")
    total_count, total_revenue = c.fetchone()

    c.execute("SELECT COUNT(*) FROM orders WHERE status = 'new'")
    new_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM orders WHERE status = 'delivered'")
    delivered_count = c.fetchone()[0]

    c.execute("SELECT box_size, COUNT(*) as cnt FROM orders GROUP BY box_size ORDER BY cnt DESC LIMIT 1")
    top_row = c.fetchone()
    top_box = BOXES.get(top_row[0], {}).get("label", "—") if top_row else "—"

    conn.close()

    orders = []
    for r in rows:
        orders.append({
            "id": r[0], "name": r[1], "phone": r[2],
            "box": BOXES.get(r[3], {}).get("label", r[3]),
            "quantity": r[4],
            "zone": ZONES.get(r[5], {}).get("name", r[5]),
            "address": r[6], "notes": r[7],
            "total": r[8],
            "status": r[9],
            "created_at": r[10][:19].replace("T", " "),
        })

    return render_template(
        "admin.html",
        orders=orders,
        search=search,
        status_filter=status_filter,
        stats={
            "revenue": total_revenue,
            "count": total_count,
            "new_count": new_count,
            "delivered_count": delivered_count,
            "top_box": top_box,
        }
    )


@app.route("/admin/order/<int:order_id>/status/<new_status>")
def admin_set_status(order_id, new_status):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    if new_status not in ("new", "delivered", "cancelled"):
        return "Invalid status", 400

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))

    # Compute stats
    total_revenue = sum(r[8] for r in rows)
    order_count   = len(rows)

    # Most popular box size
    box_counts = {}
    for r in rows:
        box_counts[r[3]] = box_counts.get(r[3], 0) + 1
    top_box = max(box_counts, key=box_counts.get) if box_counts else "—"
    top_box_label = BOXES.get(top_box, {}).get("label", "—")

    orders = []
    for r in rows:
        orders.append({
            "id": r[0], "name": r[1], "phone": r[2],
            "box": BOXES.get(r[3], {}).get("label", r[3]),
            "quantity": r[4],
            "zone": ZONES.get(r[5], {}).get("name", r[5]),
            "address": r[6], "notes": r[7],
            "total": r[8],
            "created_at": r[9][:19].replace("T", " "),
        })

    return render_template(
        "admin.html",
        orders=orders,
        stats={
            "revenue": total_revenue,
            "count": order_count,
            "top_box": top_box_label,
        }
    )

if __name__ == "__main__":
    import os
    # In production, PORT is set by the hosting platform.
    # Locally, default to 8000.
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug, host="0.0.0.0", port=port)