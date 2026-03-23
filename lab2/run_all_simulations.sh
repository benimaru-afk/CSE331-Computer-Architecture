#!/bin/bash

###############################################################################
# run_all_simulations.sh
# 
# Script to run cache simulator on all configuration and trace file combinations
# CSE 3031 - Lab 2
#
# Usage: ./run_all_simulations.sh
###############################################################################

# Check if cachesim executable exists
if [ ! -f "./cachesim" ]; then
    echo "Error: cachesim executable not found!"
    echo "Please compile first using 'make'"
    exit 1
fi

# Define directories (adjust paths as needed)
CONFIGS_DIR="./confs"
TRACES_DIR="./traces"
RESULTS_DIR="./results"

# Check if directories exist
if [ ! -d "$CONFIGS_DIR" ]; then
    echo "Error: Configuration directory '$CONFIGS_DIR' not found!"
    exit 1
fi

if [ ! -d "$TRACES_DIR" ]; then
    echo "Error: Traces directory '$TRACES_DIR' not found!"
    exit 1
fi

# Create results directory if it doesn't exist
mkdir -p "$RESULTS_DIR"

# Get list of config files and trace files
CONFIG_FILES=("$CONFIGS_DIR"/*.conf)
TRACE_FILES=("$TRACES_DIR"/*.trace)

# Check if files were found
if [ ! -e "${CONFIG_FILES[0]}" ]; then
    echo "Error: No .conf files found in $CONFIGS_DIR"
    exit 1
fi

if [ ! -e "${TRACE_FILES[0]}" ]; then
    echo "Error: No .trace files found in $TRACES_DIR"
    exit 1
fi

# Count total simulations
num_configs=${#CONFIG_FILES[@]}
num_traces=${#TRACE_FILES[@]}
total_sims=$((num_configs * num_traces))

echo "=========================================="
echo "Cache Simulator - Batch Execution"
echo "=========================================="
echo "Configurations: $num_configs"
echo "Trace files: $num_traces"
echo "Total simulations: $total_sims"
echo "=========================================="
echo ""

# Counter for progress
count=0

# Run all combinations
for config in "${CONFIG_FILES[@]}"; do
    config_name=$(basename "$config" .conf)
    
    for trace in "${TRACE_FILES[@]}"; do
        trace_name=$(basename "$trace" .trace)
        
        count=$((count + 1))
        
        # Output file name: config_trace.out
        output_file="${RESULTS_DIR}/${config_name}_${trace_name}.out"
        
        echo "[$count/$total_sims] Running: $config_name + $trace_name"
        
        # Run the simulator
        ./cachesim "$config" "$trace" > /dev/null 2>&1
        
        # Move the output file to results directory with new name
        if [ -f "${trace}.out" ]; then
            mv "${trace}.out" "$output_file"
            echo "           Output: $output_file"
        else
            echo "           ERROR: Output file not created!"
        fi
        
        echo ""
    done
done

echo "=========================================="
echo "Batch execution complete!"
echo "Results saved in: $RESULTS_DIR"
echo "=========================================="

# Generate summary
echo ""
echo "Generating summary..."
echo "Summary of Results:" > "${RESULTS_DIR}/summary.txt"
echo "==================" >> "${RESULTS_DIR}/summary.txt"
echo "" >> "${RESULTS_DIR}/summary.txt"

for result in "${RESULTS_DIR}"/*.out; do
    if [ -f "$result" ]; then
        result_name=$(basename "$result" .out)
        echo "File: $result_name" >> "${RESULTS_DIR}/summary.txt"
        echo "---" >> "${RESULTS_DIR}/summary.txt"
        cat "$result" >> "${RESULTS_DIR}/summary.txt"
        echo "" >> "${RESULTS_DIR}/summary.txt"
    fi
done

echo "Summary saved to: ${RESULTS_DIR}/summary.txt"
