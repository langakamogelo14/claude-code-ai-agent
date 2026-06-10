import argparse
import os
import sys

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY") #Securely looks up my private password (API key) without hardcoding it directly into the script.
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1") #Sets the web address of where the prompt will be sent.


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set") #If the program couldn't find my password it crashes, rather than sending a broken request.

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL) #Packages the API key & the server URL that will carry my data across the internet

    #The API Request: Sending the Message
    chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=[{"role": "user", "content": args.p}],
        tools[
            {"type": "function", 
                "function": {
                    "name": "Read", "description": "Read and return the contents of a file", 
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

    #Handling the Response
    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response") #safety check. Ensures the server actually sent a reply back.

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    #TODO: Uncomment the following line to pass the first stage
    print(chat.choices[0].message.content) 
    #Digs into the JSON bundle returned by the API, grabs the very first reply (choices[0]), finds the message, extracts the raw text content, and prints it to your terminal screen.


if __name__ == "__main__":
    main()


