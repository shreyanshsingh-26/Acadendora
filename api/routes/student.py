from fastapi import APIRouter, HTTPException
from db import get_connection

router = APIRouter()

@router.get("/{student_id}/profile")
def get_student_profile(student_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT s.Person_ID, p.Full_Name, p.Email, p.Phone,
                   s.Enrollment_No, s.Status, d.Dept_Name,
                   CASE 
                       WHEN d.Department_ID = 1 THEN 'CSE'
                       WHEN d.Department_ID = 2 THEN 'ECE'
                       WHEN d.Department_ID = 4 THEN 'MnC'
                       ELSE d.Dept_Name 
                   END AS Department_Code,
                   COALESCE(sec.Section_Name, 'Unassigned') AS Batch_Name
            FROM STUDENT s
            JOIN PERSON p ON s.Person_ID = p.Person_ID
            JOIN DEPARTMENT d ON p.Department_ID = d.Department_ID
            LEFT JOIN ENROLLMENT e ON s.Person_ID = e.Student_ID
            LEFT JOIN SECTION sec ON e.Section_ID = sec.Section_ID
            WHERE s.Person_ID = %s
            LIMIT 1;
        """
        cursor.execute(query, (student_id,))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    finally:
        cursor.close()
        conn.close()
               
@router.get("/{student_id}/attendance-summary")
def get_attendance_summary(student_id: int):
    """Queries pre-computed view Student_Attendance_Summary."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT Course_ID, Course_Code, Course_Name,
                   Total_Sessions, Present_Count, Absent_Count, Other_Count,
                   Attendance_Pct,
                   IsEligible(Student_ID, Course_ID) AS Eligibility_Status
            FROM Student_Attendance_Summary
            WHERE Student_ID = %s;
        """
        cursor.execute(query, (student_id,))
        records = cursor.fetchall()
        for r in records:
            r["Attendance_Pct"] = float(r["Attendance_Pct"])
        return records
    finally:
        cursor.close()
        conn.close()

@router.get("/{student_id}/timetable")
def get_student_timetable(student_id: int):
    """Executes the 6-table INNER JOIN for class schedules."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT c.Course_Code, c.Course_Name,
                   p.Full_Name AS Faculty_Name, f.Office_Room,
                   r.Room_Number, r.Building,
                   ts.Day_Of_Week, ts.Start_Time, ts.End_Time,
                   sec.Section_Name
            FROM ENROLLMENT e
            INNER JOIN COURSE c ON e.Course_ID = c.Course_ID
            INNER JOIN TIMETABLE t ON t.Course_ID = c.Course_ID AND t.Section_ID = e.Section_ID
            INNER JOIN FACULTY f ON t.Faculty_ID = f.Person_ID
            INNER JOIN PERSON p ON f.Person_ID = p.Person_ID
            INNER JOIN ROOM r ON t.Room_ID = r.Room_ID
            INNER JOIN TIME_SLOT ts ON t.Slot_ID = ts.Slot_ID
            INNER JOIN SECTION sec ON t.Section_ID = sec.Section_ID
            WHERE e.Student_ID = %s
            ORDER BY FIELD(ts.Day_Of_Week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'),
                     ts.Start_Time ASC;
        """
        cursor.execute(query, (student_id,))
        records = cursor.fetchall()
        for r in records:
            r["Start_Time"] = str(r["Start_Time"])
            r["End_Time"] = str(r["End_Time"])
        return records
    finally:
        cursor.close()
        conn.close()
        