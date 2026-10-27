import pandas as pd

def grade_for(percentage):
    if percentage >= 90: return "A+"
    if percentage >= 80: return "A"
    if percentage >= 70: return "B"
    if percentage >= 60: return "C"
    if percentage >= 50: return "D"
    if percentage >= 40: return "E"
    return "F"

def summarize_performance(records):
    if not records:
        return {"class_average": 0, "pass_percentage": 0, "assessed_records": 0}
    df = pd.DataFrame(records)
    return {
        "class_average": round(float(df["score"].mean()), 2),
        "pass_percentage": round(float(df["passed"].mean() * 100), 2),
        "assessed_records": int(len(df))
    }
