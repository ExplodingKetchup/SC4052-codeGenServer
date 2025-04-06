# Project Title: SC4052 Code Generation Server

## Team Members
- Dang Huy Phuong: U2120380G
- Nguyen Ngoc Nghia : U2120213H


## Project Structure
```
SC4052-codeGenServer/
│
├── app.py          # Streamlit frontend application
├── server.py       # Flask backend server
├── secret.txt      # Credentials file for login
└── gemini_caller.py # Module for code generation (import, process, plot)
```

## How to Run the Project

### Prerequisites
- Python 3.8 or higher
- Install required packages:
  ```bash
  pip install -r requirements.txt
  ```

### Step 1: Run the Flask Backend
1. Navigate to the project directory.
2. Start the Flask server:
   ```bash
   python server.py
   ```
3. The backend will run on `http://localhost:5000`.

### Step 2: Run the Streamlit Frontend
1. Open a new terminal.
2. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
3. The frontend will be accessible at `http://localhost:8501`.

## Notes
- The backend and frontend must run simultaneously for the application to function correctly.