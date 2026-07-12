import os
import pathlib
from matplotlib import pyplot as plt
import numpy as np

ROOT_DIR = "figures" # path to root database directory
# Create the output directory
OUTPUT_PATH_NAME = f"{ROOT_DIR}"
if not os.path.isdir(OUTPUT_PATH_NAME):
    pathlib.Path(OUTPUT_PATH_NAME).mkdir(parents=True, exist_ok=True)

channels = ["okumura", "cost", "log", "rural", "wif", "wix"]
labels = ["Okumura-Hata", "COST-231", "Log-distance", "3GPP-RMa", 
                                        "WI (Full 3D)", "WI (X3D)"]

colors = ["red", "purple", "blue", "goldenrod", "black", "green"]

perc_covered_ed = []
for channel in channels:
    covered_ed = np.load(f"../results/forest/covered_{channel}.npz")["arr_0"]
    percentage = (covered_ed[1]/covered_ed[0])*100
    perc_covered_ed.append(percentage)

print(perc_covered_ed)
plt.title(rf"Percentage of covered EDs ($\alpha$ = 0.8)")
bars = plt.bar(labels, perc_covered_ed, capsize=5, width=0.6, color=colors)
plt.bar_label(bars, fmt="%0.2f", padding=3, fontweight='bold')
plt.ylim(0, 120)
plt.xlabel("Channel models", fontsize=14)
plt.ylabel("EDs covered (%)", fontsize=14)
plt.yticks(fontsize=12)
plt.xticks(rotation=45)
plt.savefig(f"figures/ed_covered_forest.pdf", bbox_inches="tight")
