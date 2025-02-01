import os

# Get the absolute path of the main project directory (not src/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Define the absolute path to the API key file in the main project directory
API_KEY_FILE = os.path.join(PROJECT_ROOT, "nexus_api_key.txt")

def load_api_key():
    """Load the API key from a file."""
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            return f.read().strip()  # Read and remove any extra whitespace
    else:
        raise FileNotFoundError(
            f"API key file '{API_KEY_FILE}' not found. Please create it and add your API key."
        )

def save_api_key(api_key):
    """Save a new API key to the file (if needed in the future)."""
    with open(API_KEY_FILE, "w") as f:
        f.write(api_key.strip())
    print("API key saved successfully.")
