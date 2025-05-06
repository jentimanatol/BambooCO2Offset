import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import ast
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

# Initialize main window
root = tk.Tk()
root.title("🌿 Bamboo CO2 Offset Calculator By AJ")
root.geometry("2500x1750")

# Matplotlib figure and axis
fig, ax = plt.subplots(figsize=(10, 6))
canvas = None

# Constants
REFERENCE_YEARS_OFFSET = 75  # Fixed constant for reference period (2025-2099)
ANNUAL_EMISSION_INCREASE = 0.01  # 1% annual increase in emissions

# Default data
default_countries = ["Jamaica", "Madagascar", "Vietnam"]
default_land_area = [4244, 228531, 127932]  # in sq mi
default_emissions = [6083040, 4099000, 327905620]  # in tons CO2/yr
default_gdp_per_country = [15_000_000_000, 14_000_000_000, 700_000_000_000]  # GDP in USD
default_years_offset = [2025, 2099]  # Default years for CO2 offset
default_percent_land = 10.0  # Default percent of land available (%)
default_gdp_percentage = 0.3  # Default percent of GDP available (%)

# Sequestration rate: 25 tons CO2 per acre per year (converted to square miles)
sequestration_rate = 16000  # tons CO2/sq mi/yr

# Cost to plant bamboo (USD per square mile)
cost_planting_bamboo = 768000  # USD per square mile

# Plot type variable
plot_type = tk.StringVar(value="bar")  # Default to bar plot

def format_large_num(x):
    """Convert large numbers to readable format (e.g., 1M, 1K)"""
    if x >= 1e6:
        return f"{x/1e6:,.1f}M"
    elif x >= 1e3:
        return f"{x/1e3:,.0f}K"
    return f"{x:,.0f}"

def parse_input_data(data_str):
    try:
        return ast.literal_eval(data_str)
    except Exception as e:
        messagebox.showerror("Data Error", f"Invalid data format:\n{e}")
        return []

def calculate_equilibrium_year(initial_emission, reduction_rate):
    """Calculate the year when CO2 production equals consumption"""
    # With 1% annual growth and linear reduction
    # We need to solve: initial_emission * (1 + 0.01)^years - reduction_rate * years = 0
    # This is a non-linear equation, so we'll solve it iteratively
    
    year = 0
    current_emission = initial_emission
    total_reduction = 0
    
    while current_emission > total_reduction and year < 200:  # Set a reasonable upper limit
        year += 1
        current_emission *= (1 + ANNUAL_EMISSION_INCREASE)  # 1% annual increase
        total_reduction += reduction_rate
        
        if current_emission <= total_reduction:
            return year + 2025  # Add to base year
    
    return "Beyond 2225"  # If equilibrium is not reached within 200 years

