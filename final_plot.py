#!/usr/bin/env python3

import os
import re
import matplotlib.pyplot as plt
import numpy as np

# Directory
STATS_DIR_CORES = "m5out_cores/"
STATS_DIR_CA = "m5out_ca/"
STATS_DIR_CS = "m5out_cs/"
OUTPUT_DIR = "output_plots/"

# Regex to extract stats
STATS_TO_PARSE = {
    "sim_seconds": re.compile(r"simSeconds\s+(\d+\.\d+)"),
    "sim_ticks": re.compile(r"simTicks\s+(\d+)"),
    # We use cpu0's dcache as the representative L1D cache
    "l1d_miss_rate": re.compile(r"system.cpu0.dcache.overallMissRate::total\s+(\d+\.\d+)"),
    "l2_miss_rate": re.compile(r"system.l2.overallMissRate::total\s+(\d+\.\d+)"),
}

# Parsing Stats
def parse_stats(filepath):
    results = {}
    if not os.path.exists(filepath):
        print(f"Warning: File not found {filepath}")
        return None

    with open(filepath, 'r') as f:
        content = f.read()
    
    for key, regex in STATS_TO_PARSE.items():
        match = regex.search(content)
        if match:
            results[key] = float(match.group(1))
        else:
            if key != "l1d_miss_rate" and "system.cpu0.dcache.overallMissRate" not in content:
                 print(f"Warning: Could not find stat '{key}' in {filepath}")
            results[key] = None
            
    if "l1d_miss_rate" not in results or results["l1d_miss_rate"] is None:
        l1d_match = STATS_TO_PARSE["l1d_miss_rate"].search(content)
        if l1d_match:
            results["l1d_miss_rate"] = float(l1d_match.group(1))
        else:
            if "system.cpu0.dcache.overallMissRate" not in content:
                pass
            else:
                print(f"Warning: Could not find stat 'l1d_miss_rate' in {filepath}")
            results["l1d_miss_rate"] = None

    return results

# Core Scaling Plots
def plot_core_scaling_time():

    print("Generating Core Scaling vs. Time Plot")
    cpu_counts = [2, 4, 8, 16]
    sim_seconds = []

    for cpus in cpu_counts:
        filepath = os.path.join(STATS_DIR_CORES, f"stats_cores_{cpus}.txt")
        stats = parse_stats(filepath)
        if stats and stats.get("sim_seconds"):
            sim_seconds.append(stats["sim_seconds"])
        else:
            sim_seconds.append(np.nan)

    if all(np.isnan(sim_seconds)):
        print("Error: No data for core scaling time. Skipping plot.")
        return

    plt.figure()
    plt.plot(cpu_counts, sim_seconds, color='red', linestyle='-', marker='o')
    plt.title("Core Scaling vs. Simulation Time")
    plt.xlabel("Number of CPU Cores")
    plt.ylabel("Simulation Time (s)")
    plt.xticks(cpu_counts)
    plt.grid(True, linestyle=':')
    save_path = os.path.join(OUTPUT_DIR, "cores_vs_time.png")
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    print(f"Saved {save_path}")

def plot_core_scaling_ticks():

    print("Generating Core Scaling vs. Ticks Plot")
    cpu_counts = [2, 4, 8, 16]
    sim_ticks = []

    for cpus in cpu_counts:
        filepath = os.path.join(STATS_DIR_CORES, f"stats_cores_{cpus}.txt")
        stats = parse_stats(filepath)
        if stats and stats.get("sim_ticks"):
            sim_ticks.append(stats["sim_ticks"])
        else:
            sim_ticks.append(np.nan)

    if all(np.isnan(sim_ticks)):
        print("Error: No data for core scaling ticks. Skipping plot.")
        return

    plt.figure()
    plt.plot(cpu_counts, sim_ticks, color='red', linestyle='-', marker='o')
    plt.title("Core Scaling vs. Simulation Ticks")
    plt.xlabel("Number of CPU Cores")
    plt.ylabel("Simulation Ticks")
    plt.xticks(cpu_counts)
    plt.grid(True, linestyle=':')
    save_path = os.path.join(OUTPUT_DIR, "cores_vs_ticks.png")
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    print(f"Saved {save_path}")

