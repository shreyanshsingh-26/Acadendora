-- ========================================================
-- Acadendora: Comprehensive Realistic Seed Data
-- ========================================================

USE acadendora_db;

-- 1. DEPARTMENTS
INSERT INTO DEPARTMENT (Department_ID, Dept_Code, Dept_Name) VALUES
(1, 'CSE', 'Computer Science and Engineering'),
(2, 'IT', 'Information Technology'),
(3, 'ECE', 'Electronics and Communication Engineering'),
(4, 'MNC', 'Mathematics and Computing');

-- 2. ROOMS
INSERT INTO ROOM (Room_ID, Room_Number, Capacity, Building) VALUES
(1, 'LT-101', 60, 'Academic Block 1'),
(2, 'LT-201', 60, 'Academic Block 2'),
(3, 'LAB-3', 35, 'Academic Block 3'),
(4, 'CR-04', 40, 'Academic Block 1');

-- 3. TIME_SLOTS
INSERT INTO TIME_SLOT (Slot_ID, Day_Of_Week, Start_Time, End_Time) VALUES
(1, 'Monday', '09:00:00', '10:00:00'),
(2, 'Monday', '10:00:00', '11:00:00'),
(3, 'Tuesday', '09:00:00', '10:00:00'),
(4, 'Wednesday', '11:00:00', '12:00:00'),
(5, 'Thursday', '14:00:00', '15:00:00'),
(6, 'Friday', '10:00:00', '11:00:00');

-- 4. PERSONS (Faculty IDs 1-7, Student IDs 8-17)
-- Faculty (7 members)
INSERT INTO PERSON (Person_ID, Email, Full_Name, Department_ID, Phone) VALUES
(1, 'aarti.goel@jiit.ac.in', 'Dr. Aarti Goel', 1, '9811001122'),
(2, 'abhishek.chaudhary@jiit.ac.in', 'Prof. Abhishek Chaudhary', 1, '9811003344'),
(3, 'neetu.singh@jiit.ac.in', 'Dr. Neetu Singh', 2, '9811005566'),
(4, 'vikas.saxena@jiit.ac.in', 'Dr. Vikas Saxena', 1, '9811007788'),
(5, 'manish.thakur@jiit.ac.in', 'Dr. Manish Kumar Thakur', 1, '9811009900'),
(6, 'chetna.gupta@jiit.ac.in', 'Dr. Chetna Gupta', 1, '9811002233'),
(7, 'sandeep.singh@jiit.ac.in', 'Dr. Sandeep Kumar Singh', 4, '9811004455');

-- Students (10 students)
INSERT INTO PERSON (Person_ID, Email, Full_Name, Department_ID, Phone) VALUES
(8, 'akshat.agarwal@mail.com', 'Akshat Agarwal', 1, '9999000001'),
(9, 'krish.gupta@mail.com', 'Krish Gupta', 1, '9999000002'),
(10, 'shreyansh.singh@mail.com', 'Shreyansh Singh', 1, '9999000003'),
(11, 'ananya.sharma@mail.com', 'Ananya Sharma', 1, '9999000004'),
(12, 'tanishqa@mail.com', 'Tanishqa', 1, '9999000005'),
(13, 'yashvi@mail.com', 'Yashvi', 1, '9999000006'),
(14, 'aarav.patel@mail.com', 'Aarav Patel', 2, '9999000007'),
(15, 'diya.verma@mail.com', 'Diya Verma', 2, '9999000008'),
(16, 'siddharth.m@mail.com', 'Siddharth Mishra', 1, '9999000009'),
(17, 'kavya.joshi@mail.com', 'Kavya Joshi', 4, '9999000010');

-- 5. FACULTY SUBCLASS
INSERT INTO FACULTY (Person_ID, Employee_Code, Designation, Office_Room) VALUES
(1, 'EMP101', 'Associate Professor', 'A-302'),
(2, 'EMP102', 'Assistant Professor', 'A-304'),
(3, 'EMP103', 'Professor', 'B-105'),
(4, 'EMP104', 'Professor & HOD', 'A-301'),
(5, 'EMP105', 'Professor', 'B-201'),
(6, 'EMP106', 'Associate Professor', 'A-205'),
(7, 'EMP107', 'Assistant Professor', 'B-102');

-- 6. STUDENT SUBCLASS
INSERT INTO STUDENT (Person_ID, Enrollment_No, DOB, Status) VALUES
(8, '2501030071', '2005-04-12', 'Active'),
(9, '2501030070', '2005-08-22', 'Active'),
(10, '2501030078', '2005-01-15', 'Active'),
(11, '2501030022', '2005-06-30', 'Active'),
(12, '2501030090', '2005-09-11', 'Active'),
(13, '2501030085', '2005-03-19', 'Active'),
(14, '2501040005', '2005-02-18', 'Active'),
(15, '2501040018', '2005-09-09', 'Active'),
(16, '2501030088', '2004-12-05', 'Active'),
(17, '2501030099', '2005-03-25', 'Active');

