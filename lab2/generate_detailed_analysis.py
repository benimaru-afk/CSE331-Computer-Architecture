#!/usr/bin/env python3

"""
generate_detailed_analysis.py

Extended analysis script with additional visualizations:
- Hit rate comparison across configurations
- Memory latency comparison
- Performance heatmaps
- Per-trace analysis

CSE 3031 - Lab 2
"""

import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

def parse_output_file(filepath):
    """Parse a single .out file and return the statistics"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            if len(lines) < 5:
                return None
            
            return {
                'total_hit_rate': float(lines[0].strip()),
                'load_hit_rate': float(lines[1].strip()),
                'store_hit_rate': float(lines[2].strip()),
                'total_runtime': int(lines[3].strip()),
                'avg_mem_latency': float(lines[4].strip())
            }
    except:
        return None

def load_results_to_dataframe(results_dir):
    """Load all results into a pandas DataFrame"""
    results_path = Path(results_dir)
    
    if not results_path.exists():
        print(f"Error: Results directory '{results_dir}' does not exist")
        return None
    
    data = []
    
    for out_file in results_path.glob('*.out'):
        if out_file.name == 'summary.txt':
            continue
        
        # Parse filename: config_trace.out
        base = out_file.stem
        parts = base.split('_')
        
        if len(parts) >= 2:
            trace_name = parts[-1]
            config_name = '_'.join(parts[:-1])
            
            stats = parse_output_file(out_file)
            if stats:
                row = {
                    'config': config_name,
                    'trace': trace_name,
                    **stats
                }
                data.append(row)
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} simulation results")
    return df

def plot_heatmap_hit_rate(df, output_dir):
    """Generate heatmap of hit rates"""
    pivot = df.pivot(index='config', columns='trace', values='total_hit_rate')
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn', 
                cbar_kws={'label': 'Hit Rate (%)'}, vmin=0, vmax=100)
    plt.title('Cache Hit Rate Heatmap', fontsize=14, fontweight='bold')
    plt.xlabel('Trace File', fontsize=12, fontweight='bold')
    plt.ylabel('Configuration', fontsize=12, fontweight='bold')
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'heatmap_hit_rate.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

def plot_heatmap_latency(df, output_dir):
    """Generate heatmap of memory latency"""
    pivot = df.pivot(index='config', columns='trace', values='avg_mem_latency')
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn_r', 
                cbar_kws={'label': 'Latency (cycles)'})
    plt.title('Average Memory Access Latency Heatmap', fontsize=14, fontweight='bold')
    plt.xlabel('Trace File', fontsize=12, fontweight='bold')
    plt.ylabel('Configuration', fontsize=12, fontweight='bold')
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'heatmap_latency.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

def plot_per_trace_comparison(df, output_dir):
    """Generate individual plots for each trace showing config comparison"""
    traces = df['trace'].unique()
    
    for trace in traces:
        trace_data = df[df['trace'] == trace].sort_values('config')
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Hit rate comparison
        ax1.barh(trace_data['config'], trace_data['total_hit_rate'], color='steelblue')
        ax1.set_xlabel('Total Hit Rate (%)', fontweight='bold')
        ax1.set_ylabel('Configuration', fontweight='bold')
        ax1.set_title(f'Hit Rate - {trace}', fontweight='bold')
        ax1.set_xlim(0, 105)
        ax1.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (idx, row) in enumerate(trace_data.iterrows()):
            ax1.text(row['total_hit_rate'] + 1, i, f"{row['total_hit_rate']:.1f}%", 
                    va='center', fontsize=9)
        
        # Latency comparison
        ax2.barh(trace_data['config'], trace_data['avg_mem_latency'], color='coral')
        ax2.set_xlabel('Avg Memory Latency (cycles)', fontweight='bold')
        ax2.set_ylabel('Configuration', fontweight='bold')
        ax2.set_title(f'Memory Latency - {trace}', fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (idx, row) in enumerate(trace_data.iterrows()):
            ax2.text(row['avg_mem_latency'] + 0.5, i, f"{row['avg_mem_latency']:.1f}", 
                    va='center', fontsize=9)
        
        plt.tight_layout()
        
        output_path = Path(output_dir) / f'comparison_{trace}.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()

def plot_config_performance_summary(df, output_dir):
    """Plot average performance across all traces for each config"""
    config_avg = df.groupby('config').agg({
        'total_hit_rate': 'mean',
        'avg_mem_latency': 'mean'
    }).sort_values('total_hit_rate', ascending=False)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Average hit rate
    ax1.barh(config_avg.index, config_avg['total_hit_rate'], color='mediumseagreen')
    ax1.set_xlabel('Average Total Hit Rate (%)', fontweight='bold')
    ax1.set_ylabel('Configuration', fontweight='bold')
    ax1.set_title('Average Hit Rate Across All Traces', fontweight='bold')
    ax1.set_xlim(0, 105)
    ax1.grid(axis='x', alpha=0.3)
    
    for i, (config, row) in enumerate(config_avg.iterrows()):
        ax1.text(row['total_hit_rate'] + 1, i, f"{row['total_hit_rate']:.1f}%", 
                va='center', fontsize=9)
    
    # Average latency
    config_avg_lat = config_avg.sort_values('avg_mem_latency')
    ax2.barh(config_avg_lat.index, config_avg_lat['avg_mem_latency'], color='indianred')
    ax2.set_xlabel('Average Memory Latency (cycles)', fontweight='bold')
    ax2.set_ylabel('Configuration', fontweight='bold')
    ax2.set_title('Average Memory Latency Across All Traces', fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    for i, (config, row) in enumerate(config_avg_lat.iterrows()):
        ax2.text(row['avg_mem_latency'] + 0.5, i, f"{row['avg_mem_latency']:.1f}", 
                va='center', fontsize=9)
    
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'config_averages.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

def generate_detailed_report(df, output_dir):
    """Generate a detailed text report"""
    output_path = Path(output_dir) / 'detailed_analysis.txt'
    
    with open(output_path, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("DETAILED CACHE SIMULATOR ANALYSIS\n")
        f.write("=" * 100 + "\n\n")
        
        # Overall statistics
        f.write("OVERALL STATISTICS:\n")
        f.write("-" * 100 + "\n")
        f.write(f"Total configurations tested: {df['config'].nunique()}\n")
        f.write(f"Total traces tested: {df['trace'].nunique()}\n")
        f.write(f"Total simulations: {len(df)}\n")
        f.write(f"\nAverage hit rate across all runs: {df['total_hit_rate'].mean():.2f}%\n")
        f.write(f"Average memory latency across all runs: {df['avg_mem_latency'].mean():.2f} cycles\n")
        f.write("\n\n")
        
        # Best and worst configurations
        f.write("BEST PERFORMING CONFIGURATIONS:\n")
        f.write("-" * 100 + "\n")
        
        best_hit_rate = df.loc[df['total_hit_rate'].idxmax()]
        f.write(f"Highest hit rate: {best_hit_rate['config']} on {best_hit_rate['trace']} ")
        f.write(f"({best_hit_rate['total_hit_rate']:.2f}%)\n")
        
        best_latency = df.loc[df['avg_mem_latency'].idxmin()]
        f.write(f"Lowest latency: {best_latency['config']} on {best_latency['trace']} ")
        f.write(f"({best_latency['avg_mem_latency']:.2f} cycles)\n")
        
        f.write("\n")
        f.write("WORST PERFORMING CONFIGURATIONS:\n")
        f.write("-" * 100 + "\n")
        
        worst_hit_rate = df.loc[df['total_hit_rate'].idxmin()]
        f.write(f"Lowest hit rate: {worst_hit_rate['config']} on {worst_hit_rate['trace']} ")
        f.write(f"({worst_hit_rate['total_hit_rate']:.2f}%)\n")
        
        worst_latency = df.loc[df['avg_mem_latency'].idxmax()]
        f.write(f"Highest latency: {worst_latency['config']} on {worst_latency['trace']} ")
        f.write(f"({worst_latency['avg_mem_latency']:.2f} cycles)\n")
        
        f.write("\n\n")
        
        # Per-configuration averages
        f.write("CONFIGURATION AVERAGES (across all traces):\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'Configuration':<25} {'Avg Hit Rate':>15} {'Avg Latency':>15}\n")
        f.write("-" * 100 + "\n")
        
        config_avg = df.groupby('config').agg({
            'total_hit_rate': 'mean',
            'avg_mem_latency': 'mean'
        }).sort_values('total_hit_rate', ascending=False)
        
        for config, row in config_avg.iterrows():
            f.write(f"{config:<25} {row['total_hit_rate']:>14.2f}% {row['avg_mem_latency']:>14.2f}\n")
        
        f.write("\n\n")
        
        # Per-trace averages
        f.write("TRACE AVERAGES (across all configurations):\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'Trace':<25} {'Avg Hit Rate':>15} {'Avg Latency':>15}\n")
        f.write("-" * 100 + "\n")
        
        trace_avg = df.groupby('trace').agg({
            'total_hit_rate': 'mean',
            'avg_mem_latency': 'mean'
        }).sort_values('total_hit_rate', ascending=False)
        
        for trace, row in trace_avg.iterrows():
            f.write(f"{trace:<25} {row['total_hit_rate']:>14.2f}% {row['avg_mem_latency']:>14.2f}\n")
        
        f.write("\n" + "=" * 100 + "\n")
    
    print(f"Saved: {output_path}")

def main():
    """Main function"""
    results_dir = './results'
    output_dir = './graphs'
    
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    print("=" * 100)
    print("DETAILED CACHE SIMULATOR ANALYSIS")
    print("=" * 100)
    print(f"Results directory: {results_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Load results
    df = load_results_to_dataframe(results_dir)
    
    if df is None or len(df) == 0:
        print("Error: No results found!")
        sys.exit(1)
    
    print(f"\nConfigurations: {', '.join(df['config'].unique())}")
    print(f"Traces: {', '.join(df['trace'].unique())}")
    print()
    
    # Generate visualizations
    print("Generating heatmaps...")
    plot_heatmap_hit_rate(df, output_dir)
    plot_heatmap_latency(df, output_dir)
    
    print("\nGenerating per-trace comparisons...")
    plot_per_trace_comparison(df, output_dir)
    
    print("\nGenerating configuration summaries...")
    plot_config_performance_summary(df, output_dir)
    
    print("\nGenerating detailed report...")
    generate_detailed_report(df, output_dir)
    
    print("\n" + "=" * 100)
    print("Analysis complete!")
    print(f"All outputs saved to: {output_dir}")
    print("=" * 100)

if __name__ == '__main__':
    main()
