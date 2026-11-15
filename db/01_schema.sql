-- ========================================================
-- Acadendora: 14-Table 3NF Normalized Schema
-- Database Management System Laboratory Project
-- ========================================================

DROP DATABASE IF EXISTS acadendora_db;
CREATE DATABASE acadendora_db;
USE acadendora_db;

-- 1. DEPARTMENT
CREATE TABLE DEPARTMENT (
    Department_ID INT AUTO_INCREMENT PRIMARY KEY,
    Dept_Code VARCHAR(10) UNIQUE NOT NULL,
    Dept_Name VARCHAR(100) NOT NULL
);

-- 2. ROOM
CREATE TABLE ROOM (
    Room_ID INT AUTO_INCREMENT PRIMARY KEY,
    Room_Number VARCHAR(20) UNIQUE NOT NULL,
    Capacity INT CHECK (Capacity > 0),
    Building VARCHAR(50) NOT NULL
);

-- 3. TIME_SLOT
CREATE TABLE TIME_SLOT (
    Slot_ID INT AUTO_INCREMENT PRIMARY KEY,
    Day_Of_Week VARCHAR(10) NOT NULL,
    Start_Time TIME NOT NULL,
    End_Time TIME NOT NULL,
    UNIQUE (Day_Of_Week, Start_Time, End_Time)
);

-- 4. PERSON (Superclass: EER Disjoint Specialization)
CREATE TABLE PERSON (
    Person_ID INT AUTO_INCREMENT PRIMARY KEY,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Full_Name VARCHAR(150) NOT NULL,
    Department_ID INT NOT NULL,
    Phone VARCHAR(15),
    FOREIGN KEY (Department_ID) REFERENCES DEPARTMENT(Department_ID) ON DELETE RESTRICT
);

-- 5. STUDENT (Subclass inheriting from PERSON)
CREATE TABLE STUDENT (
    Person_ID INT PRIMARY KEY,
    Enrollment_No VARCHAR(20) UNIQUE NOT NULL,
    DOB DATE,
    Status VARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'Inactive', 'Graduated')),
    FOREIGN KEY (Person_ID) REFERENCES PERSON(Person_ID) ON DELETE CASCADE
);

-- 6. FACULTY (Subclass inheriting from PERSON)
CREATE TABLE FACULTY (
    Person_ID INT PRIMARY KEY,
    Employee_Code VARCHAR(20) UNIQUE NOT NULL,
    Designation VARCHAR(50) NOT NULL,
    Office_Room VARCHAR(20),
    FOREIGN KEY (Person_ID) REFERENCES PERSON(Person_ID) ON DELETE CASCADE
);

-- 7. COURSE
CREATE TABLE COURSE (
    Course_ID INT AUTO_INCREMENT PRIMARY KEY,
    Course_Code VARCHAR(20) UNIQUE NOT NULL,
    Course_Name VARCHAR(100) NOT NULL,
    Department_ID INT NOT NULL,
    Credits INT CHECK (Credits > 0),
    FOREIGN KEY (Department_ID) REFERENCES DEPARTMENT(Department_ID) ON DELETE RESTRICT
);

-- 8. SECTION
CREATE TABLE SECTION (
    Section_ID INT AUTO_INCREMENT PRIMARY KEY,
    Section_Name VARCHAR(10) NOT NULL,
    Department_ID INT NOT NULL,
    FOREIGN KEY (Department_ID) REFERENCES DEPARTMENT(Department_ID) ON DELETE RESTRICT
);

-- 9. ENROLLMENT (Associative Entity)
CREATE TABLE ENROLLMENT (
    Enrollment_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID INT NOT NULL,
    Course_ID INT NOT NULL,
    Section_ID INT NOT NULL,
    Semester VARCHAR(10) NOT NULL,
    UNIQUE (Student_ID, Course_ID, Semester),
    FOREIGN KEY (Student_ID) REFERENCES STUDENT(Person_ID) ON DELETE CASCADE,
    FOREIGN KEY (Course_ID) REFERENCES COURSE(Course_ID) ON DELETE RESTRICT,
    FOREIGN KEY (Section_ID) REFERENCES SECTION(Section_ID) ON DELETE RESTRICT
);

-- 10. TIMETABLE (Nexus Entity linking Course, Faculty, Section, Room, Slot)
CREATE TABLE TIMETABLE (
    Timetable_ID INT AUTO_INCREMENT PRIMARY KEY,
    Course_ID INT NOT NULL,
    Faculty_ID INT NOT NULL,
    Section_ID INT NOT NULL,
    Room_ID INT NOT NULL,
    Slot_ID INT NOT NULL,
    UNIQUE (Room_ID, Slot_ID),          -- Anti-Double-Booking Constraint for Rooms
    UNIQUE (Faculty_ID, Slot_ID),       -- Anti-Double-Booking Constraint for Faculty
    FOREIGN KEY (Course_ID) REFERENCES COURSE(Course_ID) ON DELETE RESTRICT,
    FOREIGN KEY (Faculty_ID) REFERENCES FACULTY(Person_ID) ON DELETE RESTRICT,
    FOREIGN KEY (Section_ID) REFERENCES SECTION(Section_ID) ON DELETE RESTRICT,
    FOREIGN KEY (Room_ID) REFERENCES ROOM(Room_ID) ON DELETE RESTRICT,
    FOREIGN KEY (Slot_ID) REFERENCES TIME_SLOT(Slot_ID) ON DELETE RESTRICT
);

-- 11. ATTENDANCE_SESSION
CREATE TABLE ATTENDANCE_SESSION (
    Session_ID INT AUTO_INCREMENT PRIMARY KEY,
    Timetable_ID INT NOT NULL,
    Faculty_ID INT NOT NULL,
    Session_Date DATE NOT NULL,
    Topic_Delivered VARCHAR(200),
    FOREIGN KEY (Timetable_ID) REFERENCES TIMETABLE(Timetable_ID) ON DELETE RESTRICT,
    FOREIGN KEY (Faculty_ID) REFERENCES FACULTY(Person_ID) ON DELETE RESTRICT
);

-- 12. ATTENDANCE (Composite Primary Key: Student_ID + Session_ID)
CREATE TABLE ATTENDANCE (
    Student_ID INT NOT NULL,
    Session_ID INT NOT NULL,
    Status ENUM('Present', 'Absent', 'Late', 'Excused') NOT NULL,
    Marked_At DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (Student_ID, Session_ID),
    FOREIGN KEY (Student_ID) REFERENCES STUDENT(Person_ID) ON DELETE CASCADE,
    FOREIGN KEY (Session_ID) REFERENCES ATTENDANCE_SESSION(Session_ID) ON DELETE CASCADE
);

-- 13. ATTENDANCE_AUDIT (Immutable Log populated by Triggers)
CREATE TABLE ATTENDANCE_AUDIT (
    Audit_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID INT NOT NULL,
    Session_ID INT NOT NULL,
    Old_Status VARCHAR(20),
    New_Status VARCHAR(20),
    Changed_By VARCHAR(100),
    Changed_At DATETIME DEFAULT CURRENT_TIMESTAMP,
    Change_Reason VARCHAR(300)
);

-- 14. LEAVE_REQUEST
CREATE TABLE LEAVE_REQUEST (
    Leave_ID INT AUTO_INCREMENT PRIMARY KEY,
    Person_ID INT NOT NULL,
    Leave_Date DATE NOT NULL,
    Reason VARCHAR(300),
    Status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    Applied_At DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Person_ID) REFERENCES PERSON(Person_ID) ON DELETE CASCADE
);