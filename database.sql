CREATE DATABASE IF NOT EXISTS student_performance
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE student_performance;

CREATE TABLE IF NOT EXISTS branches (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  roll_no VARCHAR(30) NOT NULL UNIQUE,
  name VARCHAR(120) NOT NULL,
  branch_id INT NOT NULL,
  semester TINYINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_student_branch FOREIGN KEY (branch_id) REFERENCES branches(id),
  CONSTRAINT chk_student_semester CHECK (semester BETWEEN 1 AND 8)
);
CREATE TABLE IF NOT EXISTS subjects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(30) NOT NULL UNIQUE,
  name VARCHAR(120) NOT NULL,
  branch_id INT NULL,
  CONSTRAINT fk_subject_branch FOREIGN KEY (branch_id) REFERENCES branches(id)
);
CREATE TABLE IF NOT EXISTS branch_subjects (
  branch_id INT NOT NULL,
  subject_id INT NOT NULL,
  PRIMARY KEY (branch_id, subject_id),
  FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS assessments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(120) NOT NULL,
  subject_id INT NOT NULL,
  semester TINYINT NOT NULL,
  max_marks DECIMAL(7,2) NOT NULL,
  exam_date DATE NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (subject_id) REFERENCES subjects(id),
  CONSTRAINT chk_assessment_semester CHECK (semester BETWEEN 1 AND 8),
  CONSTRAINT chk_max_marks CHECK (max_marks > 0)
);
CREATE TABLE IF NOT EXISTS marks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  assessment_id INT NOT NULL,
  marks_obtained DECIMAL(7,2) NOT NULL,
  UNIQUE KEY uq_student_assessment (student_id, assessment_id),
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
  CONSTRAINT chk_marks_nonnegative CHECK (marks_obtained >= 0)
);

INSERT IGNORE INTO branches(name) VALUES ('CSE'), ('ECE'), ('EEE');
INSERT IGNORE INTO students(roll_no,name,branch_id,semester)
SELECT 'CSE001','Aarav Kumar',id,3 FROM branches WHERE name='CSE';
INSERT IGNORE INTO students(roll_no,name,branch_id,semester)
SELECT 'CSE002','Meera Reddy',id,3 FROM branches WHERE name='CSE';
INSERT IGNORE INTO students(roll_no,name,branch_id,semester)
SELECT 'CSE003','Rahul Sharma',id,3 FROM branches WHERE name='CSE';
INSERT IGNORE INTO subjects(code,name,branch_id)
SELECT 'CS301','Data Structures',id FROM branches WHERE name='CSE';
INSERT IGNORE INTO subjects(code,name,branch_id)
SELECT 'CS302','Database Management Systems',id FROM branches WHERE name='CSE';
INSERT IGNORE INTO branch_subjects(branch_id,subject_id)
SELECT b.id,s.id FROM branches b JOIN subjects s ON s.branch_id=b.id;
INSERT IGNORE INTO assessments(title,subject_id,semester,max_marks,exam_date)
SELECT 'Midterm 1',id,3,100,'2026-10-15' FROM subjects WHERE code='CS301';
INSERT IGNORE INTO assessments(title,subject_id,semester,max_marks,exam_date)
SELECT 'Midterm 1',id,3,100,'2026-10-15' FROM subjects WHERE code='CS302';
INSERT IGNORE INTO marks(student_id,assessment_id,marks_obtained)
SELECT st.id,a.id,
 CASE st.roll_no WHEN 'CSE001' THEN 84 WHEN 'CSE002' THEN 67 ELSE 34 END
FROM students st CROSS JOIN assessments a
WHERE st.roll_no LIKE 'CSE%' AND a.title='Midterm 1';
