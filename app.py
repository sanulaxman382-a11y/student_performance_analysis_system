from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from config import Config
from analysis import grade_for, summarize_performance

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
mysql = MySQL(app)

def db_query(sql, params=(), one=False, commit=False):
    cur = mysql.connection.cursor(DictCursor)
    cur.execute(sql, params)
    result = cur.fetchone() if one else cur.fetchall()
    if commit:
        mysql.connection.commit()
    cur.close()
    return result

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/health")
def health():
    try:
        db_query("SELECT 1 AS ok", one=True)
        return jsonify({"status": "ok", "database": "connected"})
    except Exception as exc:
        app.logger.exception("Health check failed")
        return jsonify({"status": "error", "message": "Database connection failed"}), 503

@app.get("/api/dashboard")
def dashboard():
    try:
        counts = db_query("""
            SELECT
              (SELECT COUNT(*) FROM students) AS students,
              (SELECT COUNT(*) FROM branches) AS branches,
              (SELECT COUNT(*) FROM subjects) AS subjects,
              (SELECT COUNT(*) FROM assessments) AS assessments
        """, one=True)
        rows = db_query("""
            SELECT m.marks_obtained, a.max_marks
            FROM marks m JOIN assessments a ON a.id=m.assessment_id
        """)
        normalized = []
        for row in rows:
            normalized.append({
                "score": float(row["marks_obtained"]) / float(row["max_marks"]) * 100,
                "passed": float(row["marks_obtained"]) / float(row["max_marks"]) >= 0.40
            })
        summary = summarize_performance(normalized)
        return jsonify({**counts, **summary})
    except Exception:
        app.logger.exception("Dashboard query failed")
        return jsonify({"error": "Could not load dashboard data"}), 500

@app.route("/api/branches", methods=["GET", "POST"])
def branches():
    if request.method == "GET":
        return jsonify(db_query("SELECT * FROM branches ORDER BY name"))
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip().upper()
    if not name or len(name) > 100:
        return jsonify({"error": "Branch name is required (max 100 characters)."}), 400
    try:
        db_query("INSERT INTO branches(name) VALUES (%s)", (name,), commit=True)
        return jsonify({"message": "Branch created"}), 201
    except Exception:
        return jsonify({"error": "Could not create branch; name may already exist."}), 409

@app.route("/api/students", methods=["GET", "POST"])
def students():
    if request.method == "GET":
        rows = db_query("""SELECT s.*, b.name AS branch_name FROM students s
                           JOIN branches b ON b.id=s.branch_id ORDER BY s.roll_no""")
        return jsonify(rows)
    data = request.get_json(silent=True) or {}
    required = ["roll_no", "name", "branch_id", "semester"]
    if any(data.get(k) in (None, "") for k in required):
        return jsonify({"error": "roll_no, name, branch_id and semester are required."}), 400
    try:
        semester = int(data["semester"])
        branch_id = int(data["branch_id"])
        if not 1 <= semester <= 8 or not str(data["name"]).strip() or len(str(data["name"])) > 120:
            raise ValueError()
        db_query("""INSERT INTO students(roll_no,name,branch_id,semester)
                    VALUES (%s,%s,%s,%s)""",
                 (str(data["roll_no"]).strip(), str(data["name"]).strip(), branch_id, semester),
                 commit=True)
        return jsonify({"message": "Student created"}), 201
    except ValueError:
        return jsonify({"error": "Semester must be 1–8 and name must be valid."}), 400
    except Exception:
        return jsonify({"error": "Could not create student; check branch and unique roll number."}), 409

@app.route("/api/students/<int:student_id>", methods=["PUT", "DELETE"])
def student_detail(student_id):
    if request.method == "DELETE":
        try:
            db_query("DELETE FROM students WHERE id=%s", (student_id,), commit=True)
            return jsonify({"message": "Student deleted"})
        except Exception:
            return jsonify({"error": "Could not delete student. Remove related marks first."}), 409
    data = request.get_json(silent=True) or {}
    try:
        db_query("""UPDATE students SET name=%s, branch_id=%s, semester=%s WHERE id=%s""",
                 (str(data["name"]).strip(), int(data["branch_id"]), int(data["semester"]), student_id),
                 commit=True)
        return jsonify({"message": "Student updated"})
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Valid name, branch_id and semester are required."}), 400
    except Exception:
        return jsonify({"error": "Could not update student."}), 409