# Associativity Scaling Plots
def plot_associativity_ticks():

    print("Generating Associativity vs. Ticks Plot")
    assoc_counts = [1, 2, 4, 8]
    sim_ticks = []

    for assoc in assoc_counts:
        filepath = os.path.join(STATS_DIR_CA, f"stats_assoc_{assoc}.txt")
        stats = parse_stats(filepath)  
        if stats:
            value = stats.get("sim_ticks")
            sim_ticks.append(value if value is not None else np.nan)
        else:
            sim_ticks.append(np.nan)

    if all(np.isnan(sim_ticks)):
        print("Error: No data for assoc ticks. Skipping plot.")
        return

    plt.figure()
    plt.plot(assoc_counts, sim_ticks, marker='o', linestyle='-')
    plt.title("Cache Associativity vs. Simulation Ticks (8 Cores)")
    plt.xlabel("L1/L2 Associativity")
    plt.ylabel("Simulation Ticks")
    plt.xticks(assoc_counts)
    plt.grid(True, linestyle=':')
    save_path = os.path.join(OUTPUT_DIR, "assoc_vs_ticks.png")
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    print(f"Saved {save_path}")

def plot_associativity_l1d_miss():
    print("Generating Associativity vs. L1D Miss Rate Plot")
    assoc_counts = [1, 2, 4, 8]
    l1d_miss_rates = []

    for assoc in assoc_counts:
        filepath = os.path.join(STATS_DIR_CA, f"stats_assoc_{assoc}.txt")
        stats = parse_stats(filepath)
        if stats:
            value = stats.get("l1d_miss_rate")
            l1d_miss_rates.append(value if value is not None else np.nan)
        else:
            l1d_miss_rates.append(np.nan)

    if all(np.isnan(l1d_miss_rates)):
        print("Error: No data for assoc L1D miss rate. Skipping plot.")
        return

    plt.figure()
    plt.plot(assoc_counts, l1d_miss_rates, marker='o', linestyle='-')
    plt.title("Cache Associativity vs. L1D Miss Rate (8 Cores)")
    plt.xlabel("L1/L2 Associativity")
    plt.ylabel("L1D Miss Rate (cpu0)")
    plt.xticks(assoc_counts)
    plt.grid(True, linestyle=':')
    save_path = os.path.join(OUTPUT_DIR, "assoc_vs_l1d_miss.png")
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    print(f"Saved {save_path}")

def plot_associativity_l2_miss():
    print("Generating Associativity vs. L2 Miss Rate Plot")
    assoc_counts = [1, 2, 4, 8]
    l2_miss_rates = []
    for assoc in assoc_counts:
        filepath = os.path.join(STATS_DIR_CA, f"stats_assoc_{assoc}.txt")
        stats = parse_stats(filepath)
        
        if stats:
            value = stats.get("l2_miss_rate")
            l2_miss_rates.append(value if value is not None else np.nan)
        else:
            l2_miss_rates.append(np.nan)

    if all(np.isnan(l2_miss_rates)):
        print("Error: No data for assoc L2 miss rate. Skipping plot.")
        return

    plt.figure()
    plt.plot(assoc_counts, l2_miss_rates, marker='o', linestyle='-')
    plt.title("Cache Associativity vs. L2 Miss Rate (8 Cores)")
    plt.xlabel("L1/L2 Associativity")
    plt.ylabel("L2 Overall Miss Rate")
    plt.xticks(assoc_counts)
    plt.grid(True, linestyle=':')
    save_path = os.path.join(OUTPUT_DIR, "assoc_vs_l2_miss.png")
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    print(f"Saved {save_path}")

