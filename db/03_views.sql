-- ========================================================
-- Acadendora: Pre-computed Analytics Views
-- ========================================================

USE acadendora_db;

-- 1. VIEW: Student Attendance Summary
-- Calculates per-student per-course aggregate metrics (Total, Present, Absent, %)
CREATE OR REPLACE VIEW Student_Attendance_Summary AS
SELECT 
    s.Person_ID AS Student_ID,
    p.Full_Name,
    s.Enrollment_No,
    c.Course_ID,
    c.Course_Code,
    c.Course_Name,
    COUNT(a.Session_ID) AS Total_Sessions,
    SUM(CASE WHEN a.Status = 'Present' THEN 1 ELSE 0 END) AS Present_Count,
    SUM(CASE WHEN a.Status = 'Absent' THEN 1 ELSE 0 END) AS Absent_Count,
    SUM(CASE WHEN a.Status IN ('Late', 'Excused') THEN 1 ELSE 0 END) AS Other_Count,
    ROUND(
        (SUM(CASE WHEN a.Status = 'Present' THEN 1 ELSE 0 END) / COUNT(a.Session_ID)) * 100, 
        2
    ) AS Attendance_Pct
FROM ATTENDANCE a
JOIN ATTENDANCE_SESSION ats ON a.Session_ID = ats.Session_ID
JOIN TIMETABLE t ON ats.Timetable_ID = t.Timetable_ID
JOIN COURSE c ON t.Course_ID = c.Course_ID
JOIN STUDENT s ON a.Student_ID = s.Person_ID
JOIN PERSON p ON s.Person_ID = p.Person_ID
GROUP BY s.Person_ID, c.Course_ID;

-- 2. VIEW: Shortage Alert View (Instant Debarment Detection < 75%)
CREATE OR REPLACE VIEW Shortage_Alert_View AS
SELECT 
    Student_ID,
    Full_Name,
    Enrollment_No,
    Course_Code,
    Course_Name,
    Total_Sessions,
    Present_Count,
    Attendance_Pct,
    'DEBARRED (<75%)' AS Debarment_Status
FROM Student_Attendance_Summary
WHERE Attendance_Pct < 75.00;

-- 3. VIEW: Faculty Workload View
-- Tracks how many lecture/lab sessions each faculty member has conducted
CREATE OR REPLACE VIEW Faculty_Workload_View AS
SELECT 
    f.Person_ID AS Faculty_ID,
    p.Full_Name AS Faculty_Name,
    f.Employee_Code,
    c.Course_Code,
    c.Course_Name,
    COUNT(ats.Session_ID) AS Sessions_Conducted,
    MONTHNAME(ats.Session_Date) AS Month_Name,
    YEAR(ats.Session_Date) AS Academic_Year
FROM FACULTY f
JOIN PERSON p ON f.Person_ID = p.Person_ID
JOIN ATTENDANCE_SESSION ats ON f.Person_ID = ats.Faculty_ID
JOIN TIMETABLE t ON ats.Timetable_ID = t.Timetable_ID
JOIN COURSE c ON t.Course_ID = c.Course_ID
GROUP BY f.Person_ID, c.Course_ID, MONTHNAME(ats.Session_Date), YEAR(ats.Session_Date);

-- 4. VIEW: Room Utilization View
CREATE OR REPLACE VIEW Room_Utilization_View AS
SELECT 
    r.Room_ID,
    r.Room_Number,
    r.Capacity,
    r.Building,
    COUNT(DISTINCT t.Slot_ID) AS Slots_Occupied,
    COUNT(ats.Session_ID) AS Total_Lectures_Held
FROM ROOM r
LEFT JOIN TIMETABLE t ON r.Room_ID = t.Room_ID
LEFT JOIN ATTENDANCE_SESSION ats ON t.Timetable_ID = ats.Timetable_ID
GROUP BY r.Room_ID;