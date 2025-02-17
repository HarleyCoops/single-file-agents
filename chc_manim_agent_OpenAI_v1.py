# /// script
# dependencies = [
#   "openai>=1.63.0",
#   "rich>=13.7.0",
#   "pydantic>=2.0.0",
#   "manim>=0.18.0",
#   "python-dotenv>=1.0.0",  # Add dotenv for environment variable support
#   "latex>=0.7.0",          # Add LaTeX support
#   "latextools>=0.3.0",     # Additional LaTeX utilities
#   "dvisvgm>=0.1.0"         # For DVI to SVG conversion
# ]
# ///

import os
import sys
import subprocess
import json
import argparse
import codecs
import locale
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from openai import pydantic_function_tool
import manim
from dotenv import load_dotenv
import datetime
import glob

# Set UTF-8 as default encoding for the script
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Ensure proper encoding for file operations
locale.getpreferredencoding = lambda: 'UTF-8'

# Initialize console for rich output
console = Console(force_terminal=True, force_interactive=True, color_system="auto")

# Load environment variables
load_dotenv(override=True)  # Add override=True to ensure .env values take precedence

# Initialize OpenAI client
client = OpenAI()

class GenerateManimCodeArgs(BaseModel):
    reasoning: str = Field(..., description="Why this Manim code is being generated.")
    description: str = Field(..., description="A description of the animation to be created.")
    
def generate_manim_code(reasoning: str, description: str) -> str:
    prompt = f"""
    You are a Manim code generation expert. Create Manim code (using Manim's Python API) to visualize the following:

    {description}

    Important LaTeX Guidelines:
    1. Always use raw strings (r"") for LaTeX expressions
    2. Use MathTex() for mathematical expressions
    3. Use double backslashes (\\\\) for LaTeX commands
    4. For matrices, use proper environments (bmatrix, pmatrix, vmatrix)
    5. Use proper LaTeX spacing commands (\\;, \\:, \\,)
    6. For multi-line equations, use aligned environment with &
    7. Stick to basic math mode and amsmath/amssymb packages

    Output *only* the Python code for a Manim Scene. Do not include any explanations or surrounding text. Make sure the code defines a class that inherits from manim.Scene and implements a construct() method. The code must be runnable. Do not include comments.
    """
    response = client.chat.completions.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": "You are a Manim code generation expert. Generate only valid Manim code without explanations."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "text"}
    )
    code = response.choices[0].message.content
    
    # Create a directory for manim scenes if it doesn't exist
    os.makedirs("manim_scenes", exist_ok=True)
    
    # Use a fixed filename based on the scene name
    filename = "manim_scenes/current_scene.py"
    
    # Read existing code if file exists
    existing_code = ""
    if os.path.exists(filename):
        with open(filename, "r", encoding='utf-8') as f:
            existing_code = f.read()
    
    # Only write if the code is different
    if code != existing_code:
        with open(filename, "w", encoding='utf-8') as f:
            f.write(code)
        
        # Create a backup with timestamp for logging purposes
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"manim_scenes/backup_scene_{timestamp}.py"
        with open(backup_file, "w", encoding='utf-8') as f:
            f.write(code)
    
    console.log(f"[blue]Generated Manim Code saved to {filename}:[/blue]\n{code}")
    return {"code": code, "filename": filename}

class RunManimCodeArgs(BaseModel):
    reasoning: str = Field(..., description="Why this Manim code is being run.")
    manim_code: str = Field(..., description="The Manim Python code to execute.")
    scene_name: str = Field(..., description="The name of the Manim Scene class within the code.")    
    
