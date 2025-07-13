def route_to_llm(model, prompt):
    print(f"[LLM Router] Routing to {model} with prompt: {prompt}")
    return f"[Response from {model}]"
