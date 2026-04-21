import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "agri_insta_dev_secret")
ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(ROOT, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERS_FILE  = os.path.join(ROOT, "users.json")
POSTS_FILE  = os.path.join(ROOT, "posts.json")
ORDERS_FILE = os.path.join(ROOT, "orders.json")
CHATS_FILE  = os.path.join(ROOT, "chats.json")
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "gif"}

def ensure_json(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)

def read_json(path):
    ensure_json(path, [])
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

ensure_json(USERS_FILE, [])
ensure_json(POSTS_FILE, [])
ensure_json(ORDERS_FILE, [])
ensure_json(CHATS_FILE, [])

def find_user_by_username(username):
    for u in read_json(USERS_FILE):
        if u.get("username") == username:
            return u
    return None

def find_user_by_email(email):
    for u in read_json(USERS_FILE):
        if u.get("email") == email:
            return u
    return None

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.route("/")
def index():
    if session.get("username"):
        return redirect(url_for("home"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname     = request.form.get("fullname","").strip()
        username     = request.form.get("username","").strip()
        email        = request.form.get("email","").strip().lower()
        password     = request.form.get("password","")
        mobile       = request.form.get("mobile","").strip()
        organization = request.form.get("organization","").strip().lower()
        if not (username and email and password and organization):
            flash("Please fill required fields","danger")
            return redirect(url_for("register"))
        if find_user_by_username(username) or find_user_by_email(email):
            flash("User already exists","warning")
            return redirect(url_for("register"))
        profile_pic = None
        file = request.files.get("profile_pic")
        if file and allowed_file(file.filename):
            safe = secure_filename(file.filename)
            profile_pic = f"{username}_profile_{safe}"
            file.save(os.path.join(UPLOAD_FOLDER, profile_pic))
        users = read_json(USERS_FILE)
        users.append({
            "id": str(uuid.uuid4()), "fullname": fullname, "username": username,
            "email": email, "password": generate_password_hash(password),
            "mobile": mobile, "organization": organization,
            "profile_pic": profile_pic, "bio": "", "location": "",
            "created_at": str(datetime.utcnow())
        })
        write_json(USERS_FILE, users)
        session["username"] = username
        session["role"]     = organization
        flash("Registered successfully — welcome!","success")
        return redirect(url_for("home"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ident    = request.form.get("username","").strip()
        password = request.form.get("password","")
        user = find_user_by_username(ident) or find_user_by_email(ident)
        if user and check_password_hash(user.get("password",""), password):
            session["username"] = user["username"]
            session["role"]     = user.get("organization","")
            flash("Logged in successfully","success")
            return redirect(url_for("home"))
        flash("Invalid credentials","danger")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("role", None)
    flash("Logged out","info")
    return redirect(url_for("index"))

@app.route("/home")
def home():
    if not session.get("username"):
        return redirect(url_for("login"))
    q           = request.args.get("q","").strip().lower()
    filter_role = request.args.get("role","").strip().lower()
    posts       = read_json(POSTS_FILE)

    def matches(p):
        if q:
            text = (p.get("caption","")+" "+p.get("title","")+" "+p.get("username","")+" "+p.get("product","")).lower()
            if q not in text:
                return False
        if filter_role:
            u = find_user_by_username(p.get("username"))
            if not u or u.get("organization","").lower() != filter_role:
                return False
        return True

    posts_filtered = [p for p in sorted(posts, key=lambda x: x.get("created_at",""), reverse=True) if matches(p)]
    for p in posts_filtered:
        u = find_user_by_username(p.get("username"))
        p["_role"]        = u.get("organization","") if u else ""
        p["_profile_pic"] = u.get("profile_pic")     if u else None
    return render_template("home.html", posts=posts_filtered, q=q, filter_role=filter_role)

@app.route("/post/create", methods=["POST"])
def create_post():
    if not session.get("username"):
        flash("Login required","danger")
        return redirect(url_for("login"))
    username = session["username"]
    title    = request.form.get("title","").strip()
    caption  = request.form.get("caption","").strip()
    product  = request.form.get("product","").strip()
    quantity = request.form.get("quantity","").strip()
    price    = request.form.get("price","").strip()
    unit     = request.form.get("unit","kg").strip()
    file     = request.files.get("image")
    filename = None
    if file and allowed_file(file.filename):
        safe     = secure_filename(file.filename)
        filename = f"{username}_{int(datetime.utcnow().timestamp())}_{safe}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    posts = read_json(POSTS_FILE)
    posts.append({
        "id": str(uuid.uuid4()), "username": username, "title": title,
        "caption": caption, "product": product, "quantity": quantity,
        "price": price, "unit": unit, "image": filename,
        "likes": [], "created_at": str(datetime.utcnow())
    })
    write_json(POSTS_FILE, posts)
    flash("Post uploaded","success")
    return redirect(url_for("home"))

@app.route("/post/<post_id>/like", methods=["POST"])
def like_post(post_id):
    if not session.get("username"):
        return jsonify({"error":"not logged in"}), 401
    username = session["username"]
    posts    = read_json(POSTS_FILE)
    post     = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error":"not found"}), 404
    likes = post.get("likes", [])
    if username in likes:
        likes.remove(username)
        liked = False
    else:
        likes.append(username)
        liked = True
    post["likes"] = likes
    write_json(POSTS_FILE, posts)
    return jsonify({"liked": liked, "count": len(likes)})

@app.route('/profile/<username>')
def profile(username):
    user = find_user_by_username(username)
    if not user:
        flash("User not found","warning")
        return redirect(url_for("home"))
    posts      = read_json(POSTS_FILE)
    user_posts = [p for p in posts if p.get("username") == username]
    is_own     = session.get("username") == username
    return render_template("profile.html", user=user, posts=user_posts, is_own=is_own)

@app.route('/profile/<username>/edit', methods=["POST"])
def edit_profile(username):
    if session.get("username") != username:
        flash("Permission denied","danger")
        return redirect(url_for("profile", username=username))
    users = read_json(USERS_FILE)
    for u in users:
        if u.get("username") == username:
            u["fullname"] = request.form.get("fullname", u.get("fullname","")).strip()
            u["mobile"]   = request.form.get("mobile",   u.get("mobile","")).strip()
            u["bio"]      = request.form.get("bio",      u.get("bio","")).strip()
            u["location"] = request.form.get("location", u.get("location","")).strip()
            file = request.files.get("profile_pic")
            if file and allowed_file(file.filename):
                safe = secure_filename(file.filename)
                pic  = f"{username}_profile_{safe}"
                file.save(os.path.join(UPLOAD_FOLDER, pic))
                u["profile_pic"] = pic
            break
    write_json(USERS_FILE, users)
    flash("Profile updated!","success")
    return redirect(url_for("profile", username=username))

@app.route("/profile/<username>/upload_post", methods=["POST"])
def profile_upload_post(username):
    if session.get("username") != username:
        flash("Permission denied","danger")
        return redirect(url_for("profile", username=username))
    return create_post()

@app.route('/my_orders')
def my_orders():
    if 'username' not in session:
        return redirect(url_for('login'))
    username  = session['username']
    orders    = read_json(ORDERS_FILE)
    posts     = read_json(POSTS_FILE)
    my_orders = [o for o in orders if o.get('buyer')==username or o.get('seller')==username]
    for o in my_orders:
        post = next((p for p in posts if p["id"]==o.get("post_id")), None)
        o["_product"] = post.get("product","N/A") if post else o.get("product","N/A")
        o["_title"]   = post.get("title","")       if post else ""
    return render_template('my_orders.html', orders=my_orders, username=username)

@app.route("/place_order/<post_id>", methods=["POST"])
def place_order(post_id):
    if not session.get("username"):
        flash("Please login to place an order","danger")
        return redirect(url_for("login"))
    buyer  = session["username"]
    posts  = read_json(POSTS_FILE)
    post   = next((p for p in posts if p["id"]==post_id), None)
    if not post:
        flash("Post not found","warning")
        return redirect(url_for("home"))
    if post["username"] == buyer:
        flash("You can't order your own listing","warning")
        return redirect(url_for("home"))
    quantity_req = request.form.get("quantity_req","1").strip()
    orders = read_json(ORDERS_FILE)
    order  = {
        "id": str(uuid.uuid4()), "post_id": post_id,
        "seller": post["username"], "buyer": buyer,
        "product": post.get("product",""), "quantity_req": quantity_req,
        "price": post.get("price",""), "unit": post.get("unit","kg"),
        "status": "placed", "created_at": str(datetime.utcnow())
    }
    orders.append(order)
    write_json(ORDERS_FILE, orders)
    flash("Order placed — seller will be notified","success")
    chats   = read_json(CHATS_FILE)
    chat_id = f"{post['username']}__{buyer}"
    msgs    = next((c for c in chats if c.get("id")==chat_id), None)
    message = {
        "from": buyer, "to": post["username"],
        "text": f"📦 Order placed for '{post.get('product',post.get('title',''))}' — qty: {quantity_req} {post.get('unit','kg')}. Order ID: {order['id'][:8].upper()}",
        "time": str(datetime.utcnow()),
        "meta": {"order_id": order["id"], "type":"order_notification"}
    }
    if msgs:
        msgs["messages"].append(message)
    else:
        chats.append({"id":chat_id,"users":[buyer,post["username"]],"messages":[message]})
    write_json(CHATS_FILE, chats)
    return redirect(url_for("home"))

@app.route("/orders")
def orders():
    if not session.get("username"):
        flash("Login required","danger")
        return redirect(url_for("login"))
    username = session["username"]
    orders   = read_json(ORDERS_FILE)
    my_sells = [o for o in orders if o.get("seller")==username]
    my_buys  = [o for o in orders if o.get("buyer")==username]
    return render_template("orders.html", sells=my_sells, buys=my_buys)

@app.route("/orders/<order_id>/accept", methods=["POST"])
def accept_order(order_id):
    if not session.get("username"):
        flash("Login required","danger")
        return redirect(url_for("login"))
    username = session["username"]
    orders   = read_json(ORDERS_FILE)
    order    = next((o for o in orders if o["id"]==order_id), None)
    if not order:
        flash("Order not found","warning")
        return redirect(url_for("orders"))
    if order.get("seller") != username:
        flash("Not authorized","danger")
        return redirect(url_for("orders"))
    order["status"]      = "accepted"
    order["accepted_at"] = str(datetime.utcnow())
    chats   = read_json(CHATS_FILE)
    chat_id = f"{order['seller']}__{order['buyer']}"
    entry   = next((c for c in chats if c.get("id")==chat_id), None)
    receipt_msg = {
        "from": username, "to": order["buyer"],
        "text": f"✅ Order accepted! Receipt: ORDER-{order_id[:8].upper()}",
        "time": str(datetime.utcnow()),
        "meta": {"order_id": order_id, "type":"receipt"}
    }
    if entry:
        entry["messages"].append(receipt_msg)
    else:
        chats.append({"id":chat_id,"users":[order['seller'],order['buyer']],"messages":[receipt_msg]})
    write_json(CHATS_FILE, chats)
    write_json(ORDERS_FILE, orders)
    flash("Order accepted and receipt sent via chat","success")
    return redirect(url_for("orders"))

@app.route("/orders/<order_id>/reject", methods=["POST"])
def reject_order(order_id):
    if not session.get("username"):
        flash("Login required","danger")
        return redirect(url_for("login"))
    username = session["username"]
    orders   = read_json(ORDERS_FILE)
    order    = next((o for o in orders if o["id"]==order_id), None)
    if not order or order.get("seller") != username:
        flash("Not authorized","danger")
        return redirect(url_for("orders"))
    order["status"]      = "rejected"
    order["rejected_at"] = str(datetime.utcnow())
    write_json(ORDERS_FILE, orders)
    flash("Order rejected","info")
    return redirect(url_for("orders"))

@app.route("/chat/<user_a>/<user_b>", methods=["GET","POST"])
def chat(user_a, user_b):
    if not session.get("username"):
        flash("Login required","danger")
        return redirect(url_for("login"))
    me = session["username"]
    if me not in (user_a, user_b):
        flash("Not authorized","danger")
        return redirect(url_for("home"))
    ordered = "__".join([user_a, user_b])
    chats   = read_json(CHATS_FILE)
    entry   = next((c for c in chats if c.get("id")==ordered), None)
    if request.method == "POST":
        text = request.form.get("message","").strip()
        if text:
            msg = {"from": me, "to": user_b if me==user_a else user_a, "text": text, "time": str(datetime.utcnow())}
            if entry:
                entry["messages"].append(msg)
            else:
                entry = {"id": ordered, "users":[user_a,user_b], "messages":[msg]}
                chats.append(entry)
            write_json(CHATS_FILE, chats)
        return redirect(url_for("chat", user_a=user_a, user_b=user_b))
    messages   = entry["messages"] if entry else []
    other      = user_b if me==user_a else user_a
    other_user = find_user_by_username(other)
    return render_template("chat.html", messages=messages, user_a=user_a, user_b=user_b, other_user=other_user)

@app.route("/dashboard")
def dashboard():
    if not session.get("username"):
        flash("Login required","danger")
        return redirect(url_for("login"))
    username = session["username"]
    user     = find_user_by_username(username)
    if not user:
        flash("User not found","danger")
        return redirect(url_for("home"))
    role   = user.get("organization","")
    posts  = read_json(POSTS_FILE)
    orders = read_json(ORDERS_FILE)
    sells  = [o for o in orders if o.get("seller")==username]
    buys   = [o for o in orders if o.get("buyer")==username]
    if role == "farmer":
        return render_template("dashboard_farmer.html", user=user, sells=sells, buys=buys)
    if role == "distributor":
        return render_template("dashboard_distributor.html", user=user, sells=sells, buys=buys, posts=posts)
    return render_template("dashboard_retailer.html", user=user, sells=sells, buys=buys, posts=posts)

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/favicon.ico")
def favicon():
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)
