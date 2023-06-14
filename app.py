from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import os
from werkzeug.utils import secure_filename
from helpers import login_required, usd, allowed_file

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.add_url_rule("/uploads/<name>", endpoint="download_file", build_only=True)
sess = Session()
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["int"] = int

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///iko.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return redirect("/")


        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/profile")
@login_required
def profile():
    # Get user information
    person = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
    # Get user listings
    listings = db.execute("SELECT * FROM listings WHERE lister_id = ?", session["user_id"])
    # Get user purchases
    purchases = db.execute("SELECT * FROM purchase_log WHERE buyer_id = ?", session["user_id"])
    #show the profile template
    return render_template("profile.html", person=person, listings=listings, purchases=purchases)

@app.route('/list', methods=['GET', 'POST'])
@login_required
def list():
    if request.method == "GET":
        return render_template("list.html")
    elif request.method == 'POST':
        # Check that image is compatible
        image = request.files['image']
        if image.filename == '':
            flash('No image provided')
            return redirect("/list")
        if not allowed_file(image.filename):
            flash('Incompatible file type')
            return redirect("/list")
        filename = secure_filename(generate_password_hash(image.filename))
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Get the URL so it can be stored in the SQL database
        image = url_for('download_file', name=filename)
        # Validate title
        title = request.form.get("title")
        if title == "":
            flash('No title provided')
            return redirect("/list")
            # Validate description
        description = request.form.get("description")
        if description == "":
            description = "No Description"
            return redirect("/list")
        if len(description) > 200:
            description = "Description too long"
            return redirect("/list")
        # Validate brand
        brand = request.form.get("brand")
        if brand == "":
            description = "No Brand Provided"
            return redirect("/list")
        # Validate price
        price = request.form.get("price")
        if not price.isnumeric():
            flash('Price must be a numeric value')
            return redirect("/list")
        if int(price) < 0:
            flash('Price must be be postive')
            return redirect("/list")
        # Validate size
        size = request.form.get("size")
        if size == "":
            flash('No size provided')
            return redirect("/list")
        # Validate type
        type = request.form.get("type")
        if type == None:
            flash('No type provided')
            return redirect("/list")
        # Validate color
        color = request.form.get("color")
        if color == None:
            flash('No color provided')
            return redirect("/list")
        # Validate genre
        genre = request.form.get("genre")
        if genre == None:
            flash('No genre provided')
            return redirect("/list")
        # Validate decade
        decade = request.form.get("decade")
        if decade == None:
            flash('No decade provided')
            return redirect("/list")
        db.execute("INSERT INTO listings (lister_id, title, description, image, brand, price, size, type, color, genre, decade) VALUES (?,?,?,?,?,?,?,?,?,?,?)", session["user_id"], title, description, image, brand, price, size, type, color, genre, decade)
        return redirect("/profile")
    

@app.route("/about")
@login_required
def about():
    return render_template("about.html")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "GET":
        return render_template("search.html")
    elif request.method == "POST":
        # If the entries are left empty, make sure they are not filtered in the SQL statement
        title = request.form.get("title")
        if title == "":
            title = "%"
        brand = request.form.get("brand")
        if brand == "":
            brand = "%"
        size = request.form.get("size")
        if size == "":
            size = "%"
        type = request.form.get("type")
        if type == "Any":
            type = "%"
        color = request.form.get("color")
        if color == "Any":
            color = "%"
        genre = request.form.get("genre")
        if genre == "Any":
            genre = "%"
        decade = request.form.get("decade")
        if decade == "Any":
            decade = "%"
        minprice = request.form.get("mnprice")
        if minprice == "":
            minprice = 0
        elif not minprice.isnumeric():
            flash('Price must be numeric')
            return redirect("/list")
        maxprice = request.form.get("mxprice")
        if maxprice == "":
            maxprice = 999999
        elif not maxprice.isnumeric():
            flash('Price must be numeric')
            return redirect("/list")
        selections = db.execute("SELECT * FROM listings WHERE active = 'True' AND title LIKE ? AND brand LIKE ? AND size LIKE ? AND type LIKE ? AND color LIKE ? AND genre LIKE ? AND decade LIKE ? AND price > ? AND price < ?", title, brand, size, type, color, genre, decade, int(minprice), int(maxprice))
        return render_template("results.html", selections=selections)

@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    # Once information has been submitted...
    if request.method == "POST":
        
        # Get the amount to be deposited
        deposit = request.form.get("deposit")

        # Make sure it's a valid amount
        if deposit == "":
            return apology("enter a cash amount", 400)
        elif not deposit.isnumeric():
            return apology("deposit must be numeric", 400)
        elif float(deposit) <= 0:
            return apology("enter a positive cash amount to deposit", 400)

        # Query for the user's current cash
        current_funds = int(db.execute("SELECT funds FROM users WHERE id = ?", session["user_id"])[0]["funds"])

        # Update the user's cash to reflect the deposit
        db.execute("UPDATE users SET funds = ? WHERE id = ?", current_funds + float(deposit), session["user_id"])

        flash("Funds deposited")
        return redirect("/profile")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/browse")
@login_required
def browse():
    # Get user listings
    listings = db.execute("SELECT * FROM listings WHERE active = 'True'")
    return render_template("browse.html", listings=listings)
        
