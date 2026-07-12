import os
import pathlib
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

ROOT_DIR = "figures" # path to root database directory
# Create the output directory
OUTPUT_PATH_NAME = f"{ROOT_DIR}"
if not os.path.isdir(OUTPUT_PATH_NAME):
    pathlib.Path(OUTPUT_PATH_NAME).mkdir(parents=True, exist_ok=True)

colors = ["red", "purple", "blue", "goldenrod", "black", "green"]
scenarios = ["forest"]
channels = ["okumura", "cost", "log", "rural", "wix", "wif"]
labels = ["Okumura-Hata", "COST-231", "Log-distance", "3GPP-RMa", 
                                        "WI (Full 3D)", "WI (X3D)"]

for i in range(len(scenarios)):
    fancy_title = "Forest"
    all_pdr = []
    chosen_gateways = []
    for channel in channels:
        chosen_gateways = np.load(f"../results/{scenarios[i]}/chosen_gateways_{channel}.npz")["arr_0"]
        chosen_sfs = np.load(f"../results/{scenarios[i]}/chosen_sf_{channel}.npz")["arr_0"]
        channel_pdr = []
        counter = 0
        for gw_id in chosen_gateways:
            df = pd.read_csv(f"../pdr_results/sf_{chosen_sfs[counter]}/{channel}/{scenarios[i]}/{gw_id}.csv", header=None)
            channel_pdr.append(np.array(df).flatten())
            counter += 1
        all_pdr.append(list(channel_pdr))

    realizations = 10
    avg_all_pdr = []
    std_all_pdr = []
    for channel in range(len(all_pdr)):
        pdr_w_collision = []
        for realization in range(realizations):
            sum_pdr_lossless = 0
            for gw_id in range(len(all_pdr[channel])):
                sum_pdr_lossless += all_pdr[channel][gw_id][realization]
            avg_pdr_lossless = sum_pdr_lossless / len(all_pdr[channel])
            pdr_w_collision.append(avg_pdr_lossless * 100)
        avg_all_pdr.append(np.mean(pdr_w_collision))
        std_all_pdr.append(np.std(pdr_w_collision))
    print(f"{scenarios[i]}: {avg_all_pdr}")
    plt.title(rf"Average PDR across all GWs in {fancy_title} ($\gamma$ = -95)")
    bars = plt.bar(labels, avg_all_pdr, capsize=5, width=0.6, color=colors)
    plt.bar_label(bars, fmt="%0.2f", padding=3, fontweight='bold')
    plt.ylim(0, 115)
    plt.yticks(fontsize=12)
    plt.xticks(rotation=45)
print(std_all_pdr)
print(labels)
plt.xlabel("Channel models", fontsize=14)
plt.ylabel("Average PDR (%)", fontsize=14)
plt.tight_layout()
plt.savefig(f"figures/avg_pdr.pdf", bbox_inches='tight')
