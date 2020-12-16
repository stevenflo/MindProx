#!/usr/bin/env python3

"""
make_testcase.py

Generates a set of synthetic traces designed to be consumed by trace2ll
These traces are emphatically NOT representative of real workloads!
"""

import sys
import collections
import argparse
import numpy as np

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--regions", type=int, default=1, help="Number of regions in testcase")
    parser.add_argument("-s", "--regionstrides", type=int, default=10000, help="Number of strides in each region")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output JSON file name")
    parser.add_argument("-l", "--labels", type=str, choices=["contiguous", "shuffled", "random"], default="contiguous", help="How regions should be labeled")
    parser.add_argument("-w", "--weights", type=float, nargs="+", default=[20.0, 5.0, 5.0, 2.0, 2.0, 10.0, 1.0, 0.1, 0.1, 0.1, 0.5, 0.1, 2.0, 1.0, 0.5, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01], \
        help="List of floating-point weights corresponding to relative frequencies of log-strides"
    )
    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    if args.labels == "contiguous":
        region_labels = np.arange(args.regions)
    elif args.labels == "shuffled":
        region_labels = np.arange(args.regions)
        np.random.shuffle(region_labels)
    elif args.labels == "random":
        region_labels = np.arange(-(args.regions * 2), (args.regions * 2))
        np.random.shuffle(region_labels)
        region_labels = region_labels[0:args.regions]
    else:
        sys.exit("Unrecognized region label scheme " + str(args.labels))

    weights = args.weights
    weights[0] /= 2                 # Make 1/2 of zero-bin strides "very small" (this is a special designation in LL generator)
    weights.insert(1, weights[0])   # Add a new bin to account for this
    weights = np.array(weights)
    weights /= weights.sum()
    
    region_data = collections.OrderedDict()
    for label in region_labels:
        data = np.random.choice(weights.size, size=args.regionstrides, p=weights)   # Generate list of absolute log-strides
        data += 2                                                                   # Log-stride of 0 corresponds to 8 (2^3) bytes; but remember we added a new bin earlier
        data = 2 ** data                                                            # Convert adjusted log-strides to actual values
        data = data * np.random.uniform(1.0, 2.0, size=args.regionstrides)          # Scale values by a factor in [1, 2), which does not change the corresponding log-stride
        data = data.astype(int)                                                     # Clamp to int to get final absolute strides
        data *= np.random.choice([-1, 1], size=args.regionstrides)                  # Randomly invert ~1/2 of strides
        region_data.update({str(label): data.tolist()})
    
    # Not using json.dumps so we can have custom formatting...
    out_str = "{"
    out_str += "\n  \"min_list_stride\": 1,"
    out_str += "\n  \"min_array_access_ratio\": 0.2,"
    out_str += "\n  \"trace_data\": {"
    for idx, (label, data) in enumerate(region_data.items()):
        out_str += "\n    \"region" + str(idx) + "\": {"
        out_str += "\n      \"base_page\": " + label + ","
        out_str += "\n      \"store_ratio\": " + str(min(max(np.random.normal(0.35, 0.1), 0.05), 0.95)) + ","
        out_str += "\n      \"strides\": [" + ", ".join([str(d) for d in data]) + "]"
        out_str += "\n    }"
        if idx < len(region_data) - 1:
            out_str += ","
    out_str += "\n  }\n}\n"
    with open(args.output, "w") as out_f:
        #out_f.write(json.dumps(region_data, indent=4))
        out_f.write(out_str)
    

if __name__ == "__main__":
    main()
