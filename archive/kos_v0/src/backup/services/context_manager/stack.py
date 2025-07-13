STACK = []

def push_context(ctx):
    STACK.append(ctx)

def pop_context():
    return STACK.pop() if STACK else None
