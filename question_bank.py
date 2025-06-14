# question_bank.py

QUESTION_BANK = [
    {
        "id": 1,
        "topic": "strings",
        "question": "Write a function to reverse a string.",
        "difficulty": "easy",
        "test_cases": [
            {"input": "hello", "expected_output": "olleh"},
            {"input": "world", "expected_output": "dlrow"}
        ]
    },
    {
        "id": 2,
        "topic": "pandas",
        "difficulty": "easy",
        "question": "Write a function to create a Pandas DataFrame from a dictionary.",
        "test_cases": [
            {"input": {"A": [1, 2, 3], "B": [4, 5, 6]}, 
             "expected_output": {"A": [1, 2, 3], "B": [4, 5, 6]}},
            {"input": {"Name": ["Alice", "Bob"], "Age": [25, 30]}, 
             "expected_output": {"Name": ["Alice", "Bob"], "Age": [25, 30]}}
        ]
    },
    {
        "id": 3,
        "topic": "lists",
        "question": "Write a function that takes a list of numbers and returns the sum of all even numbers.",
        "difficulty": "easy",
        "test_cases": [
            {"input": [1, 2, 3, 4, 5], "expected_output": 6}
        ]
    },
    {
        "id": 4,
        "topic": "Pandas",
        "question": "Write a function to filter a Pandas DataFrame based on a condition.",
        "difficulty": "medium",
        "test_cases": [
            {"input": {"data": {"A": [1, 2, 3, 4], "B": [5, 6, 7, 8]}, "condition": "A > 2"}, 
             "expected_output": {"A": [3, 4], "B": [7, 8]}},
             {"input": {"data": {"A": [10, 20, 30], "B": [40, 50, 60]}, "condition": "B < 50"},
             "expected_output": {"A": [10], "B": [40]}}
        ]
    },
    {
        "id": 5,
        "topic": "strings",
        "question": "Write a function to check if a string is a palindrome.",
        "difficulty": "easy",
        "test_cases": [
            {"input": "racecar", "expected_output": True},
            {"input": "hello", "expected_output": False}
        ]
    },
    {
        "id": 6,
        "topic": "lists",
        "question": "Write a function to find the maximum number in a list of numbers.",
        "difficulty": "medium",
        "test_cases": [
            {"input": [1, 2, 3, 4, 5], "expected_output": 5},
            {"input": [5, 4, 3, 2, 1], "expected_output": 5}
        ]
    },
    {
        "id": 7,
        "topic": "strings",
        "question": "Write a function to find the first non-repeating character in a string.",
        "difficulty": "medium",
        "test_cases": [
            {"input": "swiss", "expected_output": "w"},
            {"input": "hello", "expected_output": "h"}
        ]
    },
    {
        "id": 8,
        "topic": "lists",
        "question": "Write a function to merge two sorted lists into one sorted list.",
        "difficulty": "medium",
        "test_cases": [
            {"input": ([1, 3, 5], [2, 4, 6]), "expected_output": [1, 2, 3, 4, 5, 6]},
            {"input": ([1, 2], [3, 4]), "expected_output": [1, 2, 3, 4]}
        ]
    },
    {
        "id": 9,
        "topic": "Pandas",
        "difficulty": "medium",
        "question": "Write a function to calculate the mean of a Pandas Series.",
        "test_cases": [
            {"input": [1, 2, 3, 4, 5], "expected_output": 3.0},
            {"input": [10, 20, 30], "expected_output": 20.0}
        ]
    },
    {
        "id": 10,
        "topic": "Loops",
        "difficulty": "medium",
        "question": "Write a function to print the Fibonacci sequence up to n terms.",
        "test_cases": [
            {"input": 5, "expected_output": [0, 1, 1, 2, 3]},
            {"input": 10, "expected_output": [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]}
        ]
    },
    {       
        "id": 11,
        "topic": "searching",
        "difficulty": "hard",
        "question": "Write a function to implement binary search on a sorted list.",
        "test_cases": [
            {"input": ([1, 2, 3, 4, 5], 3), "expected_output": 2},
            {"input": ([1, 2, 3, 4, 5], 6), "expected_output": -1}
        ]
    },
    {
        "id": 12,
        "difficulty": "hard",
        "topic": "lists",
        "question": "Write a function to find the intersection of two lists.",
        "test_cases": [
            {"input": ([1, 2, 3], [2, 3, 4]), "expected_output": [2, 3]},
            {"input": ([5, 6, 7], [7, 8, 9]), "expected_output": [7]}
        ]
    },
    {
        "id": 13,
        "difficulty": "hard",
        "topic": "arrays",
        "question": "Write a function to find the maximum subarray sum in a given array.",
        "test_cases": [
            {"input": [1, -3, 2, 1, -1], "expected_output": 3},
            {"input": [-2, -5, -1, -3], "expected_output": -1}
        ]
    },
    {
        "id": 14,
        "difficulty": "hard",
        "topic": "Pandas",
        "question": "Write a function to group a Pandas DataFrame by a specific column and calculate the mean of another column.",
        "test_cases": [
            {"input": {"data": {"A": [1, 2, 1, 2], "B": [3, 4, 5, 6]}, "group_by": "A", "agg_col": "B"}, 
             "expected_output": {"1": 4.0, "2": 5.0}},
            {"input": {"data": {"X": [1, 1, 2, 2], "Y": [10, 20, 30, 40]}, "group_by": "X", "agg_col": "Y"}, 
             "expected_output": {"1": 15.0, "2": 35.0}}
        ]
    
    },
    # Add more questions here
]

def get_question_by_difficulty(level):
    return [q for q in QUESTION_BANK if q['difficulty'] == level]

def get_all_questions():
    return QUESTION_BANK
