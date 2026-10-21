"""
Visualization Module for Applied Stochastic Models Hospital Flow Project.
Generates publication-quality 300 DPI figures saved to reports/figures/.
"""
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

from src.queueing import (
    erlang_b, 
    erlang_c, 
    mmc_performance_metrics, 
    mgc_allen_cunneen,
    mmck_finite_buffer_metrics
)
from src.arrival_process import fit_diurnal_arrival_intensity, diurnal_sinusoidal_rate
from src.config import get_path

def set_publication_style():
    """Sets clean styling with serif/sans-serif fonts and high contrast."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams.update({
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 14,
        "lines.linewidth": 2.0
    })

def generate_fig1_los_distributions(data: np.ndarray, out_dir: Path) -> str:
    """Figure 1: Empirical LOS distribution vs Fitted Candidates."""
    set_publication_style()
    fig, ax = plt.subplots(figsize=(9, 5))
    
    clean_data = data[~np.isnan(data) & (data > 0)]
    ax.hist(clean_data, bins=45, density=True, alpha=0.45, color="#1f77b4", edgecolor="white", label="Empirical LOS Data")
    
    x_eval = np.linspace(0.1, 25.0, 400)
    
    # Fit distributions
    exp_p = stats.expon.fit(clean_data)
    gam_p = stats.gamma.fit(clean_data)
    log_p = stats.lognorm.fit(clean_data)
    
    ax.plot(x_eval, stats.expon.pdf(x_eval, *exp_p), "r--", label="Exponential (Memoryless)")
    ax.plot(x_eval, stats.gamma.pdf(x_eval, *gam_p), color="#2ca02c", label="Gamma Distribution")
    ax.plot(x_eval, stats.lognorm.pdf(x_eval, *log_p), color="#ff7f0e", label="Lognormal Distribution")
    
    ax.set_title("Figure 1: Hospital Length of Stay (LOS) Probability Density")
    ax.set_xlabel("Length of Stay S (Days)")
    ax.set_ylabel("Probability Density f(s)")
    ax.set_xlim(0, 22)
    ax.legend(frameon=True, facecolor="white", framealpha=0.9)
    
    out_file = out_dir / "fig1_los_distributions.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    return str(out_file)

def generate_fig2_erlang_capacity_curves(offered_load: float, arrival_rate: float, service_rate: float, out_dir: Path) -> str:
    """Figure 2: Erlang-B and Erlang-C Capacity Curves."""
    set_publication_style()
    fig, ax = plt.subplots(figsize=(9, 5))
    
    c_min = int(offered_load * 0.95)
    c_max = int(offered_load * 1.25)
    capacities = np.arange(c_min, c_max + 1)
    
    b_vals = [erlang_b(c, offered_load) for c in capacities]
    c_vals = [erlang_c(c, arrival_rate, service_rate) for c in capacities]
    
    ax.plot(capacities, c_vals, "-o", color="#1f77b4", label="Erlang-C: P(Wait in Admission Queue)")
    ax.plot(capacities, b_vals, "--s", color="#d62728", label="Erlang-B: P(Bed Loss / Diversion)")
    
    ax.axhline(0.01, color="red", linestyle=":", lw=1.5, label="1% Patient Loss Target")
    ax.axhline(0.05, color="blue", linestyle=":", lw=1.5, label="5% Queue Delay Target")
    ax.axvline(offered_load, color="gray", linestyle="-.", alpha=0.7, label=f"Offered Load a={offered_load:.1f} beds")
    
    ax.set_title("Figure 2: Inpatient Bed Dimensioning (Erlang-B vs. Erlang-C)")
    ax.set_xlabel("Inpatient Bed Capacity (c)")
    ax.set_ylabel("Operating Probability")
    ax.set_ylim(-0.02, 1.02)
    ax.legend(frameon=True, facecolor="white", framealpha=0.9)
    
    out_file = out_dir / "fig2_erlang_capacity_curves.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    return str(out_file)

def generate_fig3_heavy_tail_delay_penalty(arrival_rate: float, service_rate: float, cv2_service: float, out_dir: Path) -> str:
    """Figure 3: M/M/c vs M/G/c heavy tail waiting penalty."""
    set_publication_style()
    fig, ax = plt.subplots(figsize=(9, 5))
    
    offered_load = arrival_rate / service_rate
    c_min = int(offered_load * 1.02)
    c_max = int(offered_load * 1.25)
    capacities = np.arange(c_min, c_max + 1)
    
    mmc_waits = [mmc_performance_metrics(c, arrival_rate, service_rate)["w_q"] * 24.0 for c in capacities]
    mgc_waits = [mgc_allen_cunneen(c, arrival_rate, service_rate, cv2_service=cv2_service)["w_q_mgc"] * 24.0 for c in capacities]
    
    ax.plot(capacities, mmc_waits, "g--", lw=2.2, label="M/M/c (Exponential LOS, cv^2 = 1.0)")
    ax.plot(capacities, mgc_waits, color="#ff7f0e", lw=2.5, label=f"M/G/c Heavy-Tail (Empirical cv^2 = {cv2_service:.2f})")
    
    ax.set_title("Figure 3: Variance Penalty: Expected Patient Queue Delay (Hours)")
    ax.set_xlabel("Inpatient Bed Capacity (c)")
    ax.set_ylabel("Expected Wait in Queue W_q (Hours)")
    ax.legend(frameon=True, facecolor="white", framealpha=0.9)
    
    out_file = out_dir / "fig3_heavy_tail_delay_penalty.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    return str(out_file)

def generate_fig4_diurnal_arrival_intensity(hourly_timestamps: pd.Series, out_dir: Path) -> str:
    """Figure 4: 24-Hour Diurnal Arrival Rate."""
    set_publication_style()
    res = fit_diurnal_arrival_intensity(hourly_timestamps)
    
    fig, ax = plt.subplots(figsize=(9, 5))
    hours = np.arange(24)
    empirical = res["empirical_hourly_rates"]
    
    ax.bar(hours, empirical, width=0.6, color="#4c72b0", alpha=0.6, label="Observed Hourly Rate")
    
    t_fine = np.linspace(0, 23, 200)
    fitted = diurnal_sinusoidal_rate(t_fine, res["baseline_rate_per_hour"], res["amplitude"], res["peak_hour"])
    ax.plot(t_fine, fitted, "r-", lw=2.5, label=f"NHPP Intensity Curve λ(t) (Peak: {res['peak_hour']:.1f}h)")
    
    ax.set_title("Figure 4: Non-Homogeneous Poisson Arrival Rate λ(t) Across the Day")
    ax.set_xlabel("Hour of Day (0–23)")
    ax.set_ylabel("Patient Arrivals per Hour")
    ax.set_xticks(range(0, 24, 2))
    ax.legend(frameon=True, facecolor="white", framealpha=0.9)
    
    out_file = out_dir / "fig4_diurnal_arrival_intensity.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    return str(out_file)

def generate_fig5_markov_transition_heatmap(P_matrix: np.ndarray, state_names: List[str], out_dir: Path) -> str:
    """Figure 5: Patient State Transition Probability Matrix Heatmap."""
    set_publication_style()
    fig, ax = plt.subplots(figsize=(8, 6))
    
    cax = ax.matshow(P_matrix, cmap="Blues", alpha=0.85)
    fig.colorbar(cax)
    
    ax.set_xticks(range(len(state_names)))
    ax.set_yticks(range(len(state_names)))
    ax.set_xticklabels(state_names, rotation=35, ha="left")
    ax.set_yticklabels(state_names)
    
    for i in range(len(state_names)):
        for j in range(len(state_names)):
            val = P_matrix[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="black" if val < 0.5 else "white", fontsize=9)
            
    ax.set_title("Figure 5: Patient Flow Transition Matrix P", pad=20)
    
    out_file = out_dir / "fig5_markov_transition_heatmap.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    return str(out_file)

def generate_fig6_finite_buffer_tradeoff(c: int, offered_load: float, arrival_rate: float, service_rate: float, out_dir: Path) -> str:
    """Figure 6: M/M/c/K Buffer vs Diversion Tradeoff."""
    set_publication_style()
    fig, ax1 = plt.subplots(figsize=(9, 5))
    
    buffer_sizes = range(0, 45, 2)
    diversion_rates = []
    queue_waits = []
    
    for buf in buffer_sizes:
        k_cap = c + buf
        m = mmck_finite_buffer_metrics(c=c, k_capacity=k_cap, arrival_rate=arrival_rate, service_rate=service_rate)
        diversion_rates.append(m["prob_loss_diversion"] * 100.0)
        queue_waits.append(m["w_q_days"] * 24.0)
        
    color = "#d62728"
    ax1.set_xlabel("ED Boarding Buffer Size (K - c Beds)")
    ax1.set_ylabel("Ambulance Diversion / Loss Rate (%)", color=color)
    line1 = ax1.plot(buffer_sizes, diversion_rates, "-s", color=color, label="Diversion Rate (%)")
    ax1.tick_params(axis="y", labelcolor=color)
    
    ax2 = ax1.twinx()
    color2 = "#1f77b4"
    ax2.set_ylabel("Expected Queue Delay W_q (Hours)", color=color2)
    line2 = ax2.plot(buffer_sizes, queue_waits, "-o", color=color2, label="Queue Delay (Hours)")
    ax2.tick_params(axis="y", labelcolor=color2)
    
    plt.title("Figure 6: M/M/c/K Trade-off: Diversion Probability vs. Boarding Wait")
    
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="center right", frameon=True, facecolor="white")
    
    out_file = out_dir / "fig6_finite_buffer_tradeoff.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    return str(out_file)

def generate_all_figures():
    """Generates all 6 figures and saves them in reports/figures/."""
    figures_dir = Path("reports/figures")
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating publication figures in reports/figures/...")
    
    # Load synthetic encounters
    df_enc = pd.read_csv("data/synthetic/synthetic_hospital_encounters.csv")
    los = df_enc["length_of_stay_continuous"].values
    
    # 1. LOS Distributions
    f1 = generate_fig1_los_distributions(los, figures_dir)
    print(f"Saved: {f1}")
    
    # 2. Erlang Capacity Curves
    f2 = generate_fig2_erlang_capacity_curves(offered_load=269.3, arrival_rate=50.0, service_rate=1.0/5.386, out_dir=figures_dir)
    print(f"Saved: {f2}")
    
    # 3. Heavy Tail Delay Penalty
    f3 = generate_fig3_heavy_tail_delay_penalty(arrival_rate=50.0, service_rate=1.0/5.386, cv2_service=1.99, out_dir=figures_dir)
    print(f"Saved: {f3}")
    
    # 4. Diurnal Arrivals
    f4 = generate_fig4_diurnal_arrival_intensity(df_enc["arrival_time"], figures_dir)
    print(f"Saved: {f4}")
    
    # 5. Markov Transition Heatmap
    states = ["Med", "Surg", "ICU", "Home", "HH", "SNF", "Exp"]
    P = np.array([
        [0.10, 0.05, 0.05, 0.65, 0.10, 0.03, 0.02],
        [0.05, 0.15, 0.05, 0.55, 0.12, 0.10, 0.03],
        [0.35, 0.20, 0.10, 0.15, 0.05, 0.05, 0.10],
        [0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00],
        [0.00, 0.00, 0.00, 0.00, 1.00, 0.00, 0.00],
        [0.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0.00],
        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00]
    ])
    f5 = generate_fig5_markov_transition_heatmap(P, states, figures_dir)
    print(f"Saved: {f5}")
    
    # 6. M/M/c/K Buffer Tradeoff
    f6 = generate_fig6_finite_buffer_tradeoff(c=285, offered_load=269.3, arrival_rate=50.0, service_rate=1.0/5.386, out_dir=figures_dir)
    print(f"Saved: {f6}")
    
    print("All 6 publication figures generated successfully!")

if __name__ == "__main__":
    generate_all_figures()
