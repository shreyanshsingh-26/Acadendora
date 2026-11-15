USE acadendora_db;

DROP FUNCTION IF EXISTS CalculateAttendance;

DROP FUNCTION IF EXISTS IsEligible;

DELIMITER / /

CREATE FUNCTION CalculateAttendance(p_student_id INT, p_course_id INT)
RETURNS DECIMAL(5,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_sessions INT DEFAULT 0;
    DECLARE present_sessions INT DEFAULT 0;
    DECLARE attendance_pct DECIMAL(5,2) DEFAULT 0.00;

    SELECT 
        COUNT(a.Session_ID),
        SUM(CASE WHEN a.Status = 'Present' THEN 1 ELSE 0 END)
    INTO total_sessions, present_sessions
    FROM ATTENDANCE a
    JOIN ATTENDANCE_SESSION ats ON a.Session_ID = ats.Session_ID
    JOIN TIMETABLE t ON ats.Timetable_ID = t.Timetable_ID
    WHERE a.Student_ID = p_student_id AND t.Course_ID = p_course_id;

    IF total_sessions > 0 THEN
        SET attendance_pct = ROUND((present_sessions / total_sessions) * 100, 2);
    END IF;

    RETURN attendance_pct;
END
//

CREATE FUNCTION IsEligible(p_student_id INT, p_course_id INT)
RETURNS VARCHAR(20)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE pct DECIMAL(5,2);
    SET pct = CalculateAttendance(p_student_id, p_course_id);

    IF pct >= 75.00 THEN
        RETURN 'Eligible';
    ELSE
        RETURN 'Debarred';
    END IF;
END
//

DELIMITER;