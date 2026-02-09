import os

def get_project_root():
    """Get project root, accounting for bundled SFX mode."""
    file_path = os.path.abspath(__file__)

    temp_patterns = ['.cache', 'tmp', 'temp', 'AppData/Local/Temp', 'AppData\\Local\\Temp']
    is_bundled = any(pattern in file_path for pattern in temp_patterns)

    if is_bundled:
        # In bundled mode: data files are in user's working directory
        return os.getcwd()
    else:
        # Normal mode: parent of bratt folder
        return os.path.dirname(os.path.dirname(file_path))

PROJECT_ROOT = get_project_root()
