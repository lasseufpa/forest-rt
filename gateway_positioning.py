import os
import glob
import pathlib
import pandas as pd
import numpy as np
import re
import networkx as nx
import matplotlib.pyplot as plt
import math
from pyomo.environ import *
from matplotlib import pyplot as plt
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--channel-type", "-c", help="Type of channel",
    type=str, required=False, default="sionna"
)

parser.add_argument(
    "--threshold", "-t", help="Received power threshold",
    type=float, required=False, default=-110
)

parser.add_argument(
    "--alpha", "-a", help="Minimum percentage of covered ED",
    type=float, required=False, default=0.8
)

parser.add_argument(
    "--scenario", "-s", help="3D scenario/grid to be used",
    type=str, required=False, default="etoile"
)

args = parser.parse_args()


ROOT_DIR = "results" # path to root database directory
# Create the output directory
OUTPUT_PATH_NAME = f"{ROOT_DIR}/{args.scenario}"
if not os.path.isdir(OUTPUT_PATH_NAME):
    pathlib.Path(OUTPUT_PATH_NAME).mkdir(parents=True, exist_ok=True)

def _get_pdr(path_gain_type: str):
    all_pdr = []
    spreading_factors = [7, 8, 9, 10, 11, 12]
    for sf in spreading_factors:
        pdr_per_sf = []
        files = sorted(
            glob.glob(f"pdr_results/sf_{sf}/{path_gain_type}/{args.scenario}/*.csv"),
            key=lambda x: int(os.path.splitext(os.path.basename(x))[0])
        )
        for fname in files:
            if not os.path.basename(fname).split(".")[0].isdigit():
                continue
            df = pd.read_csv(f"{fname}", header=None)
            pdr_per_sf.append(np.mean(df))
        all_pdr.append(pdr_per_sf)
    
    return np.array(all_pdr)

def _get_path_gain(path_gain_type: str):
    path_gain_db = []
    if path_gain_type == "sionna":
        files = sorted(
            glob.glob(f"path_gain_results/{path_gain_type}/{args.scenario}/*.csv"),
            key=lambda x: int(os.path.splitext(os.path.basename(x))[0])
        )
        for fname in files:
            if not os.path.basename(fname).split(".")[0].isdigit():
                continue
            df = pd.read_csv(f"{fname}", header=None)
            path_gain_db.append(df)
    elif path_gain_type == "wix" or path_gain_type == "wif":
        files = sorted(
            glob.glob(f"path_gain_results/{path_gain_type}/{args.scenario}/*.csv"),
            key=lambda x: int(os.path.splitext(os.path.basename(x))[0])
        )
        for fname in files:
            df = pd.read_csv(f"{fname}", header=None)
            path_gain_db.append(df)
    else:
        files = sorted(
            glob.glob(f"path_gain_results/ns3/{path_gain_type}/{args.scenario}/*.csv"),
            key=lambda x: int(os.path.splitext(os.path.basename(x))[0])
        )
        for fname in files:
            df = pd.read_csv(f"{fname}", header=None)
            path_gain_db.append(df)

    return np.array(path_gain_db)

# Defining the numpy seed
np.random.seed(42)

# read CSV
devices_df = pd.read_csv(f"path_gain_results/{args.scenario}_coordinates.csv",
                                            header=None)

# end_device positions -> cell indexes
end_devices_cells = list(zip(devices_df[3], devices_df[4]))

def extract_number(filename):
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 999999

G = len(devices_df.to_numpy()) # Possibles gateway positions
coordinates = devices_df.to_numpy()

rx_power = {}

path_gain_type = args.channel_type
path_gain_db = _get_path_gain(path_gain_type)
all_pdr = _get_pdr(path_gain_type)

PATH_GAIN_COLUMN = -1

G_index = list(range(G))
Nd = len(end_devices_cells)
if args.scenario == "etoile":
    D_index = [1, 2, 4, 9, 10, 12, 14, 18,
                19, 20, 22, 23, 26, 27, 28,
                30, 31, 32, 33, 34, 35, 36,
                40, 41, 42, 43, 44, 50, 51,
                52, 53, 54, 55, 59, 60, 61,
                62, 63, 64, 68, 69, 70, 71,
                72, 73, 74, 75, 81, 82, 83,
                86, 87, 91, 98]
