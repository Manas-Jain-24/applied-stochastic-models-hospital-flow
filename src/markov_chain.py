"""
Absorbing Markov Chain analysis for hospital patient flow and discharge pathways.
Calculates:
- Canonical transition matrix decomposition: P = [Q R; 0 I]
- Fundamental matrix: N = (I - Q)^(-1)
- Expected time to absorption (discharge/death): t = N * 1
- Absorption probabilities: B = N * R
"""
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd

def construct_empirical_transition_matrix(
    state_transitions: List[Tuple[str, str]], 
    transient_states: List[str], 
    absorbing_states: List[str]
) -> Tuple[np.ndarray, List[str]]:
    """
    Constructs a transition probability matrix from observed state transitions (from_state, to_state).
    States are ordered: [transient_states, absorbing_states].
    """
    all_states = transient_states + absorbing_states
    state_to_idx = {s: i for i, s in enumerate(all_states)}
    n_states = len(all_states)
    counts = np.zeros((n_states, n_states), dtype=float)
    
    for from_s, to_s in state_transitions:
        if from_s in state_to_idx and to_s in state_to_idx:
            counts[state_to_idx[from_s], state_to_idx[to_s]] += 1.0
            
    # For absorbing states, transition to self is 1.0
    for a_state in absorbing_states:
        a_idx = state_to_idx[a_state]
        if counts[a_idx].sum() == 0:
            counts[a_idx, a_idx] = 1.0
            
    # Normalize rows to form transition probabilities
    row_sums = counts.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    P = counts / row_sums
    
    return P, all_states

def analyze_absorbing_markov_chain(
    P: np.ndarray, 
    transient_states: List[str], 
    absorbing_states: List[str]
) -> Dict[str, Any]:
    """
    Solves the canonical absorbing Markov chain equations.
    P = [[Q, R], [0, I]]
    where:
    - Q is (t x t) transient-to-transient matrix
    - R is (t x r) transient-to-absorbing matrix
    """
    t = len(transient_states)
    r = len(absorbing_states)
    
    Q = P[:t, :t]
    R = P[:t, t:t+r]
    
    # Fundamental matrix N = (I - Q)^(-1)
    I_t = np.eye(t)
    try:
        N = np.linalg.inv(I_t - Q)
    except np.linalg.LinAlgError:
        raise ValueError("Matrix (I - Q) is singular. Verify that transient states lead to absorbing states.")
        
    # Expected number of steps before absorption: t_steps = N * 1
    expected_steps = N.sum(axis=1)
    
    # Absorption probabilities: B = N * R
    B = np.dot(N, R)
    
    # Format as DataFrames for readability
    df_N = pd.DataFrame(np.round(N, 4), index=transient_states, columns=transient_states)
    df_B = pd.DataFrame(np.round(B, 4), index=transient_states, columns=absorbing_states)
    df_expected_steps = pd.Series(np.round(expected_steps, 4), index=transient_states, name="Expected_Steps_To_Absorption")
    
    return {
        "Q_matrix": Q,
        "R_matrix": R,
        "fundamental_matrix_N": df_N,
        "absorption_probabilities_B": df_B,
        "expected_steps_to_absorption": df_expected_steps
    }
