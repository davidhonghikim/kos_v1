from openpass.entropy import generate_entropy

def generate_passphrase():
    entropy = generate_entropy()
    return f"pass-{entropy.hex()[:8]}"
