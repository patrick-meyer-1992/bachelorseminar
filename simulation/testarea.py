# %%
import numpy as np
import matplotlib.pyplot as plt

def draw_exponential_histogram(n, rate):
    # Draw n samples from an exponential distribution with the given rate
    samples = np.random.exponential(rate, n)
    
    # Create a histogram of the samples
    plt.hist(samples, bins=30, edgecolor='black')
    plt.title(f'Histogram of {n} samples from an Exponential Distribution (rate={rate})')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.show()

# Example usage
draw_exponential_histogram(1000, 40)

# %%
mtbf = np.random.uniform(20, 2)
sample = np.random.exponential(20)
print(f"MTBF: {20}, Sample: {sample}")
# %%
