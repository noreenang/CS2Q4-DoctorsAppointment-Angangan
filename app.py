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
patients = {
    "jaildoe": {"password": "pass123", "name": "John Doe", "age": 35, "address": "123 Maple St, Golden Grove"},
    "asmith": {"password": "hello2026", "name": "Alice Smith", "age": 29, "address": "456 Oak St, Sunset Bird"},
    "irispiris": {"password": "fa3rieiris", "name": "Samantha Faith L. Lidres", "age": 13, "address": "Dubai, UAE"},
    "usajazmin": {"password": "jamminusagi", "name": "Jazmin S. Kapa", "age": 14, "address": "Pagadian City"},
    "superannaoy": {"password": "yoanna_123", "name": "Yoanna Glorien C. Cabatingan", "age": 14, "address": "Pagadian City"},
    "gaebrahamlincoln": {"password": "gaeblu", "name": "Gabrinne Adanneij M. Lu", "age": 14, "address": "Pagadian City"},
    "theysammyrollin": {"password": "kaitlynsilao", "name": "Samantha Kaitlyn A. Silao", "age": 13, "address": "Pagadian City"},
    "kiel.nadonza": {"password": "klkiel722", "name": "KL Denise T. Nadonza", "age": 13, "address": "Pagadian City"},
    "atinapay": {"password": "athenacortes12", "name": "Athena M. Cortes", "age": 13, "address": "Pagadian City"},
    "yomizyo": {"password": "sasalele2012", "name": "Alizzandra Aeve T. Alzaabi", "age": 13, "address": "Pagadian City"},
    "tammycakes": {"password": "tammycakes123", "name": "Tamarack Baumann", "age": 14, "address": "Golden Grove"},
    "qiucakes": {"password": "qiucakes123", "name": "Qiu \"Autumn\" Lin", "age": 14, "address": "Golden Grove"},
}
appointments = [
    {"id": 1, "username": "jaildoe", "name": "John Doe", "appointment": "2026-10-10T10:00", "status": "scheduled"},
    {"id": 2, "username": "asmith", "name": "Alice Smith", "appointment": "2026-11-01T14:30", "status": "scheduled"},
    {"id": 3, "username": "jaildoe", "name": "John Doe", "appointment": "2026-09-20T09:00", "status": "cancelled"},
    {"id": 4, "username": "irispiris", "name": "Samantha Faith L. Lidres", "appointment": "2026-12-02T11:15", "status": "scheduled"},
    {"id": 5, "username": "usajazmin", "name": "Jazmin S. Kapa", "appointment": "2026-10-22T16:00", "status": "scheduled"},
    {"id": 6, "username": "superannaoy", "name": "Yoanna Glorien C. Cabatingan", "appointment": "2026-11-05T09:30", "status": "scheduled"},
    {"id": 7, "username": "gaebrahamlincoln", "name": "Gabrinne Adanneij M. Lu", "appointment": "2026-11-15T13:45", "status": "scheduled"},
    {"id": 8, "username": "theysammyrollin", "name": "Samantha Kaitlyn A. Silao", "appointment": "2026-12-10T10:30", "status": "scheduled"},
    {"id": 9, "username": "kiel.nadonza", "name": "KL Denise T. Nadonza", "appointment": "2027-01-11T09:45", "status": "scheduled"},
    {"id": 10, "username": "atinapay", "name": "Athena M. Cortes", "appointment": "2027-02-08T11:00", "status": "scheduled"},
    {"id": 11, "username": "yomizyo", "name": "Alizzandra Aeve T. Alzaabi", "appointment": "2027-03-02T15:00", "status": "scheduled"}
]
next_appointment_id = 12


# Admin credentials
admin_username = "admin"
admin_password = "admin123"


@app.route("/")
def home():
    return redirect(url_for("login"))


#REGISTER
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


#  LOGIN 
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


# PATIENT DASHBOARD
@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    # ensure session user exists and still has a patient record
    if user and user in patients:
        user_appointments = [a for a in appointments if a["username"] == user and a.get("status", "scheduled") == "scheduled"]
        cancelled = [a for a in appointments if a["username"] == user and a.get("status", "scheduled") == "cancelled"]
        return render_template("dashboard.html", patient=patients[user], appointments=user_appointments, cancelled=cancelled)
    # invalid session--clear and send to login
    session.pop("user", None)
    return redirect(url_for("login"))


# BOOK APPOINTMENT
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

            global next_appointment_id
            appointments.append({
                "id": next_appointment_id,
                "username": session["user"],
                "name": patients[session["user"]]["name"],
                "appointment": appointment_date,
                "status": "scheduled"
            })
            next_appointment_id += 1

            flash("Appointment booked successfully.", "success")
            return redirect(url_for("dashboard"))

        return render_template("book.html")

    # either not logged in or invalid user record
    session.pop("user", None)
    return redirect(url_for("login"))


