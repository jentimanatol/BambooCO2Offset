import pandas as pd

# Parameters
start_year = 2025
end_year = 2099
years = list(range(start_year, end_year + 1))

# Initial CO2 emissions in million metric tons (rounded)
initial_emissions = 8.5

# Growth scenarios
growth_rates = {
    "Low Growth (0.1%)": 0.001,
    "Medium Growth (0.5%)": 0.005,
    "High Growth (1.2%)": 0.012
}

# Calculate emissions for each scenario
emission_data = {
    "Low Growth (0.1%)": [],
    "Medium Growth (0.5%)": [],
    "High Growth (1.2%)": []
}

for scenario, rate in growth_rates.items():
    emissions = [initial_emissions]
    for _ in range(1, len(years)):
        emissions.append(emissions[-1] * (1 + rate))
    emission_data[scenario] = [(year, round(emission)) for year, emission in zip(years, emissions)]

# Combine all scenarios into a single list
estimated_co1_emission = {
    scenario: emission_data[scenario] for scenario in emission_data
}

estimated_co1_emission["Low Growth (0.1%)"][:5], estimated_co1_emission["Medium Growth (0.5%)"][:5], estimated_co1_emission["High Growth (1.2%)"][:5]
