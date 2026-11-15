-- ========================================================
-- Acadendora: Stored Procedures
-- ========================================================

USE acadendora_db;

DROP PROCEDURE IF EXISTS CreateAttendanceSession;

DROP PROCEDURE IF EXISTS OverrideAttendance;

DELIMITER $$

-- 1. PROCEDURE: CreateAttendanceSession
-- Inserts a session record and outputs the generated Session_ID
CREATE PROCEDURE CreateAttendanceSession(
    IN p_timetable_id INT,
    IN p_faculty_id INT,
    IN p_date DATE,
    IN p_topic VARCHAR(200),
    OUT p_session_id INT
)
BEGIN
    INSERT INTO ATTENDANCE_SESSION (Timetable_ID, Faculty_ID, Session_Date, Topic_Delivered)
    VALUES (p_timetable_id, p_faculty_id, p_date, p_topic);
    
    SET p_session_id = LAST_INSERT_ID();
END$$

-- 2. PROCEDURE: OverrideAttendance
-- Updates attendance record (which fires our audit trigger)
CREATE PROCEDURE OverrideAttendance(
    IN p_student_id INT,
    IN p_session_id INT,
    IN p_new_status ENUM('Present', 'Absent', 'Late', 'Excused'),
    IN p_reason VARCHAR(300),
    IN p_changed_by VARCHAR(100)
)
BEGIN
    UPDATE ATTENDANCE
    SET Status = p_new_status
    WHERE Student_ID = p_student_id AND Session_ID = p_session_id;
END$$

DELIMITER;