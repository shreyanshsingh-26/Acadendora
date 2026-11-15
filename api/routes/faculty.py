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
    changed_by: str = "Faculty / Dr. Aarti Goel"

@router.get("/{faculty_id}/assigned-classes")
def get_assigned_classes(faculty_id: int):
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
            WHERE t.Faculty_ID = %s;
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
        # 1. START ACID TRANSACTION
        conn.start_transaction()

        # 2. Call Stored Procedure to create session
        cursor.callproc(
            "CreateAttendanceSession",
            [payload.timetable_id, payload.faculty_id, payload.session_date, payload.topic, 0]
        )
        cursor.execute("SELECT @_CreateAttendanceSession_4;")
        session_id = cursor.fetchone()[0]

        # 3. Bulk insert attendance records
        insert_query = """
            INSERT INTO ATTENDANCE (Student_ID, Session_ID, Status)
            VALUES (%s, %s, %s);
        """
        records_to_insert = [
            (rec.student_id, session_id, rec.status)
            for rec in payload.attendance_records
        ]
        cursor.executemany(insert_query, records_to_insert)

        # 4. COMMIT TRANSACTION
        conn.commit()

        return {
            "status": "success",
            "transaction": "COMMITTED",
            "session_id": session_id,
            "records_marked": len(payload.attendance_records),
            "atomicity": "Guaranteed"
        }
    except Exception as e:
        # ROLLBACK TRANSACTION ON FAILURE
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
    """Calls OverrideAttendance procedure (which triggers trg_attendance_audit)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
    finally:
        cursor.close()
        conn.close()
        