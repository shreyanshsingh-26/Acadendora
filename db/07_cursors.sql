-- ========================================================
-- Acadendora: Database Cursors
-- Sequential cursor iterating active students to compile monthly digests
-- ========================================================

USE acadendora_db;

DROP PROCEDURE IF EXISTS GenerateMonthlyDigest;

DELIMITER $$

CREATE PROCEDURE GenerateMonthlyDigest(IN p_month INT, IN p_year INT)
BEGIN
    -- 1. Declare loop control and cursor variables
    DECLARE v_done INT DEFAULT 0;
    DECLARE v_student_id INT;
    DECLARE v_full_name VARCHAR(150);
    DECLARE v_enrollment_no VARCHAR(20);
    DECLARE v_avg_attendance DECIMAL(5,2);
    DECLARE v_risk_status VARCHAR(20);

    -- 2. Declare the cursor over active students
    DECLARE student_cursor CURSOR FOR
        SELECT s.Person_ID, p.Full_Name, s.Enrollment_No
        FROM STUDENT s
        JOIN PERSON p ON s.Person_ID = p.Person_ID
        WHERE s.Status = 'Active'
        ORDER BY p.Full_Name ASC;

    -- 3. Declare NOT FOUND handler to exit loop cleanly
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    -- 4. Create an in-memory temporary table for the compiled digest
    DROP TEMPORARY TABLE IF EXISTS Monthly_Performance_Digest;
    CREATE TEMPORARY TABLE Monthly_Performance_Digest (
        Student_ID INT,
        Full_Name VARCHAR(150),
        Enrollment_No VARCHAR(20),
        Average_Attendance_Pct DECIMAL(5,2),
        Risk_Category VARCHAR(20)
    );

    -- 5. Open and iterate with the cursor
    OPEN student_cursor;

    cursor_loop: LOOP
        FETCH student_cursor INTO v_student_id, v_full_name, v_enrollment_no;
        
        IF v_done = 1 THEN
            LEAVE cursor_loop;
        END IF;

        -- Calculate average attendance across all enrolled courses for this student
        SELECT IFNULL(ROUND(AVG(CalculateAttendance(v_student_id, e.Course_ID)), 2), 0.00)
        INTO v_avg_attendance
        FROM ENROLLMENT e
        WHERE e.Student_ID = v_student_id;

        -- Evaluate risk categorization
        IF v_avg_attendance < 60.00 THEN
            SET v_risk_status = 'CRITICAL RISK';
        ELSEIF v_avg_attendance < 75.00 THEN
            SET v_risk_status = 'AT RISK (<75%)';
        ELSE
            SET v_risk_status = 'GOOD STANDING';
        END IF;

        -- Insert compiled row into temporary table
        INSERT INTO Monthly_Performance_Digest VALUES (
            v_student_id,
            v_full_name,
            v_enrollment_no,
            v_avg_attendance,
            v_risk_status
        );
    END LOOP cursor_loop;

    -- 6. Close the cursor
    CLOSE student_cursor;

    -- 7. Output the compiled monthly digest ordered by highest risk first
    SELECT * 
    FROM Monthly_Performance_Digest
    ORDER BY Average_Attendance_Pct ASC;
END$$

DELIMITER;