@app.route("/api/subjects", methods=["GET", "POST"])
def subjects():
    if request.method == "GET":
        return jsonify(db_query("""SELECT s.*, b.name AS branch_name FROM subjects s
            LEFT JOIN branches b ON b.id=s.branch_id ORDER BY s.code"""))
    data = request.get_json(silent=True) or {}
    try:
        code, name = str(data["code"]).strip().upper(), str(data["name"]).strip()
        branch_id = int(data["branch_id"]) if data.get("branch_id") else None
        if not code or not name:
            raise ValueError()
        db_query("INSERT INTO subjects(code,name,branch_id) VALUES (%s,%s,%s)",
                 (code, name, branch_id), commit=True)
        return jsonify({"message": "Subject created"}), 201
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Subject code and name are required."}), 400
    except Exception:
        return jsonify({"error": "Could not create subject; check unique code/branch."}), 409

@app.route("/api/assessments", methods=["GET", "POST"])
def assessments():
    if request.method == "GET":
        return jsonify(db_query("""SELECT a.*, s.name AS subject_name FROM assessments a
            JOIN subjects s ON s.id=a.subject_id ORDER BY a.exam_date DESC, a.id DESC"""))
    data = request.get_json(silent=True) or {}
    try:
        title = str(data["title"]).strip()
        subject_id, semester = int(data["subject_id"]), int(data["semester"])
        max_marks = float(data["max_marks"])
        exam_date = data.get("exam_date") or None
        if not title or not 1 <= semester <= 8 or max_marks <= 0:
            raise ValueError()
        db_query("""INSERT INTO assessments(title,subject_id,semester,max_marks,exam_date)
                    VALUES (%s,%s,%s,%s,%s)""",
                 (title, subject_id, semester, max_marks, exam_date), commit=True)
        return jsonify({"message": "Assessment created"}), 201
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Provide title, subject, semester 1–8 and positive max marks."}), 400
    except Exception:
        return jsonify({"error": "Could not create assessment."}), 409

@app.route("/api/marks", methods=["GET", "POST"])
def marks():
    if request.method == "GET":
        return jsonify(db_query("""SELECT m.id, m.student_id, st.roll_no, st.name AS student_name,
            a.id AS assessment_id, a.title AS assessment_title, a.max_marks,
            m.marks_obtained, ROUND(m.marks_obtained/a.max_marks*100,2) AS percentage
            FROM marks m JOIN students st ON st.id=m.student_id
            JOIN assessments a ON a.id=m.assessment_id ORDER BY st.roll_no"""))
    data = request.get_json(silent=True) or {}
    try:
        student_id, assessment_id = int(data["student_id"]), int(data["assessment_id"])
        score = float(data["marks_obtained"])
        assessment = db_query("SELECT max_marks FROM assessments WHERE id=%s",
                               (assessment_id,), one=True)
        if not assessment or score < 0 or score > float(assessment["max_marks"]):
            raise ValueError()
        db_query("""INSERT INTO marks(student_id,assessment_id,marks_obtained)
                    VALUES (%s,%s,%s)
                    ON DUPLICATE KEY UPDATE marks_obtained=VALUES(marks_obtained)""",
                 (student_id, assessment_id, score), commit=True)
        return jsonify({"message": "Marks saved"}), 201
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Provide valid IDs and marks between 0 and the assessment maximum."}), 400
    except Exception:
        return jsonify({"error": "Could not save marks; check student and assessment."}), 409

@app.get("/api/results")
def results():
    try:
        rows = db_query("""SELECT st.id AS student_id, st.roll_no, st.name, b.name AS branch,
            st.semester, a.id AS assessment_id, a.title AS assessment,
            su.name AS subject, a.max_marks, m.marks_obtained
            FROM marks m JOIN students st ON st.id=m.student_id
            JOIN branches b ON b.id=st.branch_id
            JOIN assessments a ON a.id=m.assessment_id
            JOIN subjects su ON su.id=a.subject_id
            ORDER BY b.name, st.semester, st.roll_no, a.title""")
        for row in rows:
            pct = float(row["marks_obtained"]) / float(row["max_marks"]) * 100
            row["percentage"] = round(pct, 2)
            row["grade"] = grade_for(pct)
            row["status"] = "Pass" if pct >= 40 else "Needs support"
        return jsonify(rows)
    except Exception:
        app.logger.exception("Results query failed")
        return jsonify({"error": "Could not load results"}), 500

@app.get("/api/reports/branches")
def branch_report():
    rows = db_query("""SELECT b.name AS branch, st.semester,
        COUNT(DISTINCT st.id) AS students, ROUND(AVG(m.marks_obtained/a.max_marks*100),2) AS average_percentage,
        ROUND(100*SUM(CASE WHEN m.marks_obtained/a.max_marks >= 0.4 THEN 1 ELSE 0 END)/COUNT(m.id),2) AS pass_percentage
        FROM branches b JOIN students st ON st.branch_id=b.id
        LEFT JOIN marks m ON m.student_id=st.id
        LEFT JOIN assessments a ON a.id=m.assessment_id
        GROUP BY b.name, st.semester ORDER BY b.name, st.semester""")
    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)
