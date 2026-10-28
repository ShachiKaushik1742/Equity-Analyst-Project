import sys
from pathlib import Path
print(f"Python {sys.version.split()[0]} runs successfully.")
print(f"Course folder: {Path(__file__).resolve().parent}")