# Cache Size Scaling Plots
def _generate_heatmap(data_grid, title, cbar_label, filename, l1d_sizes, l2_sizes):

    if np.isnan(data_grid).all():
        print(f"Error: No data for {title}. Skipping plot.")
        return

    plt.figure(figsize=(8, 6))
    plt.imshow(data_grid, cmap='viridis_r', interpolation='nearest')
    
    cbar = plt.colorbar()
    cbar.set_label(cbar_label)

    plt.title(title)
    plt.xlabel("L2 Cache Size")
    plt.ylabel("L1D Cache Size")
    plt.xticks(np.arange(len(l2_sizes)), labels=l2_sizes)
    plt.yticks(np.arange(len(l1d_sizes)), labels=l1d_sizes)

    for i in range(len(l1d_sizes)):
        for j in range(len(l2_sizes)):
            value = data_grid[i, j]
            if not np.isnan(value):
                valid_data = data_grid[~np.isnan(data_grid)]
                if valid_data.size > 0:
                    vmin = np.nanmin(valid_data)
                    vmax = np.nanmax(valid_data)
                    threshold = vmin + (vmax - vmin) / 2.0
                    text_color = "black" if value > threshold else "white"
                else:
                    text_color = "black"

                if value > 10000:
                    text_format = f"{value:.2e}"
                else:
                    text_format = f"{value:.4f}"
                plt.text(j, i, text_format, ha="center", va="center", color=text_color, fontsize=9)

    save_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    print(f"Saved {save_path}")

def plot_cache_size_scaling():

    print("Generating Cache Size Scaling Plots")
    l1d_sizes = ["16kB", "32kB", "64kB", "128kB"]
    l2_sizes = ["128kB", "256kB", "512kB", "1MB"]

    ticks_grid = np.full((len(l1d_sizes), len(l2_sizes)), np.nan)
    l1d_miss_grid = np.full((len(l1d_sizes), len(l2_sizes)), np.nan)
    l2_miss_grid = np.full((len(l1d_sizes), len(l2_sizes)), np.nan)

    for i, l1 in enumerate(l1d_sizes):
        for j, l2 in enumerate(l2_sizes):
            filepath = os.path.join(STATS_DIR_CS, f"stats_size_l1_{l1}_l2_{l2}.txt")
            stats = parse_stats(filepath)
            
            if stats:
                ticks_val = stats.get("sim_ticks")
                l1d_val = stats.get("l1d_miss_rate")
                l2_val = stats.get("l2_miss_rate")
                
                ticks_grid[i, j] = ticks_val if ticks_val is not None else np.nan
                l1d_miss_grid[i, j] = l1d_val if l1d_val is not None else np.nan
                l2_miss_grid[i, j] = l2_val if l2_val is not None else np.nan

    _generate_heatmap(ticks_grid, "Cache Size vs. Sim Ticks (8 Cores)", 
                      "Simulation Ticks", "cache_size_vs_ticks_heatmap.png",
                      l1d_sizes, l2_sizes)
    
    _generate_heatmap(l1d_miss_grid, "Cache Size vs. L1D Miss Rate (8 Cores)", 
                      "L1D Miss Rate (cpu0)", "cache_size_vs_l1d_miss_heatmap.png",
                      l1d_sizes, l2_sizes)
    
    _generate_heatmap(l2_miss_grid, "Cache Size vs. L2 Miss Rate (8 Cores)",
                      "L2 Overall Miss Rate", "cache_size_vs_l2_miss_heatmap.png",
                      l1d_sizes, l2_sizes)

# Main Function
if __name__ == "__main__":
    print("Starting Plot Generation")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Saving Plots In : '{OUTPUT_DIR}'")
        
    # Core Scaling Plots
    plot_core_scaling_time()
    plot_core_scaling_ticks()
    
    # Associativity Scaling Plots
    plot_associativity_ticks()
    plot_associativity_l1d_miss()
    plot_associativity_l2_miss()

    # Cache Size Scaling Plots
    plot_cache_size_scaling()
    
    print("All Plots Generated Successfully!")