def compute_and_plot():
    global canvas

    try:
        # Parse input data
        countries = parse_input_data(country_input.get("1.0", tk.END).strip())
        land_area = np.array(parse_input_data(land_input.get("1.0", tk.END).strip()))
        emissions = np.array(parse_input_data(emission_input.get("1.0", tk.END).strip()))
        years_offset = parse_input_data(years_input.get("1.0", tk.END).strip())
        gdp = np.array(parse_input_data(gdp_input.get("1.0", tk.END).strip()))
        
        # Get user input for percent land and GDP
        percent_land_available = float(percent_land_input.get())
        gdp_percent_available = float(gdp_percent_input.get())

        if not (len(countries) == len(land_area) == len(emissions) == len(gdp)):
            messagebox.showerror("Data Error", "All input lists must have the same length.")
            return

        if len(years_offset) != 2:
            messagebox.showerror("Data Error", "Year offset must contain exactly two values (start and end years).")
            return

        start_year, end_year = years_offset
        n_years_offset = end_year - start_year
        if n_years_offset <= 0:
            messagebox.showerror("Data Error", "End year must be greater than start year.")
            return
            
        # Calculations
        bamboo_area_needed = emissions / sequestration_rate
        # Use reference years (REFERENCE_YEARS_OFFSET) for bamboo area calculations
        bamboo_area_needed_annually = bamboo_area_needed / REFERENCE_YEARS_OFFSET
        percent_land = (bamboo_area_needed / land_area) * 100
        planting_cost = bamboo_area_needed_annually * cost_planting_bamboo

        # Calculate GDP Percentage
        gdp_percentage = (planting_cost / gdp) * 100
        
        # Calculate land availability and cost constraints
        available_land = land_area * (percent_land_available / 100)
        affordable_cost = gdp * (gdp_percent_available / 100)
        affordable_bamboo_area = affordable_cost / cost_planting_bamboo
        
        # Calculate reduction rates based on available land and budget
        land_constrained_reduction = available_land * sequestration_rate
        budget_constrained_reduction = affordable_bamboo_area * sequestration_rate * REFERENCE_YEARS_OFFSET
        
        # Use the minimum constraint (either land or budget)
        actual_reduction_rates = np.minimum(land_constrained_reduction, budget_constrained_reduction) / REFERENCE_YEARS_OFFSET
        
        # Calculate equilibrium years
        equilibrium_years = [calculate_equilibrium_year(emission, reduction) 
                            for emission, reduction in zip(emissions, actual_reduction_rates)]

        # Clear previous plot
        ax.clear()

        # Select plot type based on radio button
        if plot_type.get() == "bar":
            # Original bar plot
            plot_bar_chart(countries, land_area, bamboo_area_needed_annually, planting_cost, 
                          percent_land, gdp_percentage, start_year, end_year, available_land, 
                          affordable_bamboo_area)
        else:
            # New time series plot with 1% annual emission increase
            plot_time_series(countries, emissions, start_year, end_year, actual_reduction_rates)

        # Draw canvas
        if canvas:
            canvas.draw()
        else:
            canvas = FigureCanvasTkAgg(fig, master=left_panel)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            canvas.draw()

        # Update data summary and calculations
        update_summary(countries, emissions, land_area, bamboo_area_needed_annually, 
                      planting_cost, percent_land, gdp_percentage, start_year, end_year,
                      percent_land_available, gdp_percent_available, available_land,
                      affordable_bamboo_area, actual_reduction_rates, equilibrium_years)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def plot_bar_chart(countries, land_area, bamboo_area_needed_annually, planting_cost, 
                  percent_land, gdp_percentage, start_year, end_year, available_land,
                  affordable_bamboo_area):
    """Draw the original bar chart visualization with constraints"""
    # Plot setup
    sns.set_style("whitegrid")
    plt.rcParams['mathtext.fontset'] = 'cm'
    palette = sns.color_palette("rocket", n_colors=5)  # Added more colors for new bars
    bar_width = 0.18  # Narrower to accommodate more bars
    x = np.arange(len(countries))

    # Plot bars
    bars_land = ax.bar(x - 2*bar_width, land_area, width=bar_width,
                       color=palette[0], alpha=0.9, edgecolor='black',
                       label='Actual Land Area')
    bars_bamboo = ax.bar(x - bar_width, bamboo_area_needed_annually, width=bar_width,
                         color=palette[1], alpha=0.9, edgecolor='black',
                         label='Annual Bamboo Area Needed')
    bars_cost = ax.bar(x, planting_cost, width=bar_width,
                       color=palette[2], alpha=0.9, edgecolor='black',
                       label='Annual Planting Cost (USD)')
    # New bars for constraints
    bars_available_land = ax.bar(x + bar_width, available_land / REFERENCE_YEARS_OFFSET, width=bar_width,
                               color=palette[3], alpha=0.9, edgecolor='black',
                               label='Available Land (Annual)')
    bars_affordable = ax.bar(x + 2*bar_width, affordable_bamboo_area, width=bar_width,
                           color=palette[4], alpha=0.9, edgecolor='black',
                           label='Affordable Bamboo Area (Annual)')

    # Add rotated labels BELOW each bar with explicit units
    for i, (land, bamboo, cost, percent, gdp_pct, avail_land, afford) in enumerate(
            zip(land_area, bamboo_area_needed_annually, planting_cost, percent_land, 
                gdp_percentage, available_land / REFERENCE_YEARS_OFFSET, affordable_bamboo_area)):
        
        ax.text(x[i] - 2*bar_width, 1, 
                f"{format_large_num(land)}\nsq mi", 
                ha='center', va='top', fontsize=8, fontweight='bold', rotation=45, transform=ax.get_xaxis_transform())

        ax.text(x[i] - bar_width, 1, 
                f"{format_large_num(bamboo)}\nsq mi/yr", 
                ha='center', va='top', fontsize=8, fontweight='bold', rotation=45, transform=ax.get_xaxis_transform())

        ax.text(x[i], 1, 
                f"${format_large_num(cost)}\n$/yr", 
                ha='center', va='top', fontsize=8, fontweight='bold', rotation=45, transform=ax.get_xaxis_transform())
                
        ax.text(x[i] + bar_width, 1, 
                f"{format_large_num(avail_land)}\nsq mi/yr", 
                ha='center', va='top', fontsize=8, fontweight='bold', rotation=45, transform=ax.get_xaxis_transform())
                
        ax.text(x[i] + 2*bar_width, 1, 
                f"{format_large_num(afford)}\nsq mi/yr", 
                ha='center', va='top', fontsize=8, fontweight='bold', rotation=45, transform=ax.get_xaxis_transform())

        ax.text(x[i], 0.95, 
                f"{gdp_pct:.2f}% of GDP", 
                ha='center', va='top', fontsize=8, fontweight='bold', color='red',
                rotation=45, transform=ax.get_xaxis_transform())

    # Aesthetics
    ax.set_title(f"National Land vs. Bamboo Area Needed and Constraints\nOffset CO2 Emissions from {start_year} to {end_year}", 
                 fontsize=16, pad=20, fontweight='bold')
    ax.set_xlabel("Country", fontsize=14, labelpad=10)
    ax.set_ylabel("Annual Area / Cost (sq mi / USD) [Log Scale]", fontsize=14, labelpad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(countries, fontsize=12)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_large_num(x)))
    ax.grid(True, which="both", ls="--", alpha=0.2)

    # Legend
    legend_elements = [
        Patch(facecolor=palette[0], label='Actual Land Area', edgecolor='black'),
        Patch(facecolor=palette[1], label='Annual Bamboo Area Needed', edgecolor='black'),
        Patch(facecolor=palette[2], label='Annual Planting Cost (USD)', edgecolor='black'),
        Patch(facecolor=palette[3], label='Available Land (Annual)', edgecolor='black'),
        Patch(facecolor=palette[4], label='Affordable Bamboo Area (Annual)', edgecolor='black'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

    # Watermark
    ax.text(0.1, 0.7, 'BHCC 2025', fontsize=20, color='gray', alpha=0.5,
            ha='center', va='center', rotation=45, transform=ax.transAxes)

def plot_time_series(countries, emissions, start_year, end_year, actual_reduction_rates):
    """Draw a time series plot showing emission reduction over time with 1% annual increase"""
    # Plot setup
    sns.set_style("whitegrid")
    plt.rcParams['mathtext.fontset'] = 'cm'
    palette = sns.color_palette("rocket", n_colors=len(countries))
    
    # Create year range for plot
    years = np.arange(start_year, end_year + 1)
    
    # For each country, create a line that shows both emissions growth and reduction
    for i, (country, initial_emission, reduction_rate) in enumerate(zip(countries, emissions, actual_reduction_rates)):
        # Calculate emissions for each year with 1% annual increase and reduction
        yearly_emissions = []
        yearly_reductions = []
        cumulative_reduction = 0
        
        for year_idx, year in enumerate(years):
            # Calculate emission with 1% annual growth
            years_passed = year - start_year
            grown_emission = initial_emission * ((1 + ANNUAL_EMISSION_INCREASE) ** years_passed)
            
            # Calculate reduction (linear)
            annual_reduction = reduction_rate
            cumulative_reduction += annual_reduction
            
            # Net emission
            net_emission = max(0, grown_emission - cumulative_reduction)
            yearly_emissions.append(net_emission)
            yearly_reductions.append(cumulative_reduction)
        
        # Plot emissions line
        ax.plot(years, yearly_emissions, marker='o', markersize=4, 
                linewidth=3, color=palette[i], label=f"{country} (Net Emissions)")
        
        # Plot reduction line as dashed
        ax.plot(years, yearly_reductions, linestyle='--', linewidth=2, 
                color=palette[i], alpha=0.7, label=f"{country} (Cumulative Reduction)")
        
        # Find intersection point (if any) - when emissions equal reductions
        for y_idx in range(1, len(years)):
            if yearly_emissions[y_idx] <= yearly_reductions[y_idx]:
                # Mark the equilibrium point
                eq_year = years[y_idx]
                eq_value = yearly_emissions[y_idx]
                ax.scatter([eq_year], [eq_value], s=100, color=palette[i], 
                          edgecolor='black', zorder=10, marker='*')
                ax.annotate(f"Equilibrium\n{eq_year}", 
                           xy=(eq_year, eq_value),
                           xytext=(10, 10),
                           textcoords='offset points',
                           fontsize=10,
                           fontweight='bold',
                           color=palette[i],
                           arrowprops=dict(arrowstyle="->", color=palette[i]))
                break
    
    # Aesthetics
    ax.set_title(f"CO2 Emissions vs. Reduction Over Time ({start_year}-{end_year})\nWith 1% Annual Emission Growth", 
                fontsize=16, pad=20, fontweight='bold')
    ax.set_xlabel("Year", fontsize=14, labelpad=10)
    ax.set_ylabel("CO2 (tons/year)", fontsize=14, labelpad=10)
    ax.set_yscale("log")  # Log scale for better visualization
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_large_num(x)))
    ax.grid(True, which="both", ls="--", alpha=0.2)
    
    # Add annotations for starting points
    for i, (country, emission) in enumerate(zip(countries, emissions)):
        # Annotate starting point
        ax.annotate(f"{country}: {format_large_num(emission)} tons",
                   xy=(start_year, emission),
                   xytext=(5, 5),
                   textcoords='offset points',
                   fontsize=10,
                   fontweight='bold',
                   color=palette[i])
    
    # Legend with smaller font and better position
    ax.legend(loc='upper right', fontsize=9, ncol=2)
    
    # Watermark
    ax.text(0.1, 0.7, 'BHCC 2025', fontsize=20, color='gray', alpha=0.5,
            ha='center', va='center', rotation=45, transform=ax.transAxes)

