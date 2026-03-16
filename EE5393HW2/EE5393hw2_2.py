import numpy as np

class BiquadCRNSimulator:
    """
    Simulates a 2nd-order Biquad Filter using Chemical Reaction Network (CRN)
    logic and an RGB (Red-Green-Blue) clocking scheme.
    """
    def __init__(self):
        # Filter coefficients from Figure 2a
        self.b0, self.b1, self.b2 = 0.125, 0.125, 0.125  # Feed-forward (1/8)
        self.a1, self.a2 = 0.5, 0.25                    # Feedback (1/2, 1/4)
        
        # State variables (Concentrations in the 'Green' storage phase)
        self.d1_g = 0.0  # Delay tap 1 (x[n-1])
        self.d2_g = 0.0  # Delay tap 2 (x[n-2])
        self.y1_g = 0.0  # Feedback tap 1 (y[n-1])
        self.y2_g = 0.0  # Feedback tap 2 (y[n-2])

    def run_cycle(self, x_input_val):
        """
        Simulates one full RGB clock cycle.
        """
        # PHASE 1: GREEN TO BLUE
        x_b = x_input_val
        d1_b, d2_b = self.d1_g, self.d2_g
        y1_b, y2_b = self.y1_g, self.y2_g

        # PHASE 2: BLUE TO RED (Computation)
        y_r = (self.b0 * x_b) + \
              (self.b1 * d1_b) + \
              (self.b2 * d2_b) + \
              (self.a1 * y1_b) + \
              (self.a2 * y2_b)
        
        # Intermediate Red states
        x_r = x_b
        d1_r = d1_b

        # PHASE 3: RED TO GREEN (State Update)
        self.d2_g = d1_r      
        self.d1_g = x_r       
        self.y2_g = self.y1_g 
        self.y1_g = y_r       

        return y_r

def main():
    inputs = [100, 5, 500, 20, 250]
    sim = BiquadCRNSimulator()
    
    filename = "biquad_results.txt"
    
    # Using 'with' ensures the file is closed properly even if an error occurs
    with open(filename, "w") as f:
        f.write("="*55 + "\n")
        f.write("EE 5393: Biquad Filter CRN Mathematical Trace\n")
        f.write(f"{'Cycle':<8} | {'Input (X)':<10} | {'Output (Y)':<10}\n")
        f.write("-" * 55 + "\n")

        for i, x in enumerate(inputs, 1):
            y_out = sim.run_cycle(x)
            f.write(f"{i:<8} | {x:<10.2f} | {y_out:<10.2f}\n")

        f.write("-" * 55 + "\n")
        f.write("Final State for next 'Initial Quantities' (.in) file:\n")
        f.write(f"D1_G: {sim.d1_g:.2f} | D2_G: {sim.d2_g:.2f}\n")
        f.write(f"Y1_G: {sim.y1_g:.2f} | Y2_G: {sim.y2_g:.2f}\n")
        f.write("="*55 + "\n")

    print(f"Results have been successfully written to {filename}")

if __name__ == "__main__":
    main()