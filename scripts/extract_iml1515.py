"""Extract cobra's bundled iJO1366.xml.gz as knowledge/models/iML1515.xml.

iJO1366 is a genome-scale E. coli model that is large enough to support
all genes in the test suite (sdhC, ppc, etc.).  iML1515 is not bundled with
cobra, so we use iJO1366 as the stand-in model file.

Usage: python scripts/extract_iml1515.py
"""
import gzip
import os

import cobra.data

data_dir = os.path.dirname(cobra.data.__file__)
src = os.path.join(data_dir, "iJO1366.xml.gz")
dst = os.path.join("knowledge", "models", "iML1515.xml")

os.makedirs(os.path.dirname(dst), exist_ok=True)
with gzip.open(src, "rb") as fin:
    content = fin.read()
with open(dst, "wb") as fout:
    fout.write(content)
print(f"Extracted {len(content)} bytes -> {dst}")
