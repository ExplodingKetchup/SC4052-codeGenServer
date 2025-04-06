from flask import Flask, request

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

@app.route("/test")
def test():
    return "hello!"

@app.route("/login", methods=["POST"])
def login():
    if request.form.get("username") not in secret:
        return "WRONG USERNAME!!"
    if request.form.get("password") != secret[request.form.get("username")]:
        return "WRONG PASSWORD!!"
    return "OK"

@app.route("/import-data", methods=["POST"])
def import_data():
    return gemini_caller.codegen_import_data(request.form.get("prompt"))


@app.route("/data-processing", methods=["POST"])
def data_processing():
    return gemini_caller.codegen_process_data(request.form.get("prompt"))


@app.route("/plot-data", methods=["POST"])
def plot_data():
    return gemini_caller.codegen_plot_data(request.form.get("prompt"))

