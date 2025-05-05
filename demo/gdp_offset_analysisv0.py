import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ======================
# DATA & CALCULATIONS
# ======================
countries = ["Jamaica", "Madagascar", "Vietnam"]
gdp_per_country = np.array([15_000_000_000, 14_000_000_000, 700_000_000_000])  # GDP in USD (example data)
annual_emissions = np.array([6_083_040, 4_099_000, 327_905_620])  # tons CO2/yr
land_area = np.array([4244, 228531, 127932])  # sq mi

# Updated sequestration rate: 25 tons CO2 per acre per year
high_seq = 16000  # tons CO2/sq mi/yr
bamboo_area_needed = annual_emissions / high_seq
percent_land = (bamboo_area_needed / land_area) * 100

# Conversion rate for financial analysis (assumed cost per square mile for bamboo offset)
cost_per_sq_mi = 100_000  # USD per square mile per year (assumed)

# Calculations for annual spending and GDP percentage
annual_spending = bamboo_area_needed * cost_per_sq_mi
gdp_percentage = (annual_spending / gdp_per_country) * 100

# ======================
# PLOT SETUP
# ======================
def generate_gdp_offset_plot():
    plt.figure(figsize=(15, 8))
    sns.set_style("whitegrid")
    plt.rcParams['mathtext.fontset'] = 'cm'  # Professional math fonts
    palette = sns.color_palette("coolwarm", n_colors=2)

    # ======================
    # GROUPED BAR PLOT
    # ======================
    bar_width = 0.35
    x = np.arange(len(countries))

    # Plot bars for annual spending
    bars_spending = plt.bar(x - bar_width/2, annual_spending, width=bar_width,
                            color=palette[0], alpha=0.9, edgecolor='black',
                            label='Annual Spending (USD)')
    bars_gdp_percent = plt.bar(x + bar_width/2, gdp_percentage, width=bar_width,
                               color=palette[1], alpha=0.9, edgecolor='black',
                               label='GDP % for Bamboo Offset')

    # ======================
    # ANNOTATIONS
    # ======================
    def format_large_num(x):
        if x >= 1e9:
            return f"${x/1e9:,.1f}B"
        elif x >= 1e6:
            return f"${x/1e6:,.1f}M"
        elif x >= 1e3:
            return f"${x/1e3:,.0f}K"
        return f"${x:,.0f}"

    for i, (spending, gdp_perc) in enumerate(zip(annual_spending, gdp_percentage)):
        plt.text(x[i] - bar_width/2, spending * 1.05, 
                 f"{format_large_num(spending)}", 
                 ha='center', va='bottom', fontsize=10, fontweight='bold')
        plt.text(x[i] + bar_width/2, gdp_perc * 1.05, 
                 f"{gdp_perc:.2f}%", 
                 ha='center', va='bottom', fontsize=10, fontweight='bold')

    # ======================
    # AESTHETICS
    # ======================
    plt.title("Annual Spending vs. GDP Percentage for Bamboo CO₂ Offset", 
              fontsize=16, pad=20, fontweight='bold')
    plt.xlabel("Country", fontsize=14, labelpad=10)
    plt.ylabel("Amount (USD) / GDP Percentage", fontsize=14, labelpad=10)
    plt.xticks(x, countries, fontsize=12)
    plt.grid(True, which="both", ls="--", alpha=0.2)

    # ======================
    # PROFESSIONAL LEGEND
    # ======================
    plt.legend(loc='upper right', fontsize=11)

    # Add a watermark with the specified text
    plt.text(0.1, 0.7, 'BHCC 2025 ', fontsize=20, color='gray', alpha=0.5, ha='center', va='center', rotation=45, transform=plt.gca().transAxes)

    # ======================
    # FINAL TOUCHES
    # ======================
    plt.tight_layout()
    plt.savefig('gdp_bamboo_co2_offset_analysis.jpg', dpi=300, bbox_inches='tight')  # Save high-res
    plt.show()