elif args.scenario == "canyon":
    D_index = [3, 4, 8, 9, 16, 17, 21, 22, 29,
               30, 34, 35, 39, 40, 41, 42, 43,
               44, 45, 46, 47, 48, 49, 50, 51,
               52, 53, 54, 55, 56, 57, 58, 59,
               60, 61, 62, 63, 64, 68, 69, 73,
               74, 81, 82, 86, 87, 94, 95, 99,
               100]
elif args.scenario == "forest":
    D_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
               11, 12, 13, 14, 15, 16, 17, 18, 19,
               20, 21, 22, 23, 24, 25, 26, 27, 28,
               30, 31, 32, 34, 35, 36, 37, 38, 39, 41]

invalid_d_index = np.zeros(100)
print("Number of ED: ", len(D_index))

for p_gateway in range(G): # Power that a ED receivers from each gateway in all positions available
    for d, (ix, iy) in enumerate(end_devices_cells):
        rx_power[(d, p_gateway)] = float(path_gain_db[p_gateway][d][PATH_GAIN_COLUMN])

print(D_index)
# Solving -inf problem
NO_SIGNAL = -1000

for key, v in list(rx_power.items()):
    if v is None or math.isnan(v) or math.isinf(v):
        rx_power[key] = NO_SIGNAL # NO_SIGNAL replaces -inf values

if args.threshold is None:
    rho = min([x for x in rx_power.values() if x != -1000]) + 20 # threshold in dBm
else:
    rho = args.threshold
print("List of power thresholds: ", rho)

all_received_power = []
all_dev_x, all_dev_y = [], []
all_xs_chosen, all_ys_chosen = [], []

# Defining an cover dict
cover = {}

for d in D_index:
    for p_gateway in G_index:
        # This indicates whether the power threshold is being reached in each
        # end-device for each gateway -> simplification to 0 or 1
        if (d, p_gateway) in rx_power:
            cover[(d, p_gateway)] = 1 if rx_power[(d, p_gateway)] >= rho else 0

SF_values = [7, 8, 9, 10, 11, 12]

all_pdr_dict = {}
for i, sf in enumerate(SF_values):
    for p_gateway in G_index:
        all_pdr_dict[(sf, p_gateway)] = all_pdr[i, p_gateway]

pdr_cover = {}
for i, sf in enumerate(SF_values):
    for p_gateway in G_index:
        pdr_cover[(sf, p_gateway)] = 1 if all_pdr_dict[(sf, p_gateway)] >= 0.7 else 0

# Optimization
model = ConcreteModel()
model.P = Set(initialize=G_index)  # all gateways positions = all positions
model.D = Set(initialize=D_index)
model.SF = Set(initialize=[7, 8, 9, 10, 11, 12])
model.pdr_cover = Param(model.SF, model.P, initialize=pdr_cover, within=Binary)
model.cover = Param(model.D, model.P, initialize=cover, within=Binary, default=0)
model.x = Var(model.P, domain=Binary)
model.y = Var(model.D, domain=Binary)  # device d is covered
model.a = Var(model.D, model.P, domain=Binary)
model.sf_selected = Var(model.SF, model.P, domain=Binary)

def sf_valid_rule(m, sf, p):
    return m.sf_selected[sf,p] <= m.pdr_cover[sf,p]

def one_sf_rule(m, p):
    return sum(m.sf_selected[sf,p] for sf in m.SF) == m.x[p]

def assignment_selected_rule(m, d, p):
    return m.a[d, p] <= m.x[p]

def assignment_coverage_rule(m, d, p):
    return m.a[d, p] <= m.cover[d, p]

def coverage_rule_percentage(m):
    return sum(m.y[d] for d in m.D) >= args.alpha * len(m.D)

def unique_assignment_rule(m, d):
    return sum(m.a[d, p] for p in m.P) == m.y[d]

model.unique_assignment = Constraint(model.D, rule=unique_assignment_rule)
model.assignment_coverage = Constraint(model.D, model.P, rule=assignment_coverage_rule)
model.assignment_selected = Constraint(model.D, model.P, rule=assignment_selected_rule)
model.one_sf = Constraint(model.P, rule=one_sf_rule)
model.valid_rule = Constraint(model.SF, model.P, rule=sf_valid_rule)
model.coverage_percentage = Constraint(rule=coverage_rule_percentage)

