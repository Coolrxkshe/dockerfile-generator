import ollama

SYSTEM_PROMPT = """You are a Docker expert assistant. 
The user has generated a Dockerfile and wants to ask questions about it.
You have the Dockerfile in front of you.
Answer clearly and concisely in plain English.
When suggesting changes, always show the exact line to change.
Keep answers short — max 4-5 sentences unless the user asks for more detail.
Never make up information. If unsure, say so."""

def chat_with_dockerfile(
    dockerfile: str,
    user_message: str,
    history: list,
    model: str = "codellama"
) -> str:
    # Build messages with dockerfile as context
    messages = [
        {
            "role": "user",
            "content": f"""Here is the Dockerfile we are discussing:

```dockerfile
{dockerfile}
```

Keep this in mind for all my questions."""
        },
        {
            "role": "assistant", 
            "content": "I have reviewed your Dockerfile and I am ready to answer your questions about it."
        }
    ]

    # Add conversation history
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add current question
    messages.append({
        "role": "user",
        "content": user_message
    })

    response = ollama.chat(
        model=model,
        messages=messages
    )

    return response["message"]["content"]


def get_quick_questions() -> list:
    return [
        "🔒 How can I make this more secure?",
        "📦 How can I reduce the image size?",
        "⚡ How can I speed up the build?",
        "🏥 How do I add a health check?",
        "🔄 How do I add environment variables?",
        "👤 How do I run as a non-root user?",
        "📋 Explain each line in plain English",
        "🐛 What could go wrong with this Dockerfile?",
    ]