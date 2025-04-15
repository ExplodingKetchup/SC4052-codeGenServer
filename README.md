# 📊 Low-Code Unified Platform for Data Analytics

This project is a **low-code data analytics platform** designed to help users—both technical and non-technical—analyze datasets with ease using **natural language prompts**. By integrating **Streamlit** for the frontend and **Flask + Google Gemini LLM** for the backend, the platform generates executable Python code for data tasks like importing, preprocessing, and visualizing data.

## 🚀 Features

- 🔤 **Natural Language to Python Code**  
  Users can describe their desired data task in plain English, and the system generates corresponding Python code using tools like `pandas`, `numpy`, `matplotlib`, and `seaborn`.

- 🤖 **AI-Powered Backend**  
  The backend uses **Gemini 2.0 Flash**, a generative large language model (LLM) by Google, capable of understanding context, function calling, and code generation with up-to-date logic.

- 🖥️ **Interactive User Interface**
  - **Login Page** – User authentication for secure access.
  - **Upload Data Page** – Upload and manage data files (e.g., CSV, Excel).
  - **Kernel Page** – Generate and run AI-assisted Python code in an interactive notebook-like environment.

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
- Populate `.env` file with your API key for GEMINI model and SERPER google search
``` bash
GEMINI_API_KEY=
SERPER_API_KEY=
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
