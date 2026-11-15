-- ========================================================
-- Acadendora: Row-Level Triggers & Automated Audit Logging
-- ========================================================

USE acadendora_db;

DROP TRIGGER IF EXISTS trg_attendance_audit;

DROP TRIGGER IF EXISTS trg_validate_enrollment;

DROP TRIGGER IF EXISTS trg_prevent_faculty_clash;

DELIMITER $$

-- 1. TRIGGER: Automated Audit Log on Attendance Update
-- Ensures institutional non-repudiation by logging any change
CREATE TRIGGER trg_attendance_audit
AFTER UPDATE ON ATTENDANCE
FOR EACH ROW
BEGIN
    INSERT INTO ATTENDANCE_AUDIT (
        Student_ID, 
        Session_ID, 
        Old_Status, 
        New_Status, 
        Changed_By, 
        Changed_At, 
        Change_Reason
    )
    VALUES (
        OLD.Student_ID,
        OLD.Session_ID,
        OLD.Status,
        NEW.Status,
        CURRENT_USER(),
        NOW(),
        'Authorized override via system'
    );
END$$

-- 2. TRIGGER: Validate Enrollment Before Marking Attendance
-- Prevents marking attendance for a student not enrolled in the course
CREATE TRIGGER trg_validate_enrollment
BEFORE INSERT ON ATTENDANCE
FOR EACH ROW
BEGIN
    DECLARE is_enrolled INT DEFAULT 0;

    SELECT COUNT(*) INTO is_enrolled
    FROM ENROLLMENT e
    JOIN TIMETABLE t ON e.Course_ID = t.Course_ID AND e.Section_ID = t.Section_ID
    JOIN ATTENDANCE_SESSION ats ON ats.Timetable_ID = t.Timetable_ID
    WHERE e.Student_ID = NEW.Student_ID 
      AND ats.Session_ID = NEW.Session_ID;

    IF is_enrolled = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Violation: Student is not enrolled in this course or section.';
    END IF;
END$$

-- 3. TRIGGER: Anti-Double-Booking Guard on Timetable
CREATE TRIGGER trg_prevent_faculty_clash
BEFORE INSERT ON TIMETABLE
FOR EACH ROW
BEGIN
    DECLARE clash_count INT DEFAULT 0;

    SELECT COUNT(*) INTO clash_count
    FROM TIMETABLE
    WHERE Faculty_ID = NEW.Faculty_ID 
      AND Slot_ID = NEW.Slot_ID;

    IF clash_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Scheduling Conflict: Faculty already has a scheduled lecture in this time slot.';
    END IF;
END$$

DELIMITER;