# 🤖 Autonomous CLI Development Agent

An autonomous, terminal-based AI software engineering assistant built entirely in Python. This agent utilizes Large Language Models (LLMs) via REST APIs to autonomously navigate local file systems, execute shell commands, and perform intelligent code edits in a continuous REPL (Read-Eval-Print Loop).

## 🚀 Core Capabilities

Unlike standard chatbots, this agent features an autonomous loop with functional tool-calling. Once given a prompt, it will independently decide which tools to use, observe the results, and iterate until the task is fully complete.

* **File System I/O (`Read` & `Write`):** Autonomously opens, reads, generates, and overwrites local files to fix bugs or scaffold new code.
* **Shell Execution (`Bash`):** Direct integration with the system shell (`subprocess`) allowing the agent to run tests, install dependencies, and manipulate directories.
* **Contextual Memory:** Manages complex state by continuously appending tool execution results and API responses back into the conversation history array.

## ⚙️ System Architecture

The agent is built on a stateless-to-stateful architecture. Since LLM APIs are inherently stateless, the Python core acts as the "brain," managing the memory and physical environment.

1.  **Input:** User provides a natural language prompt via the CLI.
2.  **Reasoning:** The Anthropic Claude 3.5 Haiku model processes the prompt and returns structured JSON defining necessary tool calls.
3.  **Execution:** Python parses the JSON arguments, executes the local system command, and captures `stdout`/`stderr`.
4.  **Feedback:** The local execution result is appended to the message history and sent back to the LLM to inform its next decision.

## 🛠️ Technical Stack

* **Language:** Python 3
* **Libraries:** `argparse`, `os`, `sys`, `json`, `subprocess`
* **API Integration:** OpenRouter (OpenAI-compatible client format) 
* **Model:** Anthropic Claude 3.5 Haiku

## 💡 Key Engineering Learnings

Building this project provided deep, hands-on experience with modern software development concepts:
* **API Boundaries & JSON Parsing:** Safely extracting and typing arguments passed dynamically from an external REST API.
* **Subprocess Management:** Securely executing shell commands from within a Python script while intercepting standard output and error streams.
* **State Management:** Designing an autonomous `while` loop that accurately maintains conversation history and links tool responses to specific `tool_call_id`s without duplicating API requests.

