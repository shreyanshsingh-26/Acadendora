from fastapi import APIRouter, HTTPException
from db import get_connection

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /api/admin/stats
# ---------------------------------------------------------------------------
@router.get("/stats")
def get_stats():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS cnt FROM STUDENT")
        total_students = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) AS cnt FROM FACULTY")
        total_faculty = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) AS cnt FROM ATTENDANCE_SESSION")
        total_sessions = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) AS cnt FROM ATTENDANCE")
        total_attendance_records = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) AS cnt FROM ATTENDANCE_AUDIT")
        total_overrides = cursor.fetchone()["cnt"]

        cursor.execute("""
            SELECT
                ROUND(
                    100.0 * SUM(CASE WHEN Status IN ('Present', 'Late') THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS pct
            FROM ATTENDANCE
        """)
        row = cursor.fetchone()
        overall_attendance_pct = float(row["pct"]) if row and row["pct"] is not None else 0.0

        return {
            "total_students":          int(total_students),
            "total_faculty":           int(total_faculty),
            "total_sessions":          int(total_sessions),
            "total_attendance_records": int(total_attendance_records),
            "total_overrides":         int(total_overrides),
            "overall_attendance_pct":  overall_attendance_pct,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


# ---------------------------------------------------------------------------
# GET /api/admin/debarred
# ---------------------------------------------------------------------------
@router.get("/debarred")
def get_debarred():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                s.Person_ID           AS Student_ID,
                p.Full_Name,
                s.Enrollment_No,
                c.Course_Code,
                c.Course_Name,
                sec.Section_Name,
                COUNT(a.Session_ID)                                                AS Total_Sessions,
                COALESCE(SUM(CASE WHEN a.Status IN ('Present','Late') THEN 1 ELSE 0 END), 0) AS Present_Count,
                ROUND(
                    100.0 * COALESCE(SUM(CASE WHEN a.Status IN ('Present','Late') THEN 1 ELSE 0 END), 0)
                    / NULLIF(COUNT(a.Session_ID), 0),
                    2
                )                                                                  AS Attendance_Pct
            FROM ENROLLMENT e
            JOIN STUDENT   s   ON e.Student_ID  = s.Person_ID
            JOIN PERSON    p   ON s.Person_ID   = p.Person_ID
            JOIN COURSE    c   ON e.Course_ID   = c.Course_ID
            JOIN SECTION   sec ON e.Section_ID  = sec.Section_ID
            LEFT JOIN (
                SELECT a2.Student_ID, a2.Session_ID, a2.Status,
                       t.Course_ID, t.Section_ID
                FROM ATTENDANCE a2
                JOIN ATTENDANCE_SESSION ats2 ON a2.Session_ID   = ats2.Session_ID
                JOIN TIMETABLE          t    ON ats2.Timetable_ID = t.Timetable_ID
            ) a ON  a.Student_ID = e.Student_ID
                AND a.Course_ID  = e.Course_ID
                AND a.Section_ID = e.Section_ID
            GROUP BY s.Person_ID, p.Full_Name, s.Enrollment_No,
                     c.Course_Code, c.Course_Name, sec.Section_Name
            HAVING Attendance_Pct < 75
               AND Total_Sessions > 0
            ORDER BY Attendance_Pct ASC
        """)

        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "Student_ID":     int(r["Student_ID"]),
                "Full_Name":      str(r["Full_Name"]),
                "Enrollment_No":  str(r["Enrollment_No"]),
                "Course_Code":    str(r["Course_Code"]),
                "Course_Name":    str(r["Course_Name"]),
                "Section_Name":   str(r["Section_Name"]),
                "Total_Sessions": int(r["Total_Sessions"]),
                "Present_Count":  int(r["Present_Count"] or 0),
                "Attendance_Pct": float(r["Attendance_Pct"] or 0.0),
            })
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


# ---------------------------------------------------------------------------
# GET /api/admin/audit-logs
# ---------------------------------------------------------------------------
@router.get("/audit-logs")
def get_audit_logs():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                aa.Audit_ID,
                p.Full_Name                                   AS Student_Name,
                aa.Session_ID,
                DATE_FORMAT(ats.Session_Date, '%Y-%m-%d')     AS Session_Date,
                c.Course_Code,
                aa.Old_Status,
                aa.New_Status,
                aa.Changed_By,
                CAST(aa.Changed_At AS CHAR)                   AS Changed_At,
                aa.Change_Reason
            FROM ATTENDANCE_AUDIT   aa
            JOIN PERSON             p   ON aa.Student_ID    = p.Person_ID
            JOIN ATTENDANCE_SESSION ats ON aa.Session_ID    = ats.Session_ID
            JOIN TIMETABLE          t   ON ats.Timetable_ID = t.Timetable_ID
            JOIN COURSE             c   ON t.Course_ID      = c.Course_ID
            ORDER BY aa.Audit_ID DESC
        """)

        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "Audit_ID":      int(r["Audit_ID"]),
                "Student_Name":  str(r["Student_Name"]),
                "Session_ID":    int(r["Session_ID"]),
                "Session_Date":  str(r["Session_Date"]),
                "Course_Code":   str(r["Course_Code"]),
                "Old_Status":    str(r["Old_Status"]),
                "New_Status":    str(r["New_Status"]),
                "Changed_By":    str(r["Changed_By"]),
                "Changed_At":    str(r["Changed_At"]),
                "Change_Reason": str(r["Change_Reason"]) if r["Change_Reason"] else "",
            })
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


