import numpy as np
import matplotlib.pyplot as plt

def main():

    bar_heights = np.array([1, 2, 4, 3, 2, 1, 4, 10, 15, 32, 42, 51, 57, 70, 85, 69, 53, 26, 12, 2])

    # Generate 20 evenly spaced values between 0 and 9
    x_positions = np.linspace(0, 9, len(bar_heights))

    plt.bar(x_positions, bar_heights, width=0.4)  # set width so bars don’t overlap
    plt.show()



if __name__ == "__main__":
    main()