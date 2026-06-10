"""
local_client.py — Send a chat request to a locally running Ollama model
via its OpenAI-compatible HTTP endpoint and print the response.

Usage:
    # Make sure Ollama is running: `ollama serve`
    python local_client.py

Requirements:
    pip install openai
    ollama pull llama3.2:3b
"""

# ---------------------------------------------------------------------------
# WHY THIS IS "THE SAME SHAPE" AS A HOSTED GEMINI (OR OPENAI) CALL
# ---------------------------------------------------------------------------
# When you call a hosted LLM (e.g. Gemini via the OpenAI-compatible endpoint,
# or api.openai.com), you're just sending an HTTP POST to a server that runs
# the model on their hardware and returns JSON.  Ollama does exactly the same
# thing — it starts a local HTTP server (default: http://localhost:11434) and
# exposes the identical /v1/chat/completions endpoint with the same request/
# response schema.  The only difference is the URL (localhost vs a remote
# host) and the fact that inference happens on YOUR CPU/GPU instead of theirs.
# The Python client code is byte-for-byte identical; you just swap `base_url`.
# This makes "LLM inference" a protocol, not a vendor.
# ---------------------------------------------------------------------------

from openai import OpenAI

MODEL = "llama3.2:3b"          # change to "qwen2.5:0.5b" for a smaller model
PROMPT = "Explain the difference between a parameter and a hyperparameter in machine learning. Be concise."

def main():
    # Point the OpenAI client at the local Ollama server instead of api.openai.com.
    # No real API key needed; Ollama accepts any non-empty string.
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",           # required by the SDK but ignored by Ollama
    )

    print(f"Sending request to local Ollama ({MODEL})...\n")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful ML tutor. Answer clearly and briefly.",
            },
            {
                "role": "user",
                "content": PROMPT,
            },
        ],
        temperature=0.7,
    )

    reply = response.choices[0].message.content
    print("=" * 60)
    print(f"Model : {MODEL}")
    print(f"Prompt: {PROMPT}")
    print("=" * 60)
    print(reply)
    print("=" * 60)

    # Show token usage if reported
    usage = response.usage
    if usage:
        print(f"\nTokens — prompt: {usage.prompt_tokens}, "
              f"completion: {usage.completion_tokens}, "
              f"total: {usage.total_tokens}")


if __name__ == "__main__":
    main()
