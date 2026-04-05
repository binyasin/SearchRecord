import sys
import os

# Replace YOUR_USERNAME below with your PythonAnywhere username
USERNAME = "YOUR_USERNAME"

sys.path.insert(0, f"/home/{USERNAME}/SearchRecord")
os.environ["PUBLIC_URL"] = f"https://{USERNAME}.pythonanywhere.com"

from app import app as application
