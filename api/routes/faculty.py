from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from db import get_connection

router = APIRouter()

class StudentAttendanceInput(BaseModel):
    student_id: int
    status: str  # Present, Absent, Late, Excused

class BulkAttendanceRequest(BaseModel):
    timetable_id: int
    faculty_id: int
    session_date: str  # YYYY-MM-DD
    topic: str
    attendance_records: List[StudentAttendanceInput]

class OverrideRequest(BaseModel):
    student_id: int
    session_id: int
    new_status: str
    reason: str
    changed_by: str = "Faculty"

@router.get("/{faculty_id}/assigned-classes")
def get_assigned_classes(faculty_id: int):
    """Fetches assigned timetable sessions with strict role isolation."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT t.Timetable_ID, c.Course_Code, c.Course_Name,
                   s.Section_Name, r.Room_Number, r.Building,
                   ts.Day_Of_Week, ts.Start_Time, ts.End_Time
            FROM TIMETABLE t
            JOIN COURSE c ON t.Course_ID = c.Course_ID
            JOIN SECTION s ON t.Section_ID = s.Section_ID
            JOIN ROOM r ON t.Room_ID = r.Room_ID
            JOIN TIME_SLOT ts ON t.Slot_ID = ts.Slot_ID
            WHERE t.Faculty_ID = %s
            ORDER BY FIELD(ts.Day_Of_Week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'),
                     ts.Start_Time ASC;
        """
        cursor.execute(query, (faculty_id,))
        records = cursor.fetchall()
        for r in records:
            r["Start_Time"] = str(r["Start_Time"])
            r["End_Time"] = str(r["End_Time"])
        return records
    finally:
        cursor.close()
        conn.close()

