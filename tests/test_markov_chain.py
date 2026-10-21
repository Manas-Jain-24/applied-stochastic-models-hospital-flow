"""
Unit tests for Absorbing Markov Chain, n-step transitions, stationary distributions, and MFPT.
"""
import unittest
import numpy as np
from src.markov_chain import (
    analyze_absorbing_markov_chain,
    compute_n_step_transition_matrix,
    compute_stationary_distribution,
    compute_mean_first_passage_times
)

class TestMarkovChain(unittest.TestCase):
    def test_absorbing_chain_analysis(self):
        # 2 transient states (T1, T2), 1 absorbing state (A)
        # P = [[0.5, 0.25, 0.25],
        #      [0.2, 0.5,  0.3 ],
        #      [0.0, 0.0,  1.0 ]]
        P = np.array([
            [0.5, 0.25, 0.25],
            [0.2, 0.5,  0.3 ],
            [0.0, 0.0,  1.0 ]
        ])
        trans = ["T1", "T2"]
        absorb = ["A"]
        
        res = analyze_absorbing_markov_chain(P, trans, absorb)
        self.assertIn("fundamental_matrix_N", res)
        self.assertIn("absorption_probabilities_B", res)
        # All absorption probabilities must sum to 1.0
        b_mat = res["absorption_probabilities_B"].values
        self.assertTrue(np.allclose(b_mat.sum(axis=1), 1.0))

    def test_n_step_transition_matrix(self):
        P = np.array([
            [0.7, 0.3],
            [0.4, 0.6]
        ])
        states = ["S1", "S2"]
        df_p2 = compute_n_step_transition_matrix(P, n_steps=2, state_names=states)
        expected_p2 = P @ P
        self.assertTrue(np.allclose(df_p2.values, expected_p2, atol=1e-4))

    def test_stationary_distribution(self):
        # Two-state chain: P = [[0.7, 0.3], [0.4, 0.6]]
        # Stationary equations: pi_1 = 0.7*pi_1 + 0.4*pi_2 => 0.3*pi_1 = 0.4*pi_2 => pi_1/pi_2 = 4/3
        # pi_1 = 4/7 = 0.5714, pi_2 = 3/7 = 0.4286
        P = np.array([
            [0.7, 0.3],
            [0.4, 0.6]
        ])
        states = ["S1", "S2"]
        pi = compute_stationary_distribution(P, states)
        self.assertAlmostEqual(pi["S1"], 4.0 / 7.0, places=3)
        self.assertAlmostEqual(pi["S2"], 3.0 / 7.0, places=3)
        self.assertAlmostEqual(pi.sum(), 1.0, places=4)

    def test_mean_first_passage_times(self):
        P = np.array([
            [0.7, 0.3],
            [0.4, 0.6]
        ])
        states = ["S1", "S2"]
        mfpt = compute_mean_first_passage_times(P, states)
        self.assertGreater(mfpt.loc["S1", "S2"], 0.0)
        self.assertGreater(mfpt.loc["S2", "S1"], 0.0)

if __name__ == "__main__":
    unittest.main()
