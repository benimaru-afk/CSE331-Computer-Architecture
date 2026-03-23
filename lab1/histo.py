"""
lab1_histogram.py
CSE 331 Lab 1 -- Alpha vs. PISA ISA Instruction Class Histogram
Generates a grouped bar chart comparing instruction class distributions
for test-math, test-fmath, test-llong, and test-printf on both ISAs.
Run: python lab1_histogram.py
Output: lab1_histogram.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------------
# Data extracted from sim-profile output
# Columns: Load%, Store%, UncondBr%, CondBr%, IntComp%, FPComp%
# ------------------------------------------------------------------
categories = ["Load", "Store", "Uncond Br", "Cond Br", "Int Comp", "FP Comp"]
benchmarks = ["test-math", "test-fmath", "test-llong", "test-printf"]

alpha_data = {
    #              Load   Store  UBr   CBr    Int    FP
    "test-math":   [17.15, 10.48, 3.83, 10.77, 55.64, 2.00],
    "test-fmath":  [17.71, 12.79, 4.58, 10.89, 53.45, 0.46],
    "test-llong":  [17.78, 15.02, 5.52, 11.93, 49.49, 0.11],
    "test-printf": [18.40, 11.09, 4.60, 11.06, 54.64, 0.09],
}

pisa_data = {
    #              Load   Store  UBr   CBr    Int    FP
    "test-math":   [14.30, 10.84, 4.29, 12.69, 56.88, 0.99],
    "test-fmath":  [12.98, 15.41, 4.43, 13.45, 53.58, 0.14],
    "test-llong":  [10.09, 21.63, 4.75, 12.23, 51.26, 0.00],
    "test-printf": [14.30,  9.17, 5.83, 14.37, 56.31, 0.02],
}

# ------------------------------------------------------------------
# Plot: one subplot per benchmark, grouped bars per instruction class
# ------------------------------------------------------------------
n_cats = len(categories)
n_benchmarks = len(benchmarks)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Alpha vs. PISA Instruction Class Distribution\n(CSE 331 Lab 1)",
             fontsize=15, fontweight="bold", y=0.98)

alpha_color = "#2C6FAC"   # blue
pisa_color  = "#E8622A"   # orange

bar_width = 0.35
x = np.arange(n_cats)

for idx, (bench, ax) in enumerate(zip(benchmarks, axes.flat)):
    a_vals = alpha_data[bench]
    p_vals = pisa_data[bench]

    bars_alpha = ax.bar(x - bar_width / 2, a_vals, bar_width,
                        label="Alpha", color=alpha_color, edgecolor="white", linewidth=0.5)
    bars_pisa  = ax.bar(x + bar_width / 2, p_vals, bar_width,
                        label="PISA",  color=pisa_color,  edgecolor="white", linewidth=0.5)

    # Value labels on top of each bar
    for bar in bars_alpha:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.4,
                f"{h:.1f}", ha="center", va="bottom", fontsize=7, color=alpha_color)
    for bar in bars_pisa:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.4,
                f"{h:.1f}", ha="center", va="bottom", fontsize=7, color=pisa_color)

    ax.set_title(bench, fontsize=12, fontweight="bold")
    ax.set_ylabel("Percentage of Instructions (%)", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9, rotation=15, ha="right")
    ax.set_ylim(0, 70)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

plt.tight_layout(rect=[0, 0, 1, 0.96])
out_file = "lab1_histogram.png"
plt.savefig(out_file, dpi=150, bbox_inches="tight")
print(f"Saved: {out_file}")

# ------------------------------------------------------------------
# Optional: summary comparison table printed to console
# ------------------------------------------------------------------
print("\n=== Instruction Class Summary ===")
header = f"{'Benchmark':<14} {'ISA':<6} " + " ".join(f"{c:>10}" for c in categories)
print(header)
print("-" * len(header))
for bench in benchmarks:
    a = alpha_data[bench]
    p = pisa_data[bench]
    print(f"{bench:<14} {'Alpha':<6} " + " ".join(f"{v:>10.2f}" for v in a))
    print(f"{'':14} {'PISA':<6} " + " ".join(f"{v:>10.2f}" for v in p))
    print()