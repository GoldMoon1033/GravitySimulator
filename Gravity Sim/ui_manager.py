"""
UI Manager module for handling user interface controls.
Provides property editing panel using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import threading
from celestial_body import CelestialBody
from utils import rgb_to_hex, hex_to_rgb
from constants import *

class UIManager:
    """
    Manages the UI control panel for the simulation.
    """
    
    def __init__(self, physics_engine, renderer):
        """
        Initialize the UI manager.
        
        Args:
            physics_engine (PhysicsEngine): Physics engine instance
            renderer (Renderer): Renderer instance
        """
        self.physics_engine = physics_engine
        self.renderer = renderer
        self.selected_body = None
        self.root = None
        self.property_vars = {}
        self.lock_vars = {}
        
        # Default values for new bodies
        self.default_mass = DEFAULT_MASS
        self.default_radius = DEFAULT_RADIUS
        self.default_density = DEFAULT_DENSITY
        self.default_vx = 0
        self.default_vy = 0
        self.default_color = "#FFFFFF"
    
    def create_panel(self):
        """Create the control panel window."""
        self.root = tk.Tk()
        self.root.title("Gravity Simulator Controls")
        self.root.geometry("400x800")
        self.root.resizable(False, True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_object_tab(notebook)
        self.create_simulation_tab(notebook)
        self.create_visual_tab(notebook)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Ready", 
                                    bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_object_tab(self, parent):
        """Create the object properties tab."""
        tab = ttk.Frame(parent)
        parent.add(tab, text="Object Properties")
        
        # Selected object info
        info_frame = tk.LabelFrame(tab, text="Selected Object", padx=10, pady=10)
        info_frame.pack(fill='x', padx=5, pady=5)
        
        self.selected_label = tk.Label(info_frame, text="No object selected")
        self.selected_label.pack()
        
        # Properties frame
        props_frame = tk.LabelFrame(tab, text="Properties", padx=10, pady=10)
        props_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create property controls
        properties = [
            ("Mass (kg)", "mass", MIN_MASS, MAX_MASS, "scientific"),
            ("Radius (px)", "radius", MIN_RADIUS, MAX_RADIUS, "normal"),
            ("Density (kg/m³)", "density", MIN_DENSITY, MAX_DENSITY, "normal"),
            ("Velocity X (m/s)", "vx", -1000, 1000, "normal"),
            ("Velocity Y (m/s)", "vy", -1000, 1000, "normal"),
        ]
        
        for i, (label, prop, min_val, max_val, notation) in enumerate(properties):
            # Label
            tk.Label(props_frame, text=label).grid(row=i*2, column=0, sticky='w', pady=2)
            
            # Lock checkbox
            lock_var = tk.BooleanVar()
            self.lock_vars[prop] = lock_var
            lock_cb = tk.Checkbutton(props_frame, text="Lock", variable=lock_var,
                                    command=lambda p=prop: self.toggle_lock(p))
            lock_cb.grid(row=i*2, column=2, sticky='w', padx=5)
            
            # Entry field
            if notation == "scientific":
                var = tk.StringVar(value=str(min_val))
            else:
                var = tk.DoubleVar(value=min_val)
            self.property_vars[prop] = var
            
            entry = tk.Entry(props_frame, textvariable=var, width=15)
            entry.grid(row=i*2, column=1, pady=2)
            entry.bind('<Return>', lambda e, p=prop: self.update_property(p))
            
            # Slider (for non-scientific notation)
            if notation == "normal":
                slider = tk.Scale(props_frame, from_=min_val, to=max_val,
                                orient='horizontal', variable=var,
                                command=lambda v, p=prop: self.update_property(p))
                slider.grid(row=i*2+1, column=0, columnspan=3, sticky='ew', pady=2)
        
        # Color selector
        color_frame = tk.Frame(props_frame)
        color_frame.grid(row=10, column=0, columnspan=3, pady=10)
        
        tk.Label(color_frame, text="Color:").pack(side='left')
        self.color_var = tk.StringVar(value="#FFFFFF")
        self.color_entry = tk.Entry(color_frame, textvariable=self.color_var, width=10)
        self.color_entry.pack(side='left', padx=5)
        self.color_entry.bind('<Return>', lambda e: self.update_color())
        
        self.color_button = tk.Button(color_frame, text="Choose", 
                                     command=self.choose_color, width=10)
        self.color_button.pack(side='left')
        
        # Action buttons
        button_frame = tk.Frame(tab)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Button(button_frame, text="Delete Selected", 
                 command=self.delete_selected).pack(side='left', padx=2)
        tk.Button(button_frame, text="Clear All", 
                 command=self.clear_all).pack(side='left', padx=2)
    
    def create_simulation_tab(self, parent):
        """Create the simulation controls tab."""
        tab = ttk.Frame(parent)
        parent.add(tab, text="Simulation")
        
        # Time controls
        time_frame = tk.LabelFrame(tab, text="Time Control", padx=10, pady=10)
        time_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(time_frame, text="Time Scale:").grid(row=0, column=0, sticky='w')
        self.time_scale_var = tk.DoubleVar(value=1.0)
        time_scale = tk.Scale(time_frame, from_=0.1, to=10.0, resolution=0.1,
                            orient='horizontal', variable=self.time_scale_var,
                            command=self.update_time_scale)
        time_scale.grid(row=0, column=1, sticky='ew')
        
        # Pause button
        self.pause_button = tk.Button(time_frame, text="Pause/Resume", 
                                     command=self.toggle_pause)
        self.pause_button.grid(row=1, column=0, columnspan=2, pady=10)
        
        # System info
        info_frame = tk.LabelFrame(tab, text="System Information", padx=10, pady=10)
        info_frame.pack(fill='x', padx=5, pady=5)
        
        self.info_text = tk.Text(info_frame, height=10, width=40)
        self.info_text.pack()
        
        # Presets
        preset_frame = tk.LabelFrame(tab, text="Presets", padx=10, pady=10)
        preset_frame.pack(fill='x', padx=5, pady=5)
        
        presets = [
            ("Binary System", self.create_binary_system),
            ("Solar System", self.create_solar_system),
            ("Galaxy Collision", self.create_galaxy_collision),
            ("Random Bodies", self.create_random_bodies),
        ]
        
        for text, command in presets:
            tk.Button(preset_frame, text=text, command=command, 
                     width=15).pack(pady=2)
    
    def create_visual_tab(self, parent):
        """Create the visual settings tab."""
        tab = ttk.Frame(parent)
        parent.add(tab, text="Visual")
        
        # Background color
        bg_frame = tk.LabelFrame(tab, text="Background", padx=10, pady=10)
        bg_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(bg_frame, text="Color:").grid(row=0, column=0, sticky='w')
        self.bg_color_var = tk.StringVar(value="#000000")
        bg_entry = tk.Entry(bg_frame, textvariable=self.bg_color_var, width=10)
        bg_entry.grid(row=0, column=1, padx=5)
        bg_entry.bind('<Return>', self.update_background_color)
        
        tk.Button(bg_frame, text="Choose", 
                 command=self.choose_bg_color).grid(row=0, column=2)
        
        # Visual options
        options_frame = tk.LabelFrame(tab, text="Display Options", padx=10, pady=10)
        options_frame.pack(fill='x', padx=5, pady=5)
        
        self.show_trails_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Show Trails", 
                      variable=self.show_trails_var,
                      command=self.update_visual_options).pack(anchor='w')
        
        self.show_vectors_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Show Vectors", 
                      variable=self.show_vectors_var,
                      command=self.update_visual_options).pack(anchor='w')
        
        self.show_grid_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Show Grid", 
                      variable=self.show_grid_var,
                      command=self.update_visual_options).pack(anchor='w')
        
        # Default object settings
        default_frame = tk.LabelFrame(tab, text="Default Object Settings", 
                                     padx=10, pady=10)
        default_frame.pack(fill='x', padx=5, pady=5)
        
        defaults = [
            ("Mass (kg):", "default_mass", 1e20, 1e30),
            ("Radius (px):", "default_radius", 5, 100),
            ("Density (kg/m³):", "default_density", 100, 20000),
        ]
        
        for i, (label, attr, min_val, max_val) in enumerate(defaults):
            tk.Label(default_frame, text=label).grid(row=i, column=0, sticky='w')
            var = tk.DoubleVar(value=getattr(self, attr))
            entry = tk.Entry(default_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entry.bind('<Return>', lambda e, a=attr, v=var: setattr(self, a, v.get()))
    
    def select_body(self, body):
        """Select a body for editing."""
        self.selected_body = body
        if body:
            self.selected_label.config(text=f"Body at ({body.x:.0f}, {body.y:.0f})")
            
            # Update property fields
            self.property_vars['mass'].set(f"{body.mass:.2e}")
            self.property_vars['radius'].set(body.radius)
            self.property_vars['density'].set(body.density)
            self.property_vars['vx'].set(body.vx)
            self.property_vars['vy'].set(body.vy)
            self.color_var.set(rgb_to_hex(body.color))
            
            # Update lock states
            for prop in self.lock_vars:
                self.lock_vars[prop].set(body.is_locked(prop))
        else:
            self.selected_label.config(text="No object selected")
    
    def update_property(self, prop_name):
        """Update a property of the selected body."""
        if not self.selected_body:
            return
        
        try:
            if prop_name == 'mass':
                value = float(self.property_vars[prop_name].get())
            else:
                value = self.property_vars[prop_name].get()
            
            self.selected_body.set_property(prop_name, value)
            self.update_status(f"Updated {prop_name}")
        except ValueError:
            self.update_status(f"Invalid value for {prop_name}")
    
    def toggle_lock(self, prop_name):
        """Toggle property lock for selected body."""
        if not self.selected_body:
            return
        
        if self.lock_vars[prop_name].get():
            self.selected_body.lock_property(prop_name)
        else:
            self.selected_body.unlock_property(prop_name)
        
        self.update_status(f"{'Locked' if self.lock_vars[prop_name].get() else 'Unlocked'} {prop_name}")
    
    def update_color(self):
        """Update color of selected body."""
        if not self.selected_body:
            return
        
        color = hex_to_rgb(self.color_var.get())
        self.selected_body.color = color
        self.update_status("Updated color")
    
    def choose_color(self):
        """Open color chooser dialog."""
        color = colorchooser.askcolor(initialcolor=self.color_var.get())
        if color[1]:
            self.color_var.set(color[1])
            self.update_color()
    
    def choose_bg_color(self):
        """Choose background color."""
        color = colorchooser.askcolor(initialcolor=self.bg_color_var.get())
        if color[1]:
            self.bg_color_var.set(color[1])
            self.update_background_color()
    
    def update_background_color(self, event=None):
        """Update background color."""
        self.renderer.set_background_color(self.bg_color_var.get())
        self.update_status("Updated background color")
    
    def update_visual_options(self):
        """Update visual display options."""
        self.renderer.show_trails = self.show_trails_var.get()
        self.renderer.show_vectors = self.show_vectors_var.get()
        self.renderer.show_grid = self.show_grid_var.get()
    
    def delete_selected(self):
        """Delete the selected body."""
        if self.selected_body:
            self.physics_engine.remove_body(self.selected_body)
            self.selected_body = None
            self.select_body(None)
            self.update_status("Deleted selected body")
    
    def clear_all(self):
        """Clear all bodies from simulation."""
        if messagebox.askyesno("Clear All", "Remove all bodies from simulation?"):
            self.physics_engine.clear_all_bodies()
            self.selected_body = None
            self.select_body(None)
            self.update_status("Cleared all bodies")
    
    def toggle_pause(self):
        """Toggle simulation pause."""
        self.physics_engine.toggle_pause()
        status = "Paused" if self.physics_engine.paused else "Running"
        self.update_status(f"Simulation {status}")
    
    def update_time_scale(self, value):
        """Update simulation time scale."""
        self.physics_engine.set_time_scale(float(value))
    
    def create_binary_system(self):
        """Create a binary star system preset."""
        self.physics_engine.clear_all_bodies()
        
        # Create two massive bodies orbiting each other
        body1 = CelestialBody(640, 300, mass=5e26, radius=30, 
                            velocity=(0, 50), color=(255, 200, 0))
        body2 = CelestialBody(640, 420, mass=5e26, radius=30, 
                            velocity=(0, -50), color=(0, 150, 255))
        
        self.physics_engine.add_body(body1)
        self.physics_engine.add_body(body2)
        self.update_status("Created binary system")
    
    def create_solar_system(self):
        """Create a simple solar system preset."""
        self.physics_engine.clear_all_bodies()
        
        # Sun
        sun = CelestialBody(640, 360, mass=2e28, radius=40, 
                          velocity=(0, 0), color=(255, 255, 0))
        self.physics_engine.add_body(sun)
        
        # Planets
        planets = [
            (440, 360, 3e24, 15, (0, 150), (180, 180, 180)),  # Mercury
            (340, 360, 5e24, 20, (0, 120), (255, 200, 100)),  # Venus
            (240, 360, 6e24, 22, (0, 100), (0, 100, 255)),    # Earth
            (140, 360, 4e24, 18, (0, 80), (255, 100, 0)),     # Mars
        ]
        
        for x, y, mass, radius, velocity, color in planets:
            planet = CelestialBody(x, y, mass=mass, radius=radius, 
                                 velocity=velocity, color=color)
            self.physics_engine.add_body(planet)
        
        self.update_status("Created solar system")
    
    def create_galaxy_collision(self):
        """Create a galaxy collision preset."""
        import random
        self.physics_engine.clear_all_bodies()
        
        # Create two galaxy centers
        center1 = CelestialBody(400, 360, mass=5e27, radius=25, 
                              velocity=(20, 0), color=(255, 255, 255))
        center2 = CelestialBody(880, 360, mass=5e27, radius=25, 
                              velocity=(-20, 0), color=(255, 200, 200))
        
        self.physics_engine.add_body(center1)
        self.physics_engine.add_body(center2)
        
        # Add orbiting bodies for each galaxy
        for _ in range(10):
            # Galaxy 1 bodies
            angle = random.uniform(0, 2 * 3.14159)
            dist = random.uniform(50, 150)
            x = 400 + dist * math.cos(angle)
            y = 360 + dist * math.sin(angle)
            vx = 20 - dist * math.sin(angle) * 0.5
            vy = dist * math.cos(angle) * 0.5
            
            body = CelestialBody(x, y, mass=1e23, radius=8, 
                               velocity=(vx, vy))
            self.physics_engine.add_body(body)
            
            # Galaxy 2 bodies
            angle = random.uniform(0, 2 * 3.14159)
            dist = random.uniform(50, 150)
            x = 880 + dist * math.cos(angle)
            y = 360 + dist * math.sin(angle)
            vx = -20 - dist * math.sin(angle) * 0.5
            vy = dist * math.cos(angle) * 0.5
            
            body = CelestialBody(x, y, mass=1e23, radius=8, 
                               velocity=(vx, vy))
            self.physics_engine.add_body(body)
        
        self.update_status("Created galaxy collision")
    
    def create_random_bodies(self):
        """Create random bodies."""
        import random
        
        for _ in range(5):
            x = random.randint(100, 1180)
            y = random.randint(100, 620)
            mass = random.uniform(1e23, 1e25)
            radius = random.randint(10, 30)
            vx = random.uniform(-50, 50)
            vy = random.uniform(-50, 50)
            
            body = CelestialBody(x, y, mass=mass, radius=radius, 
                               velocity=(vx, vy))
            self.physics_engine.add_body(body)
        
        self.update_status("Created random bodies")
    
    def update_info(self):
        """Update system information display."""
        if hasattr(self, 'info_text'):
            energy = self.physics_engine.get_system_energy()
            info = f"Bodies: {len(self.physics_engine.bodies)}\n"
            info += f"Kinetic Energy: {energy['kinetic']:.2e} J\n"
            info += f"Potential Energy: {energy['potential']:.2e} J\n"
            info += f"Total Energy: {energy['total']:.2e} J\n"
            
            self.info_text.delete('1.0', tk.END)
            self.info_text.insert('1.0', info)
    
    def update_status(self, message):
        """Update status bar message."""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
    
    def run(self):
        """Run the UI event loop."""
        if self.root:
            self.root.mainloop()
    
    def destroy(self):
        """Destroy the UI window."""
        if self.root:
            self.root.destroy()
