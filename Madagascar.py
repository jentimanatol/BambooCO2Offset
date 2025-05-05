import matplotlib.pyplot as plt

# Years and estimated/projected CO₂ emissions (in million tonnes)
years = [2020, 2023, 2025, 2030, 2040, 2050, 2080]
emissions = [4.1, 4.0, 3.95, 3.5, 3.0, 2.5, 2.0]  # Approximate projections

# Plotting the data
plt.figure(figsize=(10, 6))
plt.plot(years, emissions, marker='o', linestyle='-', color='darkred', linewidth=2)
plt.title("Madagascar's CO₂ Emissions (Historical & Projected)", fontsize=14)
plt.xlabel("Year", fontsize=12)
plt.ylabel("CO₂ Emissions (Million Tonnes)", fontsize=12)
plt.xticks(years)
plt.ylim(0, 5)
plt.grid(True)
plt.tight_layout()
plt.show()
