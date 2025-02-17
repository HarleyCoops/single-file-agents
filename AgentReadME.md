# DuckDB SQL Agent - Self-Improving Agent with `uv`

This README provides a comprehensive explanation of the `duckdb_agent.py` script, a self-improving agent designed to generate and execute DuckDB SQL queries based on natural language requests.  It leverages `uv` to manage dependencies and enable the script to run as a standalone executable.

## Table of Contents

1.  [Introduction](#introduction)
2.  [Dependencies](#dependencies)
3.  [How it Works (High-Level Overview)](#how-it-works-high-level-overview)
4.  [Agent Capabilities and Tools](#agent-capabilities-and-tools)
    *   [Tool Definitions (Pydantic Models)](#tool-definitions-pydantic-models)
    *   [Tool Functions](#tool-functions)
5.  [Agent Prompt and Instructions](#agent-prompt-and-instructions)
6.  [Main Execution Loop (`main` function)](#main-execution-loop-main-function)
    *   [Argument Parsing](#argument-parsing)
    *   [OpenAI API Key Setup](#openai-api-key-setup)
    *   [Prompt Construction](#prompt-construction)
    *   [Agent Iteration](#agent-iteration)
    *   [Function Call Handling](#function-call-handling)
    *   [Error Handling](#error-handling)
7.  [Running the Script](#running-the-script)
8.  [Self-Improvement Mechanism](#self-improvement-mechanism)
9.  [Key Concepts](#key-concepts)
    *  [`uv` for Dependency Management](#uv-for-dependency-management)
    *   [OpenAI Function Calling](#openai-function-calling)
    *   [Pydantic Models for Structured Data](#pydantic-models-for-structured-data)
    *   [Rich Library for Enhanced Output](#rich-library-for-enhanced-output)
    *   [DuckDB Integration](#duckdb-integration)
10. [Limitations and Potential Improvements](#limitations-and-potential-improvements)
11. [Troubleshooting](#troubleshooting)

## 1. Introduction

The `duckdb_agent.py` script is a powerful example of a self-improving agent that interacts with a DuckDB database.  It uses the OpenAI API (specifically, function calling capabilities) to translate natural language user requests into SQL queries. The agent can explore the database schema, sample data, test queries, and iteratively refine its approach until it generates a correct and efficient SQL query that fulfills the user's request.  The use of `uv` makes it incredibly easy to run, requiring no separate virtual environment setup.

## 2. Dependencies

The script uses the following Python libraries, which are managed by `uv` (specified in the script's header):

*   **`openai>=1.63.0`**:  The official OpenAI Python library for interacting with the OpenAI API.  This is used for natural language processing and function calling.
*   **`rich>=13.7.0`**:  A library for rich text and beautiful formatting in the terminal.  This is used for clear and organized output to the console.
*   **`pydantic>=2.0.0`**:  A data validation and parsing library.  Pydantic models are used to define the structure of the agent's tools (functions) and ensure that the OpenAI API provides arguments in the correct format.
*  **`duckdb`**: (Implicit) While not explicitly listed as a `uv` dependency, `duckdb` is used via `subprocess`.  The script assumes `duckdb` is available in the system's PATH.

`uv` handles installing these dependencies automatically when the script is run.

## 3. How it Works (High-Level Overview)

1.  **User Input:** The script takes a user's natural language request and the path to a DuckDB database file as command-line arguments.
2.  **Prompt Engineering:**  A detailed prompt is constructed, instructing the OpenAI model to act as a SQL expert and providing it with a set of tools (functions) it can use to interact with the database.
3.  **Agent Loop:** The script enters a loop where the OpenAI model:
    *   Receives the prompt and current state (messages).
    *   Chooses a tool (function) to call, along with arguments.
    *   The script executes the chosen function (e.g., listing tables, sampling data).
    *   The function's result is added to the conversation history.
    *   The loop continues until the model calls the `run_final_sql_query` function, indicating it has a solution.
4.  **Query Execution:** The final SQL query is executed against the DuckDB database, and the results are displayed to the user.
5.  **Self-Improvement:** If a test query fails or produces an error, the agent receives the error message and can adjust its strategy in the next iteration, effectively learning from its mistakes.

## 4. Agent Capabilities and Tools

The agent has a set of predefined "tools," which are essentially Python functions that it can call to interact with the DuckDB database.  These tools are defined using Pydantic models, which provide structure and validation for the function arguments.

### 4.A. Tool Definitions (Pydantic Models)

The following Pydantic models define the structure of the tools:

*   **`ListTablesArgs`**:  Takes a `reasoning` string explaining why the agent wants to list tables.
*   **`DescribeTableArgs`**: Takes a `reasoning` string and a `table_name` string.
*   **`SampleTableArgs`**: Takes `reasoning`, `table_name`, and `row_sample_size` (an integer).
*   **`RunTestSQLQuery`**: Takes `reasoning` and `sql_query` (a string).
*   **`RunFinalSQLQuery`**: Takes `reasoning` and `sql_query`.

These models ensure the OpenAI model provides the necessary arguments in the correct format when calling a tool.  The `pydantic_function_tool` function converts these models into a format understood by the OpenAI API.

### 4.B. Tool Functions

The following Python functions implement the agent's tools:

*   **`list_tables(reasoning: str) -> List[str]`**: Lists all tables in the database.  Uses `subprocess` to run the DuckDB CLI command `.tables`.
*   **`describe_table(reasoning: str, table_name: str) -> str`**:  Provides the schema (structure) of a specific table. Uses `subprocess` to run `DESCRIBE <table_name>;`.
*   **`sample_table(reasoning: str, table_name: str, row_sample_size: int) -> str`**:  Retrieves a sample of rows from a table.  Uses `subprocess` to run `SELECT * FROM <table_name> LIMIT <row_sample_size>;`.
*   **`run_test_sql_query(reasoning: str, sql_query: str) -> str`**: Executes a SQL query and returns the results *to the agent*, not the user. This allows the agent to test and refine queries before presenting a final result. Uses `subprocess` to run the query.
*   **`run_final_sql_query(reasoning: str, sql_query: str) -> str`**: Executes the final, validated SQL query and returns the results *to the user*.  This is the last function the agent should call.  Uses `subprocess` to run the query.

All these functions use the `subprocess` module to interact with the `duckdb` command-line tool, effectively treating DuckDB as an external process.

## 5. Agent Prompt and Instructions

The `AGENT_PROMPT` variable defines the instructions and context given to the OpenAI model. It's crucial for guiding the agent's behavior. Key parts of the prompt include:

*   **`<purpose>`**:  Sets the overall goal: to create accurate DuckDB SQL queries.
*   **`<instructions>`**: Provides specific steps and guidelines:
    *   Use tools to explore the database.
    *   List, describe, and sample tables.
    *   Test queries before finalizing.
    *   Only call `run_final_sql_query` when confident.
    *   Be efficient.
    *   **Self-improve:** If a test query fails, try to fix it.
    *   Think step-by-step.
    *   Specify all parameters.
    *   Include reasoning for every tool call.
*   **`<tools>`**:  Describes each available tool, its parameters, and their types.  This is a human-readable version of the tool definitions; the OpenAI API uses the structured version generated by `pydantic_function_tool`.
*   **`<user-request>`**:  A placeholder that gets replaced with the actual user's request.

This prompt is carefully crafted to encourage iterative exploration, testing, and refinement of the SQL query.

## 6. Main Execution Loop (`main` function)

The `main` function orchestrates the entire process.

### 6.A. Argument Parsing

The script uses `argparse` to handle command-line arguments:

*   **`-d` or `--db` (required):** Path to the DuckDB database file.
*   **`-p` or `--prompt` (required):** The user's natural language request.
*   **`-c` or `--compute` (optional, default=10):** The maximum number of agent loops before giving up. This prevents infinite loops.

### 6.B. OpenAI API Key Setup

The script retrieves the OpenAI API key from the `OPENAI_API_KEY` environment variable.  It's crucial to set this variable before running the script.  The script will exit with an error message if the key is not found.

### 6.C. Prompt Construction

The `AGENT_PROMPT` is combined with the user's request (from the command-line arguments) to create the complete prompt sent to the OpenAI API.

### 6.D. Agent Iteration

The `while True` loop is the core of the agent's iterative process:

1.  **API Call:** The `openai.chat.completions.create` function is called to interact with the OpenAI API.  Key parameters include:
    *   `model`: The OpenAI model to use (set to o3-mini, though gpt4-o-mini is provided as a commented out suggestion.).
    *   `messages`: The conversation history, including the initial prompt and any previous tool calls and results.
    *   `tools`: The list of available tools (functions).
    *   `tool_choice="required"`:  Forces the model to choose a tool.

2.  **Response Handling:** The response from the API is checked for a function/tool call.

### 6.E. Function Call Handling

If the model chooses to call a function:

1.  **Argument Extraction and Validation:** The function name and arguments are extracted from the API response. The script uses the appropriate Pydantic model (`ListTablesArgs`, `DescribeTableArgs`, etc.) to validate and parse the arguments.  This is a critical step to ensure the arguments are in the correct format.
2.  **Function Execution:** The corresponding Python function (e.g., `list_tables`, `describe_table`) is called with the validated arguments.
3.  **Result Appending:** The result of the function call is added to the `messages` list as a "tool" message, providing feedback to the model. This allows the model to see the results of its actions and adjust its strategy.
4.  **Final Query Handling:** If the model calls `run_final_sql_query`, the query is executed, the results are printed to the console, and the script exits.

### 6.F. Error Handling

*   **Argument Validation Errors:** If the arguments provided by the model don't match the Pydantic model's schema, a `ValidationError` is caught, an error message is printed, and the error is sent back to the model as a "tool" message. This allows the model to correct its mistake.
*   **Function Execution Errors:**  Errors within the tool functions (e.g., invalid SQL syntax) are caught, error messages are printed, and the error is returned to the model.
*   **Maximum Compute Loops:** The script keeps track of the number of iterations. If it exceeds the maximum allowed loops (`--compute` argument) without reaching a final query, an exception is raised. This prevents the agent from getting stuck in an infinite loop.
*   **Missing function call:** There is a final `else` block that raises an Exception if the model does not include a function call in its response.

## 7. Running the Script

To run the script:

1.  **Install `uv`:** If you don't have `uv` installed, follow the instructions on the official `uv` website. Usually this just requires running: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2.  **Set the `OPENAI_API_KEY` environment variable:**
    ```bash
    export OPENAI_API_KEY="your-openai-api-key"
    ```
3.  **Create a DuckDB database:** You'll need a DuckDB database file (e.g., `my_database.db`).  You can create one and populate it with data using the DuckDB CLI or Python library.
4.  **Run the script:**
    ```bash
    python duckdb_agent.py -d my_database.db -p "Show me the names of all tables"
    ```
    Replace `my_database.db` with the actual path to your database file, and the prompt with your desired request.  You can also adjust the `-c` (compute) parameter if needed.
5.  Use the single-file agent format with uv. Save the original script from above as `agent.py` and run the script, like so:
    ```bash
     uv agent.py -d my_database.db -p "Show me the names of all tables"
    ```

## 8. Self-Improvement Mechanism

The self-improvement capability comes from several key features:

*   **Iterative Loop:** The agent repeatedly interacts with the OpenAI API, refining its approach with each iteration.
*   **Tool Use and Feedback:** The agent uses tools to gather information and test hypotheses.  The results of these tool calls (including errors) are fed back into the conversation history, allowing the model to learn from its actions.
*   **Error Handling:**  When a test query fails, the agent receives the error message.  This negative feedback helps it understand what went wrong and adjust its strategy.  The agent is explicitly instructed in the prompt to try to fix errors.
*   **Reasoning Parameter:** The `reasoning` parameter in each tool forces the model to articulate its thought process. This helps with debugging and potentially improves the model's ability to plan and strategize.

## 9. Key Concepts

### 9.A. `uv` for Dependency Management

`uv` is used to manage the script's dependencies, which simplifies distribution. The lines at the top of the script:

```python
# /// script
# dependencies = [
#   "openai>=1.63.0",
#   "rich>=13.7.0",
#   "pydantic>=2.0.0",
# ]
# ///

tell `uv` which packages to install. When you run the script using `uv run duckdb_agent.py ...`, `uv` automatically creates a virtual environment, installs the specified dependencies, and then executes the script within that environment. This makes the script self-contained and portable.

### 9.B. OpenAI Function Calling

The script relies heavily on OpenAI's function calling capability.  This allows the model to interact with external tools (the Python functions defined in the script) in a structured way.  The model doesn't execute the code directly; instead, it generates a JSON object specifying which function to call and with what arguments. The script then executes the function and returns the results to the model.

### 9.C. Pydantic Models for Structured Data

Pydantic models are used to define the input and output types of the agent's tools.  This has several benefits:

*   **Data Validation:** Pydantic automatically validates the data, ensuring that the arguments provided by the OpenAI model are of the correct type and format.
*   **Type Hinting:** Pydantic models provide type hints, making the code more readable and maintainable.
*   **Integration with OpenAI:** The `pydantic_function_tool` function converts the Pydantic models into a schema that the OpenAI API understands, making it easy to define tools for function calling.

### 9.D. Rich Library for Enhanced Output

The `rich` library is used to provide clear, well-formatted output to the console.  This makes it easier to follow the agent's progress and understand the results of its actions.  Features used include:

*   `Console`:  For printing colored text and other rich content.
*   `Panel`:  For creating visually distinct blocks of text.
*   `rule`: for creating visual separation between agent runs.

### 9.E. DuckDB Integration

The script interacts with DuckDB using the `subprocess` module. This module allows the script to run external commands as if they were typed directly into the terminal. The agent interacts with the DuckDB database through a series of calls to its CLI using subprocess.

## 10. Limitations and Potential Improvements

*   **Model Choice:** The script is currently configured to use a less-capable `o3-mini` model, a suggestion for a `gpt-4o-mini` model is commented out.  Using a more powerful model like GPT-4o (if available) would likely improve the agent's performance significantly, especially on complex requests.
*   **Error Handling:** While the script has some basic error handling, it could be made more robust. For example, it could handle cases where the DuckDB database file doesn't exist or is corrupted.
*   **Tool Set:** The current set of tools is relatively limited.  Adding more tools, such as the ability to create temporary tables or views, could enhance the agent's capabilities.
*   **Context Window:** The OpenAI API has a limited context window.  For very complex databases or long conversations, the agent might run out of context. Strategies for managing context, such as summarizing previous interactions, could be implemented.
*   **Security:** The script executes SQL queries generated by an AI model.  This could be a security risk if the user input is not carefully sanitized.  For production use, it would be essential to implement strong security measures to prevent SQL injection attacks. Consider using parameterized queries instead of directly embedding user input into SQL strings.
* **State Management:** Currently, the state is maintained entirely through the `messages` list passed to the OpenAI API. For more complex scenarios, a more sophisticated state management system (e.g., using a database or external memory) might be beneficial.
* **DuckDB as a Dependency:** Currently the script relies on the `duckdb` CLI tool to be installed and on the path. It would be more robust to use the duckdb python package directly, this can be done by adding `"duckdb"` to the dependencies managed by `uv`, and changing how we interact with duckdb.
* **Model Choice** Currently the model is hard coded as `"o3-mini"`, it might be useful to expose this to the command line to permit easily switching between different models, or defaulting to different models based on their availability.
* **More robust function name handling** Currently function names and Model names are handled through a series of `if`/`elif` statements. This could be made more robust by creating a dictionary that maps between function name and associated tool.

## 11. Troubleshooting

*   **`OPENAI_API_KEY` not set:** Make sure you have set the `OPENAI_API_KEY` environment variable correctly.
*   **`duckdb` command not found:**  Ensure that the `duckdb` CLI is installed and accessible in your system's PATH.
*   **Pydantic validation errors:** If you see errors related to argument validation, double-check the user prompt and the agent's instructions to ensure they are clear and consistent.
*   **Maximum compute loops reached:**  If the agent gets stuck, try simplifying the user request or increasing the `--compute` value.
*  **`uv` command not found:** Make sure that uv is installed correctly. If you installed it via the installation script, be sure to restart your terminal or re-source your `.*rc` file.