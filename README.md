# mini-claude-code

A minimal AI coding assistant powered by LLMs with tool calling. It runs an agent loop that can read files, write files, and execute shell commands.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and an [OpenRouter](https://openrouter.ai/) API key.

```sh
export OPENROUTER_API_KEY="your-key-here"
```

## Usage

```sh
uv run mini-claude-code -p "your prompt here"
```

Or install it:

```sh
uv pip install .
mini-claude-code -p "read main.py and explain what it does"
```

## How it works

1. Sends your prompt to Claude Haiku via OpenRouter
2. The model can call tools: `Read` (files), `Write` (files), `Bash` (shell commands)
3. Tool results are fed back to the model in a loop until it produces a final text response

## Configuration

| Env var | Default | Description |
|---------|---------|-------------|
| `OPENROUTER_API_KEY` | (required) | Your OpenRouter API key |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | API base URL |
