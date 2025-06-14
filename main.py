import os
import traceback
from dotenv import load_dotenv
import streamlit as st
from streamlit_ace import st_ace
import streamlit_confetti
import json
from agent_graph import graph, llm, question_generator_node, hint_generator_node, answer_checker_node
from helper_functions import  diagnose_failed_test_case, process_submission, init_static_session_state, load_user_into_session
from auth import check_login, update_user
from preloaded_packages import preloaded_globals


# Load environment variables
load_dotenv()
openai_api_key = st.secrets("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

#initiate session state
init_static_session_state()



# Check if user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

logged_in = check_login()
if not logged_in:
    st.stop()

# Load user-dependent data into session after login
load_user_into_session(st.session_state.user)

# App title
st.title("📚 Agentic AI Python Tutor")

user = st.session_state.user
# 🧠 Sync user profile from session state updates
st.session_state.user["total_score"] = st.session_state.total_score
st.session_state.user["streak"] = st.session_state.answer_streak
st.markdown(f"👋 Welcome **{user['name']}** | 🧠 Streak: `{user['streak']}` | 🌟 Score: `{user['total_score']}`")


def logout():
    st.session_state.clear()
    st.rerun()

if st.session_state.get("logged_in"):
    with st.sidebar:
        st.markdown(f"👤 Logged in as **{st.session_state.user['name']}**")
        if st.button("🚪 Log out"):
            logout()

TOPICS = ["General", "Strings", "Lists & Dictionaries", "Loops", "Pandas", "Numpy", "Data Structures", "Recursion"]

# UI: Topic and Difficulty Selection
selected_topic = st.selectbox(
    "🎯 Choose a topic:",
    TOPICS,
    index=TOPICS.index(st.session_state.selected_topic),
    key="selected_topic"
)

prev_difficulty = st.session_state.graph_state.get("difficulty", "easy")
selected_difficulty = st.selectbox(
    "Choose your starting difficulty level:",
    ["easy", "medium", "hard"],
    index=["easy", "medium", "hard"].index(prev_difficulty),
    key="difficulty_selector"
)

# Button to generate a new question
generate_new = st.button("🎯 Generate New Question")


if generate_new:
    # Clear previous solution if present
    st.session_state.graph_state.pop("solution", None)
    st.session_state.graph_state["difficulty"] = selected_difficulty
    st.session_state.graph_state["topic"] = selected_topic
    st.session_state.graph_state = question_generator_node(st.session_state.graph_state)
    st.session_state.hints_used = 0
    st.session_state.show_confetti = False
    st.session_state.graph_state.pop("user_answer", None)
    st.session_state.graph_state.pop("answer_correct", None)

if "current_question" not in st.session_state.graph_state:
    st.info("👋 Select a topic and difficulty, then click **Generate New Question** to begin.")
    st.stop()

# Extract question data
question_data = st.session_state.graph_state["current_question"]
points = question_data.get("points_possible", "?")
question_topic = question_data.get("topic") or st.session_state.graph_state.get("topic") or selected_topic


# Display question
st.markdown(f"### {question_data['question']}")
st.markdown(f"**📘 Topic:** `{question_topic}`")
emoji = "🏆" if points >= 20 else "🎯" if points >= 12 else "💡"
st.markdown(f"<div style='font-size:20px; margin-top:8px; color:#006400;'><b>{emoji} {points} points</b></div>", unsafe_allow_html=True)

# Show test cases
st.subheader("Test Cases:")
for idx, test_case in enumerate(question_data["test_cases"], 1):
    st.markdown(f"""
    <div style="background-color:#e6f2ff; padding:12px 16px; border-left: 6px solid #3399ff; border-radius:8px; margin-bottom:15px;">
        <div style="font-weight:bold; color:#003366; margin-bottom:6px;">Test Case {idx}</div>
        <div style="font-family:monospace; color:#222;"><strong>Input:</strong> {test_case['input']}</div>
        <div style="font-family:monospace; color:#222;"><strong>Expected Output:</strong> {test_case['expected_output']}</div>
    </div>
    """, unsafe_allow_html=True)



# Code editor
st.subheader("Your Solution:")
st.info(
    "🧰 Common Python packages are preloaded for you: "
    "`math`, `pandas (pd)`, `numpy (np)`, `random`, `json`, and `datetime`."
)
user_code = st_ace(
    placeholder="Write your Python function here...",
    language="python",
    theme="monokai",
    key="ace_editor",
    height=400,
    font_size=14,
    show_gutter=True,
    wrap=True,
    auto_update=False,
)


if user_code:
    st.code(user_code, language="python")

# Save user code to session state
update_user(st.session_state.user)

if st.button("Run test Cases"):
    try:
        global_vars = {"__builtins__": __builtins__}
        local_vars = {}
        exec(user_code, preloaded_globals.copy(), local_vars)

        funcs = [name for name in local_vars if callable(local_vars[name])]
        if not funcs:
            st.warning("⚠️ No function detected in your code.")
            st.stop()
        func_name = funcs[0]
        user_func = local_vars[func_name]
        test_results = []
        failed_cases = []

        for test_case in question_data["test_cases"]:
            input_str = test_case["input"]

            st.write(f"Input string: {repr(input_str)}")  # show exact string
            try:
                input_data = eval(input_str)
            except Exception as e:
                st.error(f"Failed to eval input: {input_str}")
                st.error(str(e))
                continue  # skip this test case or handle accordingly
            expected_output = eval(test_case["expected_output"])

            try:
                output = user_func(input_data) if isinstance(input_data, (list, str, int, float)) else user_func(*input_data)
                result = (output == expected_output)
                test_results.append(result)

                if not result:
                    failed_cases.append({
                        "input": input_data,
                        "expected": expected_output,
                        "actual": output
                    })

            except Exception as e:
                test_results.append(False)
                failed_cases.append({
                    "input": input_data,
                    "expected": expected_output,
                    "actual": f"Error: {e}"
                })

        if all(test_results):
            st.success("🎉 All test cases passed! You can now submit your solution.")
            st.session_state.show_confetti = True
            streamlit_confetti.confetti(emojis=["🎉", "✨", "🏆", "💥", "🥳"])
            st.session_state.graph_state["answer_correct"] = True
        else:
            st.session_state.show_confetti = False
            st.session_state.graph_state["answer_correct"] = False

            st.error(f"❌ {len(failed_cases)} test case(s) failed.")
            for i, fc in enumerate(failed_cases, 1):
                st.markdown(f"### 🔍 Failed Test Case {i}")
                st.markdown(f"**Input:** `{fc['input']}`")
                st.markdown(f"**Expected Output:** `{fc['expected']}`")
                st.markdown(f"**Actual Output:** `{fc['actual']}`")

            
            diagnosis = diagnose_failed_test_case(
                user_code=user_code,
                input_data=fc["input"],
                expected_output=fc["expected"],
                actual_output=fc["actual"],
                llm=llm
            )
            st.info(diagnosis)

        # Always save code, even if it fails
        st.session_state.graph_state["user_answer"] = user_code

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        st.text(traceback.format_exc())
        st.session_state.graph_state["answer_correct"] = False


if st.session_state.get("show_confetti"):
    streamlit_confetti.confetti(
        emojis=["🎉", "✨", "🏆", "💥", "🥳"],
        key="confetti-effect"
    )
    st.session_state.show_confetti = False

# Hint button
if st.button("Get Hint"):
    st.session_state.graph_state = hint_generator_node(st.session_state.graph_state)
    hint = st.session_state.graph_state.get("hint", "")
    if hint:
        st.session_state.hints_used += 1
        st.info(f"💡 Hint: {hint}")
    else:
        st.warning("No hint available.")

# Submit and show solution buttons
col1, col2 = st.columns([1, 1])
with col1:
    submit_clicked = st.button("✅ Submit Your Solution", key="submit_button", use_container_width=True)
with col2:
    show_clicked = st.button("🧠 Show Solution", key="show_button", use_container_width=True)

# Handle Submit
if submit_clicked:
    st.session_state.graph_state = answer_checker_node(st.session_state.graph_state)
    result = process_submission(st.session_state.graph_state, st.session_state.user)

    if result["answer_correct"]:
        st.success(f"🎉 Correct! You earned {result['score']} points.")
    else:
        st.error(f"❌ Incorrect. You earned {result['score']} points.")

    update_user(st.session_state.user)

    if result["feedback"]:
        st.info(f"💬 Feedback: {result['feedback']}")

    st.markdown(f"**Total Score:** `{st.session_state.total_score}` | **Streak:** `{st.session_state.answer_streak}`")

# Handle Show Solution
if show_clicked:
    question_text = st.session_state.graph_state["current_question"]["question"]
    prompt = f"""
    You are a helpful Python tutor. Here is the question:\n\n{question_text}\n\n
    Provide the final solution as code.
    """
    solution = llm.invoke(prompt).content.strip()
    st.subheader("🧪 Solution:")
    st.code(solution)

# ============================
# 📘 Learning History & Summary
# ============================

st.markdown("---")
st.subheader("🧠 Your Learning Summary")

if user.get("answered_questions"):
    all_questions = "\n".join(
        f"- {q['question']} ({q.get('topic', 'General')}, {q.get('difficulty', 'easy')})"
        for q in user["answered_questions"]
    )

    summary_prompt = f"""
    Summarize what the user has learned based on these Python practice questions. Be brief and encouraging. Never go beyond 30 words.
    Suggest next steps based on their topics and difficulty levels.
    User's Total Score: {user.get('total_score', 0)} | Current Streak: {user.get('streak', 0)}
    User's Last Answered Question:{user.get('last_answered_question', 'Not available')}
    User's Hints Used: {user.get('hints_used', 0)}

    Questions:
    {all_questions}
    """

    summary = llm.invoke(summary_prompt).content.strip()
    st.success(summary)

with st.expander("📂 View All Answered Questions & Code", expanded=False):
    for idx, q in enumerate(user.get("answered_questions", [])[::-1], 1):  # Latest first
        st.markdown(f"### {idx}. {q.get('question', 'No question text')}")
        st.markdown(f"**Topic:** `{q.get('topic', 'N/A')}` | **Difficulty:** `{q.get('difficulty', 'N/A')}` | **Points:** `{q.get('points_possible', '?')}`")
        st.markdown("**Test Case Example:**")
        if q.get("test_cases"):
            st.code(f"Input: {q['test_cases'][0]['input']}\nExpected Output: {q['test_cases'][0]['expected_output']}")
        if q.get("user_code"):
            st.markdown("**Your Submitted Code:**")
            st.code(q["user_code"], language="python")
        st.markdown("---")