# ---------------------------------------------------------------------------
# GET /api/admin/dept-analytics
# ---------------------------------------------------------------------------
@router.get("/dept-analytics")
def get_dept_analytics():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                d.Dept_Name,
                d.Dept_Code,
                COALESCE(sc.Total_Students, 0) AS Total_Students,
                COALESCE(ss.Total_Sessions, 0) AS Total_Sessions,
                COALESCE(ac.Present_Count,  0) AS Present_Count,
                COALESCE(ac.Total_Records,  0) AS Total_Records,
                ROUND(
                    100.0 * COALESCE(ac.Present_Count, 0)
                    / NULLIF(COALESCE(ac.Total_Records, 0), 0),
                2) AS Attendance_Pct
            FROM DEPARTMENT d

            /* 1. Distinct students per department */
            LEFT JOIN (
                SELECT sec.Department_ID,
                       COUNT(DISTINCT e.Student_ID) AS Total_Students
                FROM SECTION sec
                JOIN ENROLLMENT e ON e.Section_ID = sec.Section_ID
                GROUP BY sec.Department_ID
            ) sc ON sc.Department_ID = d.Department_ID

            /* 2. Distinct sessions per department */
            LEFT JOIN (
                SELECT sec.Department_ID,
                       COUNT(DISTINCT ats.Session_ID) AS Total_Sessions
                FROM SECTION sec
                JOIN TIMETABLE t            ON t.Section_ID      = sec.Section_ID
                JOIN ATTENDANCE_SESSION ats ON ats.Timetable_ID  = t.Timetable_ID
                GROUP BY sec.Department_ID
            ) ss ON ss.Department_ID = d.Department_ID

            /* 3. Real attendance count per department */
            LEFT JOIN (
                SELECT sec.Department_ID,
                       SUM(CASE WHEN a.Status IN ('Present','Late') THEN 1 ELSE 0 END) AS Present_Count,
                       COUNT(a.Student_ID) AS Total_Records
                FROM SECTION sec
                JOIN TIMETABLE t            ON t.Section_ID      = sec.Section_ID
                JOIN ATTENDANCE_SESSION ats ON ats.Timetable_ID  = t.Timetable_ID
                JOIN ATTENDANCE a           ON a.Session_ID      = ats.Session_ID
                GROUP BY sec.Department_ID
            ) ac ON ac.Department_ID = d.Department_ID

            ORDER BY d.Dept_Name ASC
        """)

        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "Dept_Name":      str(r["Dept_Name"]),
                "Dept_Code":      str(r["Dept_Code"]),
                "Total_Students": int(r["Total_Students"] or 0),
                "Total_Sessions": int(r["Total_Sessions"] or 0),
                "Present_Count":  int(r["Present_Count"] or 0),
                "Total_Records":  int(r["Total_Records"] or 0),
                "Attendance_Pct": float(r["Attendance_Pct"] or 0.0),
            })
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()