def update_summary(countries, emissions, land_area, bamboo_area_needed_annually, 
                  planting_cost, percent_land, gdp_percentage, start_year, end_year,
                  percent_land_available, gdp_percent_available, available_land,
                  affordable_bamboo_area, actual_reduction_rates, equilibrium_years):
    """Update the text summary panel with calculation details"""
    summary_text = f"Calculation Overview:\n\n"
    summary_text += f"Initial Data:\n"
    for i in range(len(countries)):
        summary_text += f"• {countries[i]}: {emissions[i]:,.0f} tons CO2/yr\n"
    
    summary_text += f"\nConstraints:\n"
    summary_text += f"• Available Land: {percent_land_available:.1f}% of total land\n"
    summary_text += f"• Available GDP: {gdp_percent_available:.2f}% of GDP\n"
    
    summary_text += f"\nConversion (Bamboo Absorption):\n"
    summary_text += f"• 25 tons CO2/acre/yr * 640 acres/sq mi = 16,000 tons CO2/sq mi/yr\n"
    
    summary_text += f"\nGeneral Formulas:\n"
    summary_text += f"• Bamboo Area = CO2 Emissions / 16,000 tons CO2/sq mi/yr\n"
    summary_text += f"• Bamboo Area Annually = Bamboo Area / {REFERENCE_YEARS_OFFSET} years (fixed reference period)\n"
    summary_text += f"• Land % = Bamboo Area / Land Area * 100\n"
    summary_text += f"• Annual Planting Cost = Bamboo Area Annually * ${cost_planting_bamboo:,.0f} per sq mi\n"
    summary_text += f"• GDP % = Annual Planting Cost / GDP * 100\n"
    summary_text += f"• Annual Emission Growth: 1% compound growth\n"
    
    if plot_type.get() == "time":
        summary_text += f"\nTime Series Plot Details:\n"
        summary_text += f"• Shows emissions vs. reductions from {start_year} to {end_year}\n"
        summary_text += f"• Emissions grow at 1% annually\n"
        summary_text += f"• Reductions are constrained by available land and GDP\n"
        summary_text += f"• Stars on plot indicate equilibrium points (when production = consumption)\n"
    
    summary_text += f"\nDetailed Calculations for Each Country:\n"

    for i in range(len(countries)):
        bamboo_area = bamboo_area_needed_annually[i]
        cost = planting_cost[i]
        percent_of_land = percent_land[i]
        gdp_pct = gdp_percentage[i]
        avail_land = available_land[i] / REFERENCE_YEARS_OFFSET
        afford_area = affordable_bamboo_area[i]
        reduction_rate = actual_reduction_rates[i]
        eq_year = equilibrium_years[i]
        
        constrained_by = "land" if avail_land < afford_area else "budget"
        
        summary_text += f"\n{countries[i]}:\n"
        summary_text += f"  • Annual Bamboo Area Needed (Ideal): {format_large_num(bamboo_area)} sq mi/yr\n"
        summary_text += f"  • Available Annual Land: {format_large_num(avail_land)} sq mi/yr\n"
        summary_text += f"  • Affordable Annual Area: {format_large_num(afford_area)} sq mi/yr\n"
        summary_text += f"  • Constrained by: {constrained_by.upper()}\n"
        summary_text += f"  • Annual Planting Cost: ${format_large_num(cost)}\n"
        summary_text += f"  • Percent of Total Land Required: {percent_of_land:.2f}%\n"
        summary_text += f"  • GDP Percentage Required: {gdp_pct:.2f}%\n"
        summary_text += f"  • Actual CO2 Reduction Rate: {format_large_num(reduction_rate)} tons/yr\n"
        summary_text += f"  • Equilibrium Year (consumption = production): {eq_year}\n"

    summary_label.config(text=summary_text)

