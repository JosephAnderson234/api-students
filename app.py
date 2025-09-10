from flask import Flask, request, jsonify
import sqlite3, os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.sqlite")

def db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # para dicts
    return conn

def init_db():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT NOT NULL,
            lastname  TEXT NOT NULL,
            gender    TEXT NOT NULL,
            age       TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/students", methods=["GET","POST"])
def students():
    conn = db_connection()
    cur = conn.cursor()

    if request.method == "GET":
        cur.execute("SELECT * FROM students")
        rows = cur.fetchall()
        students = [dict(row) for row in rows]
        conn.close()
        return jsonify(students), 200

    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname  = request.form.get("lastname")
        gender    = request.form.get("gender")
        age       = request.form.get("age")
        sql = """INSERT INTO students (firstname, lastname, gender, age) VALUES (?, ?, ?, ?)"""
        cur.execute(sql, (firstname, lastname, gender, age))
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return f"Student with id: {new_id} created successfully", 201

@app.route("/student/<int:id>", methods=["GET","PUT","DELETE"])
def student(id):
    conn = db_connection()
    cur = conn.cursor()

    if request.method == "GET":
        cur.execute("SELECT * FROM students WHERE id = ?", (id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return jsonify(dict(row)), 200
        return "Not found", 404

    if request.method == "PUT":
        firstname = request.form.get("firstname")
        lastname  = request.form.get("lastname")
        gender    = request.form.get("gender")
        age       = request.form.get("age")
        cur.execute("""UPDATE students SET firstname=?, lastname=?, gender=?, age=? WHERE id=?""",
                    (firstname, lastname, gender, age, id))
        conn.commit()
        conn.close()
        return jsonify({"id": id, "firstname": firstname, "lastname": lastname, "gender": gender, "age": age}), 200

    if request.method == "DELETE":
        cur.execute("DELETE FROM students WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return f"The Student with id: {id} has been deleted.", 200

if __name__ == "__main__":
    init_db()  # <-- crea DB y tabla si no existen ANTES de arrancar
    app.run(host="0.0.0.0", port=8000, debug=False)
