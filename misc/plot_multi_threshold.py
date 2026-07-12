import os
import pathlib
from matplotlib import pyplot as plt
import numpy as np

channels = ["okumura", "cost", "log", "rural", "wix", "wif"]
ch_labels = ["Okumura-Hata", "COST-231", "Log-distance", "3GPP-RMa", 
                                        "WI (X3D)", "WI (Full 3D)"]

colors = ["red", "purple", "blue", "goldenrod", "black", "green"]

ROOT_DIR = "figures" # path to root database directory
# Create the output directory
OUTPUT_PATH_NAME = f"{ROOT_DIR}"
if not os.path.isdir(OUTPUT_PATH_NAME):
    pathlib.Path(OUTPUT_PATH_NAME).mkdir(parents=True, exist_ok=True)

all_number_of_gws = []
counter = 0
heatmap_data = []
for channel in channels:
    number_gws_data = np.load(
        f"../results/forest/multi_number_of_gws_{channel}.npz"
    )

    number_gws = number_gws_data["arr_0"]
    power_thresholds = number_gws_data["arr_1"]

    # Replace inf with NaN (or a large value if preferred)
    number_gws = np.where(np.isinf(number_gws), np.nan, number_gws)

    heatmap_data.append(number_gws)

heatmap_data = np.array(heatmap_data)

fig, ax = plt.subplots(figsize=(8, 4))

im = ax.imshow(
    heatmap_data,
    aspect="auto",
    origin="upper",
    cmap="YlOrRd"
)

# X axis = rho values
ax.set_xticks(np.arange(len(power_thresholds)))
ax.set_xticklabels(power_thresholds)

# Y axis = channel labels
ax.set_yticks(np.arange(len(ch_labels)))
ax.set_yticklabels(ch_labels)

ax.set_xlabel(r"$\rho$", fontsize=14)
ax.set_ylabel("Channel model", fontsize=14)

cbar = plt.colorbar(im)
cbar.set_label("Required number of gateways")

# Write values inside cells
for i in range(heatmap_data.shape[0]):
    for j in range(heatmap_data.shape[1]):
        value = heatmap_data[i, j]

        if np.isnan(value):
            text = "X"
        else:
            text = f"{int(value)}"

        ax.text(
            j,
            i,
            text,
            ha="center",
            va="center",
            fontsize=12
        )
plt.title(r"Number of gateways across different values of $\rho$")
plt.savefig("figures/number_of_gws.pdf", bbox_inches="tight")
