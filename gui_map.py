import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import pandas as pd
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("svg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cartopy.crs as ccrs
from ttkthemes import ThemedTk
from tkinter import ttk


class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Geospatial Data Plotter")
        self.master.geometry(f"{self.master.winfo_screenwidth() - 200}x{self.master.winfo_screenheight() - 200}")
        self.master.configure(bg='#2e2e2e')
        self.pack(fill=tk.BOTH, expand=True)
        self.preload_shapefile()  # Preload the shapefile
        self.create_widgets_initial()
        self.fig = None
        self.dot_color = '#FF0000'  # Default dot color
        self.fill_color = '#00FF00'  # Default fill color for countries
        self.color_scheme = 'viridis_r'  # Default color scheme for choropleth

    def preload_shapefile(self):
        self.shapefile_path = "_internal/ne_10m_admin_0_countries.shp"  # Path to the preloaded shapefile
        self.geo_data = gpd.read_file(self.shapefile_path)
        self.geo_data = self.geo_data.to_crs(epsg=3035)
        # Ensure geometries are valid
        self.geo_data = self.geo_data[self.geo_data.is_valid]
        print("Shapefile loaded.")

    def create_widgets_initial(self):
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 12), padding=10)
        style.configure('TLabel', font=('Helvetica', 12), padding=10)
        style.configure('TCheckbutton', font=('Helvetica', 12), padding=10)
        style.configure('TSeparator', background='#808080')  # Change to a darker gray

        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.separator = ttk.Separator(self, orient='vertical', style='TSeparator')
        self.separator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=(10, 10))

        self.select_file_button = ttk.Button(self.left_frame, text="Select Datafile", command=self.select_file)
        self.select_file_button.pack(pady=10)

        self.header_var = tk.BooleanVar()
        self.header_check = ttk.Checkbutton(self.left_frame, text="First row is header", variable=self.header_var)
        self.header_check.pack(pady=10)

        self.plot_type_var = tk.StringVar(value='choropleth')
        self.plot_type_frame = ttk.Frame(self.left_frame)
        self.plot_type_frame.pack(pady=10)
        self.choropleth_radio = ttk.Radiobutton(self.plot_type_frame, text="Choropleth", variable=self.plot_type_var, value='choropleth', command=self.update_plot_type)
        self.choropleth_radio.pack(side=tk.LEFT, padx=5)
        self.point_radio = ttk.Radiobutton(self.plot_type_frame, text="Point Plot", variable=self.plot_type_var, value='point', command=self.update_plot_type)
        self.point_radio.pack(side=tk.LEFT, padx=5)

        self.load_file_button = ttk.Button(self.left_frame, text="Load file", command=self.load_file)
        self.load_file_button.pack(pady=10)
        self.load_file_button.pack_forget()  # Hide initially

        self.upload_shapefile_button = ttk.Button(self.left_frame, text="Upload Shapefile", command=self.upload_shapefile)
        self.upload_shapefile_button.pack(pady=10)

        self.reset_plot_frame = ttk.Frame(self.left_frame)
        self.reset_button = ttk.Button(self.reset_plot_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        self.plot_button = ttk.Button(self.reset_plot_frame, text="PLOT", command=self.plot, state='disabled')
        self.plot_button.pack(side=tk.LEFT, padx=5)
        self.save_button = ttk.Button(self.reset_plot_frame, text="Save to Disk", command=self.save_to_disk, state='disabled')
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.reset_plot_frame.pack(side=tk.BOTTOM, pady=10)  # Pack at bottom initially

        self.map_frame = ttk.Frame(self)
        self.map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_widgets_after_file_load(self):
        self.column_selection_frame = ttk.Frame(self.left_frame)
        self.column_selection_frame.pack(pady=10)

        self.country_code_label = ttk.Label(self.column_selection_frame, text="Select Datafile Code Column:")
        self.country_code_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.country_code_var = tk.StringVar(self)
        self.country_code_var.set(self.columns[0])
        self.country_code_menu = ttk.OptionMenu(self.column_selection_frame, self.country_code_var, self.columns[0], *self.columns)
        self.country_code_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.shapefile_code_label = ttk.Label(self.column_selection_frame, text="Select Shapefile Code Column:")
        self.shapefile_code_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.shapefile_code_var = tk.StringVar(self)
        self.shapefile_code_var.set(self.geo_data.columns[0])
        self.shapefile_code_menu = ttk.OptionMenu(self.column_selection_frame, self.shapefile_code_var, self.geo_data.columns[0], *self.geo_data.columns)
        self.shapefile_code_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.var_label = ttk.Label(self.column_selection_frame, text="Select Variable Column:")
        self.var_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.var_var = tk.StringVar(self)
        self.var_var.set(self.columns[0])
        self.var_menu = ttk.OptionMenu(self.column_selection_frame, self.var_var, self.columns[0], *self.columns)
        self.var_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.color_scheme_label = ttk.Label(self.column_selection_frame, text="Select Color Scheme:")
        self.color_scheme_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.color_scheme_var = tk.StringVar(self)
        self.color_scheme_var.set(self.color_scheme)
        # Create the color scheme dropdown
        self.color_scheme_menu = ttk.OptionMenu(self.column_selection_frame, self.color_scheme_var, 'viridis_r', 'viridis', 'plasma', 'inferno', 'magma', 'cividis')
        self.color_scheme_menu.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.lat_label = ttk.Label(self.column_selection_frame, text="Select Latitude Column:")
        self.lat_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.lat_var = tk.StringVar(self)
        self.lat_var.set(self.columns[0])
        self.lat_menu = ttk.OptionMenu(self.column_selection_frame, self.lat_var, self.columns[0], *self.columns)
        self.lat_menu.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        self.lon_label = ttk.Label(self.column_selection_frame, text="Select Longitude Column:")
        self.lon_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        self.lon_var = tk.StringVar(self)
        self.lon_var.set(self.columns[0])
        self.lon_menu = ttk.OptionMenu(self.column_selection_frame, self.lon_var, self.columns[0], *self.columns)
        self.lon_menu.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        self.dot_size_color_frame = ttk.Frame(self.left_frame)
        self.dot_size_color_frame.pack(pady=10)

        self.dot_size_label = ttk.Label(self.dot_size_color_frame, text="Dot Size:")
        self.dot_size_label.pack(side=tk.LEFT, padx=5)
        self.dot_size_slider = ttk.Scale(self.dot_size_color_frame, from_=1, to=20, orient=tk.HORIZONTAL)
        self.dot_size_slider.pack(side=tk.LEFT, padx=5)
        self.dot_size_slider.set(5)  # Default dot size

        self.color_button = ttk.Button(self.dot_size_color_frame, text="Select Dot Color", command=self.choose_dot_color)
        self.color_button.pack(side=tk.LEFT, padx=5)

        self.fill_countries_frame = ttk.Frame(self.left_frame)
        self.fill_countries_var = tk.BooleanVar()
        self.fill_countries_check = ttk.Checkbutton(self.fill_countries_frame, text="Fill Countries", variable=self.fill_countries_var)
        self.fill_countries_check.pack(side=tk.LEFT, padx=5)
        
        self.color_fill_button = ttk.Button(self.fill_countries_frame, text="Select Fill Color", command=self.choose_fill_color)
        self.color_fill_button.pack(side=tk.LEFT, padx=5)
        self.fill_countries_frame.pack(pady=10)

        self.size_based_var = tk.BooleanVar()
        self.size_based_check = ttk.Checkbutton(self.dot_size_color_frame, text="Size of points based on column", variable=self.size_based_var, command=self.toggle_size_based_column)
        self.size_based_check.pack(side=tk.LEFT, padx=5)
        self.size_based_column_var = tk.StringVar(self)
        self.size_based_column_menu = ttk.OptionMenu(self.dot_size_color_frame, self.size_based_column_var, self.columns[0], *self.columns)
        self.size_based_column_menu.pack(side=tk.LEFT, padx=5)

        self.update_plot_type()  # Ensure the correct widgets are shown based on plot type

    def toggle_size_based_column(self):
        if self.size_based_var.get():
            self.size_based_column_menu.pack(side=tk.LEFT, padx=5)
        else:
            self.size_based_column_menu.pack_forget()

    def update_plot_type(self):
        if self.plot_type_var.get() == 'choropleth':
            self.lat_label.grid_remove()
            self.lat_menu.grid_remove()
            self.lon_label.grid_remove()
            self.lon_menu.grid_remove()
            self.dot_size_color_frame.pack_forget()
            self.fill_countries_frame.pack_forget()
            self.size_based_check.pack_forget()
            self.size_based_column_menu.pack_forget()

            self.country_code_label.grid()
            self.country_code_menu.grid()
            self.shapefile_code_label.grid()
            self.shapefile_code_menu.grid()
            self.var_label.grid()
            self.var_menu.grid()
            self.color_scheme_label.grid()
            self.color_scheme_menu.grid()
        elif self.plot_type_var.get() == 'point':
            self.lat_label.grid()
            self.lat_menu.grid()
            self.lon_label.grid()
            self.lon_menu.grid()
            self.dot_size_color_frame.pack(pady=10)
            self.fill_countries_frame.pack(pady=10)
            self.size_based_check.pack(side=tk.LEFT, padx=5)
            self.toggle_size_based_column()

            self.country_code_label.grid_remove()
            self.country_code_menu.grid_remove()
            self.shapefile_code_label.grid_remove()
            self.shapefile_code_menu.grid_remove()
            self.var_label.grid_remove()
            self.var_menu.grid_remove()
            self.color_scheme_label.grid_remove()
            self.color_scheme_menu.grid_remove()

    def choose_dot_color(self):
        color_code = colorchooser.askcolor(title="Choose Dot Color")
        if color_code[1] is not None:
            self.dot_color = color_code[1]

    def choose_fill_color(self):
        color_code = colorchooser.askcolor(title="Choose Fill Color")
        if color_code[1] is not None:
            self.fill_color = color_code[1]

    def select_file(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[
                ("All supported files", "*.csv;*.xls;*.xlsx;*.tsv"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xls;*.xlsx"),
                ("TSV files", "*.tsv")
            ]
        )
        if self.file_path:
            self.select_file_button.state(['disabled'])
            self.header_check.state(['!disabled'])
            self.load_file_button.pack(pady=10)  # Show the load file button


    def load_file(self):
        file_extension = self.file_path.split('.')[-1].lower()
        if file_extension == 'csv':
            self.data = pd.read_csv(self.file_path, header=0 if self.header_var.get() else None)
        elif file_extension in ['xls', 'xlsx']:
            self.data = pd.read_excel(self.file_path, header=0 if self.header_var.get() else None)
        elif file_extension == 'tsv':
            self.data = pd.read_csv(self.file_path, sep='\t', header=0 if self.header_var.get() else None)
        else:
            messagebox.showerror("File Error", "Unsupported file format!")
            return
        
        self.columns = self.data.columns.tolist()
        self.header_check.state(['disabled'])
        self.load_file_button.pack_forget()  # Hide the load file button after loading
        self.upload_shapefile_button.pack_forget()  # Hide the upload shapefile button after loading

        self.create_widgets_after_file_load()

        # Hide the initial elements
        self.select_file_button.pack_forget()
        self.header_check.pack_forget()
        self.plot_type_frame.pack_forget()

        # Enable plot and save buttons
        self.plot_button.state(['!disabled'])
        self.save_button.state(['!disabled'])

    def upload_shapefile(self):
        self.shapefile_path = filedialog.askopenfilename(
            filetypes=[
                ("Shapefiles", "*.shp"),
                ("All files", "*.*")
            ]
        )
        if self.shapefile_path:
            self.geo_data = gpd.read_file(self.shapefile_path)
            self.geo_data = self.geo_data.to_crs(epsg=3035)
            self.geo_data = self.geo_data[self.geo_data.is_valid]
            print("Uploaded shapefile loaded.")

    def plot(self):
        proj = ccrs.LambertAzimuthalEqualArea(central_longitude=10, central_latitude=52, false_easting=4321000, false_northing=3210000)

        self.fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': proj})
        ax.set_extent([-20, 45, 30, 75], crs=ccrs.PlateCarree())  # Set extent to focus on Europe

        # Plot the base map with borders
        self.geo_data.boundary.plot(ax=ax, linewidth=1, edgecolor='black')

        plot_type = self.plot_type_var.get()
        if plot_type == 'choropleth':
            # Plot the data overlay for choropleth
            merged_data = self.geo_data.set_index(self.shapefile_code_var.get()).join(self.data.set_index(self.country_code_var.get()))
            merged_data.plot(column=self.var_var.get(), ax=ax, legend=False, cmap=self.color_scheme_var.get(), edgecolor='black', missing_kwds={"color": "lightgrey"})
        elif plot_type == 'point':
            # Plot the data overlay for point plot
            for index, row in self.data.iterrows():
                lat = row[self.lat_var.get()]
                lon = row[self.lon_var.get()]
                size = self.dot_size_slider.get()
                if self.size_based_var.get():
                    size = row[self.size_based_column_var.get()] / self.data[self.size_based_column_var.get()].max() * 20
                ax.plot(lon, lat, 'o', color=self.dot_color, markersize=size, transform=ccrs.PlateCarree())

            if self.fill_countries_var.get():
                self.geo_data['filled'] = False
                for index, row in self.data.iterrows():
                    lat = row[self.lat_var.get()]
                    lon = row[self.lon_var.get()]
                    point = gpd.GeoSeries([gpd.points_from_xy([lon], [lat])[0]], crs="EPSG:4326").to_crs(epsg=3035)
                    countries_containing_point = self.geo_data[self.geo_data.contains(point[0])]
                    if not countries_containing_point.empty:
                        self.geo_data.loc[countries_containing_point.index, 'filled'] = True
                self.geo_data[self.geo_data['filled']].plot(ax=ax, color=self.fill_color, edgecolor='black')
                self.geo_data[~self.geo_data['filled']].plot(ax=ax, color='none', edgecolor='black')

        ax.coastlines(resolution='50m')
        #ax.gridlines(draw_labels=True)

        ax.spines['geo'].set_visible(False)  # Remove the rectangle border

        for widget in self.map_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(self.fig, master=self.map_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.save_button.state(['!disabled'])

    def save_to_disk(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG files", "*.svg")])
        if file_path:
            proj = ccrs.LambertAzimuthalEqualArea(central_longitude=10, central_latitude=52, false_easting=4321000, false_northing=3210000)

            high_res_fig, high_res_ax = plt.subplots(figsize=(20, 20), subplot_kw={'projection': proj})
            high_res_ax.set_extent([-20, 45, 30, 75], crs=ccrs.PlateCarree())  # Set extent to focus on Europe

            # Plot the base map with borders
            self.geo_data.boundary.plot(ax=high_res_ax, linewidth=1, edgecolor='black')

            plot_type = self.plot_type_var.get()
            if plot_type == 'choropleth':
                # Plot the data overlay for choropleth
                merged_data = self.geo_data.set_index(self.shapefile_code_var.get()).join(self.data.set_index(self.country_code_var.get()))
                merged_data.plot(column=self.var_var.get(), ax=high_res_ax, cmap=self.color_scheme_var.get(), edgecolor='black', missing_kwds={"color": "lightgrey"})
            elif plot_type == 'point':
                # Scale the dot size to match the figure size ratio
                scale_factor = 20 / 10  # High-res figure size / low-res figure size
                for index, row in self.data.iterrows():
                    lat = row[self.lat_var.get()]
                    lon = row[self.lon_var.get()]
                    size = self.dot_size_slider.get() * scale_factor
                    if self.size_based_var.get():
                        size = row[self.size_based_column_var.get()] / self.data[self.size_based_column_var.get()].max() * 20 * scale_factor
                    high_res_ax.plot(lon, lat, 'o', color=self.dot_color, markersize=size, transform=ccrs.PlateCarree())

                if self.fill_countries_var.get():
                    self.geo_data['filled'] = False
                    for index, row in self.data.iterrows():
                        lat = row[self.lat_var.get()]
                        lon = row[self.lon_var.get()]
                        point = gpd.GeoSeries([gpd.points_from_xy([lon], [lat])[0]], crs="EPSG:4326").to_crs(epsg=3035)
                        countries_containing_point = self.geo_data[self.geo_data.contains(point[0])]
                        if not countries_containing_point.empty:
                            self.geo_data.loc[countries_containing_point.index, 'filled'] = True
                    self.geo_data[self.geo_data['filled']].plot(ax=high_res_ax, color=self.fill_color, edgecolor='black')
                    self.geo_data[~self.geo_data['filled']].plot(ax=high_res_ax, color='none', edgecolor='black')

            high_res_ax.coastlines(resolution='10m')
            #high_res_ax.gridlines(draw_labels=True)
            high_res_ax.spines['geo'].set_visible(False)  # Remove the rectangle border

            high_res_fig.savefig(file_path, format='svg')
            plt.close(high_res_fig)
            messagebox.showinfo("Save to Disk", f"Map saved as {file_path}")

    def reset(self):
        self.select_file_button.state(['!disabled'])
        self.header_check.state(['disabled'])
        self.load_file_button.pack_forget()  # Hide the load file button
        self.plot_button.state(['disabled'])
        self.save_button.state(['disabled'])

        self.preload_shapefile()  # Reset to default shapefile

        # Destroy only the dynamically created widgets
        for widget in self.left_frame.winfo_children():
            if widget not in {self.select_file_button, self.header_check, self.plot_type_frame, self.load_file_button, self.reset_plot_frame, self.upload_shapefile_button}:
                widget.destroy()
        for widget in self.map_frame.winfo_children():
            widget.destroy()

        # Reset to initial UI
        self.select_file_button.pack(pady=10)
        self.header_check.pack(pady=10)
        self.plot_type_frame.pack(pady=10)
        self.upload_shapefile_button.pack(pady=10)  # Show the upload shapefile button
        # Note: Load file button is not packed here; it will be shown after file selection

        # Hide the reset plot frame until needed
        self.reset_plot_frame.pack_forget()

        # Re-pack the reset_plot_frame to the bottom
        self.reset_plot_frame.pack(side=tk.BOTTOM, pady=10)


root = ThemedTk(theme="equilux")
root.set_theme("equilux")

app = Application(master=root)
app.mainloop()

while True:
    wait = input("Press q to quit: ")
    if wait.lower() == 'q':
        break

