from flask import Flask, request, redirect, session, render_template, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = "ecommerce_secret"

# Database connection
def db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ecommerce"
    )

# Home - Product Catalog
@app.route("/")
def home():
    con = db()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    con.close()

    return render_template("products.html", products=products)


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        con = db()
        cur = con.cursor()

        cur.execute(
            "INSERT INTO users(username,password,role) VALUES(%s,%s,'User')",
            (username, password)
        )

        con.commit()
        con.close()

        return redirect("/login")

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        con = db()
        cur = con.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cur.fetchone()
        con.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect("/")

        return "Invalid username or password"

    return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# Add product to cart
@app.route("/add_cart/<int:product_id>")
def add_cart(product_id):

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]
    cart.append(product_id)

    session["cart"] = cart

    return redirect("/cart")


# Cart
@app.route("/cart")
def cart():

    if "cart" not in session:
        return "Cart is empty"

    cart = session["cart"]

    con = db()
    cur = con.cursor(dictionary=True)

    products = []

    for product_id in cart:
        cur.execute(
            "SELECT * FROM products WHERE id=%s",
            (product_id,)
        )

        product = cur.fetchone()

        if product:
            products.append(product)

    con.close()

    total = sum(p["price"] for p in products)

    return render_template(
        "cart.html",
        products=products,
        total=total
    )


# Checkout
@app.route("/checkout", methods=["POST"])
def checkout():

    if "user_id" not in session:
        return redirect("/login")

    cart = session.get("cart", [])

    if not cart:
        return "Cart is empty"

    con = db()
    cur = con.cursor()

    for product_id in cart:
        cur.execute(
            "INSERT INTO orders(user_id,product_id,status) VALUES(%s,%s,'Ordered')",
            (session["user_id"], product_id)
        )

    con.commit()
    con.close()

    session["cart"] = []

    return "Order placed successfully!"


# User orders
@app.route("/orders")
def orders():

    if "user_id" not in session:
        return redirect("/login")

    con = db()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT orders.id, products.name,
               products.price, orders.status
        FROM orders
        JOIN products ON orders.product_id = products.id
        WHERE orders.user_id=%s
    """, (session["user_id"],))

    orders = cur.fetchall()

    con.close()

    return jsonify(orders)


# Admin - View products
@app.route("/api/products")
def products_api():

    con = db()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    con.close()

    return jsonify(products)


# Admin - Add product
@app.route("/api/products/add", methods=["POST"])
def add_product():

    if session.get("role") != "Admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.json

    con = db()
    cur = con.cursor()

    cur.execute(
        "INSERT INTO products(name,price,quantity) VALUES(%s,%s,%s)",
        (
            data["name"],
            data["price"],
            data["quantity"]
        )
    )

    con.commit()
    con.close()

    return jsonify({"message": "Product added successfully"})


# Admin - Delete product
@app.route("/api/products/<int:id>", methods=["DELETE"])
def delete_product(id):

    if session.get("role") != "Admin":
        return jsonify({"error": "Admin access required"}), 403

    con = db()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM products WHERE id=%s",
        (id,)
    )

    con.commit()
    con.close()

    return jsonify({"message": "Product deleted"})


# Admin - View all orders
@app.route("/api/orders")
def all_orders():

    if session.get("role") != "Admin":
        return jsonify({"error": "Admin access required"}), 403

    con = db()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT orders.id,
               users.username,
               products.name,
               products.price,
               orders.status
        FROM orders
        JOIN users ON orders.user_id = users.id
        JOIN products ON orders.product_id = products.id
    """)

    orders = cur.fetchall()

    con.close()

    return jsonify(orders)


if __name__ == "__main__":
    app.run(debug=True)
