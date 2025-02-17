# /// script
# dependencies = [
#   "openai>=1.63.0",
#   "rich>=13.7.0",
#   "pydantic>=2.0.0",
#   "manim>=0.18.0",
#   "python-dotenv>=1.0.0"  # Add dotenv for environment variable support
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
    console.log(f"[blue]Generated Manim Code:[/blue]\n{code}")
    return code    

class RunManimCodeArgs(BaseModel):
    reasoning: str = Field(..., description="Why this Manim code is being run.")
    manim_code: str = Field(..., description="The Manim Python code to execute.")
    scene_name: str = Field(..., description="The name of the Manim Scene class within the code.")    
    
def run_manim_code(reasoning: str, manim_code: str, scene_name: str) -> str:
    try:
        # 1. Write the code to a temporary file with UTF-8 encoding
        with open("temp_manim_scene.py", "w", encoding='utf-8') as f:
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

        # 2. Run Manim using subprocess with python -m
        result = subprocess.run(
            [
                "python",
                "-m",
                "manim",
                "temp_manim_scene.py",
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

        # 3. Check for errors and return appropriate message
        if result.returncode == 0:
            console.log("[green]Manim execution successful![/green]")
            return "Manim execution successful."
        else:
            console.log("[red]Manim execution failed:[/red]")
            error_message = result.stderr
            console.log(error_message)
            return f"Manim execution failed: {error_message}"

    except Exception as e:
        console.log(f"[red]Error running Manim: {e}[/red]")
        return f"Error running Manim: {str(e)}"

    finally:
        # Clean up the temporary file
        if os.path.exists("temp_manim_scene.py"):
            os.remove("temp_manim_scene.py")

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
    <instruction>If the code runs successfully, you're done. If there are errors, use the error message to refine the code. If the errors seem configuration related, use `get_manim_configuration` to see the current configuration.</instruction>
    <instruction>Iterate until the Manim code runs without errors.</instruction>
    <instruction>Be precise and ensure the generated code defines a Manim `Scene` class with a `construct` method.</instruction>
    <instruction>Think step by step. Explain your reasoning for each tool call.</instruction>
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

    # Prepare the prompt
    completed_prompt = AGENT_PROMPT.replace("{{user_request}}", prompt)
    messages = [
        {"role": "system", "content": "You are a Manim animation expert that helps create and debug Manim code."},
        {"role": "user", "content": completed_prompt}
    ]

    # Agent Loop
    compute_iterations = 0
    consecutive_non_tool_responses = 0  # Track consecutive non-tool responses
    while True:
        console.rule(f"[yellow]Agent Loop {compute_iterations+1}/{args.compute}[/yellow]")
        compute_iterations += 1

        if compute_iterations >= args.compute:
            console.print("[yellow]Warning: Reached maximum compute loops without successful Manim run[/yellow]")
            raise Exception(f"Maximum compute loops reached: {compute_iterations}/{args.compute}")

        try:
            # If we've had one non-tool response, force tool usage
            tool_choice = None if consecutive_non_tool_responses == 0 else "auto"
            
            response = client.chat.completions.create(
                model="o3-mini",
                messages=messages,
                tools=[
                    pydantic_function_tool(GenerateManimCodeArgs, name="generate_manim_code"),
                    pydantic_function_tool(RunManimCodeArgs, name="run_manim_code"),
                    pydantic_function_tool(GetConfigurationArgs, name="get_manim_configuration"),
                ],
                tool_choice=tool_choice
            )

            if response.choices:
                assert len(response.choices) == 1
                message = response.choices[0].message

                if message.tool_calls and len(message.tool_calls) > 0:
                    consecutive_non_tool_responses = 0  # Reset counter when tools are used
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
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps({"result": result, "scene_name": args.scene}),
                                }
                            )

                        elif func_name == "run_manim_code":
                            args_parsed = RunManimCodeArgs.model_validate_json(func_args_str)
                            result = run_manim_code(reasoning=args_parsed.reasoning, manim_code=args_parsed.manim_code, scene_name=args_parsed.scene_name)
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps({"result": result})
                                }
                            )
                            if "successful" in result:
                                console.print("\n[green]Manim animation created successfully![/green]")
                                return

                        elif func_name == "get_manim_configuration":
                            args_parsed = GetConfigurationArgs.model_validate_json(func_args_str)
                            result = get_manim_configuration(reasoning=args_parsed.reasoning)
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
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": error_msg})
                        })

                else:
                    if consecutive_non_tool_responses > 0:
                        console.print("[red]Forcing tool usage after consecutive non-tool response[/red]")
                        continue
                        
                    # Handle case where model responds with content instead of a tool call
                    console.print("[yellow]Model responded with content instead of a tool call. Will require tool usage on next iteration.[/yellow]")
                    consecutive_non_tool_responses += 1
                    if hasattr(message, 'content') and message.content:
                        console.print(f"[blue]Model Response:[/blue]\n{message.content}")
                        messages.append({
                            "role": "assistant",
                            "content": message.content
                        })
                    else:
                        console.print("[red]Model response had no content or tool calls[/red]")
                        messages.append({
                            "role": "assistant",
                            "content": "Error: No response content provided"
                        })

        except Exception as e:
            console.print(f"[red]Error in agent loop: {e}[/red]")
            raise

if __name__ == "__main__":
    main()
            