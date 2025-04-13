import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
import requests
from bs4 import BeautifulSoup

load_dotenv()

gemini_model_id = "gemini-2.0-flash"
gemini_system_instruction = \
    f"""
    Your task is to generate Python code to accomplish the data science related tasks I provided. Use google search function to verify your code for most updated document. Only generate executable Python code, no need to generate explanations.
    """

def search_google(query: str) -> str:
    """
    Search for documentation on Google using the Serper API.
    """
    print(f"Searching Google for: {query}")
    api_key = os.getenv("SERPER_API_KEY")
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key}
    payload = {"q": query}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        composed_text = {}
        for result in data['organic']:
            if 'snippet' in result:
                response = requests.get(result['link'])
                text = BeautifulSoup(response.text, 'html.parser').get_text()
            composed_text[result['link']] = text
        return composed_text
    except Exception as e:
        return f"An error occurred: {e}"

search_google_declaration = types.FunctionDeclaration(
    name="search_google",
    description="Search for documentation on Google.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search for.",
            },
        },
    },
)
available_tools = [
    search_google_declaration,
]
available_functions = {
    "search_google": search_google,
}

def new_gemini_chat():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    tool = types.Tool(function_declarations=available_tools)
    config = types.GenerateContentConfig(system_instruction=gemini_system_instruction, tools=[tool])
    return client.chats.create(model=gemini_model_id, config=config)

chat = new_gemini_chat()


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

def gemini_query(message: str) -> str:
    response = chat.send_message(message=message)
    print(response.text)
    while response.function_calls:
        concat_function_call_results = []
        for function_call in response.function_calls:
            function_name = function_call.name
            arguments = function_call.args
            if function_name in available_functions:
                result = available_functions[function_name](**arguments)
            concat_function_call_results.append(
                types.Part.from_function_response(
                    name=function_call.name, response={"response": result}
                )
            )
        response = chat.send_message(concat_function_call_results)
    return response.text

def codegen_import_data(message: str) -> str:
    formatted_message = f"""
    Based on your previous response to generate code.
    Input: Using numpy and pandas, import data from the file assorted_cookies.csv to a pandas DataFrame. Also print the imported data.
    Output: import pandas as pd\nimport numpy as np\n\ntry:\n    df = pd.read_csv("assorted_cookies.csv")\n    print(df)\nexcept FileNotFoundError:\n    print("Error: The file 'assorted_cookies.csv' was not found.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
    Input: Using numpy and pandas, import data from the file assorted_cookies.xlsx to a pandas DataFrame. Also print the imported data.
    Output: import pandas as pd\nimport numpy as np\n\ntry:\n    df = pd.read_excel("assorted_cookies.xlsx")\n    print(df)\nexcept FileNotFoundError:\n    print("Error: The file 'assorted_cookies.xlsx' was not found.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
    Input: Using numpy and pandas, {clean_user_prompt(message)}. Also print the imported data.
    Output:
    """
    return gemini_query(formatted_message)

def codegen_process_data(message: str) -> str:
    formatted_message = f"""
    Based on your previous response to generate code
    Input: Calculate the mean of the column Col-3 in DataFrame df. Also print the affected data.
    Output: try:\n    mean_col3 = df['Col-3'].mean()\n    print(f"The mean of Col-3 is: {{mean_col3}}")\nexcept KeyError:\n    print("Error: The column 'Col-3' does not exist in the DataFrame.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
    Input: Calculate the median of the column Col-5 in DataFrame df123. Also print the affected data.
    Output: try:\n    median_col5 = df123['Col-5'].median()\n    print(f"The median of Col-5 is: {{median_col5}}")\nexcept KeyError:\n    print("Error: The column 'Col-5' does not exist in the DataFrame.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
    Input: Remove rows in DataFrame data where column abc is null. Also print the affected data.
    Output: try:\n    data = data.dropna(subset=['abc'])\n    print("Rows with null values in 'abc' have been removed.")\n    print(df['abc'])\nexcept KeyError:\n    print("Error: The column 'abc' does not exist in the DataFrame.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
    Input: Remove duplicate rows in DataFrame my_data. Also print the affected data.
    Output: try:\n    my_data = my_data.drop_duplicates()\n    print("Duplicate rows have been removed from the DataFrame.")\n    print(df)\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
    Input: Perform data normalization in column df['my_col']. Also print the affected data.
    Output: import pandas as pd\nimport numpy as np\n\ntry:\n    df['my_col'] = (df['my_col'] - df['my_col'].min()) / (df['my_col'].max() - df['my_col'].min())\n    print("Data normalization performed on column 'my_col'.")\n    print(df['my_col'])\nexcept KeyError:\n    print("Error: The column 'my_col' does not exist in the DataFrame.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
    Input: {clean_user_prompt(message)}. Also print the affected data.
    Output:
    """
    return gemini_query(formatted_message)

def codegen_plot_data(message: str) -> str:
    formatted_message = f"""
    Based on your previous response to generate code
    Input: Using matplotlib and seaborn, plot a scatter plot of the 2 arrays x and y, label the horizontal axis 'x' and the vertical axis 'y', name the graph 'x vs y'. Show the plot on a streamlit application.
    Output: import matplotlib.pyplot as plt\nimport seaborn as sns\nimport numpy as np\n\ntry:\n    # Ensure x and y are numpy arrays (or convert them)\n    x = np.array(x)\n    y = np.array(y)\n\n    plt.figure(figsize=(8, 6))  # Adjust figure size if needed\n    sns.scatterplot(x=x, y=y)\n    plt.xlabel("x")\n    plt.ylabel("y")\n    plt.title("x vs y")\n    plt.grid(True)  # Add gridlines for better readability (optional)\n    # Show the plot in Streamlit\n    st.pyplot(fig)\n\nexcept NameError:\n    print("Error: The arrays 'x' and/or 'y' are not defined. Make sure they are defined before calling this code.")\nexcept Exception as e:\n    print(f"An error occurred: {{e}}")
    Input: Using matplotlib and seaborn, {clean_user_prompt(message)}. Show the plot on a streamlit application.
    Output:
    """
    return gemini_query(formatted_message)


if __name__== "__main__":
    # Example usage
    response = codegen_plot_data("Plot trend of stock price")
    print(response)