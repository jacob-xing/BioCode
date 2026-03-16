def simulate_fibonacci_to_file(a_start, b_start, steps, filename, mode='a'):
    """
    Simulates Fibonacci iteration and writes the trace to a text file.
    a_start, b_start: Starting molecular concentrations (Green Phase)
    steps: Total number of iterations after the initial state.
    filename: The .txt file to write to
    mode: 'w' for overwrite, 'a' for append
    """
    with open(filename, mode) as f:
        f.write(f"--- Starting Simulation: A={a_start}, B={b_start} ---\n")
        f.write(f"{'Step':<6} | {'A (Fn-2)':<10} | {'B (Fn-1)':<10}\n")
        f.write("-" * 35 + "\n")
        
        a_g = a_start
        b_g = b_start
        
        # Step 0: The Initial state
        # For 0 and 1, stage 0 shows A=0. For 3 and 7, stage 0 shows A=3.
        f.write(f"{0:<6} | {a_g:<10} | {b_g:<10}\n")
        
        for i in range(1, steps + 1):
            # Fibonacci CRN Logic (RGB Shift):
            # The next 'A' becomes the current 'B'
            # The next 'B' becomes the sum of current 'A' and 'B'
            new_a = b_g
            new_b = a_g + b_g
            
            a_g = new_a
            b_g = new_b
            
            f.write(f"{i:<6} | {a_g:<10} | {b_g:<10}\n")
        
        # The 'B' variable holds the newest number in the sequence.
        # At Step 11, for (0,1), B will be 144.
        f.write(f"\nFinal Result (B) after Step {steps}: {b_g}\n")
        f.write("=" * 35 + "\n\n")

def main():
    output_file = "fibonacci_results.txt"
    
    # Task 1: Starting values 0, 1. 
    # To end at step 11 and produce 144, we perform 11 iterations.
    simulate_fibonacci_to_file(0, 1, 11, output_file, mode='w')
    
    # Task 2: Starting values 3, 7.
    # Same logic, ending at step 11.
    simulate_fibonacci_to_file(3, 7, 11, output_file, mode='a')
    
    print(f"Simulation complete. Results written to {output_file}")

if __name__ == "__main__":
    main()