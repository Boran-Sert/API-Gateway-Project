"""
conftest.py — Root dizini sys.path'e ekler.
Shared kütüphanesine erişim sağlamak için gereklidir.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
