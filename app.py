import tkinter as tk
from tkinter import messagebox
from models.user import User
from models.geofence import Geofence
from models.ad import Ad
from utils.geofence_logic import get_relevant_ads  

class LocationBasedAdsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Location-Based Ads & Offers")

        # Logged-in user ID
        self.logged_in_user_id = None

        self.create_login_screen()

    def create_login_screen(self):
        """
        Create the login screen for both business and personal users.
        """
        self.clear_window()
        tk.Label(self.root, text="Location-Based Ads", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Email:").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        tk.Label(self.root, text="Login as:").pack()
        self.user_type_var = tk.StringVar(value="business")
        tk.Radiobutton(self.root, text="Business", variable=self.user_type_var, value="business").pack()
        tk.Radiobutton(self.root, text="Personal", variable=self.user_type_var, value="personal").pack()

        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)

    def login(self):
        """
        Handle login for business and personal users.
        """
        email = self.email_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type_var.get()

        user = User.login(email, password)
        if user and user[4] == user_type:  # user[4] is the user_type
            self.logged_in_user_id = user[0]  # user[0] is the user ID
            messagebox.showinfo("Success", f"Welcome, {user[1]}!")  # user[1] is the username

            if user_type == "business":
                self.create_business_dashboard()
            elif user_type == "personal":
                self.create_personal_user_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials or user type.")

    def create_business_dashboard(self):
        """
        Create the dashboard for business users to manage geofences and ads.
        """
        self.clear_window()
        tk.Label(self.root, text="Business Dashboard", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text="Add Geofence and Ad", command=self.add_geofence_and_ad).pack(pady=5)
        tk.Button(self.root, text="View Geofences and Ads", command=self.view_geofences_and_ads).pack(pady=5)

    def create_personal_user_dashboard(self):
        """
        Create the dashboard for personal users to view offers.
        """
        self.clear_window()
        tk.Label(self.root, text="Personal User Dashboard", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Enter Your Current Location (latitude, longitude):").pack(pady=5)
        self.latitude_entry = tk.Entry(self.root)
        self.latitude_entry.pack(pady=5)
        self.longitude_entry = tk.Entry(self.root)
        self.longitude_entry.pack(pady=5)

        tk.Button(self.root, text="Check for Offers", command=self.check_for_offers).pack(pady=10)
        self.offers_text = tk.Text(self.root, width=50, height=15)
        self.offers_text.pack(pady=5)

    def add_geofence_and_ad(self):
        """
        Placeholder for adding geofence and ad.
        """
        messagebox.showinfo("Coming Soon", "Add Geofence and Ad functionality will be implemented.")

    def view_geofences_and_ads(self):
        """
        Placeholder for viewing geofences and ads.
        """
        messagebox.showinfo("Coming Soon", "View Geofences and Ads functionality will be implemented.")

    def check_for_offers(self):
        """
        Check for relevant ads based on the user's location.
        """
        try:
            user_lat = float(self.latitude_entry.get())
            user_lon = float(self.longitude_entry.get())
            user_location = (user_lat, user_lon)

            ads = get_relevant_ads(user_location)
            self.offers_text.delete("1.0", tk.END)

            if ads:
                for ad in ads:
                    self.offers_text.insert(tk.END, f"Ad Title: {ad['title']}\nDescription: {ad['description']}\n\n")
            else:
                self.offers_text.insert(tk.END, "No offers available in your area.\n")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid latitude and longitude.")

    def clear_window(self):
        """
        Clear the current window content.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        """
        Start the main loop of the application.
        """
        self.root.mainloop()


import random
import time
from tkinter import messagebox, ttk
class LocationBasedAdsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Location-Based Ads & Offers")

        # Logged-in user ID
        self.logged_in_user_id = None

        # Create a notebook (tabbed widget)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.customer_tab = ttk.Frame(self.notebook)
        self.admin_tab = ttk.Frame(self.notebook)
        self.demo_tab = ttk.Frame(self.notebook)

        # Add tabs to the notebook
        self.notebook.add(self.customer_tab, text="Customer")
        self.notebook.add(self.admin_tab, text="Admin")
        self.notebook.add(self.demo_tab, text="Demo")

        self.create_login_screen() 








if __name__ == "__main__":
    app = LocationBasedAdsApp()
    app.run()