def save_plot():
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png")])
    if file_path:
        fig.savefig(file_path)
        messagebox.showinfo("Saved", f"Plot saved to:\n{file_path}")

def exit_app():
    root.destroy()

# Layout
top_frame = tk.Frame(root, bg="#e6f0ff", padx=10, pady=5)
top_frame.pack(fill=tk.X)
tk.Label(top_frame, text="🌿 Bamboo CO2 Offset Calculator", bg="#e6f0ff", font=("Arial", 28, "bold")).pack(side=tk.LEFT)

control_frame = tk.Frame(root, pady=10)
control_frame.pack(fill=tk.X)

# Input fields
tk.Label(control_frame, text="Enter Countries (as Python list):", font=("Arial", 16)).pack(anchor="w", padx=10)
country_input = tk.Text(control_frame, height=2, font=("Courier", 14), wrap=tk.NONE)
country_input.insert(tk.END, str(default_countries))
country_input.pack(fill=tk.X, padx=10)

tk.Label(control_frame, text="Enter Land Areas (sq mi) (as Python list):", font=("Arial", 16)).pack(anchor="w", padx=10)
land_input = tk.Text(control_frame, height=2, font=("Courier", 14), wrap=tk.NONE)
land_input.insert(tk.END, str(default_land_area))
land_input.pack(fill=tk.X, padx=10)

