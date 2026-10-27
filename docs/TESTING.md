# Testing and delivery checklist

## Unit tests
- Run `pytest -q`.
- Check grade thresholds: 39.99, 40, 50, 60, 70, 80 and 90.
- Check summary behavior for an empty record list and mixed pass/fail records.

## API and database integration tests
Run the application, then use browser devtools, Postman, or curl.

1. `GET /api/health` returns HTTP 200 and `{"status":"ok","database":"connected"}`.
2. `GET /api/branches` returns seeded branches.
3. Create a branch with `POST /api/branches` and JSON `{"name":"IT"}`; expect 201. Repeat the same name; expect 409.
4. Create a student using an existing branch ID. Missing required fields should return 400; duplicate roll number should return 409.
5. Create a subject, then an assessment with positive maximum marks.
6. Record a mark at 0 and at the maximum; both should be accepted. A negative mark or mark above maximum should return 400.
7. Submit a second mark for the same student/assessment; it should update the value rather than create a duplicate.
8. `GET /api/results` includes percentage, grade, and status.
9. `GET /api/reports/branches` groups records by branch and semester.
10. Delete a test student and verify their marks are removed due to the foreign-key cascade.

## Frontend checks
- Open every sidebar page at desktop and mobile widths.
- Add a branch, student, subject, assessment, and mark using forms.
- Verify dashboard counts and charts update after data changes.
- Search the student directory and results register.
- Export the results table to CSV and open it in a spreadsheet application.
- Confirm empty states and error notifications are readable.

## Database validation
- Confirm unique roll numbers, branch names, subject codes, and student/assessment mark pairs.
- Confirm foreign keys reject invalid branch, subject, student, and assessment IDs.
- Confirm `marks_obtained` cannot be negative and does not exceed assessment maximum through API validation.
- Back up the database before experimenting with real data.

## Delivery checklist
- Include `README.md`, `database.sql`, `.env.example`, `requirements.txt`, `docs/TESTING.md`, and source code.
- Remove real credentials and any real student-identifying data from the repository.
- Run tests in a clean virtual environment.
- Record Python/MySQL versions and screenshots of the working app in the project report.
- If publishing to GitHub, verify `.gitignore` excludes `.venv`, `.env`, `__pycache__`, and secrets before the first push.
