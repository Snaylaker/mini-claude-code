import argparse
import os
import sys

import shlex
import json
import subprocess
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

    messages = [{"role": "user", "content": args.p}]

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
                                    "description": "The path to the file to read",
                                }
                            },
                            "required": ["file_path"],
                        },
                    },
                },
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
                                    "description": "The command to execute",
                                }
                            },
                        },
                    },
                },
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
                                    "description": "The path of the file to write to",
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The content to write to the file",
                                },
                            },
                        },
                    },
                },
            ],
        )

        if not chat.choices:
            raise RuntimeError("no choices in response")

        messages.append(chat.choices[0].message)

        if not chat.choices[0].message.tool_calls:
            print(chat.choices[0].message.content)
            break

        tool_call = chat.choices[0].message.tool_calls[0]

        tool_name = tool_call.function.name
        function_arguments = json.loads(tool_call.function.arguments)

        match tool_name:
            case "Bash":
                print("tool_call", tool_call, file=sys.stderr)
                command = function_arguments["command"]
                args = shlex.split(command)
                result = subprocess.run(args, capture_output=True, text=True)

                tool_result = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.stdout + result.stderr,
                }

                messages.append(
                    make_tool_response(tool_call.id, result.stdout + result.stderr)
                )

            case "Read":
                file_path = function_arguments["file_path"]
                with open(file_path, "r") as file:
                    data = file.read()

                tool_result = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": data,
                }
                messages.append(make_tool_response(tool_call.id, data))

            case "Write":
                file_path = function_arguments["file_path"]
                content = function_arguments["content"]

                with open(file_path, "w") as file:
                    file.write(content)

                messages.append(make_tool_response(tool_call.id, content))


def make_tool_response(tool_call_id: str, content: str):
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": content,
    }


if __name__ == "__main__":
    main()
