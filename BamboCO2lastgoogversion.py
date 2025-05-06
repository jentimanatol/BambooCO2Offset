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

# Default data
default_countries = ["Jamaica", "Madagascar", "Vietnam"]
default_land_area = [4244, 228531, 127932]  # in sq mi
default_emissions = [6083040, 4099000, 327905620]  # in tons CO2/yr
gdp_per_country = np.array([15_000_000_000, 14_000_000_000, 700_000_000_000])  # GDP in USD
default_years_offset = [2025, 2099]  # Default years for CO2 offset

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

def compute_and_plot():
    global canvas

    try:
        # Parse input data
        countries = parse_input_data(country_input.get("1.0", tk.END).strip())
        land_area = np.array(parse_input_data(land_input.get("1.0", tk.END).strip()))
        emissions = np.array(parse_input_data(emission_input.get("1.0", tk.END).strip()))
        years_offset = parse_input_data(years_input.get("1.0", tk.END).strip())
        gdp = np.array(parse_input_data(gdp_input.get("1.0", tk.END).strip()))

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
            
        # Always use reference period (2025-2099) for calculations to maintain consistency
        reference_years_offset = 75
        
        # Calculations
        bamboo_area_needed = emissions / sequestration_rate
        # Use reference years (2025-2099) for bamboo area calculations regardless of displayed years
        bamboo_area_needed_annually = bamboo_area_needed / reference_years_offset
        percent_land = (bamboo_area_needed / land_area) * 100
        planting_cost = bamboo_area_needed_annually * cost_planting_bamboo

        # Calculate GDP Percentage
        gdp_percentage = (planting_cost / gdp) * 100

        # Clear previous plot
        ax.clear()

        # Select plot type based on radio button
        if plot_type.get() == "bar":
            # Original bar plot
            plot_bar_chart(countries, land_area, bamboo_area_needed_annually, planting_cost, percent_land, gdp_percentage, start_year, end_year)
        else:
            # New time series plot
            plot_time_series(countries, emissions, start_year, end_year)

        # Draw canvas
        if canvas:
            canvas.draw()
        else:
            canvas = FigureCanvasTkAgg(fig, master=left_panel)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            canvas.draw()

        # Update data summary and calculations
        update_summary(countries, emissions, land_area, bamboo_area_needed_annually, 
                       planting_cost, percent_land, gdp_percentage, start_year, end_year)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def plot_bar_chart(countries, land_area, bamboo_area_needed_annually, planting_cost, percent_land, gdp_percentage, start_year, end_year):
    """Draw the original bar chart visualization"""
    # Plot setup
    sns.set_style("whitegrid")
    plt.rcParams['mathtext.fontset'] = 'cm'
    palette = sns.color_palette("rocket", n_colors=3)
    bar_width = 0.25
    x = np.arange(len(countries))

    # Plot bars
    bars_land = ax.bar(x - bar_width, land_area, width=bar_width,
                       color=palette[0], alpha=0.9, edgecolor='black',
                       label='Actual Land Area')
    bars_bamboo = ax.bar(x, bamboo_area_needed_annually, width=bar_width,
                         color=palette[1], alpha=0.9, edgecolor='black',
                         label='Annual Bamboo Area Needed')
    bars_cost = ax.bar(x + bar_width, planting_cost, width=bar_width,
                       color=palette[2], alpha=0.9, edgecolor='black',
                       label='Annual Planting Cost (USD)')

    # Add rotated labels BELOW each bar with explicit units
    for i, (land, bamboo, cost, percent, gdp_pct) in enumerate(zip(land_area, bamboo_area_needed_annually, planting_cost, percent_land, gdp_percentage)):
        ax.text(x[i] - bar_width, 1, 
                f"{format_large_num(land)}\nsq mi", 
                ha='center', va='top', fontsize=10, fontweight='bold', rotation=45, transform=ax.get_xaxis_transform())

        ax.text(x[i], 1, 
                f"{format_large_num(bamboo)}\nsq mi/yr (bamboo)", 
                ha='center', va='top', fontsize=10, fontweight='bold', rotation=45, transform=ax.get_xaxis_transform())

        ax.text(x[i] + bar_width, 1, 
                f"${format_large_num(cost)}\n$/yr", 
                ha='center', va='top', fontsize=10, fontweight='bold', rotation=45, transform=ax.get_xaxis_transform())

        ax.text(x[i] + bar_width, 0.95, 
                f"{gdp_pct:.2f}% of GDP", 
                ha='center', va='top', fontsize=10, fontweight='bold', color='red',
                rotation=45, transform=ax.get_xaxis_transform())

    # Aesthetics
    ax.set_title(f"National Land vs. Bamboo Area Needed Annually and Planting Cost\nOffset CO2 Emissions from {start_year} to {end_year}", 
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
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11)

    # Watermark
    ax.text(0.1, 0.7, 'BHCC 2025', fontsize=20, color='gray', alpha=0.5,
            ha='center', va='center', rotation=45, transform=ax.transAxes)

