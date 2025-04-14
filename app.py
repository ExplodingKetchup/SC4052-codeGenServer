from ast import literal_eval
from io import BytesIO
import os

import streamlit as st
import random
import time
import io
import requests
from streamlit_ace import st_ace

st.set_page_config(layout="wide")

BACKEND_URL = "http://localhost:5000"
SAVE_FOLDER = "uploaded_files"


def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(
            f"{BACKEND_URL}/login", json={"username": username, "password": password}
        )
        print(response.text)
        if response.status_code == 200:
            st.session_state.username = username
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password.")
    return False


prompt_options = [
    "Import data",
    "Data processing",
    "Data visualization",
]

def kernel_page():
    st.title("📓 Streamlit Notebook – Jupyter Style")


    # Initialize session state
    if "code_cells" not in st.session_state:
        st.session_state.code_cells = [""]  # Start with one empty cell
    if "globals_dict" not in st.session_state:
        st.session_state.globals_dict = {}

    if "prompts_function" not in st.session_state:
        st.session_state.prompts_function = [""] * len(st.session_state.code_cells)
    if "prompts" not in st.session_state:
        st.session_state.prompts = [""] * len(st.session_state.code_cells)
    # Output buffer for each cell
    if "outputs" not in st.session_state:
        st.session_state.outputs = [""] * len(st.session_state.code_cells)


    def run_code(cell_index):
        code = st.session_state.code_cells[cell_index]
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                exec(code, st.session_state.globals_dict)
            st.session_state.outputs[cell_index] = buffer.getvalue()
        except Exception:
            st.session_state.outputs[cell_index] = traceback.format_exc()

    def generate_code(cell_index):
        prompt = st.session_state.prompts[cell_index]
        function = st.session_state.prompts_function[cell_index]

        if function == "Import data":
            response = requests.post(
                f"{BACKEND_URL}/import-data", json={"prompt": prompt, "data_source_list": os.listdir(SAVE_FOLDER)}
            )
        elif function == "Data processing":
            response = requests.post(
                f"{BACKEND_URL}/data-processing", json={"prompt": prompt, "globals_dict": str(st.session_state.globals_dict)}
            )
        elif function == "Data visualization":
            response = requests.post(
                f"{BACKEND_URL}/plot-data", json={"prompt": prompt, "globals_dict": str(st.session_state.globals_dict)}
            )
        else:
            st.error("Invalid function selected.")
            return ""

        if response.status_code == 200:
            return response.text
        else:
            st.error(f"Error: {response.status_code}")
            return ""

    # Display each code cell
    for i in range(len(st.session_state.code_cells)):
        col1, col2 = st.columns([2, 5])
        with col1:
            st.markdown(f"### 🧮 Cell {i + 1}")
        with col2:
            st.session_state.prompts_function[i] = st.selectbox(
                label="Function",
                options=prompt_options,
                index=0,
                key=f"prompt_function_{i}",
            )
            st.session_state.prompts[i] = st.text_input(
                label="Prompt",
                placeholder="Describe the code you want to run",
                help="This will be used to generate the code",
                value=st.session_state.prompts[i],
                key=f"prompt_{i}",
            )
            if st.button("Generate Code", key=f"generate_code_{i}") and st.session_state.prompts[i]:
                st.session_state.code_cells[i] = generate_code(i)
                
        st.session_state.code_cells[i] = st_ace(
            language="python",
            auto_update=True,
            value=st.session_state.code_cells[i],
            height=200,
        )

        if st.button("▶️ Run", key=f"run_button_{i}"):
            run_code(i)
            
        st.code(st.session_state.outputs[i], language="python")

    st.divider()
    if st.button("➕ Add New Cell"):
        st.session_state.code_cells.append("")
        st.session_state.outputs.append("")
        st.session_state.prompts.append("")
        st.session_state.prompts_function.append("")

def main():
    logged_in = st.session_state.get("logged_in", True)
    username = st.session_state.get("username", 'ádas')

    if logged_in and username:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.sidebar.write(f"Welcome, {st.session_state.username}! ✨")
        option = st.sidebar.radio(
            "Choose your functions:",
            ["Upload data", "Data Analysis"]
        )
        if option == "Upload data":
            uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx"])
            if uploaded_file is not None:
                # Get the filename
                file_name = uploaded_file.name
                
                # Save path
                save_path = f'./{SAVE_FOLDER}/{file_name}' 
                
                # Save the file locally
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            if os.path.exists(SAVE_FOLDER):
                st.write("Datasets")
                files = os.listdir(SAVE_FOLDER)
                for file in files:
                    st.write(f"- {file}")
                    if file.endswith(".csv"):
                        df = pd.read_csv(os.path.join(SAVE_FOLDER, file))
                        st.dataframe(df)
                    elif file.endswith(".xlsx"):
                        df = pd.read_excel(os.path.join(SAVE_FOLDER, file))
                        st.dataframe(df)
        else:
            kernel_page()
    else:
        login()


if __name__ == "__main__":
    import contextlib
    import io
    import traceback
    import pandas as pd
    import numpy as np
    import seaborn as sns
    main()