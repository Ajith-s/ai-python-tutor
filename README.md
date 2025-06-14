# AI Python Tutor

A personalized, agentic Python tutoring application built with Streamlit and OpenAI. The app helps users strengthen their Python skills by guiding them through coding challenges, evaluating their logic and code, and offering targeted hints without giving away full solutions.

Designed to feel like an intelligent, interactive tutor rather than a simple answer generator.

## Features

- Guided Python problem solving with AI support  
- Contextual hints and feedback to improve problem-solving ability  
- Test case breakdown showing which passed or failed and why  
- Dynamic scoring system based on difficulty, hint usage, and attempt history  
- Firebase authentication with user-specific progress tracking  
- Memory features (in development) to retain context and user history  
- Clean UI with visual cues for progress and correctness  

## Tech Stack

- **Frontend**: Streamlit  
- **AI**: OpenAI GPT models  
- **Backend**: Python 3.10+  
- **Authentication & Database**: Firebase (Firestore + Auth)  
- **Other**: Python libraries like `dotenv`, `PIL`, and `hashlib`  

## Getting Started

### Prerequisites

- Python 3.10+
- Firebase project with Firestore and Authentication enabled
- OpenAI API key

### Installation

```bash
git clone https://github.com/Ajith-s/ai-python-tutor.git
cd ai-python-tutor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory and add your OpenAI API key:

```env
OPENAI_API_KEY=your-api-key-here
```

### Firebase Configuration

1. Go to your Firebase project console.
2. Enable **Firestore** and **Authentication**.
3. Download the Admin SDK service account key:
   - Navigate to **Project Settings > Service accounts**
   - Click **“Generate new private key”**
   - Save the file as `firebase_service_account.json` in the project root

> ⚠️ Make sure `firebase_service_account.json` is included in your `.gitignore` to avoid pushing secrets.

### Running the App

```bash
streamlit run main.py
```
