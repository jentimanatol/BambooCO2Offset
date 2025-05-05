import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import ast
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

root = tk.Tk()
root.title("🌿 Bamboo CO2 Offset Calculator By AJ")
root.geometry("2500x1750")

fig, ax = plt.subplots(figsize=(10, 6))
canvas = None

default_countries = ["Jamaica", "Madagascar", "Vietnam"]
default_land_area = [4244, 228531, 127932]
default_emissions = [6083040, 4099000, 327905620]
gdp_per_country = np.array([15_000_000_000, 14_000_000_000, 700_000_000_000])
default_years_offset = [2025, 2099]

sequestration_rate = 16000
cost_planting_bamboo = 768000

plot_type = tk.StringVar(value="bar")

def format_large_num(x):
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
            
        reference_years_offset = 2099 - 2025
        
        bamboo_area_needed = emissions / sequestration_rate
        bamboo_area_needed_annually = bamboo_area_needed / reference_years_offset
        percent_land = (bamboo_area_needed / land_area) * 100
        planting_cost = bamboo_area_needed_annually * cost_planting_bamboo

        gdp_percentage = (planting_cost / gdp) * 100

        ax.clear()

        if plot_type.get() == "bar":
            plot_bar_chart(countries, land_area, bamboo_area_needed_annually, planting_cost, percent_land, gdp_percentage, start_year, end_year)
        else:
            plot_time_series(countries, emissions, start_year, end_year)

        if canvas:
            canvas.draw()
        else:
            canvas = FigureCanvasTkAgg(fig, master=left_panel)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            canvas.draw()

        update_summary(countries, emissions, land_area, bamboo_area_needed_annually, 
                       planting_cost, percent_land, gdp_percentage, start_year, end_year)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def plot_bar_chart(countries, land_area, bamboo_area_needed_annually, planting_cost, percent_land, gdp_percentage, start_year, end_year):
    sns.set_style("whitegrid")
    plt.rcParams['mathtext.fontset'] = 'cm'
    palette = sns.color_palette("rocket", n_colors=3)
    bar_width = 0.25
    x = np.arange(len(countries))

    bars_land = ax.bar(x - bar_width, land_area, width=bar_width,
                       color=palette[0], alpha=0.9, edgecolor='black',
                       label='Actual Land Area')
    bars_bamboo = ax.bar(x, bamboo_area_needed_annually, width=bar_width,
                         color=palette[1], alpha=0.9, edgecolor='black',
                         label='Annual Bamboo Area Needed')
    bars_cost = ax.bar(x + bar_width, planting_cost, width=bar_width,
                       color=palette[2], alpha=0.9, edgecolor='black',
                       label='Annual Planting Cost (USD)')

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

    ax.set_title(f"National Land vs. Bamboo Area Needed Annually and Planting Cost\nOffset CO2 Emissions from {start_year} to {end_year}", 
                 fontsize=16, pad=20, fontweight='bold')
    ax.set_xlabel("Country", fontsize=14, labelpad=10)
    ax.set_ylabel("Annual Area / Cost (sq mi / USD) [Log Scale]", fontsize=14, labelpad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(countries, fontsize=12)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_large_num(x)))
    ax.grid(True, which="both", ls="--", alpha=0.2)

    legend_elements = [
        Patch(facecolor=palette[0], label='Actual Land Area', edgecolor='black'),
        Patch(facecolor=palette[1], label='Annual Bamboo Area Needed', edgecolor='black'),
        Patch(facecolor=palette[2], label='Annual Planting Cost (USD)', edgecolor='black'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11)

    ax.text(0.1, 0.7, 'BHCC 2025', fontsize=20, color='gray', alpha=0.5,
            ha='center', va='center', rotation=45, transform=ax.transAxes)

def plot_time_series(countries, emissions, start_year, end_year):
    sns.set_style("whitegrid")
    plt.rcParams['mathtext.fontset'] = 'cm'
    palette = sns.color_palette("rocket", n_colors=len(countries))
    
    years = np.arange(start_year, end_year + 1)
    n_years = end_year - start_year
    
    annual_growth_rate = 0.01
    
    bamboo_sequestration_rates = emissions / (2099 - 2025)
    
    for i, (country, initial_emission, sequestration_rate) in enumerate(zip(countries, emissions, bamboo_sequestration_rates)):
        yearly_emissions = []
        yearly_raw_emissions = []
        yearly_sequestration = []
        
        peak_year = None
        peak_emission = 0
        
        for j, year in enumerate(years):
            years_passed = year - 2025
            
            raw_emission = initial_emission * ((1 + annual_growth_rate) ** years_passed)
            bamboo_effect = sequestration_rate * years_passed
            net_emission = max(0, raw_emission - bamboo_effect)
            
            yearly_raw_emissions.append(raw_emission)
            yearly_sequestration.append(bamboo_effect)
            yearly_emissions.append(net_emission)
            
            if j > 0 and yearly_emissions[j] < yearly_emissions[j-1] and peak_year is None:
                peak_year = year
                peak_emission = yearly_emissions[j-1]
        
        ax.plot(years, yearly_emissions, marker='o', markersize=5, 
                linewidth=3, color=palette[i], label=f"{country} (Net Emissions)")
        
        ax.plot(years, yearly_raw_emissions, linestyle='--', linewidth=2, 
                color=palette[i], alpha=0.6, label=f"{country} (Raw Emissions)")
        
        ax.plot(years, yearly_sequestration, linestyle='-.', linewidth=2,
                color=palette[i], alpha=0.4, label=f"{country} (Bamboo Sequestration)")
        
        if peak_year is not None and peak_year <= end_year:
            ax.annotate(f"Peak: {peak_year}",
                      xy=(peak_year, peak_emission),
                      xytext=(10, 10),
                      textcoords='offset points',
                      fontsize=12,
                      fontweight='bold',
                      color=palette[i],
                      arrowprops=dict(arrowstyle="->", color=palette[i]))
    
    ax.set_title(f"CO2 Emissions Reduction Over Time ({start_year}-{end_year})\nWith 1% Annual Emission Growth", 
                fontsize=16, pad=20, fontweight='bold')
    ax.set_xlabel("Year", fontsize=14, labelpad=10)
    ax.set_ylabel("CO2 (tons/year)", fontsize=14, labelpad=10)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_large_num(x)))
    ax.grid(True, which="both", ls="--", alpha=0.2)
    
    for i, (country, emission) in enumerate(zip(countries, emissions)):
        ax.annotate(f"{country}: {format_large_num(emission)} tons",
                   xy=(start_year, emission),
                   xytext=(5, 5),
                   textcoords='offset points',
                   fontsize=12,
                   fontweight='bold',
                   color=palette[i])
    
    handles, labels = ax.get_legend_handles_labels()
    by_country = {}
    for h, l in zip(handles, labels):
        country = l.split(' (')[0]
        if country not in by_country:
            by_country[country] = []
        by_country[country].append((h, l.split(' (')[1][:-1]))
    
    new_handles = []
    new_labels = []
    for country, items in by_country.items():
        for h, label_type in items:
            new_handles.append(h)
            new_labels.append(f"{country}: {label_type}")
    
    ax.legend(new_handles, new_labels, loc='upper left', fontsize=10)
    
    ax.text(0.1, 0.7, 'BHCC 2025', fontsize=20, color='gray', alpha=0.5,
            ha='center', va='center', rotation=45, transform=ax.transAxes)

