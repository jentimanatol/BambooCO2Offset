import matplotlib.pyplot as plt

# Historical and projected CO₂ emissions in million tonnes (Mt)
years = [2020, 2022, 2023, 2025, 2030, 2040, 2050, 2080]
emissions = [6.1, 6.08, 6.87, 6.5, 5.5, 4.0, 3.0, 2.5]  # Example data

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(years, emissions, marker='o', linestyle='-', color='darkblue', linewidth=2)
plt.title("Jamaica's CO₂ Emissions (Historical and Projected)", fontsize=14)
plt.xlabel("Year", fontsize=12)
plt.ylabel("CO₂ Emissions (Million Tonnes)", fontsize=12)
plt.grid(True)
plt.xticks(years, rotation=45)
plt.ylim(0, 8)
plt.tight_layout()
plt.show()
