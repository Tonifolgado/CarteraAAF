#!/usr/bin/env python3
import sys
print(f"Python path: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import pandas as pd
    print("✅ pandas importado correctamente")
    print(f"pandas version: {pd.__version__}")
except ImportError as e:
    print(f"❌ Error importando pandas: {e}")

try:
    import yfinance as yf
    print("✅ yfinance importado correctamente")
except ImportError as e:
    print(f"❌ Error importando yfinance: {e}")