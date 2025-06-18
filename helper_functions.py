import streamlit as st

def init_static_session_state():
    static_defaults = {
        "graph_state": {"difficulty": "easy"},
        "submit_requested": False,
        "selected_topic": "General",
        "points_earned": 0,
        "hints_used": 0,
    }
    for key, value in static_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def load_user_into_session(user):
    st.session_state.user = user
    st.session_state.total_score = user.get("total_score", 0)
    st.session_state.answer_streak = user.get("streak", 0)
    st.session_state.hints_used = user.get("hints_used", 0)
    # Backfill defaults if missing (esp. for older users)
    if "answered_questions" not in user:
        user["answered_questions"] = []
    if "last_answered_question" not in user:
        user["last_answered_question"] = None


def diagnose_failed_test_case(user_code: str, input_data, expected_output, actual_output, llm) -> str:
    diagnosis_prompt = f"""
    You are a Python tutor helping a student debug their function.

    The student's code is:

    {user_code}

    It failed on the following test case:
    - Input: {input_data}
    - Expected Output: {expected_output}
    - Actual Output: {actual_output}

    Please help by:
    1. Explaining what might have gone wrong (in 2–3 sentences).
    2. Giving a minimal hint that guides the student, but doesn't reveal the full solution.

    Respond in this format:
    Explanation: ...
    Hint: ...
    """
    return llm.invoke(diagnosis_prompt).content.strip()

def process_submission(graph_state, user):
    feedback = graph_state.get("feedback", "")
    answer_correct = graph_state.get("answer_correct", False)
    question_data = graph_state.get("current_question", {})
    question_text = question_data.get("question", "")
    points = int(question_data.get("points_possible", 0) or 0)
    hints_used = graph_state.get("hint_count", 0)

    score = max(points - (2 * hints_used), 0)

    # Update user
    if answer_correct:
        user["total_score"] += score
        user["streak"] += 1
        user["last_answered_question"] = question_text
        user["hints_used"] = hints_used

        if "answered_questions" not in user:
            user["answered_questions"] = []

        already_answered = any(q["question"] == question_text for q in user["answered_questions"])
        if not already_answered:
            question_data["score_earned"] = score
            user["answered_questions"].append({
                "question": question_text,
                "topic": question_data.get("topic", "General"),
                "difficulty": question_data.get("difficulty", "easy"),
                "points_possible": question_data.get("points_possible", 0),
                "test_cases": question_data.get("test_cases", []),
                "user_code": graph_state.get("user_answer", "")
            })
    else:
        user["streak"] = 0

    return {
        "answer_correct": answer_correct,
        "score": score,
        "feedback": feedback
    }

def is_output_equal(actual, expected):
    # Handle numeric comparison with tolerance
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(actual - expected) < 1e-5

    # Handle strings: ignore leading/trailing whitespace
    if isinstance(actual, str) and isinstance(expected, str):
        return actual.strip() == expected.strip()

    # Handle unordered list/set comparison
    if isinstance(actual, (list, set)) and isinstance(expected, (list, set)):
        return sorted(actual) == sorted(expected)

    # Handle dict comparison
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual == expected  # you can deep sort keys if needed

    # Final fallback: strict equality
    return actual == expected