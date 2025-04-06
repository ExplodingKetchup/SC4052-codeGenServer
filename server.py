from click import prompt
from flask import Flask, request, Request

import gemini_caller

app = Flask(__name__)

def load_credentials(filename):
    credentials = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                user, pwd = line.strip().split(':')
                credentials[user] = pwd
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except ValueError:
        print(f"Error: Incorrect file format in '{filename}'. Each line should contain 'username:password'.")
    return credentials

secret = load_credentials("secret.txt")

def get_prompt(received_request: Request) -> str:
    data = received_request.get_json()
    if not data or "prompt" not in data:
        return ""
    return data["prompt"]

@app.route("/test")
def test():
    return "hello!"

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "username" not in data or data["username"] not in secret:
        return "WRONG USERNAME!!", 401
    if not data or "password" not in data or data["password"] != secret[data["username"]]:
        return "WRONG PASSWORD!!", 401
    return "OK"

@app.route("/import-data", methods=["POST"])
def import_data():
    received_prompt = get_prompt(request)
    if len(received_prompt) == 0:
        return "Where prompt?", 400
    return gemini_caller.codegen_import_data(received_prompt)


@app.route("/data-processing", methods=["POST"])
def data_processing():
    received_prompt = get_prompt(request)
    if len(received_prompt) == 0:
        return "Where prompt?", 400
    return gemini_caller.codegen_process_data(received_prompt)


@app.route("/plot-data", methods=["POST"])
def plot_data():
    received_prompt = get_prompt(request)
    if len(received_prompt) == 0:
        return "Where prompt?", 400
    return gemini_caller.codegen_plot_data(received_prompt)

