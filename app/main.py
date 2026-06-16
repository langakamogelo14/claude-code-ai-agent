import argparse
import os
import sys
import json
from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY") # Securely looks up my private password (API key) without hardcoding it directly into the script.
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1") # Sets the web address of where the prompt will be sent.

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set") # If the program couldn't find my password it crashes, rather than sending a broken request.

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL) # Packages the API key & the server URL that will carry my data across the internet

    # 1. Initialize the conversation history
    messages = [{"role": "user", "content": args.p}]

    # 2. Start the Agent Loop
    while True:
        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=[
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
                }
            ]
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response") # safety check. Ensures the server actually sent a reply back.

        message = chat.choices[0].message
        
        # 3. Append the AI's action/response to the history
        messages.append(message)

        # 4. Handle Tool Calls
        if message.tool_calls:
            for tc in message.tool_calls:
                if tc.function.name == "Read":
                    tool_args = json.loads(tc.function.arguments)
                    file_path = tool_args.get("file_path")
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            result = f.read()
                    except Exception as e:
                        result = f"Error reading file: {e}"
                    
                    # 5. Append the file contents back to the history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result
                    })
                    
        # 6. Break the loop when a standard text response is given
        elif message.content:
            print(message.content)
            break 

if __name__ == "__main__":
    main()