def run_manim_code(reasoning: str, manim_code: str, scene_name: str) -> str:
    try:
        # Always use the fixed current scene file
        current_file = "manim_scenes/current_scene.py"
        
        # Update the file with the new code
        with open(current_file, "w", encoding='utf-8') as f:
            f.write(manim_code)

        # Get quality setting from environment variable
        quality = os.getenv("MANIM_QUALITY", "medium").lower()
        quality_flag = {
            "low": "-ql",
            "medium": "-qm",
            "high": "-qh"
        }.get(quality, "-qm")

        # Set PYTHONIOENCODING environment variable for subprocess
        my_env = os.environ.copy()
        my_env["PYTHONIOENCODING"] = "utf-8"

        # Run Manim using subprocess with python -m
        result = subprocess.run(
            [
                "python",
                "-m",
                "manim",
                current_file,
                scene_name,
                quality_flag,
                "--disable_caching",
            ],
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            env=my_env
        )

        # Check for errors and return appropriate message
        if result.returncode == 0:
            console.log(f"[green]Manim execution successful! Scene file: {current_file}[/green]")
            return f"Manim execution successful. Scene file: {current_file}"
        else:
            console.log(f"[red]Manim execution failed for {current_file}:[/red]")
            error_message = result.stderr
            console.log(error_message)
            return f"Manim execution failed: {error_message}"

    except Exception as e:
        console.log(f"[red]Error running Manim: {e}[/red]")
        return f"Error running Manim: {str(e)}"

class GetConfigurationArgs(BaseModel):
    reasoning: str = Field(..., description="Why are you requesting the Manim Configuration")

def get_manim_configuration(reasoning: str) -> str:
    """This tool returns the current manim configuration"""
    result = subprocess.run(
        [
            "python",
            "-m",
            "manim",
            "cfg",
            "show"
        ],
        capture_output=True,
        text=True,
        check=False, 
    )
    return result.stdout

def validate_api_key():
    """Validate that we have a valid OpenAI API key format"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY not found in .env file[/red]")
        sys.exit(1)
    if not api_key.startswith("sk-"):
        console.print("[red]Error: Invalid OpenAI API key format. Key should start with 'sk-'[/red]")
        sys.exit(1)
    return api_key

AGENT_PROMPT = """
<purpose>
    You are a Manim animation expert. Your goal is to create Manim code that visualizes a given description.
</purpose>

<instructions>
    <instruction>Use the provided tools to generate and test Manim code.</instruction>
    <instruction>Start by generating Manim code using the `generate_manim_code` tool.</instruction>
    <instruction>Then, run the generated code using the `run_manim_code` tool to check for errors.</instruction>
    <instruction>If the code runs successfully, compare the current implementation against the original prompt.</instruction>
    <instruction>Continue development until ALL elements from the prompt are implemented.</instruction>
    <instruction>Only mark the scene as complete when it fully matches ALL requirements from the prompt.</instruction>
    <instruction>If errors occur, use the error message to refine the code. If the errors seem configuration related, use `get_manim_configuration` to see the current configuration.</instruction>
    <instruction>Be precise and ensure the generated code defines a Manim `Scene` class with a `construct` method.</instruction>
    <instruction>Think step by step. Explain your reasoning for each tool call.</instruction>
    
    <critical_rules>
        <rule>NEVER simplify or omit any elements from the requested animation.</rule>
        <rule>NEVER add disclaimers about simplification - implement exactly what is requested.</rule>
        <rule>ALL aspects of the animation must be implemented exactly as specified in the prompt.</rule>
        <rule>If something seems complex, break it down into steps but implement it fully.</rule>
        <rule>Do not skip or simplify mathematical expressions, transitions, or visual elements.</rule>
        <rule>Keep working until every single detail from the prompt is implemented.</rule>
    </critical_rules>
    
    <latex_guidelines>
        <guideline>Always use raw strings (r"") for LaTeX expressions to avoid escape character issues.</guideline>
        <guideline>Wrap complex mathematical expressions in Tex() or MathTex() instead of Text().</guideline>
        <guideline>For equations with special characters, use double backslashes (\\) for LaTeX commands.</guideline>
        <guideline>For multi-line equations, use aligned environment with proper alignment points (&).</guideline>
        <guideline>Avoid unsupported LaTeX packages - stick to amsmath, amssymb, and basic math mode.</guideline>
        <guideline>Use proper LaTeX spacing commands (\\;, \\:, \\,) instead of manual spaces.</guideline>
        <guideline>For matrices, use the bmatrix, pmatrix, or vmatrix environments with proper \\\\ for row breaks.</guideline>
    </latex_guidelines>
</instructions>