def get_appointment(appt_id):
    for appt in appointments:
        if appt["id"] == appt_id:
            return appt
    return None


def authorized_for_appointment(appt):
    if "admin" in session:
        return True
    if "user" in session and appt["username"] == session["user"]:
        return True
    return False


@app.route("/appointment/<int:appt_id>/edit")
def edit_appointment(appt_id):
    appt = get_appointment(appt_id)
    if not appt:
        flash("Appointment not found.", "error")
        return redirect(url_for("dashboard"))

    if not authorized_for_appointment(appt):
        flash("Unauthorized.", "error")
        return redirect(url_for("login"))

    return_url = url_for("admin") if "admin" in session else url_for("dashboard")
    return render_template("edit_appointment.html", appointment=appt, return_url=return_url)


@app.route("/appointment/<int:appt_id>/update", methods=["POST"])
def update_appointment(appt_id):
    appt = get_appointment(appt_id)
    if not appt:
        flash("Appointment not found.", "error")
        return redirect(url_for("dashboard"))

    if not authorized_for_appointment(appt):
        flash("Unauthorized.", "error")
        return redirect(url_for("login"))

    if appt.get("status", "scheduled") == "cancelled":
        flash("Cannot edit a cancelled appointment.", "error")
        return redirect(url_for("admin") if "admin" in session else url_for("dashboard"))

    appointment_date = request.form.get("appointment", "").strip()
    if not appointment_date:
        flash("Appointment date cannot be empty.", "error")
        return redirect(url_for("edit_appointment", appt_id=appt_id))

    try:
        year = int(appointment_date.split("-")[0])
    except Exception:
        flash("Invalid appointment date format.", "error")
        return redirect(url_for("edit_appointment", appt_id=appt_id))

    if year < 2026:
        flash("Appointment update year must be 2026 or later.", "error")
        return redirect(url_for("edit_appointment", appt_id=appt_id))

    appt["appointment"] = appointment_date
    flash("Appointment updated successfully.", "success")
    return redirect(url_for("admin") if "admin" in session else url_for("dashboard"))


@app.route("/appointment/<int:appt_id>/cancel", methods=["POST"])
def cancel_appointment(appt_id):
    appt = get_appointment(appt_id)
    if not appt:
        flash("Appointment not found.", "error")
        return redirect(url_for("dashboard"))
    if not authorized_for_appointment(appt):
        flash("Unauthorized.", "error")
        return redirect(url_for("login"))

    appt["status"] = "cancelled"
    flash("Appointment cancelled successfully.", "success")
    return redirect(url_for("admin") if "admin" in session else url_for("dashboard"))


#  ADMIN PAGE 
@app.route("/admin")
def admin():
    if "admin" in session:
        return render_template("admin.html", patients=patients, appointments=appointments)
    return redirect(url_for("login"))


@app.route("/admin/patient/<username>/delete", methods=["POST"])
def delete_patient(username):
    if "admin" not in session:
        return redirect(url_for("login"))
    if username not in patients:
        flash("Patient not found.", "error")
        return redirect(url_for("admin"))

    # Remove patient and related appointments
    patients.pop(username, None)
    global appointments
    appointments = [a for a in appointments if a["username"] != username]

    flash("Patient record deleted successfully.", "success")
    return redirect(url_for("admin"))


@app.route("/admin/patient/<username>/edit")
def edit_patient(username):
    if "admin" not in session:
        return redirect(url_for("login"))
    if username not in patients:
        flash("Patient not found.", "error")
        return redirect(url_for("admin"))

    return render_template("edit_patient.html", patient=patients[username], username=username)


@app.route("/admin/patient/<username>/update", methods=["POST"])
def update_patient(username):
    if "admin" not in session:
        return redirect(url_for("login"))
    if username not in patients:
        flash("Patient not found.", "error")
        return redirect(url_for("admin"))

    name = request.form.get("name", "").strip()
    age_str = request.form.get("age", "").strip()
    address = request.form.get("address", "").strip()

    # Validation for empty fields
    if not name:
        flash("Name cannot be empty.", "error")
        return redirect(url_for("edit_patient", username=username))
    if not age_str:
        flash("Age cannot be empty.", "error")
        return redirect(url_for("edit_patient", username=username))
    if not address:
        flash("Address cannot be empty.", "error")
        return redirect(url_for("edit_patient", username=username))

    # Age validation
    try:
        age = int(age_str)
        if age <= 0:
            flash("Age must be a positive number.", "error")
            return redirect(url_for("edit_patient", username=username))
    except ValueError:
        flash("Age must be a valid number.", "error")
        return redirect(url_for("edit_patient", username=username))

    # Update patient info
    patients[username]["name"] = name
    patients[username]["age"] = age
    patients[username]["address"] = address

    flash("Patient information updated successfully.", "success")
    return redirect(url_for("admin"))


#LOGOUT 
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
