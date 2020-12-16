#!/usr/bin/python3.6

"""
plot_regions.py

Graphically plots (unculled/unoptimized) trace regions
Intended as a visual aid to interpret trace2ll.py outputs
"""

import os
import sys
import json
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

if len(sys.argv) != 3:
    print("Usage: ./plot_regions.py <input JSON> <output dir>")

in_fname = sys.argv[1]
out_dir = sys.argv[2]

if os.path.exists(out_dir):
    warnings.warn(f"Output directory {out_dir} already exists")

os.makedirs(out_dir, exist_ok=True)

with open(in_fname, "r") as in_f:
    config = json.loads(in_f.read())

for region_name, region in config["trace_data"].items():
    strides = region["strides"]
    locations = [0]
    for stride in strides:
        locations.append(locations[-1] + (stride/8))
    df_locations = pd.DataFrame(locations)
    df_locations.plot.line(figsize=(20,10))
    plt.xlabel("Node ID")
    plt.ylabel("Location")
    plt.title(f"Trace for {region_name}")
    save_path = os.path.join(out_dir, f"{region_name.lower()}.png")
    plt.savefig(save_path, bbox_inches = "tight")

