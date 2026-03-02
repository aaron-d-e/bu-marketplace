"""
Vercel serverless entrypoint. Exposes Django WSGI app as `app` so Vercel can route requests to it.
"""
import os
import sys

# Project root (parent of api/) so Django and main can be imported
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

from main.wsgi import application

app = application