<tools>
    <tool>
        <name>generate_manim_code</name>
        <description>Generates Manim code based on a natural language description.</description>
        <parameters>
            <parameter>
                <name>reasoning</name>
                <type>string</type>
                <description>Why this Manim code is being generated.</description>
                <required>true</required>
            </parameter>
            <parameter>
                <name>description</name>
                <type>string</type>
                <description>A description of the animation to be created.</description>
                <required>true</required>
            </parameter>
        </parameters>
    </tool>

    <tool>
        <name>run_manim_code</name>
        <description>Runs Manim code and returns the results (success or error message).</description>
        <parameters>
            <parameter>
                <name>reasoning</name>
                <type>string</type>
                <description>Why this Manim code is being run.</description>
                <required>true</required>
            </parameter>
            <parameter>
                <name>manim_code</name>
                <type>string</type>
                <description>The Manim Python code to execute.</description>
                <required>true</required>
            </parameter>
            <parameter>
                <name>scene_name</name>
                <type>string</type>
                <description>The name of the Manim Scene class within the code.</description>
                <required>true</required>
            </parameter>
        </parameters>
    </tool>

    <tool>
        <name>get_manim_configuration</name>
        <description>Returns the current Manim Configuration</description>
        <parameters>
            <parameter>
                <name>reasoning</name>
                <type>string</type>
                <description>Why are you requesting the Manim Configuration</description>
                <required>true</required>
            </parameter>
        </parameters>
    </tool>
</tools>

<user-request>
    {{user_request}}