def calculate_peak_years(countries, emissions):
    annual_growth_rate = 0.01
    
    bamboo_sequestration_rates = emissions / (2099 - 2025)
    
    peak_data = []
    
    for i, (country, initial_emission, sequestration_rate) in enumerate(zip(countries, emissions, bamboo_sequestration_rates)):
        growth_factor = initial_emission * annual_growth_rate
        if growth_factor <= 0:
            peak_year = 2025
        else:
            try:
                t = np.log(sequestration_rate / growth_factor) / np.log(1 + annual_growth_rate)
                peak_year = 2025 + max(0, int(np.ceil(t)))
            except:
                peak_year = "Beyond 2200"
        
        if isinstance(peak_year, int):
            years_passed = peak_year - 2025
            raw_emission = initial_emission * ((1 + annual_growth_rate) ** years_passed)
            bamboo_effect = sequestration_rate * years_passed
            peak_emission = raw_emission - bamboo_effect
        else:
            peak_emission = "N/A"
            
        peak_data.append((country, peak_year, peak_emission))
    
    return peak_data

def update_summary(countries, emissions, land_area, bamboo_area_needed_annually, 
                  planting_cost, percent_land, gdp_percentage, start_year, end_year):
    reference_years_offset = 2099 - 2025
    n_years_offset = end_year - start_year
    
    peak_data = calculate_peak_years(countries, emissions)
    
    summary_text = f"Calculation Overview:\n\n"
    summary_text += f"Initial Data:\n"
    for i in range(len(countries)):
        summary_text += f"• {countries[i]}: {emissions[i]:,.0f} tons CO2/yr (with 1% annual growth)\n"
    summary_text += f"\nConversion (Bamboo Absorption):\n"
    summary_text += f"• 25 tons CO2/acre/yr * 640 acres/sq mi = 16,000 tons CO2/sq mi/yr\n"
    summary_text += f"\nEmission Peak Years (when bamboo sequestration exceeds 1% growth):\n"
    for country, peak_year, peak_emission in peak_data:
        if isinstance(peak_year, int) and isinstance(peak_emission, (int, float)):
            summary_text += f"• {country}: Year {peak_year} at {format_large_num(peak_emission)} tons CO2/yr\n"
        else:
            summary_text += f"• {country}: {peak_year}\n"
    
    summary_text += f"\nGeneral Formulas:\n"
    summary_text += f"• Annual Emission Growth: Previous year emissions * 1.01\n"
    summary_text += f"• Bamboo Area = CO2 Emissions / 16,000 tons CO2/sq mi/yr\n"
    summary_text += f"• Bamboo Area Annually = Bamboo Area / {reference_years_offset} years (2025-2099)\n"
    summary_text += f"• Land % = Bamboo Area / Land Area * 100\n"
    summary_text += f"• Annual Planting Cost = Bamboo Area Annually * ${cost_planting_bamboo:,.0f} per sq mi\n"
    summary_text += f"• GDP % = Annual Planting Cost / GDP * 100\n"
    
    if plot_type.get() == "time":
        summary_text += f"\nTime Series Plot Details:\n"
        summary_text += f"• Shows emissions with 1% annual growth from {start_year} to {end_year}\n"
        summary_text += f"• Dotted lines show raw emissions growth without bamboo effect\n"
        summary_text += f"• Solid lines show net emissions (raw emissions minus bamboo sequestration)\n"
        summary_text += f"• Peak points show when bamboo sequestration exceeds emission growth\n"
    
    summary_text += f"\nDetailed Calculations for Each Country:\n"

    for i in range(len(countries)):
        bamboo_area = bamboo_area_needed_annually[i]
        cost = planting_cost[i]
        percent_of_land = percent_land[i]
        gdp_pct = gdp_percentage[i]
        sequestration_rate = emissions[i] / reference_years_offset
        
        summary_text += f"\n{countries[i]}:\n"
        summary_text += f"  • Annual Bamboo Area Needed = {format_large_num(bamboo_area)} sq mi/yr\n"
        summary_text += f"  • Annual Planting Cost = ${format_large_num(cost)}\n"
        summary_text += f"  • Percent of Total Land = {percent_of_land:.2f}%\n"
        summary_text += f"  • GDP Percentage = {gdp_pct:.2f}%\n"
        summary_text += f"  • Bamboo Sequestration Rate = {format_large_num(sequestration_rate)} tons CO2/yr\n"
        summary_text += f"  • Initial Annual Emission Growth = {format_large_num(emissions[i] * 0.01)} tons CO2/yr\n"
        
        country_peak = next((p for p in peak_data if p[0] == countries[i]), None)
        if country_peak:
            peak_year, peak_emission = country_peak[1], country_peak[2]
            if isinstance(peak_year, int) and isinstance(peak_emission, (int, float)):
                if peak_year <= end_year:
                    summary_text += f"  • Emissions peak in {peak_year} at {format_large_num(peak_emission)} tons CO2/yr\n"
                else:
                    summary_text += f"  • Emissions will peak beyond displayed years (in {peak_year})\n"
            else:
                summary_text += f"  • Emissions continue to rise beyond calculation period\n"

    summary_label.config(text=summary_text)

