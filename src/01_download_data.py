"""Step 1 - Download the three public Kaggle datasets into data/raw/.

Kaggle serves public datasets as a zip at /api/v1/datasets/download/<owner>/<name>.
If that endpoint ever needs a login, set up ~/.kaggle/kaggle.json and run
`kaggle datasets download -d <ref>` instead (same files).
"""
import io
import shutil
import sys
import urllib.request
import zipfile

from config import KAGGLE_DATASETS, RAW

URL = "https://www.kaggle.com/api/v1/datasets/download/{ref}"


def download(name, spec, force=False):
    target = RAW / spec["save_as"]
    if target.exists() and not force:
        print(f"[skip] {target.name} already present")
        return target
    print(f"[get ] {spec['ref']} ...", flush=True)
    with urllib.request.urlopen(URL.format(ref=spec["ref"])) as resp:
        payload = resp.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        member = next(m for m in zf.namelist() if m.endswith(spec["file"]))
        with zf.open(member) as src, open(target, "wb") as dst:
            shutil.copyfileobj(src, dst)
    print(f"[done] {target.name} ({target.stat().st_size / 1e6:.1f} MB)")
    return target


if __name__ == "__main__":
    force = "--force" in sys.argv
    for name, spec in KAGGLE_DATASETS.items():
        download(name, spec, force=force)
