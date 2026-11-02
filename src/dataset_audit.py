from pathlib import Path
from PIL import Image
import pandas as pd
import hashlib

DATASET_DIRS = {
    "AI": Path("data/AiArtData/AiArtData"),
    "Real": Path("data/RealArt/RealArt"),
}

records = []
corrupt_files = []

for class_name, folder in DATASET_DIRS.items():
    for file_path in folder.rglob("*"):

        if not file_path.is_file():
            continue

        try:
            # Calculate SHA-256 hash
            sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)

            # Read image information
            with Image.open(file_path) as img:
                width, height = img.size
                colour_mode = img.mode
                image_format = img.format

            records.append({
                "class": class_name,
                "file_path": str(file_path),
                "file_size_bytes": file_path.stat().st_size,
                "width": width,
                "height": height,
                "colour_mode": colour_mode,
                "format": image_format,
                "sha256": sha256.hexdigest(),
            })

        except Exception as e:
            corrupt_files.append({
                "file_path": str(file_path),
                "error": str(e)
            })

df = pd.DataFrame(records)

# Save full audit
df.to_csv("dataset_audit.csv", index=False)

# Find exact duplicates using SHA-256
duplicate_mask = df.duplicated(subset=["sha256"], keep=False)
duplicates = df[duplicate_mask]
duplicates.to_csv("duplicate_images.csv", index=False)

# Save corrupt files
pd.DataFrame(corrupt_files).to_csv("corrupt_files.csv", index=False)

print("\n========== VISIONGUARD DATASET AUDIT ==========")

print("\nVALID IMAGE COUNTS PER CLASS")
print(df.groupby("class").size())

print("\nWIDTH STATISTICS")
print(df.groupby("class")["width"].agg(["min", "median", "max"]))

print("\nHEIGHT STATISTICS")
print(df.groupby("class")["height"].agg(["min", "median", "max"]))

print("\nFILE SIZE STATISTICS (BYTES)")
print(df.groupby("class")["file_size_bytes"].agg(["min", "median", "max"]))

print("\nCORRUPT / UNREADABLE FILES")
print(len(corrupt_files))

print("\nFILES INVOLVED IN EXACT DUPLICATES")
print(len(duplicates))

print("\nUNIQUE DUPLICATE HASH GROUPS")
if len(duplicates) > 0:
    print(duplicates["sha256"].nunique())
else:
    print(0)

print("\nAudit files created:")
print("dataset_audit.csv")
print("duplicate_images.csv")
print("corrupt_files.csv")