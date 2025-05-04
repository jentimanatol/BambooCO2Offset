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
root.title("🌿 Bamboo CO₂ Offset Calculator")
root.geometry("2500x1750")

# Matplotlib figure and axis
fig, ax = plt.subplots(figsize=(10, 6))
canvas = None

# Default data
default_countries = ["Jamaica", "Madagascar", "Vietnam"]
default_land_area = [4244, 228531, 127932]  # in sq mi
default_emissions = [6083040, 4099000, 327905620]  # in tons CO₂/yr

# Sequestration rate: 25 tons CO₂ per acre per year
# Convert to per square mile: 25 * 640 = 16,000 tons CO₂/sq mi/yr
sequestration_rate = 16000  # tons CO₂/sq mi/yr

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

        if not (len(countries) == len(land_area) == len(emissions)):
            messagebox.showerror("Data Error", "All input lists must have the same length.")
            return

        # Calculations
        bamboo_area_needed = emissions / sequestration_rate
        percent_land = (bamboo_area_needed / land_area) * 100

        # Clear previous plot
        ax.clear()

        # Plot setup
        sns.set_style("whitegrid")
        plt.rcParams['mathtext.fontset'] = 'cm'
        palette = sns.color_palette("rocket", n_colors=2)
        bar_width = 0.35
        x = np.arange(len(countries))

        # Plot bars
        bars_land = ax.bar(x - bar_width/2, land_area, width=bar_width,
                           color=palette[0], alpha=0.9, edgecolor='black',
                           label='Actual Land Area')
        bars_bamboo = ax.bar(x + bar_width/2, bamboo_area_needed, width=bar_width,
                             color=palette[1], alpha=0.9, edgecolor='black',
                             label='Bamboo Area Needed')

        # Annotations
        for i, (land, bamboo, percent) in enumerate(zip(land_area, bamboo_area_needed, percent_land)):
            ax.text(x[i] - bar_width/2, land * 1.05, 
                    f"{format_large_num(land)} sq mi", 
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax.text(x[i] + bar_width/2, bamboo * 1.05, 
                    f"{format_large_num(bamboo)} sq mi\n({percent:.2f}% of land)", 
                    ha='center', va='bottom', fontsize=10, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

        # Aesthetics
        ax.set_title("National Land vs. Bamboo Needed for 100% CO₂ Offset\n(Best-Case: 16,000 t/sq mi/yr)", 
                     fontsize=16, pad=20, fontweight='bold')
        ax.set_xlabel("Country", fontsize=14, labelpad=10)
        ax.set_ylabel("Area (sq mi) [Log Scale]", fontsize=14, labelpad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(countries, fontsize=12)
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_large_num(x)))
        ax.grid(True, which="both", ls="--", alpha=0.2)

        # Legend
        legend_elements = [
            Patch(facecolor=palette[0], label='Actual Land Area', edgecolor='black'),
            Patch(facecolor=palette[1], label='Bamboo Area Needed', edgecolor='black'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=11)

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

        # Update data summary
        summary_text = "Country\tLand Area (sq mi)\tEmissions (tons CO₂/yr)\tBamboo Area Needed (sq mi)\t% of Land\n"
        for i in range(len(countries)):
            summary_text += f"{countries[i]}\t{land_area[i]:,.0f}\t{emissions[i]:,.0f}\t{bamboo_area_needed[i]:,.2f}\t{percent_land[i]:.2f}%\n"
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

# Input fields
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

tk.Label(right_panel, text="📊 Data Summary", font=("Helvetica", 24, "bold"), bg="#f0f6ff", fg="#003366").pack(pady=(5, 2))
summary_label = tk.Label(right_panel, text="", bg="#f0f6ff", justify="left", font=("Courier", 14), anchor="nw")
summary_label.pack(pady=(0, 10), fill=tk.X)

# Run main loop
root.mainloop()
