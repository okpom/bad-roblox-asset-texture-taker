import os

def debug_print(*args, **kwargs):
    """Debug print function to control debug output."""
    if os.getenv("DEBUG"):
        print(*args, **kwargs)