@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    if request.method == "POST":
        id = request.form.get("id")
        # Remove listing
        db.execute("DELETE FROM listings WHERE id  = ?", id)
        flash('Listing Removed')
        return redirect("/profile")

@app.route("/unwatch", methods=["GET", "POST"])
@login_required
def unwatch():
    if request.method == "POST":
        id = request.form.get("id")
        # Remove an item from watchlist
        db.execute("DELETE FROM watchlist WHERE item_id  = ? and watcher_id = ?", id, session["user_id"])
        flash('Listing Removed From Watchlist')
        return redirect("/profile")

@app.route("/watchlist", methods=["GET", "POST"])
@login_required
def watchlist():
    if request.method == "GET":
        # Get user watchlisted items
        items=db.execute("SELECT * FROM listings WHERE id IN (SELECT item_id FROM watchlist WHERE watcher_id  = ?)", session["user_id"])
        return render_template("watchlist.html", items=items)
    elif request.method == "POST":
        id = request.form.get("id")

        # Ensure that item is not already in watchlist
        current = db.execute("SELECT item_id FROM watchlist WHERE item_id = ? AND watcher_id = ?", id, session["user_id"])
        if len(current) > 0:
            flash("Listing already in watchlist")
            return redirect("/watchlist")

        # If it isn't, add it
        db.execute("INSERT INTO watchlist (item_id, watcher_id) VALUES (?,?)", id, session["user_id"])
        flash("Listing added to watchlist")
        return redirect("/watchlist")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    id = request.form.get("id")

    # Remove listing from the market
    db.execute("UPDATE listings SET active = 'False' WHERE id = ?", id)

    # Add transaction to purchase log
    item = db.execute("SELECT lister_id, title, price FROM listings WHERE id = ?", id)
    seller_id = item[0]["lister_id"]
    title = item[0]["title"]
    price = int(item[0]["price"])
    print(price)
    db.execute("INSERT INTO purchase_log (seller_id, buyer_id, item_name, item_id, price, timestamp) VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)",seller_id, session["user_id"], title,id, price)
    
    # Remove price from buyer
    current_buyer_funds = int(db.execute("SELECT funds FROM users WHERE id = ?", session["user_id"])[0]["funds"])
    db.execute("UPDATE users SET funds = ? WHERE id = ?", current_buyer_funds - price, session["user_id"])

    # Add price to seller
    current_seller_funds = db.execute("SELECT funds FROM users WHERE id = ?", seller_id)[0]["funds"]
    db.execute("UPDATE users SET funds = ? WHERE id = ?", current_seller_funds + price, seller_id)
    flash('Purchase Successful')
    return redirect("/profile")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        confirmation = request.form.get("confirmation")

        # Check for username
        if not username:
            flash("Please Enter a Valid Username")
            return redirect("/register")
        # Check for password
        elif not password:
            flash("Please Enter a Valid Password")
            return redirect("/register")
        #Check for name
        elif not full_name:
            flash("Please Enter a Valid Name")
            return redirect("/register")
        #Check for email
        elif not email:
            flash("Please Enter a Valid Email")
            return redirect("/register")
        #Check for phone number
        elif not phone:
            flash("Please Enter a Valid Phone Number")
            return redirect("/register")
        #Check for address
        elif not address:
            flash("Please Enter a Valid Address")
            return redirect("/register")
        # Check for confirmation
        elif not confirmation:
            flash("Password Confirmation Required")
            return redirect("/register")
        # Check if the password and confirmation match
        if password != confirmation:
            flash("Please Make Sure Your Passwords Match")
            return redirect("/register")
        try:
            hash = generate_password_hash(password)
            # Insert new user
            db.execute("INSERT INTO users (username, full_name, email, phone, address, hash) VALUES (?, ?, ?, ?, ?, ?)", username, full_name, email, phone, address, hash)
            # Remember session
            return redirect("/")
        except:
            flash("Username Already Taken")
            return redirect("/register")
    else:
        return render_template("register.html")

@app.route("/edit", methods = ["GET", "POST"])
@login_required
def edit():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        confirmation = request.form.get("confirmation")

        # Check for username
        if not username:
            flash("Please Enter a Valid Username")
            return redirect("/edit")
        # Check for password
        elif not password:
            flash("Please Enter a Valid Password")
            return redirect("/edit")
        #Check for name
        elif not full_name:
            flash("Please Enter a Valid Name")
            return redirect("/edit")
        #Check for email
        elif not email:
            flash("Please Enter a Valid Email")
            return redirect("/edit")
        #Check for phone number
        elif not phone:
            flash("Please Enter a Valid Phone Number")
            return redirect("/edit")
        #Check for address
        elif not address:
            flash("Please Enter a Valid Address")
            return redirect("/edit")
        # Check for confirmation
        elif not confirmation:
            flash("Password Confirmation Required")
            return redirect("/edit")
        # Check if the password and confirmation match
        if password != confirmation:
            flash("Please Make Sure Your Passwords Match")
            return redirect("/edit")
        try:
            hash = generate_password_hash(password)
            # Update user
            db.execute("UPDATE users SET username = ?, full_name = ?, email = ?, phone=?, address=?, hash=? WHERE id= ?", username, full_name, email, phone, address, hash)
            # Remember session
            return redirect("/profile")
        except:
            flash("Username Already Taken")
            return redirect("/edit")
    else:
        return render_template("edit.html")