# I used AI to help me write the answer into a .txt file

def simulate_fibonacci_to_file(a_start, b_start, steps, filename, mode='a'):
   
    with open(filename, mode) as f:
        f.write(f"--- Starting Simulation: A={a_start}, B={b_start} ---\n")
        f.write(f"{'Step':<6} | {'A (Fn-2)':<10} | {'B (Fn-1)':<10}\n")
        f.write("-" * 35 + "\n")
        
        a_g = a_start
        b_g = b_start
        
        f.write(f"{0:<6} | {a_g:<10} | {b_g:<10}\n")
        
        for i in range(1, steps + 1):
            # The next 'A' becomes the current 'B'
            # The next 'B' becomes the sum of current 'A' and 'B'
            new_a = b_g
            new_b = a_g + b_g
            
            a_g = new_a
            b_g = new_b
            
            f.write(f"{i:<6} | {a_g:<10} | {b_g:<10}\n")
        
        f.write(f"\nFinal Result (B) after Step {steps}: {b_g}\n")
        f.write("=" * 35 + "\n\n")

def main():
    output_file = "fibonacci_results.txt"
    
    simulate_fibonacci_to_file(0, 1, 11, output_file, mode='w')
    
    simulate_fibonacci_to_file(3, 7, 11, output_file, mode='a')
    
    print(f"Simulation complete. Results written to {output_file}")

if __name__ == "__main__":
    main()