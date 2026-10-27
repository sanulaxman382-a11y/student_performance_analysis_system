from analysis import grade_for, summarize_performance

def test_grade_boundaries():
    assert grade_for(90) == "A+"
    assert grade_for(80) == "A"
    assert grade_for(70) == "B"
    assert grade_for(60) == "C"
    assert grade_for(50) == "D"
    assert grade_for(40) == "E"
    assert grade_for(39.99) == "F"

def test_summary():
    result = summarize_performance([
        {"score": 80, "passed": True},
        {"score": 20, "passed": False},
    ])
    assert result == {"class_average": 50.0, "pass_percentage": 50.0, "assessed_records": 2}

def test_empty_summary():
    assert summarize_performance([]) == {
        "class_average": 0, "pass_percentage": 0, "assessed_records": 0
    }