def plot_time_series(countries, emissions, start_year, end_year):
    """Draw a time series plot showing emission reduction over time"""
    # Plot setup
    sns.set_style("whitegrid")
    plt.rcParams['mathtext.fontset'] = 'cm'
    palette = sns.color_palette("rocket", n_colors=len(countries))
    
    # Create year range for actual plot (from start_year to end_year)
    years = np.arange(start_year, end_year + 1)
    n_years = end_year - start_year
    
    # Calculate reduction rates (how much emissions decrease per year)
    annual_reduction_rates = emissions / (2099 - 2025)  # Always calculate based on 2025-2099 reference
    
    # For each country, create a line that decreases based on the original calculation rate
    for i, (country, initial_emission, reduction_rate) in enumerate(zip(countries, emissions, annual_reduction_rates)):
        # Calculate emissions for each year using the constant reduction rate
        yearly_emissions = []
        for year in years:
            years_passed = year - 2025  # Years since reference start (2025)
            remaining_emission = max(0, initial_emission - (reduction_rate * years_passed))
            yearly_emissions.append(remaining_emission)
        
        ax.plot(years, yearly_emissions, marker='o', markersize=5, 
                linewidth=3, color=palette[i], label=country)
    
    # Aesthetics
    ax.set_title(f"CO2 Emissions Reduction Over Time ({start_year}-{end_year})\nBased on 2025-2099 Reduction Rate", 
                fontsize=16, pad=20, fontweight='bold')
    ax.set_xlabel("Year", fontsize=14, labelpad=10)
    ax.set_ylabel("CO2 Emissions (tons/year)", fontsize=14, labelpad=10)
    ax.set_yscale("log")  # Log scale for better visualization of different magnitudes
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_large_num(x)))
    ax.grid(True, which="both", ls="--", alpha=0.2)
    
    # Add annotations for starting points and final points if visible
    for i, (country, emission, reduction_rate) in enumerate(zip(countries, emissions, annual_reduction_rates)):
        # Annotate starting point
        ax.annotate(f"{country}: {format_large_num(emission)} tons",
                   xy=(start_year, emission),
                   xytext=(5, 5),
                   textcoords='offset points',
                   fontsize=12,
                   fontweight='bold',
                   color=palette[i])
        
        # Calculate end emission for the visible time period
        end_years_passed = end_year - 2025
        end_emission = max(0, emission - (reduction_rate * end_years_passed))
        
        # Annotate end point if it's significantly different from zero
        if end_emission > emission * 0.05:  # Only if more than 5% of initial remains
            ax.annotate(f"{format_large_num(end_emission)} tons",
                       xy=(end_year, end_emission),
                       xytext=(-5, 5),
                       textcoords='offset points',
                       fontsize=12,
                       fontweight='bold',
                       ha='right',
                       color=palette[i])
    
    # Legend
    ax.legend(loc='upper right', fontsize=12)
    
    # Watermark
    ax.text(0.1, 0.7, 'BHCC 2025', fontsize=20, color='gray', alpha=0.5,
            ha='center', va='center', rotation=45, transform=ax.transAxes)