</user-request>
"""

class AgentLogger:
    def __init__(self, prompt, scene_name):
        self.log_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "prompt": prompt,
            "scene_name": scene_name,
            "iterations": [],
            "final_result": None,
            "final_scene_file": None
        }
        
    def log_iteration(self, iteration_num, tool_name, reasoning, result, code=None):
        iteration_data = {
            "iteration_number": iteration_num,
            "timestamp": datetime.datetime.now().isoformat(),
            "tool_used": tool_name,
            "reasoning": reasoning,
            "result": result
        }
        if code:
            iteration_data["code"] = code
        self.log_data["iterations"].append(iteration_data)
        self._save_log()
        
    def log_final_result(self, success, scene_file=None):
        self.log_data["final_result"] = "success" if success else "failure"
        self.log_data["final_scene_file"] = scene_file
        self._save_log()
        
    def _save_log(self):
        # Create logs directory if it doesn't exist
        os.makedirs("manim_logs", exist_ok=True)
        timestamp = self.log_data["timestamp"].replace(":", "-").split(".")[0]
        filename = f"manim_logs/agent_log_{timestamp}.json"
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Manim Agent using OpenAI API")
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("-p", "--prompt", help="The description of the animation")
    prompt_group.add_argument("-f", "--file", help="Path to a file containing the prompt")
    parser.add_argument("-s", "--scene", required=True, help="The name of the scene class (e.g., MyScene)")
    parser.add_argument("-c", "--compute", type=int, default=25, help="Maximum number of agent loops (default: 25)")
    args = parser.parse_args()

    # Setup OpenAI client with validated API key
    client.api_key = validate_api_key()  # Update the client's API key

    # Get prompt either from command line or file
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                prompt = f.read().strip()
        except UnicodeDecodeError:
            # Fallback to latin-1 if UTF-8 fails
            try:
                with open(args.file, 'r', encoding='latin-1') as f:
                    prompt = f.read().strip()
            except Exception as e:
                console.print(f"[red]Error reading prompt file with latin-1 encoding: {e}[/red]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error reading prompt file: {e}[/red]")
            sys.exit(1)
    else:
        prompt = args.prompt

    # Initialize the agent logger
    agent_logger = AgentLogger(prompt, args.scene)

    # Prepare the prompt
    completed_prompt = AGENT_PROMPT.replace("{{user_request}}", prompt)
    messages = [
        {"role": "system", "content": "You are a Manim animation expert that helps create and debug Manim code."},
        {"role": "user", "content": completed_prompt}
    ]

    # Agent Loop
    compute_iterations = 0
    current_scene_file = None
    scene_complete = False
    
    while not scene_complete and compute_iterations < args.compute:
        console.rule(f"[yellow]Agent Loop {compute_iterations+1}/{args.compute}[/yellow]")
        compute_iterations += 1

        try:
            response = client.chat.completions.create(
                model="o3-mini",
                messages=messages,
                tools=[
                    pydantic_function_tool(GenerateManimCodeArgs, name="generate_manim_code"),
                    pydantic_function_tool(RunManimCodeArgs, name="run_manim_code"),
                    pydantic_function_tool(GetConfigurationArgs, name="get_manim_configuration"),
                ],
                tool_choice="auto"  # Always force tool usage
            )

            if response.choices:
                assert len(response.choices) == 1
                message = response.choices[0].message

                if not message.tool_calls or len(message.tool_calls) == 0:
                    # Check if this is a completion message
                    if "animation is complete" in message.content.lower():
                        scene_complete = True
                        console.print("\n[green]Animation sequence completed successfully![/green]")
                        agent_logger.log_final_result(True, current_scene_file)
                        return
                    
                    # Otherwise, reject non-tool responses
                    console.print("[red]Received non-tool response. Forcing tool usage by adding explicit instruction.[/red]")
                    messages.append({
                        "role": "user",
                        "content": """You must use one of the provided tools. Do not provide explanations or code directly in the message.
                        - Use generate_manim_code to create new code
                        - Use run_manim_code to execute code
                        - Use get_manim_configuration to check settings
                        Choose the appropriate tool and proceed."""
                    })
                    continue

                # Normal tool call handling
                tool_call = message.tool_calls[0]
                func_call = tool_call.function
                func_name = func_call.name
                func_args_str = func_call.arguments

                messages.append(
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": func_call,
                            }
                        ],
                    }
                )

                console.print(f"[blue]Function Call:[/blue] {func_name}({func_args_str})")

                try:
                    # Validate arguments and call the appropriate function
                    if func_name == "generate_manim_code":
                        args_parsed = GenerateManimCodeArgs.model_validate_json(func_args_str)
                        result = generate_manim_code(reasoning=args_parsed.reasoning, description=args_parsed.description)
                        current_scene_file = result["filename"]
                        agent_logger.log_iteration(
                            compute_iterations,
                            "generate_manim_code",
                            args_parsed.reasoning,
                            "Code generated successfully",
                            result["code"]
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"result": result["code"], "scene_name": args.scene}),
                            }
                        )

                    elif func_name == "run_manim_code":
                        args_parsed = RunManimCodeArgs.model_validate_json(func_args_str)
                        result = run_manim_code(reasoning=args_parsed.reasoning, manim_code=args_parsed.manim_code, scene_name=args_parsed.scene_name)
                        agent_logger.log_iteration(
                            compute_iterations,
                            "run_manim_code",
                            args_parsed.reasoning,
                            result
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"result": result})
                            }
                        )
                        # Only check for successful execution, no content-specific checks
                        if "successful" in result:
                            # Let the model decide if more work is needed through its next response
                            messages.append({
                                "role": "user",
                                "content": "The scene ran successfully. Compare the current implementation against the original prompt. If the animation is incomplete or missing elements, continue development. If the animation fully matches the prompt requirements, mark it as complete."
                            })
                            continue

                    elif func_name == "get_manim_configuration":
                        args_parsed = GetConfigurationArgs.model_validate_json(func_args_str)
                        result = get_manim_configuration(reasoning=args_parsed.reasoning)
                        agent_logger.log_iteration(
                            compute_iterations,
                            "get_manim_configuration",
                            args_parsed.reasoning,
                            result
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"result": result})
                            }
                        )

                    else:
                        raise ValueError(f"Unknown function call: {func_name}")

                except ValidationError as e:
                    error_msg = f"Argument validation failed for {func_name}: {e}"
                    console.print(f"[red]{error_msg}[/red]")
                    agent_logger.log_iteration(
                        compute_iterations,
                        func_name,
                        "Validation Error",
                        error_msg
                    )
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"error": error_msg})
                    })

        except Exception as e:
            console.print(f"[red]Error in agent loop: {e}[/red]")
            agent_logger.log_final_result(False)
            raise

    if not scene_complete:
        console.print("[yellow]Warning: Maximum compute loops reached without completing the full animation sequence[/yellow]")
        agent_logger.log_final_result(False)
        raise Exception(f"Maximum compute loops reached: {compute_iterations}/{args.compute}")

if __name__ == "__main__":
    main()
            