def obj_rule(m):
    return sum(m.x[p_gateway] for p_gateway in m.P)

model.obj = Objective(rule=obj_rule, sense=minimize)

# initialize solver parameters
solver = SolverFactory("glpk")
result = solver.solve(model) #, tee=True)

received_power = np.zeros(len(G_index))
if (result.solver.status == SolverStatus.ok and
        result.solver.termination_condition == TerminationCondition.optimal):
    # Chosen gateways
    chosen_gateways = [p for p in model.P if value(model.x[p]) > 0.5]
    ed_covered = [d for d in model.D if value(model.y[d]) > 0.5]

    print("Number of devices covered: ", len(ed_covered))

    print("\nChosen gateways (details):")
    for p in chosen_gateways:
        print(f"  p = {p}, coords = {coordinates[p]}")

    chosen_sf = []
    for sf in model.SF:
        for p in model.P:
            if value(model.x[p]) > 0.5:
                if value(model.sf_selected[sf, p]) > 0.5:
                    chosen_sf.append(sf)
                    print(f"Gateway {p}: SF{sf}")
                    
    gw_ed_links = {}
    for p in model.P:
        if value(model.x[p]) > 0.5:
            if gw_ed_links == {}:
                gw_ed_links = {f"{p}": []}
            else:
                gw_ed_links.update({f"{p}": []})
            for d in model.D:
                if value(model.a[d, p]) == 1:
                    gw_ed_links[f"{p}"].append(d)

    for d in D_index:
        total_mW = 0.0
        for p in G_index:
            if (d, p) not in rx_power:
                continue
            if value(model.x[p]) > 0.5:   # chosen gateway
                rp_dbm = rx_power[(d, p)]
                # converting dBm -> mW
                rp_mw = 10**(rp_dbm / 10.0)
                
                total_mW += rp_mw
        # avoiding problem with log(0)
        if total_mW > 0:
            received_power[d] = 10 * np.log10(total_mW) # back to dBm
        else:
            received_power[d] = NO_SIGNAL # very negative value
        # End-device positions

    dev_x = devices_df[0].values
    dev_y = devices_df[1].values

    # gateways positions
    xs_gate = [coordinates[p][0] for p in G_index]
    ys_gate = [coordinates[p][1] for p in G_index]

    # end devices positions

    xs_ed = [coordinates[p][0] for p in D_index]
    ys_ed = [coordinates[p][1] for p in D_index]

    # chosen gateways positions
    xs_chosen = [coordinates[p][0] for p in chosen_gateways]
    ys_chosen = [coordinates[p][1] for p in chosen_gateways]
        
    print("Number of gateways: ", len(xs_chosen))
    np.savez(f"{OUTPUT_PATH_NAME}/gw_ed_links_{path_gain_type}.npz",
                                            gw_ed_links)
    np.savez(f"{OUTPUT_PATH_NAME}/chosen_sf_{path_gain_type}.npz",
                                            np.array(chosen_sf))
    # saving number of covered end-devices
    np.savez(f"{OUTPUT_PATH_NAME}/covered_{path_gain_type}.npz",
                                            np.array([len(D_index), len(ed_covered)]))
    # saving receiver power for each end-device
    np.savez(f"{OUTPUT_PATH_NAME}/receiver_power_{path_gain_type}.npz", received_power)
    # saving all position coordinates
    np.savez(f"{OUTPUT_PATH_NAME}/all_position.npz", dev_x, dev_y)
    # saving gateway positioning coordinates
    np.savez(f"{OUTPUT_PATH_NAME}/chosen_position_{path_gain_type}.npz", xs_chosen, ys_chosen)
    # saving end devices positioning coordinates
    np.savez(f"{OUTPUT_PATH_NAME}/ed_position.npz", xs_ed, ys_ed)
    # saving chosen gateways
    np.savez(f"{OUTPUT_PATH_NAME}/chosen_gateways_{path_gain_type}.npz", chosen_gateways)
else:
        print(f"Solver did not find a feasible solution for threshold {rho}")
        print("Status:", result.solver.status)
        print("Termination:", result.solver.termination_condition)