tk.Label(control_frame, text="Enter Annual CO2 Emissions (tons) (as Python list):", font=("Arial", 16)).pack(anchor="w", padx=10)
emission_input = tk.Text(control_frame, height=2, font=("Courier", 14), wrap=tk.NONE)
emission_input.insert(tk.END, str(default_emissions))
emission_input.pack(fill=tk.X, padx=10)

tk.Label(control_frame, text="Enter GDP per Country (USD) (as Python list):", font=("Arial", 16)).pack(anchor="w", padx=10)
gdp_input = tk.Text(control_frame, height=2, font=("Courier", 14), wrap=tk.NONE)
gdp_input.insert(tk.END, str(default_gdp_per_country))
gdp_input.pack(fill=tk.X, padx=10)

tk.Label(control_frame, text="Enter CO2 Offset Years (Start, End):", font=("Arial", 16)).pack(anchor="w", padx=10)
years_input = tk.Text(control_frame, height=2, font=("Courier", 14), wrap=tk.NONE)
years_input.insert(tk.END, str(default_years_offset))
years_input.pack(fill=tk.X, padx=10)

# New sliders for percent_land and gdp_percentage
constraint_frame = tk.Frame(control_frame)
constraint_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

# Percent land available slider
tk.Label(constraint_frame, text="Available Land (% of total):", font=("Arial", 16)).grid(row=0, column=0, sticky="w")
percent_land_input = tk.Scale(constraint_frame, from_=0.1, to=30.0, resolution=0.1, orient=tk.HORIZONTAL, 
                             length=300, font=("Arial", 12))
