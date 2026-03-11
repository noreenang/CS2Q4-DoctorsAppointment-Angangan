from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey"

# template filter to format stored appointment timestamps
@app.template_filter('format_date')
def format_date(value):
    try:
        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M")
        # Display in 12-hour format with AM/PM
        return dt.strftime("%m-%d-%Y, %I:%M %p")
    except Exception:
        return value

# storing data 
patients = {}
appointments = []


# Admin credentials
admin_username = "admin"
admin_password = "admin123"


@app.route("/")
def home():
    return redirect(url_for("login"))


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        name = request.form["name"].strip()
        age = request.form["age"].strip()
        address = request.form["address"].strip()

        
        if not username or not password or not name or not address:
            error = "All fields are required and cannot be blank."
            flash(error, "error")
            return redirect(url_for("register"))

        # username uniqueness
        if username in patients:
            error = "Username already exists. Choose another."
            flash(error, "error")
            return redirect(url_for("register"))

        # age validation (separate so we can give a clear numeric error)
        if not age:
            error = "Age must be a number greater than 0."
            flash(error, "error")
            return redirect(url_for("register"))

        try:
            age_val = int(age)
            if age_val <= 0:
                error = "Age must be a number greater than 0."
                flash(error, "error")
                return redirect(url_for("register"))
        except ValueError:
            error = "Age must be a number greater than 0."
            flash(error, "error")
            return redirect(url_for("register"))

        patients[username] = {
            "password": password,
            "name": name,
            "age": age_val,
            "address": address
        }

        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

       
        if not username or not password:
            error = "Please fill in both username and password."
            flash(error, "error")
            return redirect(url_for("login"))

        # Admin login
        if username == admin_username and password == admin_password:
            session["admin"] = True
            flash("Logged in as admin.", "success")
            return redirect(url_for("admin"))

        # Patient login
        if username in patients and patients[username]["password"] == password:
            session["user"] = username
            flash(f"Welcome, {patients[username]['name']}!", "success")
            return redirect(url_for("dashboard"))

        error = "Invalid username or password."
        flash(error, "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# ---------------- PATIENT DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    # ensure session user exists and still has a patient record
    if user and user in patients:
        user_appointments = [a for a in appointments if a["username"] == user]
        return render_template("dashboard.html", patient=patients[user], appointments=user_appointments)
    # invalid session--clear and send to login
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- BOOK APPOINTMENT ----------------
@app.route("/book", methods=["GET", "POST"])
def book():
    if "user" in session and session["user"] in patients:
        if request.method == "POST":
            appointment_date = request.form["appointment"]

            # ensure year is 2026 or later
            try:
                # datetime-local format: YYYY-MM-DDTHH:MM
                year = int(appointment_date.split("-")[0])
            except Exception:
                flash("Invalid appointment date format.", "error")
                return render_template("book.html")

            if year < 2026:
                flash("Appointment year must be 2026 or later.", "error")
                return render_template("book.html")

            appointments.append({
                "username": session["user"],
                "name": patients[session["user"]]["name"],
                "appointment": appointment_date
            })

            flash("Appointment booked successfully.", "success")
            return redirect(url_for("dashboard"))

        return render_template("book.html")

    # either not logged in or invalid user record
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- ADMIN PAGE ----------------
@app.route("/admin")
def admin():
    if "admin" in session:
        
        return render_template("admin.html", patients=patients, appointments=appointments)
    return redirect(url_for("login"))


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
