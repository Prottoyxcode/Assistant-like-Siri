from transformers import pipeline, set_seed, logging

# 🔇 Disable annoying logs and warnings
logging.set_verbosity_error()

def generate_text(prompt):
    generator = pipeline("text-generation", model="distilgpt2")
    set_seed(42)
    result = generator(
        prompt,
        max_new_tokens=50,
        truncation=True,
        pad_token_id=50256
    )
    return result[0]['generated_text']

# CLI loop
while True:
    command = input("Give command (or type 'exit'): ")
    if command.lower() == "exit":
        break
    print(generate_text(command), "\n")