percent_land_input.set(default_percent_land)
percent_land_input.grid(row=0, column=1, padx=10)

# GDP percentage slider
tk.Label(constraint_frame, text="Available GDP (%):", font=("Arial", 16)).grid(row=1, column=0, sticky="w")
gdp_percent_input = tk.Scale(constraint_frame, from_=0.01, to=5.0, resolution=0.01, orient=tk.HORIZONTAL, 
                            length=300, font=("Arial", 12))
gdp_percent_input.set(default_gdp_percentage)
gdp_percent_input.grid(row=1, column=1, padx=10)

# Plot type selection
plot_type_frame = tk.Frame(control_frame)
plot_type_frame.pack(anchor="w", padx=10, pady=(10, 0))
tk.Label(plot_type_frame, text="Select Plot Type:", font=("Arial", 16)).pack(side=tk.LEFT)
tk.Radiobutton(plot_type_frame, text="Bar Chart (Constraints)", variable=plot_type, value="bar", font=("Arial", 14)).pack(side=tk.LEFT, padx=(20, 10))
tk.Radiobutton(plot_type_frame, text="Time Series (Equilibrium Years)", variable=plot_type, value="time", font=("Arial", 14)).pack(side=tk.LEFT, padx=10)

# Buttons
btn_frame = tk.Frame(control_frame)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="🔍 Analyze", command=compute_and_plot, font=("Arial", 16), bg="#007acc", fg="white").pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="💾 Save Plot", command=save_plot, font=("Arial", 16), bg="#28a745", fg="white").pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="❌ Exit", command=exit_app, font=("Arial", 16), bg="#cc0000", fg="white").pack(side=tk.LEFT, padx=10)

# Main Panels
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

left_panel = tk.Frame(main_frame)
left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right_panel = tk.Frame(main_frame, bg="#f0f6ff", width=820, padx=30)
right_panel.pack(side=tk.RIGHT, fill=tk.Y)
right_panel.pack_propagate(0)

tk.Label(right_panel, text="📊 Calculation Steps", font=("Helvetica", 24, "bold"), bg="#f0f6ff", fg="#003366").pack(pady=(5, 2))
summary_label = tk.Label(right_panel, text="", bg="#f0f6ff", justify="left", font=("Courier", 14), anchor="nw")
summary_label.pack(pady=(0, 10), fill=tk.X)

# Initialize with default values
compute_and_plot()

# Ensure full shutdown when window is closed
root.protocol("WM_DELETE_WINDOW", exit_app)

# Run main loop
root.mainloop()