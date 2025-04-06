from ast import literal_eval
from io import BytesIO

import streamlit as st
import random
import time
import io
import requests
from streamlit_ace import st_ace

st.set_page_config(layout="wide")

BACKEND_URL = "http://localhost:5000"


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

def profile_page():
    all_users = db_manager.get_users()
    user_names = [u[1] for u in all_users]
    user_id_map = {u[1]: u[0] for u in all_users}

    current_user_index = user_names.index(st.session_state.username)

    selected_user = st.selectbox(
        "Select Profile", user_names, index=current_user_index)
    selected_user_id = user_id_map[selected_user]

    user_images = db_manager.get_user_images(selected_user_id)
    is_owner = st.session_state.user_id == selected_user_id

    st.header(f"{'Your' if is_owner else selected_user} Profile")

    if len(user_images) == 0:
        st.write("This user doesn't have any generated images.")
        return

    num_columns = 4
    images_to_delete = []
    images_per_row = len(user_images) // num_columns + 1
    for i in range(images_per_row):
        col = st.columns(num_columns)
        for j in range(num_columns):
            index = i * num_columns + j
            if index < len(user_images):
                image = user_images[index]
                if is_owner:
                    delete_checkbox = col[j].checkbox(
                        f"Delete Image {image[0]}", key=f"delete_{image[0]}"
                    )
                    if delete_checkbox:
                        images_to_delete.append(image[0])
                col[j].image(
                    image[-1],
                )
                step_str = (
                    f"**_Steps:_** Base ({literal_eval(image[3])['base_step']}) | Refiner ({literal_eval(image[3])['refiner_step']})<br>"
                    if "base_step" in literal_eval(image[3]).keys()
                    else ""
                )
                cfg_str = (
                    f"**_Guidance scale:_** {literal_eval(image[3])['cfg']}<br>"
                    if "cfg" in literal_eval(image[3]).keys()
                    else ""
                )
                img2img_str = (
                    f"**_Image to Image mode_**<br>"
                    if step_str == "" and cfg_str == ""
                    else ""
                )
                col[j].markdown(
                    f"**_Model:_** {image[2]}<br>\
                    {step_str}\
                    {cfg_str}\
                    {img2img_str}\
                    **_Seed:_** {literal_eval(image[3])['seed']}<br>\
                    **_Prompt:_** {literal_eval(image[3])['prompt']}\
                    ",
                    unsafe_allow_html=True,
                )
                # col[j].image(
                #     image[-1],
                #     caption=f"Model: {image[2]},\tSeed: {literal_eval(image[3])['seed']},\tPrompt: {literal_eval(image[3])['prompt']}",
                # )

    if st.button("Delete Images") and images_to_delete:
        db_manager.delete_images(images_to_delete)
        st.rerun()


def request_text2image(**kwargs):
    url = "http://localhost:5000/text2img"
    payload = {
        "prompt": kwargs.get("prompt"),
        "negative_prompt": kwargs.get("negative_prompt"),
        "batch_size": kwargs.get("batch_size"),
        "width": kwargs.get("width"),
        "height": kwargs.get("height"),
        "seed": kwargs.get("seed"),
        "mode": kwargs.get("mode"),
        "base_step": kwargs.get("base_step"),
        "refiner_step": kwargs.get("refiner_step"),
        "cfg": kwargs.get("cfg"),
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        image_bytes_stream = response.content
        delimiter = b"--DELIMITER--"
        image_bytes_list = image_bytes_stream.split(delimiter)
        images = []
        for image_bytes in image_bytes_list:
            if image_bytes:
                image = Image.open(BytesIO(image_bytes))
                images.append(image)
        return images
    else:
        st.error(f"Error: {response.status_code}")
        return None


def request_image2image(**kwargs):
    url = "http://localhost:5000/img2img"
    payload = {
        "prompt": kwargs.get("prompt"),
        "negative_prompt": kwargs.get("negative_prompt", ""),
        "seed": kwargs.get("seed"),
        "mode": kwargs.get("mode"),
        "denoise": kwargs.get("denoise"),
    }
    headers = {"Content-Type": "application/octet-stream"}
    response = requests.post(
        url, data=kwargs.get("image"), headers=headers, params=payload
    )

    if response.status_code == 200:
        image_bytes_stream = response.content
        delimiter = b"--DELIMITER--"
        image_bytes_list = image_bytes_stream.split(delimiter)
        images = []
        for image_bytes in image_bytes_list:
            if image_bytes:
                image = Image.open(BytesIO(image_bytes))
                images.append(image)
        return images
    else:
        st.error(f"Error: {response.status_code} {response.text}")
        return None

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
                f"{BACKEND_URL}/import-data", json={"prompt": prompt}
            )
        elif function == "Data processing":
            response = requests.post(
                f"{BACKEND_URL}/data-processing", json={"prompt": prompt}
            )
        elif function == "Data visualization":
            response = requests.post(
                f"{BACKEND_URL}/plot-data", json={"prompt": prompt}
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

        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("▶️ Run", key=f"run_button_{i}"):
                run_code(i)

        with col2:
            st.markdown("**Output:**")
            st.code(st.session_state.outputs[i], language="python")

    st.divider()
    if st.button("➕ Add New Cell"):
        st.session_state.code_cells.append("")
        st.session_state.outputs.append("")

def main():
    logged_in = st.session_state.get("logged_in", False)
    username = st.session_state.get("username", None)

    if logged_in and username:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.sidebar.write(f"Welcome, {st.session_state.username}! ✨")
        kernel_page()
    else:
        login()


if __name__ == "__main__":
    import contextlib
    import streamlit as st
    import io
    import traceback
    main()