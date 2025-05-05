import matplotlib.pyplot as plt
import pandas as pd

# Parameters
start_year = 2025
end_year = 2099
years = list(range(start_year, end_year + 1))

# Initial CO2 emissions in million metric tons
initial_emissions = 8.5

# Growth scenarios
growth_rates = {
    "Low Growth (0.1%)": 0.001,
    "Medium Growth (0.5%)": 0.005,
    "High Growth (1.2%)": 0.012
}

# Calculate emissions for each scenario
data = {"Year": years}
for scenario, rate in growth_rates.items():
    emissions = [initial_emissions]
    for _ in range(1, len(years)):
        emissions.append(emissions[-1] * (1 + rate))
    data[scenario] = emissions

# Convert to DataFrame
df = pd.DataFrame(data)

# Plotting
plt.figure(figsize=(12, 6))
for scenario in growth_rates.keys():
    plt.plot(df["Year"], df[scenario], label=scenario)

plt.title("Projected CO₂ Emissions in Jamaica (2025–2099)")
plt.xlabel("Year")
plt.ylabel("CO₂ Emissions (Million Metric Tons)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
