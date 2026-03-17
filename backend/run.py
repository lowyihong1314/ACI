import os
import sys

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend import create_app

app = create_app("development")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, debug=True)
