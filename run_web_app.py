#!/usr/bin/env python3
"""
Run the Learning Intelligence Tool Web Application
"""

import os
import sys

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import and run the app
from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
