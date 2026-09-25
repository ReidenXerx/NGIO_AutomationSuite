"""Build the MO2 plugin archive: python mo2/package.py -> mo2/dist/NGIO_Grass_Cache_MO2_<version>.zip

The archive holds one folder, ngio_grass/, meant to be extracted into MO2's plugins folder.
The tests run first; a red suite builds nothing.
"""
import hashlib
import os
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ngio_grass import version_string  # noqa: E402

tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=HERE)
if tests.returncode:
    sys.exit("tests failed; nothing built")

out_dir = os.path.join(HERE, "dist")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, f"NGIO_Grass_Cache_MO2_{version_string()}.zip")
src = os.path.join(HERE, "ngio_grass")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for name in sorted(files):
            if name.endswith((".py", ".md")):
                full = os.path.join(root, name)
                z.write(full, os.path.relpath(full, HERE))
    z.write(os.path.join(HERE, "README.md"), "ngio_grass/README.md")
digest = hashlib.sha256(open(out, "rb").read()).hexdigest()
print(out)
print("sha256", digest)
