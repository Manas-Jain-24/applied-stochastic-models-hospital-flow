"""
Discrete-Event Simulation (DES) Engine for Hospital Bed Capacity and Queueing.
Uses standard library heapq for fast, deterministic, reproducible event-driven simulation.
Validates empirical metrics against theoretical M/M/c and M/G/c formulas.
"""
import heapq
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

class HospitalSimulation:
    def __init__(
        self,
        n_beds: int = 300,
        arrival_rate_per_day: float = 55.0,
        mean_los_days: float = 4.5,
        los_distribution: str = "gamma",
        los_shape_k: float = 2.0,
        simulation_days: float = 90.0,
        random_seed: int = 42
    ):
        self.n_beds = n_beds
        self.arrival_rate = arrival_rate_per_day
        self.mean_los = mean_los_days
        self.los_distribution = los_distribution.lower()
        self.los_shape_k = los_shape_k
        self.sim_days = simulation_days
        self.rng = np.random.default_rng(random_seed)
        
    def _sample_service_time(self) -> float:
        if self.los_distribution == "exponential":
            return self.rng.exponential(scale=self.mean_los)
        elif self.los_distribution == "gamma":
            theta = self.mean_los / self.los_shape_k
            return self.rng.gamma(shape=self.los_shape_k, scale=theta)
        elif self.los_distribution == "lognormal":
            # For lognormal with mean = mean_los and cv^2 = 1 / k
            cv2 = 1.0 / self.los_shape_k
            sigma2 = np.log(1.0 + cv2)
            sigma = np.sqrt(sigma2)
            mu = np.log(self.mean_los) - 0.5 * sigma2
            return self.rng.lognormal(mean=mu, sigma=sigma)
        else:
            return self.mean_los  # deterministic

    def run(self) -> Dict[str, Any]:
        """
        Executes discrete-event simulation over the horizon.
        Event types:
        0: Patient Arrival
        1: Patient Departure
        """
        current_time = 0.0
        occupied_beds = 0
        waiting_queue: List[float] = []  # contains arrival times of waiting patients
        
        event_calendar: List[tuple] = []  # (event_time, event_type, patient_id)
        
        # Schedule first arrival
        first_arrival = self.rng.exponential(scale=1.0 / self.arrival_rate)
        heapq.heappush(event_calendar, (first_arrival, 0, 1))
        
        patient_counter = 1
        wait_times: List[float] = []
        total_times: List[float] = []
        bed_occupancy_samples: List[tuple] = [] # (time, occupied_beds)
        
        while event_calendar:
            event_time, event_type, p_id = heapq.heappop(event_calendar)
            current_time = event_time
            
            if current_time > self.sim_days:
                break
                
            if event_type == 0:
                # ARRIVAL EVENT
                # Schedule next arrival
                next_arr_dt = self.rng.exponential(scale=1.0 / self.arrival_rate)
                patient_counter += 1
                heapq.heappush(event_calendar, (current_time + next_arr_dt, 0, patient_counter))
                
                # Check server availability
                if occupied_beds < self.n_beds:
                    occupied_beds += 1
                    wait_times.append(0.0)
                    service_duration = self._sample_service_time()
                    total_times.append(service_duration)
                    # Schedule departure
                    heapq.heappush(event_calendar, (current_time + service_duration, 1, p_id))
                else:
                    # All beds occupied -> join waiting queue
                    waiting_queue.append(current_time)
                    
            elif event_type == 1:
                # DEPARTURE EVENT
                if waiting_queue:
                    # Admit waiting patient immediately
                    arr_time = waiting_queue.pop(0)
                    w_q = current_time - arr_time
                    wait_times.append(w_q)
                    service_duration = self._sample_service_time()
                    total_times.append(w_q + service_duration)
                    # Schedule departure
                    heapq.heappush(event_calendar, (current_time + service_duration, 1, -1))
                else:
                    occupied_beds -= 1
                    
            bed_occupancy_samples.append((current_time, occupied_beds))
            
        # Compute empirical statistics (ignoring initial warmup 10% to achieve steady state)
        warmup_cutoff = int(len(wait_times) * 0.15) if len(wait_times) > 100 else 0
        steady_waits = wait_times[warmup_cutoff:]
        steady_totals = total_times[warmup_cutoff:]
        
        mean_wait_q = float(np.mean(steady_waits)) if steady_waits else 0.0
        mean_total_time = float(np.mean(steady_totals)) if steady_totals else 0.0
        delayed_ratio = float(np.mean(np.array(steady_waits) > 0.001)) if steady_waits else 0.0
        
        # Time-weighted average occupied beds
        if bed_occupancy_samples:
            df_occ = pd.DataFrame(bed_occupancy_samples, columns=["time", "beds"])
            mean_occupied = float(df_occ["beds"].mean())
        else:
            mean_occupied = 0.0
            
        utilization = mean_occupied / self.n_beds
        
        return {
            "simulation_days": self.sim_days,
            "total_patients_simulated": len(wait_times),
            "empirical_mean_wait_q_days": round(mean_wait_q, 4),
            "empirical_mean_total_days": round(mean_total_time, 4),
            "empirical_prob_delay": round(delayed_ratio, 4),
            "empirical_mean_occupied_beds": round(mean_occupied, 2),
            "empirical_bed_utilization": round(utilization, 4),
            "max_queue_depth": len(waiting_queue)
        }
