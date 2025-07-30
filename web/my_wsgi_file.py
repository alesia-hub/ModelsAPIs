# wsgi.py
import sys
import os
from dotenv import load_dotenv

# Add your project directory to the sys.path
project_home = os.path.expanduser('/home/apscientist/ModelsAPI/')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables (optional)
load_dotenv(os.path.join(project_home, ".env"))

# Import the Flask app
from app import app as application  # THIS is what PythonAnywhere looks for