def save_plot():
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png")])
    if file_path:
        fig.savefig(file_path)
        messagebox.showinfo("Saved", f"Plot saved to:\n{file_path}")

def exit_app():
    root.destroy()

top_frame = tk.Frame(root, bg="#e6f0ff", padx=10, pady=5)
top_frame.pack(fill=tk.X)
tk.Label(top_frame, text="🌿 Bamboo CO2 Offset Calculator", bg="#e6f0ff", font=("Arial", 28, "bold")).pack(side=tk.LEFT)

control_frame = tk.Frame(root, pady=10)
control_frame.pack(fill=tk.X)

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

plot_type_frame = tk.Frame(control_frame)
plot_type_frame.pack(anchor="w", padx=10, pady=(10, 0))
tk.Label(plot_type_frame, text="Select Plot Type:", font=("Arial", 16)).pack(side=tk.LEFT)
tk.Radiobutton(plot_type_frame, text="Bar Chart (Original)", variable=plot_type, value="bar", font=("Arial", 14)).pack(side=tk.LEFT, padx=(20, 10))
tk.Radiobutton(plot_type_frame, text="Time Series (CO2 Reduction Over Time)", variable=plot_type, value="time", font=("Arial", 14)).pack(side=tk.LEFT, padx=10)

btn_frame = tk.Frame(control_frame)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="🔍 Analyze", command=compute_and_plot, font=("Arial", 16), bg="#007acc", fg="white").pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="💾 Save Plot", command=save_plot, font=("Arial", 16), bg="#28a745", fg="white").pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="❌ Exit", command=exit_app, font=("Arial", 16), bg="#cc0000", fg="white").pack(side=tk.LEFT, padx=10)

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

root.protocol("WM_DELETE_WINDOW", exit_app)

root.mainloop()