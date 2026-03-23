#!/usr/bin/env python3

"""
analyze_results.py

Parses cache simulator output files and generates required graphs:
1. Total Hit Rate bar chart
2. Average Memory Access Latency bar chart

CSE 3031 - Lab 2
"""

import os
import sys
import re
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

class SimulationResult:
    """Stores results from a single simulation run"""
    def __init__(self, config_name, trace_name, data):
        self.config_name = config_name
        self.trace_name = trace_name
        self.total_hit_rate = data[0]
        self.load_hit_rate = data[1]
        self.store_hit_rate = data[2]
        self.total_runtime = data[3]
        self.avg_mem_latency = data[4]

def parse_output_file(filepath):
    """Parse a single .out file and return the statistics"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            if len(lines) < 5:
                print(f"Warning: {filepath} has fewer than 5 lines")
                return None
            
            data = []
            for i, line in enumerate(lines[:5]):
                try:
                    if i == 3:  # Total runtime is an integer
                        data.append(int(line.strip()))
                    else:
                        data.append(float(line.strip()))
                except ValueError:
                    print(f"Warning: Could not parse line {i+1} in {filepath}")
                    return None
            
            return data
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def parse_filename(filename):
    """Extract config and trace names from result filename"""
    # Expected format: config_trace.out
    base = filename.replace('.out', '')
    parts = base.split('_')
    
    if len(parts) >= 2:
        # Last part is trace name, everything before is config name
        trace_name = parts[-1]
        config_name = '_'.join(parts[:-1])
        return config_name, trace_name
    
    return None, None

def load_all_results(results_dir):
    """Load all simulation results from the results directory"""
    results = []
    results_path = Path(results_dir)
    
    if not results_path.exists():
        print(f"Error: Results directory '{results_dir}' does not exist")
        return results
    
    # Find all .out files
    out_files = list(results_path.glob('*.out'))
    
    # Filter out summary.txt if it exists
    out_files = [f for f in out_files if f.name != 'summary.txt']
    
    for out_file in out_files:
        config_name, trace_name = parse_filename(out_file.name)
        
        if config_name and trace_name:
            data = parse_output_file(out_file)
            if data:
                result = SimulationResult(config_name, trace_name, data)
                results.append(result)
    
    print(f"Loaded {len(results)} simulation results")
    return results

def get_unique_configs_and_traces(results):
    """Extract unique configuration and trace names"""
    configs = sorted(list(set([r.config_name for r in results])))
    traces = sorted(list(set([r.trace_name for r in results])))
    return configs, traces

def plot_total_hit_rate(results, output_dir):
    """Generate bar chart for total hit rate"""
    configs, traces = get_unique_configs_and_traces(results)
    
    # Create data matrix
    data = np.zeros((len(configs), len(traces)))
    
    for result in results:
        config_idx = configs.index(result.config_name)
        trace_idx = traces.index(result.trace_name)
        data[config_idx][trace_idx] = result.total_hit_rate
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Set up bar positions
    x = np.arange(len(traces))
    width = 0.8 / len(configs)
    
    # Plot bars for each configuration
    for i, config in enumerate(configs):
        offset = (i - len(configs)/2 + 0.5) * width
        ax.bar(x + offset, data[i], width, label=config)
    
    # Customize the plot
    ax.set_xlabel('Trace File', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Hit Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Cache Performance: Total Hit Rate by Configuration and Trace', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(traces, rotation=45, ha='right')
    ax.legend(title='Configuration', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_ylim(0, 105)
    
    # Add value labels on bars
    for i, config in enumerate(configs):
        offset = (i - len(configs)/2 + 0.5) * width
        for j, trace in enumerate(traces):
            height = data[i][j]
            if height > 0:
                ax.text(j + offset, height + 1, f'{height:.1f}', 
                       ha='center', va='bottom', fontsize=7, rotation=90)
    
    plt.tight_layout()
    
    # Save the plot
    output_path = Path(output_dir) / 'total_hit_rate.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    
    plt.close()

def plot_avg_mem_latency(results, output_dir):
    """Generate bar chart for average memory access latency"""
    configs, traces = get_unique_configs_and_traces(results)
    
    # Create data matrix
    data = np.zeros((len(configs), len(traces)))
    
    for result in results:
        config_idx = configs.index(result.config_name)
        trace_idx = traces.index(result.trace_name)
        data[config_idx][trace_idx] = result.avg_mem_latency
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Set up bar positions
    x = np.arange(len(traces))
    width = 0.8 / len(configs)
    
    # Plot bars for each configuration
    for i, config in enumerate(configs):
        offset = (i - len(configs)/2 + 0.5) * width
        ax.bar(x + offset, data[i], width, label=config)
    
    # Customize the plot
    ax.set_xlabel('Trace File', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Memory Access Latency (cycles)', fontsize=12, fontweight='bold')
    ax.set_title('Cache Performance: Average Memory Access Latency by Configuration and Trace', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(traces, rotation=45, ha='right')
    ax.legend(title='Configuration', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, config in enumerate(configs):
        offset = (i - len(configs)/2 + 0.5) * width
        for j, trace in enumerate(traces):
            height = data[i][j]
            if height > 0:
                ax.text(j + offset, height + 0.5, f'{height:.1f}', 
                       ha='center', va='bottom', fontsize=7, rotation=90)
    
    plt.tight_layout()
    
    # Save the plot
    output_path = Path(output_dir) / 'avg_mem_latency.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    
    plt.close()

def generate_summary_table(results, output_dir):
    """Generate a summary table in text format"""
    configs, traces = get_unique_configs_and_traces(results)
    
    output_path = Path(output_dir) / 'analysis_summary.txt'
    
    with open(output_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("CACHE SIMULATOR ANALYSIS SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        
        # Total Hit Rate Table
        f.write("TOTAL HIT RATE (%):\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Configuration':<20}")
        for trace in traces:
            f.write(f"{trace:>12}")
        f.write("\n")
        f.write("-" * 80 + "\n")
        
        for config in configs:
            f.write(f"{config:<20}")
            for trace in traces:
                # Find the result
                result = next((r for r in results 
                             if r.config_name == config and r.trace_name == trace), None)
                if result:
                    f.write(f"{result.total_hit_rate:>12.2f}")
                else:
                    f.write(f"{'N/A':>12}")
            f.write("\n")
        
        f.write("\n" * 2)
        
        # Average Memory Latency Table
        f.write("AVERAGE MEMORY ACCESS LATENCY (cycles):\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Configuration':<20}")
        for trace in traces:
            f.write(f"{trace:>12}")
        f.write("\n")
        f.write("-" * 80 + "\n")
        
        for config in configs:
            f.write(f"{config:<20}")
            for trace in traces:
                # Find the result
                result = next((r for r in results 
                             if r.config_name == config and r.trace_name == trace), None)
                if result:
                    f.write(f"{result.avg_mem_latency:>12.2f}")
                else:
                    f.write(f"{'N/A':>12}")
            f.write("\n")
        
        f.write("\n" * 2)
        f.write("=" * 80 + "\n")
    
    print(f"Saved: {output_path}")

def main():
    """Main function"""
    # Default directories
    results_dir = './results'
    output_dir = './graphs'
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    print("=" * 80)
    print("Cache Simulator Results Analysis")
    print("=" * 80)
    print(f"Results directory: {results_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Load all results
    results = load_all_results(results_dir)
    
    if not results:
        print("Error: No results found!")
        sys.exit(1)
    
    # Generate plots
    print("\nGenerating graphs...")
    plot_total_hit_rate(results, output_dir)
    plot_avg_mem_latency(results, output_dir)
    
    # Generate summary table
    print("\nGenerating summary table...")
    generate_summary_table(results, output_dir)
    
    print("\n" + "=" * 80)
    print("Analysis complete!")
    print(f"Graphs and summary saved to: {output_dir}")
    print("=" * 80)

if __name__ == '__main__':
    main()