@router.get("/roster/{timetable_id}")
def get_class_roster(timetable_id: int):
    """Resolves students enrolled in the exact course and section of the timetable slot."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT s.Person_ID AS Student_ID, p.Full_Name, s.Enrollment_No
            FROM TIMETABLE t
            JOIN ENROLLMENT e ON t.Course_ID = e.Course_ID AND t.Section_ID = e.Section_ID
            JOIN STUDENT s ON e.Student_ID = s.Person_ID
            JOIN PERSON p ON s.Person_ID = p.Person_ID
            WHERE t.Timetable_ID = %s
            ORDER BY p.Full_Name ASC;
        """
        cursor.execute(query, (timetable_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router.get("/{faculty_id}/history")
def get_faculty_history(faculty_id: int):
    """Fetches past attendance sessions marked by this faculty, including audit change count."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT ats.Session_ID, ats.Session_Date, ats.Topic_Delivered,
                   c.Course_Code, c.Course_Name, sec.Section_Name,
                   COUNT(a.Student_ID) AS Total_Students,
                   COALESCE(SUM(CASE WHEN a.Status = 'Present' THEN 1 ELSE 0 END), 0) AS Present_Count,
                   COALESCE(SUM(CASE WHEN a.Status = 'Absent' THEN 1 ELSE 0 END), 0) AS Absent_Count,
                   (SELECT COUNT(*) FROM ATTENDANCE_AUDIT au WHERE au.Session_ID = ats.Session_ID) AS Override_Count
            FROM ATTENDANCE_SESSION ats
            JOIN TIMETABLE t ON ats.Timetable_ID = t.Timetable_ID
            JOIN COURSE c ON t.Course_ID = c.Course_ID
            JOIN SECTION sec ON t.Section_ID = sec.Section_ID
            LEFT JOIN ATTENDANCE a ON ats.Session_ID = a.Session_ID
            WHERE t.Faculty_ID = %s OR ats.Faculty_ID = %s
            GROUP BY ats.Session_ID, ats.Session_Date, ats.Topic_Delivered,
                     c.Course_Code, c.Course_Name, sec.Section_Name
            ORDER BY ats.Session_ID DESC
            LIMIT 25;
        """
        cursor.execute(query, (faculty_id, faculty_id))
        records = cursor.fetchall()
        for r in records:
            r["Session_Date"] = str(r["Session_Date"])
            r["Total_Students"] = int(r["Total_Students"] or 0)
            r["Present_Count"] = int(r["Present_Count"] or 0)
            r["Absent_Count"] = int(r["Absent_Count"] or 0)
            r["Override_Count"] = int(r["Override_Count"] or 0)
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/audit-logs")
def get_audit_logs(faculty_id: int = None):
    """Fetches audit trail entries isolated to the active faculty."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if faculty_id:
            query = """
                SELECT au.Audit_ID, au.Student_ID, p.Full_Name AS Student_Name,
                       au.Session_ID, au.Old_Status, au.New_Status,
                       au.Changed_By, au.Changed_At, au.Change_Reason
                FROM ATTENDANCE_AUDIT au
                LEFT JOIN PERSON p ON au.Student_ID = p.Person_ID
                LEFT JOIN ATTENDANCE_SESSION ats ON au.Session_ID = ats.Session_ID
                LEFT JOIN TIMETABLE t ON ats.Timetable_ID = t.Timetable_ID
                WHERE t.Faculty_ID = %s 
                   OR ats.Faculty_ID = %s
                   OR au.Changed_By = (SELECT Full_Name FROM PERSON WHERE Person_ID = %s)
                ORDER BY au.Audit_ID DESC
                LIMIT 25;
            """
            cursor.execute(query, (faculty_id, faculty_id, faculty_id))
        else:
            query = """
                SELECT au.Audit_ID, au.Student_ID, p.Full_Name AS Student_Name,
                       au.Session_ID, au.Old_Status, au.New_Status,
                       au.Changed_By, au.Changed_At, au.Change_Reason
                FROM ATTENDANCE_AUDIT au
                LEFT JOIN PERSON p ON au.Student_ID = p.Person_ID
                ORDER BY au.Audit_ID DESC
                LIMIT 25;
            """
            cursor.execute(query)
        records = cursor.fetchall()
        for r in records:
            r["Changed_At"] = str(r["Changed_At"])
        return records
    finally:
        cursor.close()
        conn.close()

@router.post("/mark-attendance")
def bulk_mark_attendance(payload: BulkAttendanceRequest):
    """
    EXPLICIT ACID TRANSACTION:
    START TRANSACTION -> CreateAttendanceSession -> Bulk Insert Attendance -> COMMIT.
    Rolls back automatically on ANY error.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        cursor.execute(
            "CALL CreateAttendanceSession(%s, %s, %s, %s, @sess_id);",
            (payload.timetable_id, payload.faculty_id, payload.session_date, payload.topic)
        )
        cursor.execute("SELECT @sess_id;")
        row = cursor.fetchone()
        session_id = row[0] if row else None

        if not session_id or session_id == 0:
            cursor.execute("SELECT LAST_INSERT_ID();")
            session_id = cursor.fetchone()[0]

        insert_query = """
            INSERT INTO ATTENDANCE (Student_ID, Session_ID, Status)
            VALUES (%s, %s, %s);
        """
        records_to_insert = [
            (rec.student_id, session_id, rec.status)
            for rec in payload.attendance_records
        ]
        cursor.executemany(insert_query, records_to_insert)
        conn.commit()
        return {
            "status": "success",
            "transaction": "COMMITTED",
            "session_id": session_id,
            "records_marked": len(payload.attendance_records),
            "atomicity": "Guaranteed"
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail={"error": str(e), "transaction": "ROLLED BACK"}
        )
    finally:
        cursor.close()
        conn.close()

@router.put("/override-attendance")
def override_student_attendance(payload: OverrideRequest):
    """Calls OverrideAttendance procedure (which activates trg_attendance_audit)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SET @audit_user = %s;", (payload.changed_by,))
        cursor.execute("SET @audit_reason = %s;", (payload.reason,))
        cursor.callproc(
            "OverrideAttendance",
            [payload.student_id, payload.session_id, payload.new_status, payload.reason, payload.changed_by]
        )
        conn.commit()
        return {
            "status": "success",
            "message": "Attendance overridden successfully",
            "audit_trigger_fired": True
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ── NEW ENDPOINT ──────────────────────────────────────────────────────────────
@router.get("/roster-by-session/{session_id}")
def get_roster_by_session(session_id: int):
    """Returns all students + their current status for a given session (for override dropdown)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT s.Person_ID AS Student_ID, p.Full_Name, s.Enrollment_No,
                   a.Status AS Current_Status
            FROM ATTENDANCE a
            JOIN STUDENT s ON a.Student_ID = s.Person_ID
            JOIN PERSON p ON s.Person_ID = p.Person_ID
            WHERE a.Session_ID = %s
            ORDER BY p.Full_Name ASC;
        """
        cursor.execute(query, (session_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()