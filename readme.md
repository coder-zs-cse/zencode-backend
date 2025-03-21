# FastAPI Project

This is a basic FastAPI project setup.

## Requirements

- Python 3.7 or higher
- Virtual environment (venv)

## Setup Instructions

1. **Clone the repository** (if applicable):
   ```bash
   git clone https://github.com/coder-zs-cse/zencode-backend.git
   cd zencode-backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the FastAPI application**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**:
   Open your web browser and go to `http://127.0.0.1:8000` to see the response.

## API Documentation

You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.
