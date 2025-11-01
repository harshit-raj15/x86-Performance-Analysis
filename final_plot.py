import os
import re
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

# --- Configuration ---
STATS_DIR = 'm5out'

L1D_SIZES_LIST = ["16kB", "32kB", "64kB", "128kB"]
L2_SIZES_LIST = ["128kB", "256kB", "512kB", "1MB"]
ASSOC_LIST = [1, 2, 4, 8]
CORES_LIST = [2, 4, 8, 16]


# --- Regex for Filenames ---
RE_CORE = re.compile(r'stats_cores_(\d+).txt')
RE_ASSOC = re.compile(r'stats_assoc_(\d+).txt')
RE_SIZE = re.compile(r'stats_l1_([\w+]+)_l2_([\w+]+).txt')

# --- Regex for Stats ---
STAT_PATTERNS = {
    'seconds': re.compile(r'system.cpu.exec_context.thread_0.simSeconds\s+([\d\.]+)'),
    'ticks': re.compile(r'simTicks\s+(\d+)'),
    'l1d_miss_rate': re.compile(r'system.cpu0.dcache.overall_miss_rate\s+([\d\.]+)'),
    'l2_miss_rate': re.compile(r'system.l2.overall_miss_rate\s+([\d\.]+)')
}

def parse_stats_file(filepath):
    metrics = {}
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            for key, pattern in STAT_PATTERNS.items():
                match = pattern.search(content)
                if match:
                    metrics[key] = float(match.group(1))
    except Exception as e:
        print(f"Warning: Error parsing {filepath}: {e}")
        return None
    return metrics

def plot_core_scaling(data):
    if not data:
        print("No core scaling data found to plot.")
        return

    print("Plotting core scaling...")
    sorted_cores = sorted(data.keys())
    times = [data[c].get('seconds', np.nan) for c in sorted_cores]
    ticks = [data[c].get('ticks', np.nan) for c in sorted_cores]

    # Plot 1: Cores vs. Time
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_cores, times, marker='o', linestyle='-')
    plt.title('CPU Cores vs Execution Time')
    plt.xlabel('Number of CPU Cores')
    plt.ylabel('Execution Time (seconds)')
    plt.grid(True)
    plt.xticks(sorted_cores)
    plt.savefig('cores_vs_time.png')
    plt.close()

    # Plot 2: Cores vs. Ticks
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_cores, ticks, marker='o', linestyle='-', color='r')
    plt.title('CPU Cores vs Total Ticks')
    plt.xlabel('Number of CPU Cores')
    plt.ylabel('Total Simulation Ticks')
    plt.grid(True)
    plt.xticks(sorted_cores)
    plt.savefig('cores_vs_ticks.png')
    plt.close()

def plot_assoc_scaling(data):
    if not data:
        print("No associativity scaling data found to plot.")
        return
        
    print("Plotting associativity scaling...")
    sorted_assoc = sorted(data.keys())
    ticks = [data[a].get('ticks', np.nan) for a in sorted_assoc]
    l1d_miss = [data[a].get('l1d_miss_rate', np.nan) for a in sorted_assoc]
    l2_miss = [data[a].get('l2_miss_rate', np.nan) for a in sorted_assoc]

    # Plot 1: Assoc vs. Ticks
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_assoc, ticks, marker='o', linestyle='-')
    plt.title('Cache Associativity vs Total Ticks (8 Cores)')
    plt.xlabel('L1/L2 Associativity')
    plt.ylabel('Total Simulation Ticks')
    plt.grid(True)
    plt.xticks(sorted_assoc)
    plt.savefig('assoc_vs_ticks.png')
    plt.close()

    # Plot 2: Assoc vs. L1D Miss Rate
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_assoc, l1d_miss, marker='o', linestyle='-', color='g')
    plt.title('Cache Associativity vs L1D Miss Rate (8 Cores)')
    plt.xlabel('L1/L2 Associativity')
    plt.ylabel('L1D Miss Rate (cpu0.dcache)')
    plt.grid(True)
    plt.xticks(sorted_assoc)
    plt.savefig('assoc_vs_l1d_miss.png')
    plt.close()

    # Plot 3: Assoc vs. L2 Miss Rate
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_assoc, l2_miss, marker='o', linestyle='-', color='purple')
    plt.title('Cache Associativity vs L2 Miss Rate (8 Cores)')
    plt.xlabel('L1/L2 Associativity')
    plt.ylabel('L2 Miss Rate (system.l2)')
    plt.grid(True)
    plt.xticks(sorted_assoc)
    plt.savefig('assoc_vs_l2_miss.png')
    plt.close()

