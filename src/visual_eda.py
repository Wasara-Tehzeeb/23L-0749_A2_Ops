from pathlib import Path
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import random

# Load audit data created in Task 1.2
df = pd.read_csv("dataset_audit.csv")

# Create folder for EDA figures
OUTPUT_DIR = Path("eda_figures")
OUTPUT_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# 1. SAMPLE IMAGE GRID
# --------------------------------------------------

random.seed(42)

for class_name in ["AI", "Real"]:
    class_df = df[df["class"] == class_name]

    # Select 9 reproducible random samples
    sample_df = class_df.sample(
        n=min(9, len(class_df)),
        random_state=42
    )

    fig, axes = plt.subplots(3, 3, figsize=(10, 10))
    axes = axes.flatten()

    for ax, (_, row) in zip(axes, sample_df.iterrows()):
        try:
            with Image.open(row["file_path"]) as img:
                img = img.convert("RGB")
                ax.imshow(img)

            ax.set_title(class_name)
            ax.axis("off")

        except Exception:
            ax.axis("off")

    plt.suptitle(f"{class_name} Image Samples", fontsize=16)
    plt.tight_layout()

    output_path = OUTPUT_DIR / f"{class_name.lower()}_sample_grid.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


# --------------------------------------------------
# 2. WIDTH HISTOGRAM
# --------------------------------------------------

plt.figure(figsize=(9, 6))

for class_name in ["AI", "Real"]:
    values = df[df["class"] == class_name]["width"]
    plt.hist(values, bins=30, alpha=0.5, label=class_name)

plt.xlabel("Image Width (pixels)")
plt.ylabel("Number of Images")
plt.title("Distribution of Image Width by Class")
plt.legend()
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "width_histogram.png",
    dpi=150,
    bbox_inches="tight"
)
plt.close()


# --------------------------------------------------
# 3. HEIGHT HISTOGRAM
# --------------------------------------------------

plt.figure(figsize=(9, 6))

for class_name in ["AI", "Real"]:
    values = df[df["class"] == class_name]["height"]
    plt.hist(values, bins=30, alpha=0.5, label=class_name)

plt.xlabel("Image Height (pixels)")
plt.ylabel("Number of Images")
plt.title("Distribution of Image Height by Class")
plt.legend()
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "height_histogram.png",
    dpi=150,
    bbox_inches="tight"
)
plt.close()


# --------------------------------------------------
# 4. FILE SIZE HISTOGRAM
# --------------------------------------------------

plt.figure(figsize=(9, 6))

for class_name in ["AI", "Real"]:
    # Convert bytes to KB
    values = df[df["class"] == class_name]["file_size_bytes"] / 1024
    plt.hist(values, bins=30, alpha=0.5, label=class_name)

plt.xlabel("File Size (KB)")
plt.ylabel("Number of Images")
plt.title("Distribution of File Size by Class")
plt.legend()
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "file_size_histogram.png",
    dpi=150,
    bbox_inches="tight"
)
plt.close()


print("Visual EDA completed successfully.")
print("\nFigures created:")
print("eda_figures/ai_sample_grid.png")
print("eda_figures/real_sample_grid.png")
print("eda_figures/width_histogram.png")
print("eda_figures/height_histogram.png")
print("eda_figures/file_size_histogram.png")