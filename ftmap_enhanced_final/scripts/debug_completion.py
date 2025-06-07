#!/usr/bin/env python3
"""
Debug version of FTMap Project Completion
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

print("=== FTMap Project Completion Debug ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Script path: {__file__}")

try:
    print("Creating completion directory...")
    workspace = Path("/home/murilo/girias/ftmapcaseiro")
    completion_dir = workspace / "project_completion"
    completion_dir.mkdir(exist_ok=True)
    print(f"✓ Created directory: {completion_dir}")
    
    print("Testing basic functionality...")
    
    # Test file creation
    test_file = completion_dir / "test.txt"
    with open(test_file, 'w') as f:
        f.write("Test file created successfully\n")
    print(f"✓ Created test file: {test_file}")
    
    print("✅ Basic functionality working")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=== Debug Complete ===")
