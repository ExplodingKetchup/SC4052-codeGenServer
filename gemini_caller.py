import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

gemini_model_id = "gemini-2.0-flash"
gemini_system_instruction = \
    f"""
    Your task is to generate Python code to accomplish the data science related tasks I provided. Only generate executable Python code, no need to generate explanations.
    """

def new_gemini_chat():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    config = types.GenerateContentConfig(system_instruction=gemini_system_instruction)
    return client.chats.create(model=gemini_model_id, config=config)

gemini=new_gemini_chat()

def clean_user_prompt(message: str) -> str:
    if message[-1] == ".":
        message = message[:-1]
    return message

def extract_code(response: str) -> str:
    if response.startswith("```python"):
        response = response[10:]
    if response.endswith("```"):
        response = response[:-4]
    return response

def codegen_import_data(message: str) -> str:
    return extract_code(gemini.send_message(message=f"""
Input: Using numpy and pandas, import data from the file assorted_cookies.csv to a pandas DataFrame.
Output: import pandas as pd\nimport numpy as np\n\ntry:\n    df = pd.read_csv("assorted_cookies.csv")\nexcept FileNotFoundError:\n    print("Error: The file 'assorted_cookies.csv' was not found.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
Input: Using numpy and pandas, import data from the file assorted_cookies.xlsx to a pandas DataFrame.
Output: import pandas as pd\nimport numpy as np\n\ntry:\n    df = pd.read_excel("assorted_cookies.xlsx")\nexcept FileNotFoundError:\n    print("Error: The file 'assorted_cookies.xlsx' was not found.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
Input: Using numpy and pandas, {clean_user_prompt(message)}.
Output:
""").text)

def codegen_process_data(message: str) -> str:
    return extract_code(gemini.send_message(message=f"""
Input: Calculate the mean of the column Col-3 in DataFrame df.
Output: try:\n    mean_col3 = df['Col-3'].mean()\nexcept KeyError:\n    print("Error: The column 'Col-3' does not exist in the DataFrame.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
Input: Calculate the median of the column Col-5 in DataFrame df123.
Output: try:\n    median_col5 = df123['Col-5'].median()\nexcept KeyError:\n    print("Error: The column 'Col-5' does not exist in the DataFrame.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
Input: Remove rows in DataFrame data where column abc is null.
Output: try:\n    data = data.dropna(subset=['abc'])\nexcept KeyError:\n    print("Error: The column 'abc' does not exist in the DataFrame.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
Input: Remove duplicate rows in DataFrame my_data.
Output: try:\n    my_data = my_data.drop_duplicates()\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
Input: Perform data normalization in column df['my_col'].
Output: import pandas as pd\nimport numpy as np\n\ntry:\n    df['my_col'] = (df['my_col'] - df['my_col'].min()) / (df['my_col'].max() - df['my_col'].min())\nexcept KeyError:\n    print("Error: The column 'my_col' does not exist in the DataFrame.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
Input: {clean_user_prompt(message)}.
Output:
""").text)

def codegen_plot_data(message: str) -> str:
    return extract_code(gemini.send_message(message=f"""
Input: Using matplotlib and seaborn, plot a scatter plot of the 2 arrays x and y, label the horizontal axis 'x' and the vertical axis 'y', name the graph 'x vs y'.
Output: import matplotlib.pyplot as plt\nimport seaborn as sns\nimport numpy as np\n\ntry:\n    # Ensure x and y are numpy arrays (or convert them)\n    x = np.array(x)\n    y = np.array(y)\n\n    plt.figure(figsize=(8, 6))  # Adjust figure size if needed\n    sns.scatterplot(x=x, y=y)\n    plt.xlabel("x")\n    plt.ylabel("y")\n    plt.title("x vs y")\n    plt.grid(True)  # Add gridlines for better readability (optional)\n    plt.show()\n\nexcept NameError:\n    print("Error: The arrays 'x' and/or 'y' are not defined. Make sure they are defined before calling this code.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
Input: Using matplotlib and seaborn, {clean_user_prompt(message)}.
Output:
""").text)
