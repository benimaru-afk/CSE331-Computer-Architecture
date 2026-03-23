# Cache Simulator - CSE 3031 Lab 2

## Overview

This is a cache simulator implementation in C that simulates different cache configurations and measures their performance on various memory access traces.

## Project Structure

```
.
├── cachesim.c               # Main cache simulator source code
├── Makefile                 # Build configuration
├── README.md                # This file
├── run_all_simulations.sh   # Automated batch execution script
├── confs/                   # Configuration files directory
│   ├── 2way-nwa.conf
│   ├── 2way-wa.conf
│   ├── 4way-fifo.conf
│   ├── 4way-rand.conf
│   ├── large-dm.conf
│   ├── medium-dm.conf
│   ├── mega.conf
│   └── small-dm.conf
└── traces/                  # Trace files directory
    ├── gcc.trace
    ├── gzip.trace
    ├── mcf.trace
    ├── swim.trace
    └── twolf.trace
```

## Compilation

### Prerequisites
- GCC compiler
- Make utility
- Standard C library with math library support

### Build Instructions

1. **Compile the simulator:**
   ```bash
   make
   ```

2. **Clean build artifacts:**
   ```bash
   make clean
   ```

3. **Clean all output files:**
   ```bash
   make cleanall
   ```

## Usage

### Basic Usage

```bash
./cachesim <config_file> <trace_file>
```

**Example:**
```bash
./cachesim confs/sample.conf traces/gcc.trace
```

This will create an output file named `gcc.trace.out` containing the simulation statistics.

### Batch Execution

To run all configuration and trace file combinations automatically:

```bash
./run_all_simulations.sh
```

This script will:
- Run the simulator on all 8 configurations × 5 traces = 40 combinations
- Save results in the `results/` directory
- Generate a summary file with all results

**Output Location:**
- Individual results: `results/<config>_<trace>.out`
- Summary: `results/summary.txt`

## Configuration File Format

Configuration files contain 6 lines in the following order:

1. **Line size** (bytes): Must be a power of 2
2. **Associativity**: 1 = direct-mapped, 0 = fully-associative, N = N-way set-associative
3. **Data size** (KB): Total cache data size (power of 2)
4. **Replacement policy**: 0 = random, 1 = FIFO
5. **Miss penalty** (cycles): Positive integer
6. **Write allocate**: 0 = no-write-allocate (with write-through), 1 = write-allocate (with write-back)

**Example Configuration:**
```
8       # 8-byte line size
1       # Direct-mapped
16      # 16 KB cache
1       # FIFO replacement
100     # 100 cycle miss penalty
1       # Write-allocate
```

## Trace File Format

Trace files contain one memory access per line with three space-separated fields:

1. **Access type**: 'l' (load) or 's' (store)
2. **Address**: 32-bit hexadecimal address (e.g., 0xff32e100)
3. **Instructions**: Number of instructions executed since last memory access

**Example Trace Lines:**
```
l 0x1000 5
s 0x2000 3
l 0x1000 2
```

## Output File Format

Output files contain 5 lines with the following statistics:

1. **Total Hit Rate** (percentage)
2. **Load Hit Rate** (percentage)
3. **Store Hit Rate** (percentage)
4. **Total Run Time** (cycles)
5. **Average Memory Access Latency** (cycles)

**Example Output:**
```
85.4321
87.6543
82.1098
1234567
2.3456
```

## Implementation Details

### Cache Structure
- Uses a set-associative cache structure
- Supports direct-mapped (assoc=1), N-way set-associative, and fully-associative (assoc=0) configurations
- Implements both random and FIFO replacement policies
- Handles write-allocate and no-write-allocate policies

### Statistics Tracked
- Total memory accesses, hits, and misses
- Separate tracking for loads and stores
- Total program execution cycles (instructions + memory latency)
- Average memory access latency

### Key Assumptions
- Hit time: 1 cycle
- Miss time: 1 cycle (cache access) + miss penalty
- CPI for non-memory instructions: 1 cycle
- Write-through is used with no-write-allocate
- Write-back is used with write-allocate

## Testing

### Manual Testing
1. Run with a simple configuration:
   ```bash
   ./cachesim confs/small-dm.conf traces/gcc.trace
   ```

2. Verify output file is created:
   ```bash
   cat gcc.trace.out
   ```

### Batch Testing
Run all combinations and check results:
```bash
./run_all_simulations.sh
ls -la results/
cat results/summary.txt
```

## Troubleshooting

### Compilation Errors
- Ensure GCC is installed: `gcc --version`
- Install math library if missing: `sudo apt-get install build-essential`

### Runtime Errors
- **Config file not found**: Check that config files are in `confs/` directory
- **Trace file not found**: Check that trace files are in `traces/` directory
- **Permission denied**: Make script executable: `chmod +x run_all_simulations.sh`

### Output Issues
- **No output file created**: Check file permissions in current directory
- **Incorrect results**: Verify configuration file format

## Authors

[Your Name]
CSE 3031 - Spring 2026

## Assignment Information

- **Course**: CSE 3031
- **Instructor**: Zheng
- **Lab**: #2
- **Assigned**: 3/3/2026
- **Due**: 3/24/2026
