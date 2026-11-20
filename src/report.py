"""Aggregate question rows by paired seed and plot between-seed variability."""
import csv
from collections import defaultdict
from statistics import mean, stdev

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt

from src.design import BUDGETS, SEEDS, TOPICS
from src.pickers import ARMS
from src.sweep import RESULTS

LABELS = {
    "ecan": "ECAN",
    "harness": "Harness",
    "random": "Random",
    "ecan_no_feedback": "ECAN no feedback",
    "ecan_no_stimulus": "ECAN no stimulus",
    "ecan_neither": "ECAN neither",
    "harness_ecan": "Harness ECAN",
    "harness_ecan_nofeedback": "Harness ECAN no feedback",
}


def report():
    runs, groups = defaultdict(list), defaultdict(list)
    for seed in SEEDS:
        with (RESULTS / f"raw-{seed}.csv").open(newline="") as file:
            for row in csv.DictReader(file):
                arm, k = row["arm"], int(row["k"])
                outcome = int(row["correct"]), float(row["runtime_us"])
                for block in ("all", int(row["block"])):
                    runs[arm, k, block, seed].append(outcome)
    for (arm, k, block, _), rows in runs.items():
        groups[arm, k, block].append((mean(c for c, _ in rows), sum(t for _, t in rows) / 1e6))
    metrics = {}
    with (RESULTS / "summary.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("arm", "k", "block", "seeds", "accuracy", "accuracy_sd", "mean_runtime_s"))
        for k in BUDGETS:
            for arm in ARMS:
                for block in ("all", *range(len(TOPICS))):
                    acc, runtime = zip(*groups[arm, k, block])
                    metrics[arm, k, block] = mean(acc), stdev(acc)
                    writer.writerow((arm, k, block, len(acc), f"{mean(acc):.6f}", f"{stdev(acc):.6f}",
                                     f"{mean(runtime):.6f}"))
    print("K | " + " | ".join(LABELS[arm] for arm in ARMS))
    for k in BUDGETS:
        print(f"{k} | " + " | ".join(f"{metrics[arm, k, 'all'][0]:.1%}" for arm in ARMS))
    plot(metrics, False)
    plot(metrics, True)


def plot(metrics, drift):
    fig, ax = plt.subplots(figsize=(9, 5), layout="constrained")
    xs = list(range(len(TOPICS))) if drift else BUDGETS
    for i, arm in enumerate(ARMS):
        ys, errors = zip(*(metrics[arm, BUDGETS[0], x] if drift else metrics[arm, x, "all"] for x in xs))
        jitter = (i - (len(ARMS) - 1) / 2) * (0.042 if drift else 0.42)
        ax.errorbar([x + jitter for x in xs], [100 * y for y in ys],
                    yerr=[100 * error for error in errors], label=LABELS[arm], marker="o",
                    linestyle="--" if "no" in arm or arm == "ecan_neither" else "-", capsize=2)
    ax.set_ylabel("Questions answered correctly (%)")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncols=2, fontsize=9)
    if drift:
        ax.set_title(f"Topic drift at K = {BUDGETS[0]} (mean ± seed SD)")
        ax.set_xticks(xs, [topic[0].title() for topic in TOPICS])
        ax.set_xlabel("Stream block (dominant topic)")
    else:
        ax.set_title("Accuracy under an attention budget (mean ± seed SD)")
        ax.set_xticks(xs)
        ax.set_xlabel("Selectable entries visible to the reasoner (K)")
    fig.savefig(RESULTS / ("drift.png" if drift else "accuracy.png"), dpi=160)
    plt.close(fig)
