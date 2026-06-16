import argparse
import os
import sys
import json
import subprocess  # Added for running shell commands
from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY") 
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1") 

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set") 

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL) 

    # 1. Initialize the conversation history
    messages = [{"role": "user", "content": args.p}]

    # 2. Start the Agent Loop
    while True:
        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=[
                # --- READ TOOL ---
                {
                    "type": "function",
                    "function": {
                        "name": "Read",
                        "description": "Read and return the contents of a file",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path to file to read"
                                }
                            },
                            "required": ["file_path"]
                        }
                    }
                },
                # --- WRITE TOOL ---
                {
                    "type": "function",
                    "function": {
                        "name": "Write",
                        "description": "Write content to a file",
                        "parameters": {
                            "type": "object",
                            "required": ["file_path", "content"],
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path of the file to write to"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The content to write to the file"
                                }
                            }
                        }
                    }
                },
                # --- BASH TOOL ---
                {
                    "type": "function",
                    "function": {
                        "name": "Bash",
                        "description": "Execute a shell command",
                        "parameters": {
                            "type": "object",
                            "required": ["command"],
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "The command to execute"
                                }
                            }
                        }
                    }
                }
            ]
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        message = chat.choices[0].message
        
        # 3. Append the AI's action/response to the history
        messages.append(message)

        # 4. Handle Tool Calls
        if message.tool_calls:
            for tc in message.tool_calls:
                
                # --- EXECUTE READ TOOL ---
                if tc.function.name == "Read":
                    tool_args = json.loads(tc.function.arguments)
                    file_path = tool_args.get("file_path")
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            result = f.read()
                    except Exception as e:
                        result = f"Error reading file: {e}"
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result
                    })

                # --- EXECUTE WRITE TOOL ---
                elif tc.function.name == "Write":
                    tool_args = json.loads(tc.function.arguments)
                    file_path = tool_args.get("file_path")
                    content = tool_args.get("content")
                    
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        result = "File written successfully."
                    except Exception as e:
                        result = f"Error writing file: {e}"
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result
                    })

                # --- EXECUTE BASH TOOL ---
                elif tc.function.name == "Bash":
                    tool_args = json.loads(tc.function.arguments)
                    command = tool_args.get("command")
                    
                    try:
                        # Execute command, capturing both standard output and error output streams
                        completed_process = subprocess.run(
                            command,
                            shell=True,
                            capture_output=True,
                            text=True
                        )
                        # Combine standard output and error messages so the AI sees the full picture
                        result = completed_process.stdout + completed_process.stderr
                    except Exception as e:
                        result = f"Error executing command: {e}"
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result
                    })
                    
        # 5. Break the loop when a standard text response is given
        elif message.content:
            print(message.content)
            break 

if __name__ == "__main__":
    main()