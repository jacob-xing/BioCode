import numpy as np

def solve_part_c(t_val, num_bits=100000):
    # 1. Generate 5 independent stochastic streams for input t (degree n=5)
    t_streams = [np.random.random(num_bits) < t_val for _ in range(5)]
    
    # 2. Adder block: count the number of ones across the 5 streams (k = 0 to 5)
    selection = np.sum(t_streams, axis=0)
    
    # 3. Define Bernstein coefficients (b0, b1, b2, b3, b4, b5)
    # These are the constant probability inputs to the MUX
    b_coeffs = [1/2, 1/4, 1/2, 1/4, 1/2, 1.0]
    
    # 4. Generate the constant bit streams for the MUX ports
    mux_inputs = [np.random.random(num_bits) < b for b in b_coeffs]
    
    # 5. Multiplexer logic: select input bit based on the count k
    output_bits = np.choose(selection, mux_inputs)
    
    return np.mean(output_bits)

# Demonstrate for requested values
test_values = [0, 0.25, 0.5, 0.75, 1]
print(f"{'Input (t)':<10} | {'Simulated Output':<20}")
print("-" * 35)
for v in test_values:
    res = solve_part_c(v)
    print(f"{v:<10} | {res:<20.5f}")