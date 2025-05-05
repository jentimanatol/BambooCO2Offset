import matplotlib.pyplot as plt

# Extended projection data for 2025 to 2080 (synthetic values for illustration)
years = [2025, 2030, 2040, 2050, 2060, 2070, 2080]
co2_percentages = [65, 68, 72, 75, 77, 78, 78.5]  # Hypothetical projected shares

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(years, co2_percentages, marker='o', linestyle='-', color='forestgreen', linewidth=2)
plt.title("Projected Share of Global CO₂ Emissions from Group B Developing Countries (2025–2080)", fontsize=14)
plt.xlabel("Year", fontsize=12)
plt.ylabel("Share of Global CO₂ Emissions (%)", fontsize=12)
plt.grid(True)
plt.ylim(60, 85)
plt.xticks(years)
plt.tight_layout()
plt.show()
