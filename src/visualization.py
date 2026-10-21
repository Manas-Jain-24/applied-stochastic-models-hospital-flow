"""
Visualization Module for Applied Stochastic Models Hospital Flow Project.
Generates publication-quality 300 DPI figures saved to reports/figures/.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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

def generate_fig7_jackson_network(out_dir: Path) -> str:
    """Figure 7: Jackson Queueing Network Department Utilization & Traffic."""
    from src.jackson_network import analyze_jackson_network
    
    depts = ["Emergency", "ICU", "MedSurg", "StepDown"]
    gamma = [45.0, 5.0, 15.0, 0.0]
    P = np.array([
        [0.00, 0.15, 0.40, 0.05],
        [0.05, 0.00, 0.70, 0.15],
        [0.00, 0.05, 0.00, 0.05],
        [0.00, 0.10, 0.80, 0.00]
    ])
    capacities = [35, 30, 160, 25]
    los_means = [0.5, 3.2, 5.2, 2.8]
    
    res = analyze_jackson_network(depts, gamma, P, capacities, los_means)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    x = np.arange(len(depts))
    width = 0.35
    
    ext_rates = [st.exogenous_rate for st in res.stations]
    tot_rates = [st.arrival_rate for st in res.stations]
    
    ax1.bar(x - width/2, ext_rates, width, label="Direct External Arrival (gamma_j)", color="#2ca02c")
    ax1.bar(x + width/2, tot_rates, width, label="Total Effective Traffic (Lambda_j)", color="#1f77b4")
    ax1.set_xticks(x)
    ax1.set_xticklabels(depts)
    ax1.set_ylabel("Patients per Day")
    ax1.set_title("(A) External vs. Total Traffic Rates (Lambda = gamma + P^T Lambda)")
    ax1.legend(frameon=True, facecolor="white")
    
    rhos = [st.utilization * 100 for st in res.stations]
    colors = ["#d62728" if st.name == res.bottleneck_station else "#3b528b" for st in res.stations]
    bars = ax2.bar(depts, rhos, color=colors, width=0.5)
    ax2.axhline(85.0, color="orange", linestyle="--", linewidth=1.5, label="Target Safety Threshold (85%)")
    ax2.set_ylabel("Bed Utilization rho (%)")
    ax2.set_title(f"(B) Department Utilization (Bottleneck: {res.bottleneck_station})")
    ax2.set_ylim(0, 105)
    ax2.legend(frameon=True, facecolor="white")
    
    for bar in bars:
        h = bar.get_height()
        ax2.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontweight="bold")
                     
    plt.suptitle(f"Figure 7: Multi-Stage Jackson Queueing Network (End-to-End Hospital Dwell: {res.mean_end_to_end_los:.2f} Days)", fontsize=13, y=1.02)
    out_file = out_dir / "fig7_jackson_network_flow.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    return str(out_file)

def generate_fig8_time_varying_psa(out_dir: Path) -> str:
    """Figure 8: 24-Hour Diurnal Queueing & Pointwise Stationary Staffing."""
    from src.time_varying import compare_constant_vs_dynamic_staffing
    
    c_res, d_res = compare_constant_vs_dynamic_staffing(base_beds=425, surge_delta=25)
    
    hours = np.arange(24)
    arrivals = [st.arrival_rate_per_hour for st in c_res.hourly_states]
    c_waits = [st.wait_time_hours * 60.0 for st in c_res.hourly_states]
    d_waits = [st.wait_time_hours * 60.0 for st in d_res.hourly_states]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    
    ax1.plot(hours, arrivals, "-o", color="#2ca02c", linewidth=2.2, label="Arrival Rate lambda(t)")
    ax1.axvline(c_res.peak_hour, color="red", linestyle=":", label=f"Peak Hour ({c_res.peak_hour}:00)")
    ax1.set_ylabel("Arrival Rate (Patients/Hour)")
    ax1.set_title("(A) Diurnal Non-Homogeneous Poisson Arrival Rate lambda(t)")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right", frameon=True, facecolor="white")
    
    ax2.plot(hours, c_waits, "-s", color="#d62728", linewidth=2.0, label=f"Constant Staffing (Peak Wait: {c_res.peak_wait_time_hours*60:.1f} min)")
    ax2.plot(hours, d_waits, "-^", color="#1f77b4", linewidth=2.0, label=f"Dynamic Shift Staffing (Peak Wait: {d_res.peak_wait_time_hours*60:.1f} min)")
    ax2.set_xlabel("Hour of Day (00:00 to 23:00)")
    ax2.set_ylabel("Expected Delay W_q (Minutes)")
    ax2.set_title("(B) Pointwise Stationary Queueing Delay: Constant vs. Dynamic Staffing")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="upper right", frameon=True, facecolor="white")
    ax2.set_xticks(hours)
    
    plt.suptitle("Figure 8: Time-Varying Queueing Dynamics & Staffing Mitigation", fontsize=13, y=1.01)
    out_file = out_dir / "fig8_time_varying_diurnal_queue.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    return str(out_file)

def generate_fig9_bed_allocation_frontier(out_dir: Path) -> str:
    """Figure 9: Optimal Multi-Department Bed Allocation Frontier."""
    from src.bed_allocation import DepartmentSpec, compute_capacity_expansion_frontier
    
    depts = [
        DepartmentSpec(name="ICU", offered_load=25.0, weight=5.0, min_beds=26),
        DepartmentSpec(name="Emergency_Ward", offered_load=35.0, weight=2.0, min_beds=36),
        DepartmentSpec(name="MedSurg", offered_load=180.0, weight=1.0, min_beds=181),
    ]
    
    frontier = compute_capacity_expansion_frontier(depts, min_total_beds=250, max_total_beds=300, step=2)
    
    total_beds = [pt["total_beds"] for pt in frontier]
    opt_blocking = [pt["optimal_weighted_blocking"] * 100 for pt in frontier]
    prop_blocking = [pt["proportional_weighted_blocking"] * 100 for pt in frontier]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    ax1.plot(total_beds, prop_blocking, "--o", color="#d62728", label="Proportional Sizing", linewidth=2)
    ax1.plot(total_beds, opt_blocking, "-s", color="#2ca02c", label="Optimal Marginal Sizing (Fox Algorithm)", linewidth=2.5)
    ax1.set_xlabel("Total Hospital Bed Capacity (C_total)")
    ax1.set_ylabel("Weighted System Blocking Probability (%)")
    ax1.set_title("(A) Hospital Capacity Expansion Pareto Frontier")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(frameon=True, facecolor="white")
    
    # Department breakdown for optimal at 270 beds
    opt_at_270 = next(pt for pt in frontier if pt["total_beds"] == 270)
    dept_names = list(opt_at_270["optimal_beds_by_dept"].keys())
    opt_alloc = [opt_at_270["optimal_beds_by_dept"][k] for k in dept_names]
    prop_alloc = [opt_at_270["proportional_beds_by_dept"][k] for k in dept_names]
    
    x = np.arange(len(dept_names))
    width = 0.35
    ax2.bar(x - width/2, prop_alloc, width, label="Proportional", color="#d62728", alpha=0.85)
    ax2.bar(x + width/2, opt_alloc, width, label="Optimal (Fox)", color="#2ca02c", alpha=0.85)
    ax2.set_xticks(x)
    ax2.set_xticklabels(dept_names)
    ax2.set_ylabel("Allocated Beds")
    ax2.set_title("(B) Bed Distribution Comparison at Budget C = 270 Beds")
    ax2.legend(frameon=True, facecolor="white")
    
    plt.suptitle("Figure 9: Multi-Department Bed Allocation Optimization (Erlang-B)", fontsize=13, y=1.02)
    out_file = out_dir / "fig9_optimal_bed_allocation.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    return str(out_file)

def generate_all_figures():
    """Generates all 9 publication figures and saves them in reports/figures/."""
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

    # 7. Jackson Network Flow
    f7 = generate_fig7_jackson_network(figures_dir)
    print(f"Saved: {f7}")

    # 8. Time-Varying PSA
    f8 = generate_fig8_time_varying_psa(figures_dir)
    print(f"Saved: {f8}")

    # 9. Optimal Bed Allocation
    f9 = generate_fig9_bed_allocation_frontier(figures_dir)
    print(f"Saved: {f9}")
    
    print("All 9 publication figures generated successfully!")

if __name__ == "__main__":
    generate_all_figures()

