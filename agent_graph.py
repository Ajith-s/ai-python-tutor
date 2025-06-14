from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda
from question_bank import QUESTION_BANK
from langgraph.graph import StateGraph
from typing import TypedDict
import streamlit as st

import random

# Load OpenAI key
import os
#pulling key from secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]


# Define the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

class GraphState(TypedDict, total=False):
    difficulty: str
    current_question: dict
    user_answer: str
    feedback: str
    hint: str

# Define the prompt template for generating questions
QUESTION_PROMPT_TEMPLATE = """
You are a helpful Data SciencePython tutor helping candidates prepare for a coding interview. You can generate a Python question for selected topic based on the difficulty level. 

Here are some example questions and test cases. These are not to be used for generating new questions, but to provide context for the type of questions you can generate:
{few_shot_examples}

Generate a new question at the difficulty level specified below:
- Relevant to the topic: {topic}
- Difficulty: {difficulty}

Use the following format:
Format:
Question: <the question here>
Test case:
Input: <input>
Expected Output: <output>

Provide 2 to 3 test cases. Make sure to ALWAYS include at least one test case!

Your task is to ask students to solve the question and check if the answer is correct.
If neded by the student, provide hints in a way that guides the student and start with basic hints and then move to more advanced hints if the student asks for more help.

Evaluate the student's answer and provide feedback.

Provide next question based on the student's quality and performance. Better quality and performance means harder questions.
"""

# 🔹 Helper function to build few-shot examples
def build_few_shot_examples(question_bank, num_examples=3):
    # Build few-shot examples from the question bank
    examples = random.sample(question_bank, min(num_examples, len(question_bank)))
    examples_text = ""
    for i, example in enumerate(examples, 1):
        question = example["question"]
        input_data = example["test_cases"][0]["input"]
        expected_output = example["test_cases"][0]["expected_output"]
        topic = example.get("topic", "General")
        examples_text += (
            f"Example {i}:\n"
            f"Topic: {topic}\n"
            f"Question: {question}\n"
            f"Test case:\n"
            f"Input: {input_data}\n"
            f"Expected Output: {expected_output}\n\n"
        )
    return examples_text

    

def question_generator_node(state: GraphState) -> GraphState:
    difficulty = state.get("difficulty", "easy")
    user = state.get("user", {})
    answered_questions = user.get("answered_questions", [])


    # Generate few-shot examples
    few_shot_examples = build_few_shot_examples(QUESTION_BANK, num_examples=3)
    

    max_attempts = 5
    for _ in range(max_attempts):
        # 📜 Format prompt
        prompt = PromptTemplate.from_template(QUESTION_PROMPT_TEMPLATE).format(
            few_shot_examples=few_shot_examples,
            difficulty=difficulty,
            topic=state.get("topic", "general")
        )

        # 💬 Call LLM
        response_text = llm.invoke(prompt)
        response_text = response_text.content.strip() if hasattr(response_text, "content") else response_text.strip()

        # 🧩 Parse
        question_text = ""
        test_cases = []
        current_input = ""
        current_output = ""

        for line in response_text.split("\n"):
            if line.lower().startswith("question:"):
                question_text = line.split(":", 1)[1].strip()
            elif line.lower().startswith("input:"):
                current_input = line.split(":", 1)[1].strip()
            elif line.lower().startswith("expected output:"):
                current_output = line.split(":", 1)[1].strip()
                test_cases.append({
                    "input": current_input,
                    "expected_output": current_output
                })

        # ⛔️ Skip if already answered
        if question_text and question_text not in answered_questions:
            break

    # TODO: Upgrade to semantic deduplication using embeddings if repeated patterns emerge.
    
    else:
        # 😬 Fallback after too many retries
        question_text = "You've answered all available questions! Come back later for more."
        test_cases = []

    # 🎯 Assign points
    points = assign_point_value(question_text, difficulty)

    # reset hint count
    state["hint_count"] = 0
    # Update the state
    state["current_question"] = {
        "question": question_text,
        "topic": state.get("topic", "General"),
        "test_cases": test_cases,
        "difficulty": difficulty,
        "points_possible": points
    }

    return state

def assign_point_value(question_text, difficulty):
    prompt = f"""
    You are an expert coding tutor.

    Given the following Python coding question and its difficulty level, assign a point value based on its depth, complexity, and required reasoning.

    Rules:
    - Easy: 5 to 10 points
    - Medium: 12 to 18 points
    - Hard: 20 to 25 points

    Return just the number. No explanation.

    Difficulty: {difficulty}
    Question: {question_text}
    """
    response = llm.invoke(prompt)
    try:
        return int(response.content.strip())
    except:
        return 5  # fallback



def hint_generator_node(state: GraphState) -> GraphState:
    question_text = state.get("current_question", {}).get("question", "")
    prompt = f"""
    You are a helpful Python tutor.
    Given the question:\n\n{question_text}
    Provide a hint to help the student.
    """
    response = llm.invoke(prompt)
    state["hint"] = response.content
    # Track number of hints used
    state["hint_count"] = state.get("hint_count", 0) + 1
    return state



def answer_checker_node(state: GraphState) -> GraphState:
    user_answer = state.get("user_answer", "")
    question_text = state.get("current_question", {}).get("question", "")
    prompt = f"""
    You are a helpful Python tutor.
    Given the question:\n\n{question_text}
    and the student's code:\n\n{user_answer}
    Give clear and concise feedback in less than 15 words — mention if the logic is correct, if any edge cases are missed, or if the code can be improved.
    """
    response = llm.invoke(prompt)
    state["feedback"] = response.content
    return state

def compute_score(base_points: int, hint_count: int) -> int:
    deduction = min(hint_count * 2, base_points - 1)  # 2 points per hint
    return base_points - deduction

    
graph = StateGraph(GraphState)


graph.add_node("question_generator", question_generator_node)
graph.add_node("answer_checker", answer_checker_node)
graph.add_node("hint_generator", hint_generator_node)

# Connect the nodes
graph.set_entry_point("question_generator")
graph.add_edge("question_generator", "answer_checker")
graph.add_edge("answer_checker", "hint_generator")

# Define entry point
graph.set_entry_point("question_generator")

# Compile the graph
graph = graph.compile()

# Save the graph to a file
# graph.save("agent_graph.json")