def update_summary(countries, emissions, land_area, bamboo_area_needed_annually, 
                  planting_cost, percent_land, gdp_percentage, start_year, end_year):
    """Update the text summary panel with calculation details"""
    # Always use 2025-2099 as reference for calculations to maintain consistency
    reference_years_offset = 2099 - 2025
    n_years_offset = end_year - start_year
    
    summary_text = f"Calculation Overview:\n\n"
    summary_text += f"Initial Data:\n"
    for i in range(len(countries)):
        summary_text += f"• {countries[i]}: {emissions[i]:,.0f} tons CO2/yr\n"
    summary_text += f"\nConversion (Bamboo Absorption):\n"
    summary_text += f"• 25 tons CO2/acre/yr * 640 acres/sq mi = 16,000 tons CO2/sq mi/yr\n"
    summary_text += f"\nGeneral Formulas:\n"
    summary_text += f"• Bamboo Area = CO2 Emissions / 16,000 tons CO2/sq mi/yr\n"
    summary_text += f"• Bamboo Area Annually = Bamboo Area / {reference_years_offset} years (2025-2099)\n"
    summary_text += f"• Land % = Bamboo Area / Land Area * 100\n"
    summary_text += f"• Annual Planting Cost = Bamboo Area Annually * ${cost_planting_bamboo:,.0f} per sq mi\n"
    summary_text += f"• GDP % = Annual Planting Cost / GDP * 100\n"
    
    if plot_type.get() == "time":
        summary_text += f"\nTime Series Plot Details:\n"
        summary_text += f"• Shows emissions decrease from {start_year} to {end_year}\n"
        summary_text += f"• Uses consistent reduction rate based on 2025-2099 timeline\n"
        summary_text += f"• Annual reduction rates are consistent regardless of displayed years\n"
        summary_text += f"• Complete offset would be achieved by 2099 at this reduction rate\n"
    
    summary_text += f"\nDetailed Calculations for Each Country:\n"

    for i in range(len(countries)):
        bamboo_area = bamboo_area_needed_annually[i]
        cost = planting_cost[i]
        percent_of_land = percent_land[i]
        gdp_pct = gdp_percentage[i]
        # Calculate reduction rate based on reference period (2025-2099)
        reduction_rate = emissions[i] / reference_years_offset
        
        summary_text += f"\n{countries[i]}:\n"
        summary_text += f"  • Annual Bamboo Area Needed = {format_large_num(bamboo_area)} sq mi/yr\n"
        summary_text += f"  • Annual Planting Cost = ${format_large_num(cost)}\n"
        summary_text += f"  • Percent of Total Land = {percent_of_land:.2f}%\n"
        summary_text += f"  • GDP Percentage = {gdp_pct:.2f}%\n"
        summary_text += f"  • Emissions Reduction Rate = {format_large_num(reduction_rate)} tons CO2/yr\n"
        
        # Calculate how much will be reduced within the displayed time period
        visible_reduction = min(emissions[i], reduction_rate * n_years_offset)
        remaining_emission = max(0, emissions[i] - visible_reduction)
        percent_reduced = (visible_reduction / emissions[i]) * 100
        
        summary_text += f"  • By {end_year}: {format_large_num(visible_reduction)} tons reduced ({percent_reduced:.1f}%)\n"
        if remaining_emission > 0:
            summary_text += f"  • Remaining after {end_year}: {format_large_num(remaining_emission)} tons\n"

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
gdp_input.insert(tk.END, str(gdp_per_country.tolist()))
gdp_input.pack(fill=tk.X, padx=10)

tk.Label(control_frame, text="Enter CO2 Offset Years (Start, End):", font=("Arial", 16)).pack(anchor="w", padx=10)
years_input = tk.Text(control_frame, height=2, font=("Courier", 14), wrap=tk.NONE)
years_input.insert(tk.END, str(default_years_offset))
years_input.pack(fill=tk.X, padx=10)

# Plot type selection
plot_type_frame = tk.Frame(control_frame)
plot_type_frame.pack(anchor="w", padx=10, pady=(10, 0))
tk.Label(plot_type_frame, text="Select Plot Type:", font=("Arial", 16)).pack(side=tk.LEFT)
tk.Radiobutton(plot_type_frame, text="Bar Chart (Original)", variable=plot_type, value="bar", font=("Arial", 14)).pack(side=tk.LEFT, padx=(20, 10))
tk.Radiobutton(plot_type_frame, text="Time Series (CO2 Reduction Over Time)", variable=plot_type, value="time", font=("Arial", 14)).pack(side=tk.LEFT, padx=10)

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

# Ensure full shutdown when window is closed
root.protocol("WM_DELETE_WINDOW", exit_app)

# Run main loop
root.mainloop()