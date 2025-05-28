import sys
import os

from app import app


# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


if __name__ == "__main__":
    app.run()
