import ollama

model = "qwen2.5:3b"
existing_memory = "I prefer Python"
new_memory = "I prefer Java"

prompt = f"""
    You are a contradiction detector.
    Memory A:
    {existing_memory}
    Memory B:
    {new_memory}
    Determine whether the two memories directly contradict each other.
    Rules:
    - Return YES if they conflict.
    - Return NO if they do not conflict.
    - Return ONLY YES or NO.
    Examples:
    Memory A:
    I prefer Python
    Memory B:
    I prefer Java
    YES
    Memory A:
    I prefer Python
    Memory B:
    I prefer Strawberries

    NO
"""

response = ollama.chat(
    model=model,
    messages=[
        {"role": "user", "content": prompt}
    ]
)
print("Response content:")
print(repr(response["message"]["content"]))
