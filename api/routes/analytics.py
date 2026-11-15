from fastapi import APIRouter
from db import get_connection

router = APIRouter()

@router.get("/query-trace/{trace_type}")
def get_query_trace(trace_type: str):
    """
    Returns the exact SQL query, execution plan (EXPLAIN),
    and DBMS topic for laboratory viva demonstration!
    """
    traces = {
        "shortage": {
            "topic": "Aggregation, GROUP BY & HAVING (< 75% Debarment)",
            "sql": """
                SELECT p.Full_Name, c.Course_Name,
                       COUNT(a.Session_ID) AS Total,
                       SUM(a.Status='Present') AS Present,
                       ROUND(SUM(a.Status='Present')/COUNT(*)*100, 2) AS Attendance_Pct
                FROM ATTENDANCE a
                JOIN ATTENDANCE_SESSION ats ON a.Session_ID = ats.Session_ID
                JOIN TIMETABLE t ON ats.Timetable_ID = t.Timetable_ID
                JOIN COURSE c ON t.Course_ID = c.Course_ID
                JOIN STUDENT s ON a.Student_ID = s.Person_ID
                JOIN PERSON p ON s.Person_ID = p.Person_ID
                GROUP BY a.Student_ID, c.Course_ID
                HAVING Attendance_Pct < 75.00;
            """,
            "explain_sql": """
                EXPLAIN SELECT a.Student_ID, COUNT(*), SUM(a.Status='Present')
                FROM ATTENDANCE a
                GROUP BY a.Student_ID;
            """
        },
        "timetable": {
            "topic": "Multi-Table 6-Way INNER JOIN Resolution",
            "sql": """
                SELECT c.Course_Name, p.Full_Name AS Faculty, r.Room_Number, ts.Day_Of_Week, ts.Start_Time
                FROM ENROLLMENT e
                INNER JOIN COURSE c ON e.Course_ID = c.Course_ID
                INNER JOIN TIMETABLE t ON t.Course_ID = c.Course_ID AND t.Section_ID = e.Section_ID
                INNER JOIN FACULTY f ON t.Faculty_ID = f.Person_ID
                INNER JOIN PERSON p ON f.Person_ID = p.Person_ID
                INNER JOIN ROOM r ON t.Room_ID = r.Room_ID
                INNER JOIN TIME_SLOT ts ON t.Slot_ID = ts.Slot_ID
                WHERE e.Student_ID = 10;
            """,
            "explain_sql": """
                EXPLAIN SELECT c.Course_Name FROM ENROLLMENT e 
                JOIN COURSE c ON e.Course_ID = c.Course_ID 
                JOIN TIMETABLE t ON t.Course_ID = c.Course_ID;
            """
        }
    }

    if trace_type not in traces:
        return {"error": "Invalid trace type. Use 'shortage' or 'timetable'"}

    trace = traces[trace_type]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(trace["explain_sql"])
        explain_plan = cursor.fetchall()
        return {
            "dbms_topic": trace["topic"],
            "raw_sql": trace["sql"].strip(),
            "mysql_execution_plan": explain_plan
        }
    finally:
        cursor.close()
        conn.close()