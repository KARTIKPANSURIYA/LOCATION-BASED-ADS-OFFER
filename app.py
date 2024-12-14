"""
This module provides a GUI application for managing location-based advertisements and offers.
The application allows business users to create and manage geofences and ads, while personal users can view offers based
on their location (automatic or manually entry).
"""

import tkinter as tk
from tkinter import messagebox
from models.user import User
from utils.geofence_logic import get_relevant_ads
from utils.db_connection import create_connection, get_ad_views_for_business
import requests
from models.analytics import plot_geofences_on_map, count_users_in_geofences, plot_user_geofence_counts, plot_ad_views
from datetime import datetime

class LocationBasedAdsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Location-Based Ads & Offers")

        # Logged-in user ID
        self.logged_in_user_id = None

        self.create_login_screen()

    def create_login_screen(self):
        """
        Creating the login screen for both business and personal users.
        """
        self.clear_window()
        self.root.update_idletasks()  # Force UI refresh for a clean slate

        tk.Label(self.root, text="Location-Based Ads", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Email:").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack(pady=5)
        self.email_entry.focus_set()  # Set focus to the email field for better UX

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
        Creating the signup screen for new users.
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
        Handling user signup and save to the database.
        """
        name = self.signup_name_entry.get()
        email = self.signup_email_entry.get()
        password = self.signup_password_entry.get()
        user_type = self.signup_user_type_var.get()

        if not name or not email or not password:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        # Checking if the email already exists
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            messagebox.showerror("Error", "Email already registered. Please log in.")
            return

        # Save the new user to db
        try:
            new_user = User(name, email, password, user_type)
            new_user.save_to_db()
            messagebox.showinfo("Success", "User registered successfully! Please log in.")
            self.create_login_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register user: {e}")

    def login(self):
        """
        Handling login for business and personal users.
        """
        email = self.email_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type_var.get()

        user = User.login(email, password)
        if user and user[4] == user_type:
            self.logged_in_user_id = user[0]
            messagebox.showinfo("Success", f"Welcome, {user[1]}!")

            if user_type == "business":
                self.create_business_dashboard()
            elif user_type == "personal":
                self.create_personal_user_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials or user type.")

    def logout(self):
        """
        Logging out the user and returning to the login screen.
        """
        self.logged_in_user_id = None
        messagebox.showinfo("Logout", "You have been logged out successfully!")
        self.create_login_screen()

    def create_business_dashboard(self):
        """
        Creating the dashboard for business users to manage geofences and ads.
        """
        self.clear_window()
        tk.Label(self.root, text="Business Dashboard", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text="Add Geofence and Ad", command=self.add_geofence_and_ad).pack(pady=5)
        tk.Button(self.root, text="View Geofences and Ads", command=self.view_geofences_and_ads).pack(pady=5)
        tk.Button(self.root, text="View Analytics", command=self.show_analytics).pack(pady=10)
        tk.Button(self.root, text="Logout", command=self.logout).pack(pady=10)
    def create_personal_user_dashboard(self):
        """
        Creating the dashboard for personal users to view offers.
        """
        self.clear_window()
        tk.Label(self.root, text="Personal User Dashboard", font=("Arial", 16)).pack(pady=10)

        # Initializing location mode variable
        self.location_mode_var = tk.StringVar(value="automatic")

        # Location Mode: Automatic or Manual
        tk.Label(self.root, text="Select Location Mode:").pack(pady=5)
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

        # Checkin for Offers Button
        tk.Button(self.root, text="Check for Offers", command=self.check_for_offers).pack(pady=10)

        self.offers_text = tk.Text(self.root, width=50, height=15)
        self.offers_text.pack(pady=5)

        # Logout Button
        tk.Button(self.root, text="Logout", command=self.logout).pack(pady=10)

        # Automatically fetch location on start
        self.handle_location_mode()

    def handle_location_mode(self):
        """
        Handling the selected location mode: automatic or manual.
        """
        if self.location_mode_var.get() == "automatic":
            # Fetching current location
            current_location = self.get_current_location()
            if current_location:
                self.latitude_entry.delete(0, tk.END)
                self.longitude_entry.delete(0, tk.END)
                self.latitude_entry.insert(0, str(current_location[0]))
                self.longitude_entry.insert(0, str(current_location[1]))
                self.check_for_offers()
            else:
                messagebox.showerror("Error", "Unable to fetch current location.")
            self.manual_location_frame.pack_forget()  # Hide manual location frame
        else:
            self.manual_location_frame.pack(pady=10)  # Show manual location frame

    def show_analytics(self):
        """
        Show ad views analytics using a bar chart.
        """
        # Fetching ad views for the logged-in business owner
        ad_views = get_ad_views_for_business(self.logged_in_user_id)
        print("Ad views fetched:", ad_views)  # Debugging

        if not ad_views:
            messagebox.showwarning("No Data", "No ad views available for your ads.")
            return

        # Plotting the ad views
        plot_ad_views(ad_views)

    def view_geofences_and_ads(self):
        """
        Display all geofences and ads created by the business user with proper alignment and a scrollbar.
        """
        self.clear_window()
        tk.Label(self.root, text="Your Geofences and Ads", font=("Arial", 16)).pack(pady=10)

        # Creating a frame to hold the canvas and scrollbar
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        # Creating a canvas for widgets
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar creation
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame inside the canvas to hold the content
        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # Fetching the data from the database
        conn = create_connection()
        cursor = conn.cursor()

        query = """
            SELECT g.id, g.latitude, g.longitude, g.radius_km, a.title, a.description
            FROM geofences g
            LEFT JOIN ads a ON g.id = a.geofence_id
            WHERE g.business_id = ?
        """
        cursor.execute(query, (self.logged_in_user_id,))
        records = cursor.fetchall()
        conn.close()

        # Adding geofences and ads to the content frame with alignment and padding
        for record in records:
            geofence_id, latitude, longitude, radius_km, title, description = record

            tk.Label(content_frame, text=f"Geofence ID: {geofence_id}", font=("Arial", 12, "bold"), anchor="w").pack(
                fill=tk.X, padx=10, pady=5)
            tk.Label(content_frame, text=f"Center: ({latitude:.6f}, {longitude:.6f})", anchor="w").pack(fill=tk.X,
                                                                                                        padx=20)
            tk.Label(content_frame, text=f"Radius: {radius_km} km", anchor="w").pack(fill=tk.X, padx=20)

            if title and description:
                tk.Label(content_frame, text=f"Ad Title: {title}", font=("Arial", 12, "italic"), anchor="w").pack(
                    fill=tk.X, padx=20)
                tk.Label(content_frame, text=f"Description: {description}", anchor="w").pack(fill=tk.X, padx=20, pady=5)
            else:
                tk.Label(content_frame, text="No ads linked to this geofence.", anchor="w", fg="gray").pack(fill=tk.X,padx=20, pady=5)

            # Adding a separator
            tk.Label(content_frame, text="").pack()

        # Adding a "Back to Dashboard" button inside the scrollable area
        tk.Button(content_frame, text="Back to Dashboard", command=self.create_business_dashboard).pack(pady=10, anchor="center")

        # Updating the canvas to reflect the size of the content
        content_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def add_geofence_and_ad(self):
        """
        Allowing business users to add geofences and ads.
        """
        self.clear_window()
        print("Debug: Executing add_geofence_and_ad")  # Debugging message

        tk.Label(self.root, text="Add Geofence and Ad", font=("Arial", 16)).pack(pady=10)

        # Geofence Inputs
        tk.Label(self.root, text="Geofence Center (latitude, longitude):").pack(pady=5)
        self.geo_lat_entry = tk.Entry(self.root)  # Setting as instance variable
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

    def get_current_location(self):
        """
        Fetching the user's current location using Google Maps Geolocation API.
        Returns (latitude, longitude) if successful, or None if not.
        """
        API_KEY = "AIzaSyC8dmyIo4iOlAGywPxU1JmYjm9olNPRDAQ"  # Replace with your valid API Key
        endpoint = f"https://www.googleapis.com/geolocation/v1/geolocate?key={API_KEY}"

        try:
            # Making a request to Google's Geolocation API
            response = requests.post(endpoint, json={})
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Parse the response JSON
            location = response.json()["location"]
            lat, lng = location["lat"], location["lng"]
            print(f"Detected location: Latitude {lat}, Longitude {lng}")
            return lat, lng
        except requests.exceptions.RequestException as e:
            print(f"Error fetching location: {e}")
            return None

    def display_ads(self, ads):
        """
        Displaying ads in the personal dashboard.
        """
        self.offers_text.delete(1.0, tk.END)
        if ads:
            for ad in ads:
                self.offers_text.insert(tk.END, f"{ad[0]} - {ad[1]}\n")
        else:
            self.offers_text.insert(tk.END, "No ads available nearby.")

    def save_geofence_and_ad(self):
        """
        Save the geofence and associated ad to the database.
        """
        try:
            print(f"Debug: geo_lat_entry={self.geo_lat_entry}, geo_lon_entry={self.geo_lon_entry}, "
                  f"geo_radius_entry={self.geo_radius_entry}, ad_title_entry={self.ad_title_entry}, "
                  f"ad_description_entry={self.ad_description_entry}")  # Debugging

            if not hasattr(self, "geo_lat_entry") or not hasattr(self, "geo_lon_entry"):
                raise AttributeError("Instance variables for geofence inputs are not set.")

            latitude = float(self.geo_lat_entry.get())
            longitude = float(self.geo_lon_entry.get())
            radius_km = float(self.geo_radius_entry.get())
            title = self.ad_title_entry.get()
            description = self.ad_description_entry.get()

            if not title or not description:
                messagebox.showerror("Input Error", "Ad Title and Description are required.")
                return

            conn = create_connection()
            cursor = conn.cursor()

            # Insert geofence
            cursor.execute("""
                INSERT INTO geofences (business_id, latitude, longitude, radius_km)
                VALUES (?, ?, ?, ?)
            """, (self.logged_in_user_id, latitude, longitude, radius_km))
            geofence_id = cursor.lastrowid

            # Insert ad linked to the geofence
            cursor.execute("""
                INSERT INTO ads (geofence_id, title, description)
                VALUES (?, ?, ?)
            """, (geofence_id, title, description))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Geofence and Ad added successfully!")
            self.create_business_dashboard()
        except AttributeError as ae:
            messagebox.showerror("Attribute Error", f"{ae}")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid latitude, longitude, or radius.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save geofence and ad: {e}")

    from datetime import datetime

    def check_for_offers(self):
        """
        Checking for relevant ads based on the user's selected location.
        """
        try:
            # Fetch user-provided or detected location
            user_lat = float(self.latitude_entry.get())
            user_lon = float(self.longitude_entry.get())

            # Fetch relevant ads based on user location
            ads = get_relevant_ads(user_lat, user_lon)
            self.offers_text.delete("1.0", tk.END)

            if ads:
                conn = create_connection()
                cursor = conn.cursor()
                for ad in ads:
                    # Display ad on the Personal Dashboard
                    self.offers_text.insert(tk.END, f"Ad Title: {ad[0]}\nDescription: {ad[1]}\n\n")

                    # Log the ad view (impression) in the database
                    cursor.execute("""
                        INSERT INTO ad_views (ad_id, timestamp)
                        SELECT id, ? FROM ads WHERE title = ? LIMIT 1
                    """, (datetime.now(), ad[0]))
                conn.commit()
                conn.close()
            else:
                self.offers_text.insert(tk.END, "No offers available nearby.\n")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid latitude and longitude.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def clear_window(self):
        """
        Clearing the current content of the window.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        """
        Running the application.
        """
        self.root.mainloop()


if __name__ == "__main__":
    app = LocationBasedAdsApp()
    app.run()
