import tkinter as tk
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import ast
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

# Initialize main window
root = tk.Tk()
root.title("🌿 Bamboo CO₂ Offset Calculator By AJ")
root.geometry("2500x1750")  # Same size as before

# Matplotlib figure and axis
fig, ax = plt.subplots(figsize=(10, 6))
canvas = None

# Default data (same as your old app)
default_countries = ["Jamaica", "Madagascar", "Vietnam"]
default_land_area = [4244, 228531, 127932]  # in sq mi
default_emissions = [6083040, 4099000, 327905620]  # in tons CO₂/yr
gdp_per_country = np.array([15_000_000_000, 14_000_000_000, 700_000_000_000])  # GDP in USD
default_years_offset = [2025, 2099]  # Default years for CO2 offset

# Sequestration rate: 25 tons CO₂ per acre per year (converted to square miles)
sequestration_rate = 16000  # tons CO₂/sq mi/yr

# Cost to plant bamboo (USD per square mile)
cost_planting_bamboo = 768000  # USD per square mile

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

        # Calculations
        bamboo_area_needed = emissions / sequestration_rate
        bamboo_area_needed_annually = bamboo_area_needed / n_years_offset
        percent_land = (bamboo_area_needed / land_area) * 100
        planting_cost = bamboo_area_needed_annually * cost_planting_bamboo

        # Calculate GDP Percentage
        gdp_percentage = (planting_cost / gdp) * 100

        # Clear previous plot
        ax.clear()

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

        # Annotations with text at the bottom of each bar at 45-degree rotation


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



        # for i, (land, bamboo, cost, percent, gdp_pct) in enumerate(zip(land_area, bamboo_area_needed_annually, planting_cost, percent_land, gdp_percentage)):
        #     ax.text(x[i] - bar_width, -land * 0.05, 
        #             f"{format_large_num(land)} sq mi", 
        #             ha='center', va='top', fontsize=10, fontweight='bold', rotation=45)
        #     ax.text(x[i], -bamboo * 0.05, 
        #             f"{format_large_num(bamboo)} sq mi/yr\n({percent:.2f}% of land)", 
        #             ha='center', va='top', fontsize=10, fontweight='bold',
        #             bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'), rotation=45)
        #     ax.text(x[i] + bar_width, -cost * 0.05, 
        #             f"${format_large_num(cost)}", 
        #             ha='center', va='top', fontsize=10, fontweight='bold',
        #             bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'), rotation=45)
        #     ax.text(x[i] + bar_width, -cost * 0.10, 
        #             f"{gdp_pct:.2f}% of GDP", 
        #             ha='center', va='top', fontsize=10, fontweight='bold',
        #             color='red', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'), rotation=45)






        # Aesthetics
        ax.set_title(f"National Land vs. Bamboo Area Needed Annually and Planting Cost\nOffset CO₂ Emissions from {start_year} to {end_year}", 
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

        # Draw canvas
        if canvas:
            canvas.draw()
        else:
            canvas = FigureCanvasTkAgg(fig, master=left_panel)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            canvas.draw()

        # Update data summary and calculations
        summary_text = f"Calculation Overview:\n\n"
        summary_text += f"Initial Data:\n"
        for i in range(len(countries)):
            summary_text += f"• {countries[i]}: {emissions[i]:,.0f} tons CO₂/yr\n"
        summary_text += f"\nConversion (Bamboo Absorption):\n"
        summary_text += f"• 25 tons CO₂/acre/yr × 640 acres/sq mi = 16,000 tons CO₂/sq mi/yr\n"
        summary_text += f"\nGeneral Formulas:\n"
        summary_text += f"• Bamboo Area = CO₂ Emissions / 16,000 tons CO₂/sq mi/yr\n"
        summary_text += f"• Bamboo Area Annually = Bamboo Area / n_years_offset\n"
        summary_text += f"• Land % = Bamboo Area / Land Area × 100\n"
        summary_text += f"• Annual Planting Cost = Bamboo Area Annually × ${cost_planting_bamboo:,.0f} per sq mi\n"
        summary_text += f"• GDP % = Annual Planting Cost / GDP × 100\n"
        summary_text += f"\nDetailed Calculations for Each Country:\n"

        for i in range(len(countries)):
            bamboo_area = bamboo_area_needed_annually[i]
            cost = planting_cost[i]
            percent_of_land = percent_land[i]
            gdp_pct = gdp_percentage[i]
            summary_text += f"\n{countries[i]}:\n"
            summary_text += f"  • Annual Bamboo Area Needed = {format_large_num(bamboo_area)} sq mi/yr\n"
            summary_text += f"  • Annual Planting Cost = ${format_large_num(cost)}\n"
            summary_text += f"  • Percent of Total Land = {percent_of_land:.2f}%\n"
            summary_text += f"  • GDP Percentage = {gdp_pct:.2f}%\n"

        summary_label.config(text=summary_text)

    except Exception as e:
        messagebox.showerror("Error", str(e))

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
tk.Label(top_frame, text="🌿 Bamboo CO₂ Offset Calculator", bg="#e6f0ff", font=("Arial", 28, "bold")).pack(side=tk.LEFT)

control_frame = tk.Frame(root, pady=10)
control_frame.pack(fill=tk.X)

# Input fields (same as old app)
tk.Label(control_frame, text="Enter Countries (as Python list):", font=("Arial", 16)).pack(anchor="w", padx=10)
country_input = tk.Text(control_frame, height=2, font=("Courier", 14), wrap=tk.NONE)
country_input.insert(tk.END, str(default_countries))
country_input.pack(fill=tk.X, padx=10)

tk.Label(control_frame, text="Enter Land Areas (sq mi) (as Python list):", font=("Arial", 16)).pack(anchor="w", padx=10)
land_input = tk.Text(control_frame, height=2, font=("Courier", 14), wrap=tk.NONE)
land_input.insert(tk.END, str(default_land_area))
land_input.pack(fill=tk.X, padx=10)

tk.Label(control_frame, text="Enter Annual CO₂ Emissions (tons) (as Python list):", font=("Arial", 16)).pack(anchor="w", padx=10)
emission_input = tk.Text(control_frame, height=2, font=("Courier", 14), wrap=tk.NONE)
emission_input.insert(tk.END, str(default_emissions))
emission_input.pack(fill=tk.X, padx=10)

tk.Label(control_frame, text="Enter GDP per Country (USD) (as Python list):", font=("Arial", 16)).pack(anchor="w", padx=10)
gdp_input = tk.Text(control_frame, height=2, font=("Courier", 14), wrap=tk.NONE)
gdp_input.insert(tk.END, str(gdp_per_country.tolist()))
gdp_input.pack(fill=tk.X, padx=10)

tk.Label(control_frame, text="Enter CO₂ Offset Years (Start, End):", font=("Arial", 16)).pack(anchor="w", padx=10)
years_input = tk.Text(control_frame, height=2, font=("Courier", 14), wrap=tk.NONE)
years_input.insert(tk.END, str(default_years_offset))
years_input.pack(fill=tk.X, padx=10)

# Buttons (same style and position)
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

# Run main loop
#root.mainloop()

# Ensure full shutdown when window is closed
root.protocol("WM_DELETE_WINDOW", exit_app)

root.mainloop()