def plot_heatmap(data, title, filename, x_labels, y_labels, metric_label):
    plt.figure(figsize=(12, 8))
    # Use logarithmic color scale for ticks, linear for miss rates
    norm = None
    if 'Ticks' in metric_label:
        norm = colors.LogNorm(vmin=data.min(), vmax=data.max())
        
    c = plt.imshow(data, cmap='viridis', aspect='auto', norm=norm)
    plt.title(title)
    plt.xlabel("L2 Cache Size")
    plt.ylabel("L1D Cache Size")
    
    # Set labels
    plt.xticks(np.arange(len(x_labels)), x_labels)
    plt.yticks(np.arange(len(y_labels)), y_labels)
    
    # Add text annotations
    for i in range(len(y_labels)):
        for j in range(len(x_labels)):
            val = data[i, j]
            text = f"{val:.2e}" if 'Ticks' in metric_label else f"{val:.4f}"
            plt.text(j, i, text, ha='center', va='center', color='white', fontsize=8)
            
    plt.colorbar(c, label=metric_label)
    plt.savefig(filename)
    plt.close()

def plot_size_scaling(data):
    """Generates heatmaps for cache size scaling."""
    if not data:
        print("No cache size scaling data found to plot.")
        return

    print("Plotting cache size scaling (heatmaps)...")
    
    # Create 2D numpy arrays to hold the data for the heatmaps
    # Rows: L1D Size, Cols: L2 Size
    grid_ticks = np.full((len(L1D_SIZES_LIST), len(L2_SIZES_LIST)), np.nan)
    grid_l1d_miss = np.full((len(L1D_SIZES_LIST), len(L2_SIZES_LIST)), np.nan)
    grid_l2_miss = np.full((len(L1D_SIZES_LIST), len(L2_SIZES_LIST)), np.nan)

    # Populate the grids
    for i, l1 in enumerate(L1D_SIZES_LIST):
        for j, l2 in enumerate(L2_SIZES_LIST):
            key = f"{l1}_{l2}"
            if key in data:
                grid_ticks[i, j] = data[key].get('ticks', np.nan)
                grid_l1d_miss[i, j] = data[key].get('l1d_miss_rate', np.nan)
                grid_l2_miss[i, j] = data[key].get('l2_miss_rate', np.nan)

    # Create plots
    plot_heatmap(grid_ticks, 
                 'Total Ticks vs. L1D/L2 Cache Sizes (8 Cores, Assoc=4)', 
                 'cache_size_vs_ticks_heatmap.png', 
                 L2_SIZES_LIST, L1D_SIZES_LIST, 'Total Simulation Ticks (Log Scale)')

    plot_heatmap(grid_l1d_miss, 
                 'L1D Miss Rate vs. L1D/L2 Cache Sizes (8 Cores, Assoc=4)', 
                 'cache_size_vs_l1d_miss_heatmap.png', 
                 L2_SIZES_LIST, L1D_SIZES_LIST, 'L1D Miss Rate (cpu0.dcache)')

    plot_heatmap(grid_l2_miss, 
                 'L2 Miss Rate vs. L1D/L2 Cache Sizes (8 Cores, Assoc=4)', 
                 'cache_size_vs_l2_miss_heatmap.png', 
                 L2_SIZES_LIST, L1D_SIZES_LIST, 'L2 Miss Rate (system.l2)')


def main():
    print(f"--- Starting Full Experiment Plotter ---")
    print(f"Scanning for stats files in '{STATS_DIR}'...")

    core_data = {}
    assoc_data = {}
    size_data = {}

    all_stats_files = glob.glob(os.path.join(STATS_DIR, 'stats_*.txt'))
    
    if not all_stats_files:
        print(f"\nError: No 'stats_*.txt' files found in '{STATS_DIR}'.")
        print("Please run your simulation scripts first.\n")
        return

    print(f"Found {len(all_stats_files)} stats files. Parsing...")

    for filepath in all_stats_files:
        filename = os.path.basename(filepath)
        metrics = parse_stats_file(filepath)
        if not metrics:
            continue

        # Match each pattern
        match_core = RE_CORE.match(filename)
        match_assoc = RE_ASSOC.match(filename)
        match_size = RE_SIZE.match(filename)

        if match_core:
            cores = int(match_core.group(1))
            core_data[cores] = metrics
        
        elif match_assoc:
            assoc = int(match_assoc.group(1))
            assoc_data[assoc] = metrics
            
        elif match_size:
            l1 = match_size.group(1)
            l2 = match_size.group(2)
            key = f"{l1}_{l2}"
            size_data[key] = metrics

    # --- Generate all plots ---
    plot_core_scaling(core_data)
    plot_assoc_scaling(assoc_data)
    plot_size_scaling(size_data)
    
    print("\n--- All plots generated successfully in your project folder! ---")

if __name__ == "__main__":
    main()
