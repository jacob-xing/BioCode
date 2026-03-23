# I used AI to help me write the answer into a .txt file

def simulate_biquad_to_file(inputs, filename="biquad_results.txt"):
    x_n1, x_n2 = 0, 0
    y_n1, y_n2 = 0, 0
    
    with open(filename, "w") as f:
        # Header for the file
        header = f"{'Cycle':<8} | {'Input (X)':<10} | {'Output (Y)':<10}\n"
        separator = "-" * 35 + "\n"
        f.write("Biquad Filter Simulation Results\n")
        f.write(f"Equation: y[n] = 1/8 * (x[n] + x[n-1] + x[n-2] + y[n-1] + y[n-2])\n")
        f.write(separator)
        f.write(header)
        f.write(separator)
        
        for i, x_n in enumerate(inputs, 1):
            y_n = (1/8) * (x_n + x_n1 + x_n2 + y_n1 + y_n2)
            
            line = f"{i:<8} | {x_n:<10} | {y_n:<10.4f}\n"
            f.write(line)
            
            x_n2 = x_n1
            x_n1 = x_n
            y_n2 = y_n1
            y_n1 = y_n

    print(f"Simulation complete. Results written to {filename}")

x_values = [100, 5, 500, 20, 250]

simulate_biquad_to_file(x_values)