-- 7. COURSES
INSERT INTO COURSE (Course_ID, Course_Code, Course_Name, Department_ID, Credits) VALUES
(1, '24B15CS213', 'Database Management System Lab', 1, 2),
(2, '24B11CS211', 'Database Management Systems', 1, 4),
(3, '24B11CS212', 'Operating Systems', 1, 4),
(4, '24B11MA211', 'Discrete Mathematics', 4, 4);

-- 8. SECTIONS
INSERT INTO SECTION (Section_ID, Section_Name, Department_ID) VALUES
(1, 'B-11', 1),
(2, 'B-12', 1),
(3, 'MNC-1', 4);

-- 9. ENROLLMENTS (Section B-11 students)
INSERT INTO ENROLLMENT (Enrollment_ID, Student_ID, Course_ID, Section_ID, Semester) VALUES
(1, 8, 1, 1, 'Sem 3'),
(2, 9, 1, 1, 'Sem 3'),
(3, 10, 1, 1, 'Sem 3'),
(4, 11, 1, 1, 'Sem 3'),
(5, 12, 1, 1, 'Sem 3'),
(6, 13, 1, 1, 'Sem 3'),
(7, 16, 1, 1, 'Sem 3'),
(8, 17, 1, 1, 'Sem 3'),
-- DBMS Theory (Course 2)
(9, 8, 2, 1, 'Sem 3'),
(10, 9, 2, 1, 'Sem 3'),
(11, 10, 2, 1, 'Sem 3'),
(12, 11, 2, 1, 'Sem 3'),
(13, 12, 2, 1, 'Sem 3');

-- 10. TIMETABLE
INSERT INTO TIMETABLE (Timetable_ID, Course_ID, Faculty_ID, Section_ID, Room_ID, Slot_ID) VALUES
(1, 1, 1, 1, 3, 1), -- Dr. Aarti Goel | DBMS Lab | Section B-11 | LAB-3 (Academic Block 3) | Mon 9-10
(2, 2, 2, 1, 1, 2), -- Prof. Abhishek Chaudhary | DBMS Theory | Section B-11 | LT-101 (Academic Block 1) | Mon 10-11
(3, 3, 3, 1, 2, 3), -- Dr. Neetu Singh | OS | Section B-11 | LT-201 (Academic Block 2) | Tue 9-10
(4, 1, 1, 1, 3, 4); -- Dr. Aarti Goel | DBMS Lab | Section B-11 | LAB-3 (Academic Block 3) | Wed 11-12

-- 11. ATTENDANCE SESSIONS (4 sessions held)
INSERT INTO ATTENDANCE_SESSION (Session_ID, Timetable_ID, Faculty_ID, Session_Date, Topic_Delivered) VALUES
(1, 1, 1, '2026-11-02', 'Lab 1: EER Modeling and ER-to-Relational Mapping'),
(2, 1, 1, '2026-11-04', 'Lab 2: DDL Statements, Constraints, and Keys'),
(3, 1, 1, '2026-11-09', 'Lab 3: Advanced Joins and Aggregation Queries'),
(4, 1, 1, '2026-11-11', 'Lab 4: Triggers, Procedures, and ACID Transactions');

-- 12. ATTENDANCE RECORDS (32 total rows)
-- Session 1
INSERT INTO ATTENDANCE (Student_ID, Session_ID, Status) VALUES
(8, 1, 'Present'), (9, 1, 'Present'), (10, 1, 'Present'), (11, 1, 'Absent'),
(12, 1, 'Present'), (13, 1, 'Present'), (16, 1, 'Present'), (17, 1, 'Absent');

-- Session 2
INSERT INTO ATTENDANCE (Student_ID, Session_ID, Status) VALUES
(8, 2, 'Present'), (9, 2, 'Present'), (10, 2, 'Present'), (11, 2, 'Absent'),
(12, 2, 'Present'), (13, 2, 'Present'), (16, 2, 'Present'), (17, 2, 'Present');

-- Session 3
INSERT INTO ATTENDANCE (Student_ID, Session_ID, Status) VALUES
(8, 3, 'Present'), (9, 3, 'Present'), (10, 3, 'Present'), (11, 3, 'Absent'),
(12, 3, 'Present'), (13, 3, 'Present'), (16, 3, 'Absent'), (17, 3, 'Absent');

-- Session 4
INSERT INTO ATTENDANCE (Student_ID, Session_ID, Status) VALUES
(8, 4, 'Present'), (9, 4, 'Present'), (10, 4, 'Present'), (11, 4, 'Present'),
(12, 4, 'Present'), (13, 4, 'Present'), (16, 4, 'Present'), (17, 4, 'Present');

-- Resulting Attendance % in DBMS Lab:
-- Akshat (8), Krish (9), Shreyansh (10), Tanishqa (12), Yashvi (13): 4/4 = 100% (Eligible)
-- Siddharth (16): 3/4 = 75% (Eligible border)
-- Kavya (17): 2/4 = 50% (DEBARRED / SHORTAGE < 75%)
-- Ananya (11): 1/4 = 25% (DEBARRED / SHORTAGE < 75%)

-- 13. SAMPLE LEAVE REQUEST (Ananya on medical leave)
INSERT INTO LEAVE_REQUEST (Leave_ID, Person_ID, Leave_Date, Reason, Status) VALUES
(1, 11, '2026-11-09', 'Medical Leave: Severe Typhoid', 'Approved');