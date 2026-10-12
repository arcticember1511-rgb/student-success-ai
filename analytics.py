
import pandas as pd


def load_student_data(file_path="data/students_master.csv"):
    """Load and validate student data."""
    df = pd.read_csv(file_path)

    required_columns = [
        "student_id",
        "student_name",
        "attendance_pct",
        "marks_pct",
        "engagement_pct",
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )

    score_columns = [
        "attendance_pct",
        "marks_pct",
        "engagement_pct",
    ]

    for col in score_columns:
        df[col] = pd.to_numeric(df[col], errors="raise")

        if not df[col].between(0, 100).all():
            raise ValueError(f"{col} must be between 0 and 100.")

    if df["student_id"].isna().any() or df["student_id"].duplicated().any():
        raise ValueError("Student IDs must be present and unique.")

    if df["student_name"].isna().any():
        raise ValueError("Student names cannot be empty.")

    return df


def calculate_success_scores(df):
    """Calculate a transparent, rule-based success score."""
    result = df.copy()

    result["success_score"] = (
        result["attendance_pct"] * 0.30
        + result["marks_pct"] * 0.50
        + result["engagement_pct"] * 0.20
    ).round(1)

    return result


def identify_at_risk_students(df):
    """Flag students who meet the demo support criteria."""
    result = df.copy()

    result["at_risk"] = (
        (result["success_score"] < 60)
        | (result["attendance_pct"] < 60)
    )

    return result


def recommend_interventions(row):
    """Generate supportive recommendations from student indicators."""
    recommendations = []

    if row["attendance_pct"] < 75:
        recommendations.append(
            "Discuss attendance barriers and offer support."
        )

    if row["marks_pct"] < 60:
        recommendations.append(
            "Offer subject-specific tutoring or a study plan."
        )

    if row["engagement_pct"] < 50:
        recommendations.append(
            "Check in with the student and explore engagement needs."
        )

    if not recommendations:
        recommendations.append(
            "Continue current support and monitor progress."
        )

    return recommendations
