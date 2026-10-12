from fastapi import FastAPI, HTTPException
from analytics import (
    load_student_data,
    calculate_success_scores,
    identify_at_risk_students,
)

app = FastAPI(
    title="Student Success AI API",
    description="Backend API for student analytics and risk analysis",
    version="1.0.0",
)


def get_student_results():
    """Load student data and calculate analytics."""
    try:
        df = load_student_data()
        df = calculate_success_scores(df)
        df = identify_at_risk_students(df)
        return df
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Student dataset not found. Check data/students_master.csv.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process student data: {exc}",
        )


@app.get("/")
def home():
    return {
        "message": "Student Success AI API is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/students")
def get_students():
    """Return all students with calculated success scores and risk flags."""
    df = get_student_results()
    return df.to_dict(orient="records")


@app.get("/students/{student_id}")
def get_student(student_id: str):
    """Return one student by ID."""
    df = get_student_results()

    student = df[
        df["student_id"].astype(str) == str(student_id)
    ]

    if student.empty:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return student.iloc[0].to_dict()


@app.get("/analytics/summary")
def analytics_summary():
    """Return a basic overview of student results."""
    df = get_student_results()

    return {
        "total_students": int(len(df)),
        "average_success_score": round(
            float(df["success_score"].mean()), 1
        ) if len(df) else 0,
        "at_risk_students": int(df["at_risk"].sum()),
        "students_needing_support": int(
            (df["attendance_pct"] < 75).sum()
        ),
    }