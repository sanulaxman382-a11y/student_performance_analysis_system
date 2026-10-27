# Student Performance Analysis System

A full-stack academic performance dashboard using HTML/CSS/JavaScript, Flask REST APIs, MySQL, pandas, and Chart.js. This starter project includes sample records and testable grade-analysis helpers.

## Features
- Dashboard metrics: student/branch/subject/assessment counts, class average, pass percentage and at-risk assessment records.
- Student, branch, subject and assessment management.
- Marks entry with validation and upsert behavior for a student's existing assessment mark.
- Results register with grade and support-needed status.
- Branch/semester report and CSV export.
- Responsive desktop/mobile layout.
- Sample data for demonstration.

## Requirements
- Python 3.10+
- MySQL 8+
- A C compiler / MySQL client development libraries may be required by `mysqlclient` (used by Flask-MySQLdb).
- VS Code and MySQL Workbench are recommended.

## 1. Create and activate a virtual environment
Windows PowerShell:
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Create the database
Start MySQL, then run `database.sql` in MySQL Workbench (File → Open SQL Script → execute). The script creates the schema and inserts synthetic demo records. It uses `INSERT IGNORE`, so it can be re-run for most sample rows.

## 3. Configure credentials
Set environment variables in the terminal before starting Flask. Do not commit real credentials.

Windows PowerShell:
```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your_mysql_password"
$env:MYSQL_DB="student_performance"
$env:SECRET_KEY="replace-with-a-long-random-secret"
```
macOS/Linux:
```bash
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD='your_mysql_password'
export MYSQL_DB=student_performance
export SECRET_KEY='replace-with-a-long-random-secret'
```
`.env.example` is a reference only; Flask does not automatically load it.

## 4. Run the application
```bash
python app.py
```
Open http://127.0.0.1:5000. Verify the backend with http://127.0.0.1:5000/api/health.

## API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API/database health |
| GET, POST | `/api/branches` | List/create branches |
| GET, POST | `/api/students` | List/create students |
| PUT, DELETE | `/api/students/<id>` | Update/delete a student |
| GET, POST | `/api/subjects` | List/create subjects |
| GET, POST | `/api/assessments` | List/create assessments |
| GET, POST | `/api/marks` | List/record marks |
| GET | `/api/results` | Results with percentage, grade and status |
| GET | `/api/dashboard` | Dashboard totals and performance metrics |
| GET | `/api/reports/branches` | Branch and semester comparison |

POST endpoints accept JSON. For example:
```json
{"roll_no":"CSE004","name":"Ananya Rao","branch_id":1,"semester":3}
```

## Grade rules
- A+: 90–100
- A: 80–89.99
- B: 70–79.99
- C: 60–69.99
- D: 50–59.99
- E: 40–49.99
- F: below 40

Pass threshold is 40%. These are demonstration rules: confirm your institution's actual grading policy before using real academic records. “Needs support” is an indicator based on the chosen threshold, not a complete assessment of a student's ability.

## Testing
```bash
pytest -q
```
The included unit tests validate grade boundaries and summary calculations. Run API/database integration tests manually using the checklist in `docs/TESTING.md`.

## Notes and known limitations
- This is an educational project starter, not a production-ready student information system.
- Add authentication/role-based authorization, CSRF protection where applicable, audit logging, pagination, backups, and deployment hardening before handling real student data.
- The dashboard class average is based on entered assessment records (each mark is one record), not an average of each student's overall final score.
- The branch report is a summary over recorded assessment marks; the student count includes branch/semester students whether or not they have marks.
- Matplotlib is listed for optional report image generation; the dashboard uses Chart.js in-browser.
- The current UI supports creating records, deleting students, and updating marks via re-entry. Student update API exists but editing is not wired into the UI.
