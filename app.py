import tkinter as tk
from tkinter import messagebox
from models.user import User
from models.geofence import Geofence
from models.ad import Ad
from utils.geofence_logic import get_relevant_ads
from utils.db_connection import create_connection
import threading
import time
from random import uniform
from opencage.geocoder import OpenCageGeocode
import geocoder
import requests

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
        tk.Button(self.root, text="Sign Up", command=self.create_signup_screen).pack(pady=5)

    def create_signup_screen(self):
        """
        Create the signup screen for new users.
        """
        self.clear_window()
        tk.Label(self.root, text="Sign Up", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Name:").pack()
        self.signup_name_entry = tk.Entry(self.root)
        self.signup_name_entry.pack(pady=5)

        tk.Label(self.root, text="Email:").pack()
        self.signup_email_entry = tk.Entry(self.root)
        self.signup_email_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack()
        self.signup_password_entry = tk.Entry(self.root, show="*")
        self.signup_password_entry.pack(pady=5)

        tk.Label(self.root, text="Sign up as:").pack()
        self.signup_user_type_var = tk.StringVar(value="business")
        tk.Radiobutton(self.root, text="Business", variable=self.signup_user_type_var, value="business").pack()
        tk.Radiobutton(self.root, text="Personal", variable=self.signup_user_type_var, value="personal").pack()

        tk.Button(self.root, text="Register", command=self.signup).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.create_login_screen).pack(pady=5)

    def signup(self):
        """
        Handle user signup and save to the database.
        """
        name = self.signup_name_entry.get()
        email = self.signup_email_entry.get()
        password = self.signup_password_entry.get()
        user_type = self.signup_user_type_var.get()

        if not name or not email or not password:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        # Check if the email already exists
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            messagebox.showerror("Error", "Email already registered. Please log in.")
            return

        # Save the new user
        try:
            new_user = User(name, email, password, user_type)
            new_user.save_to_db()
            messagebox.showinfo("Success", "User registered successfully! Please log in.")
            self.create_login_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register user: {e}")

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

        # Location Mode: Automatic or Manual
        tk.Label(self.root, text="Select Location Mode:").pack(pady=5)
        self.location_mode_var = tk.StringVar(value="automatic")
        tk.Radiobutton(self.root, text="Automatic", variable=self.location_mode_var, value="automatic",
                       command=self.handle_location_mode).pack()
        tk.Radiobutton(self.root, text="Manual", variable=self.location_mode_var, value="manual",
                       command=self.handle_location_mode).pack()

        # Manual Location Input
        self.manual_location_frame = tk.Frame(self.root)
        tk.Label(self.manual_location_frame, text="Enter Your Current Location (latitude, longitude):").pack(pady=5)
        self.latitude_entry = tk.Entry(self.manual_location_frame)
        self.latitude_entry.pack(pady=5)
        self.longitude_entry = tk.Entry(self.manual_location_frame)
        self.longitude_entry.pack(pady=5)
        self.manual_location_frame.pack(pady=10)

        # Check Offers Button
        tk.Button(self.root, text="Check for Offers", command=self.check_for_offers).pack(pady=10)

        self.offers_text = tk.Text(self.root, width=50, height=15)
        self.offers_text.pack(pady=5)

        # Automatically fetch location on start
        self.handle_location_mode()

    def add_geofence_and_ad(self):
        """
        Allow business users to add geofences and ads.
        """
        self.clear_window()
        tk.Label(self.root, text="Add Geofence and Ad", font=("Arial", 16)).pack(pady=10)

        # Geofence Inputs
        tk.Label(self.root, text="Geofence Center (latitude, longitude):").pack(pady=5)
        self.geo_lat_entry = tk.Entry(self.root)
        self.geo_lat_entry.pack(pady=5)
        self.geo_lon_entry = tk.Entry(self.root)
        self.geo_lon_entry.pack(pady=5)

        tk.Label(self.root, text="Radius (km):").pack(pady=5)
        self.geo_radius_entry = tk.Entry(self.root)
        self.geo_radius_entry.pack(pady=5)

        # Ad Inputs
        tk.Label(self.root, text="Ad Title:").pack(pady=5)
        self.ad_title_entry = tk.Entry(self.root)
        self.ad_title_entry.pack(pady=5)

        tk.Label(self.root, text="Ad Description:").pack(pady=5)
        self.ad_description_entry = tk.Entry(self.root)
        self.ad_description_entry.pack(pady=5)

        tk.Button(self.root, text="Add", command=self.save_geofence_and_ad).pack(pady=10)
        tk.Button(self.root, text="Back to Dashboard", command=self.create_business_dashboard).pack(pady=5)

    def save_geofence_and_ad(self):
        """
        Save the geofence and associated ad to the database.
        """
        try:
            # Geofence Inputs
            latitude = float(self.geo_lat_entry.get())
            longitude = float(self.geo_lon_entry.get())
            radius_km = float(self.geo_radius_entry.get())

            # Ad Inputs
            ad_title = self.ad_title_entry.get()
            ad_description = self.ad_description_entry.get()

            # Save Geofence
            geofence = Geofence(self.logged_in_user_id, latitude, longitude, radius_km)
            geofence.save_to_db()

            # Fetch the ID of the newly created geofence
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT last_insert_rowid()")
            geofence_id = cursor.fetchone()[0]
            conn.close()

            # Save Ad
            ad = Ad(geofence_id, ad_title, ad_description)
            ad.save_to_db()

            messagebox.showinfo("Success", "Geofence and Ad added successfully!")
            self.create_business_dashboard()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid geofence and ad details.")

    def view_geofences_and_ads(self):
        """
        Display all geofences and ads created by the business user.
        """
        self.clear_window()
        tk.Label(self.root, text="Your Geofences and Ads", font=("Arial", 16)).pack(pady=10)

        # Fetch Geofences and Ads
        geofences = Geofence.get_all_geofences()
        conn = create_connection()
        cursor = conn.cursor()

        for geofence in geofences:
            if geofence[1] == self.logged_in_user_id:  # Only show geofences created by this user
                tk.Label(self.root, text=f"Geofence ID: {geofence[0]}").pack()
                tk.Label(self.root, text=f"Center: ({geofence[2]}, {geofence[3]})").pack()
                tk.Label(self.root, text=f"Radius: {geofence[4]} km").pack()

                # Fetch ads for this geofence
                ads = Ad.get_ads_by_geofence(geofence[0])
                for ad in ads:
                    tk.Label(self.root, text=f"    Ad Title: {ad[2]}").pack()
                    tk.Label(self.root, text=f"    Description: {ad[3]}").pack()
                tk.Label(self.root, text="").pack()  # Blank line for spacing

        tk.Button(self.root, text="Back to Dashboard", command=self.create_business_dashboard).pack(pady=10)

    def check_for_offers(self):
        """
        Check for relevant ads based on the user's selected location.
        """
        try:
            user_lat = float(self.latitude_entry.get())
            user_lon = float(self.longitude_entry.get())
            user_location = (user_lat, user_lon)

            # Fetch relevant ads
            ads = get_relevant_ads(user_location)
            self.offers_text.delete("1.0", tk.END)  # Clear previous offers

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

    def simulate_user_movement(self):
        """
        Simulate a user moving through random locations with the ability to stop.
        """
        self.simulation_active = True
        tk.Label(self.root, text="Simulated Movement Active", fg="blue").pack(pady=5)
        last_ads = []  # Keep track of the last set of ads

        def move():
            nonlocal last_ads
            while self.simulation_active:
                user_lat = uniform(40.7000, 40.8000)  # Latitude range near NYC
                user_lon = uniform(-74.1000, -73.9000)  # Longitude range near NYC
                user_location = (user_lat, user_lon)

                # Fetch relevant ads
                ads = get_relevant_ads(user_location)

                if ads != last_ads:
                    last_ads = ads
                    self.offers_text.delete("1.0", tk.END)

                    if ads:
                        for ad in ads:
                            self.offers_text.insert(tk.END,
                                                    f"Ad Title: {ad['title']}\nDescription: {ad['description']}\n\n")
                    else:
                        self.offers_text.insert(tk.END, "No offers available in your area.\n")

                time.sleep(5)

        threading.Thread(target=move, daemon=True).start()

    def stop_simulation(self):
        """
        Stop the simulation of user movement.
        """
        self.simulation_active = False
        tk.Label(self.root, text="Simulation Stopped", fg="red").pack(pady=5)

    def get_current_location(self):
        """
        Fetch the user's current location using Google Maps Geolocation API.
        Returns (latitude, longitude) if successful, or None if not.
        """
        API_KEY = "AIzaSyC8dmyIo4iOlAGywPxU1JmYjm9olNPRDAQ"  # Use your Google API Key
        endpoint = f"https://www.googleapis.com/geolocation/v1/geolocate?key={API_KEY}"

        try:
            # Make the request to Google's Geolocation API
            response = requests.post(endpoint, json={})
            response.raise_for_status()  # Raise HTTPError for bad responses

            # Parse the response JSON
            location = response.json()["location"]
            lat, lng = location["lat"], location["lng"]
            print(f"Detected location: Latitude {lat}, Longitude {lng}")
            return lat, lng
        except requests.exceptions.RequestException as e:
            print(f"Error fetching location: {e}")
            return None

    def handle_location_mode(self):
        """
        Handle the selected location mode: automatic or manual.
        """
        if self.location_mode_var.get() == "automatic":
            # Hide manual location input
            self.manual_location_frame.pack_forget()

            # Fetch current location
            current_location = self.get_current_location()
            if current_location:
                print(f"Setting GUI to detected location: {current_location}")  # Debug
                self.latitude_entry.delete(0, tk.END)
                self.longitude_entry.delete(0, tk.END)
                self.latitude_entry.insert(0, str(current_location[0]))
                self.longitude_entry.insert(0, str(current_location[1]))
                self.check_for_offers()
            else:
                messagebox.showerror("Error", "Unable to fetch current location.")
        else:
            # Show manual location input
            self.manual_location_frame.pack(pady=10)

    def update_location_periodically(self):
        """
        Fetch and update the user's location periodically.
        """

        def update():
            while self.location_mode_var.get() == "automatic":
                current_location = self.get_current_location()
                if current_location:
                    print(f"Periodic location update: {current_location}")  # Debug
                    self.latitude_entry.delete(0, tk.END)
                    self.longitude_entry.delete(0, tk.END)
                    self.latitude_entry.insert(0, str(current_location[0]))
                    self.longitude_entry.insert(0, str(current_location[1]))
                    self.check_for_offers()
                time.sleep(10)  # Update every 10 seconds

        threading.Thread(target=update, daemon=True).start()


if __name__ == "__main__":
    app = LocationBasedAdsApp()
    app.run()
