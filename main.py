from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from datetime import datetime, timedelta
import json
import requests

# Firebase Realtime Database URL (replace with your Firebase URL)
FIREBASE_URL = "https://advisorroadmap-default-rtdb.firebaseio.com/"

# Predefined list of advisors
ADVISORS = [
    "Eskinder", "Leta", "Alemu", "Mandela", "Hawi", "Fikadu", "Chala", "Debebe",
    "Degaga", "Asefa", "Aman G", "Aman Getu", "Abdulhakim"
]

# Default coach password
COACH_PASSWORD = "coach123"

class FirstPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout()

        title = Label(
            text="📅 JO07 Roadmap", 
            font_size=50, 
            bold=True, 
            color=(0.1, 0.5, 0.8, 1),
            size_hint=(None, None),
            size=(500, 100),
            pos_hint={"center_x": 0.5, "top": 0.95}
        )

        button_style = {"size_hint": (None, None), "size": (450, 100), "font_size": 32}

        advisor_btn = Button(
            text="👨‍💼 For Advisor", background_color=(0.2, 0.6, 0.3, 1),
            pos_hint={"center_x": 0.5, "top": 0.80},
            **button_style
        )
        advisor_btn.bind(on_release=self.go_to_advisor_login)

        coach_btn = Button(
            text="🏆 For Coach", background_color=(0.9, 0.4, 0.3, 1),
            pos_hint={"center_x": 0.5, "top": 0.65},
            **button_style
        )
        coach_btn.bind(on_release=self.go_to_coach_login)

        layout.add_widget(title)
        layout.add_widget(advisor_btn)
        layout.add_widget(coach_btn)
        self.add_widget(layout)

    def go_to_advisor_login(self, instance):
        self.manager.current = "advisor_login"

    def go_to_coach_login(self, instance):
        self.manager.current = "coach_login"


class AdvisorLogin(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout()

        title = Label(
            text="👨‍💼 Advisor Login", font_size=48, bold=True, color=(0.1, 0.5, 0.8, 1),
            size_hint=(None, None), size=(500, 100), pos_hint={"center_x": 0.5, "top": 0.95}
        )

        self.username_input = TextInput(
            font_size=30, hint_text="Enter Username", multiline=False,
            size_hint=(None, None), size=(450, 90), pos_hint={"center_x": 0.5, "top": 0.85}
        )
        self.password_input = TextInput(
            font_size=30, hint_text="Enter Password", multiline=False, password=True,
            size_hint=(None, None), size=(450, 90), pos_hint={"center_x": 0.5, "top": 0.75}
        )

        self.show_password_btn = Button(
            text="👁 Show Password", font_size=28, size_hint=(None, None), size=(450, 80),
            background_color=(0.5, 0.7, 0.9, 1), pos_hint={"center_x": 0.5, "top": 0.65}
        )
        self.show_password_btn.bind(on_release=self.toggle_password)

        login_btn = Button(
            text="✅ Login", font_size=30, size_hint=(None, None), size=(450, 100),
            background_color=(0.1, 0.7, 0.3, 1), pos_hint={"center_x": 0.5, "top": 0.55}
        )
        login_btn.bind(on_release=self.validate_login)

        forgot_btn = Button(
            text="🔄 Forgot Password?", font_size=28, size_hint=(None, None), size=(450, 90),
            background_color=(0.9, 0.4, 0.3, 1), pos_hint={"center_x": 0.5, "top": 0.40}
        )
        forgot_btn.bind(on_release=self.forgot_password)

        back_btn = Button(
            text="⬅ Back", font_size=28, size_hint=(None, None), size=(450, 90),
            background_color=(0.5, 0.5, 0.5, 1), pos_hint={"center_x": 0.5, "top": 0.25}
        )
        back_btn.bind(on_release=self.go_back)

        layout.add_widget(title)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.show_password_btn)
        layout.add_widget(login_btn)
        layout.add_widget(forgot_btn)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def validate_login(self, instance):
        name = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not name or not password:
            self.show_popup("Error", "Please enter both name and password.")
            return

        if name not in ADVISORS:
            self.show_popup("Error", "Not a registered advisor.")
            return

        # Load passwords from Firebase
        passwords = self.fetch_passwords()

        if name not in passwords:
            # First login: create password
            passwords[name] = password
            self.save_passwords(passwords)
            self.show_popup("Success", "Password created successfully!")
            self.manager.current = "weekly_roadmap"
        elif passwords[name] == password:
            # Valid login
            self.manager.current = "weekly_roadmap"
        else:
            self.show_popup("Error", "Incorrect password.")

    def toggle_password(self, instance):
        self.password_input.password = not self.password_input.password

    def go_back(self, instance):
        self.manager.current = "home"

    def forgot_password(self, instance):
        self.show_popup("Forgot Password", "Please contact Eskinder or call 0920003516.")

    def fetch_passwords(self):
        try:
            response = requests.get(f"{FIREBASE_URL}/passwords.json")
            return response.json() or {}
        except Exception as e:
            self.show_popup("Error", f"Failed to fetch passwords: {str(e)}")
            return {}

    def save_passwords(self, passwords):
        try:
            requests.patch(f"{FIREBASE_URL}/passwords.json", data=json.dumps(passwords))
        except Exception as e:
            self.show_popup("Error", f"Failed to save passwords: {str(e)}")

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        popup.open()


class WeeklyRoadmap(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout()

        # Title
        title = Label(
            text="📅 Weekly Roadmap of Next Week", font_size=48, bold=True, color=(0, 0.4, 0.7, 1),
            size_hint=(None, None), size=(650, 120), pos_hint={"center_x": 0.5, "top": 0.98}
        )

        # Welcome Message (With Background)
        welcome_bg = Button(
            text="👋 Welcome! Tap the days you're on leave.", font_size=35, bold=True,
            background_color=(0.8, 0.9, 1, 0.7),  # Light blue transparent
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(None, None), size=(620, 80), pos_hint={"center_x": 0.5, "top": 0.88},
            disabled=True  # Acts as a label with background
        )

        # Day Buttons
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.buttons = {}

        for i, day in enumerate(days):
            button = Button(
                text=day, font_size=40, size_hint=(None, None), size=(600, 100),
                background_color=(0.9, 0.9, 0.9, 1),  # Default color (Light Gray)
                color=(0, 0, 0, 1),  # Black text
                pos_hint={"center_x": 0.5, "top": 0.78 - (i * 0.10)}
            )
            button.bind(on_release=self.toggle_button)
            self.buttons[day] = button
            layout.add_widget(button)

        # Save Button (Attractive Green)
        save_btn = Button(
            text="✅ Save", font_size=40, bold=True, size_hint=(None, None), size=(600, 100),
            background_color=(0, 0.6, 0.2, 1),  # Dark Green
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5, "top": 0.10}
        )
        save_btn.bind(on_release=self.save_selections)

        # Back Button
        back_btn = Button(
            text="⬅ Back", font_size=28, size_hint=(None, None), size=(450, 90),
            background_color=(0.5, 0.5, 0.5, 1), pos_hint={"center_x": 0.5, "top": 0.05}
        )
        back_btn.bind(on_release=self.go_back)

        layout.add_widget(title)
        layout.add_widget(welcome_bg)
        layout.add_widget(save_btn)
        layout.add_widget(back_btn)
        self.add_widget(layout)

        # Defer loading existing data until the screen is displayed
        self.bind(on_enter=self.load_existing_data)

    def toggle_button(self, instance):
        """Toggle button color when clicked (Light Gray ↔ Green)."""
        if instance.background_color == [0.9, 0.9, 0.9, 1]:  # Light Gray -> Green
            instance.background_color = (0, 0.7, 0.3, 1)
            instance.color = (1, 1, 1, 1)  # White text when selected
        else:  # Green -> Light Gray
            instance.background_color = (0.9, 0.9, 0.9, 1)
            instance.color = (0, 0, 0, 1)  # Black text when unselected

    def save_selections(self, instance):
        """Save selected days to Firebase."""
        selected_days = [day for day, button in self.buttons.items() if button.background_color == [0, 0.7, 0.3, 1]]
        if not selected_days:
            self.show_popup("Error", "Select at least one day.")
            return

        # Check for conflicts (max 2 advisors per day)
        conflicts = self.check_conflicts(selected_days)
        if conflicts:
            conflict_message = "The following days are full:\n"
            for day, advisors in conflicts.items():
                conflict_message += f"{day}: {', '.join(advisors)}\n"
            conflict_message += "Please choose another day or contact the advisors."
            self.show_popup("Conflict", conflict_message)
            return

        # Save availability to Firebase
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "advisor": self.manager.get_screen("advisor_login").username_input.text.strip(),
            "days": selected_days,
            "timestamp": timestamp
        }
        self.save_to_firebase(data)
        self.show_popup("Success", "Availability saved successfully!")

    def check_conflicts(self, selected_days):
        """Check if more than 2 advisors are assigned to the same day."""
        data = self.fetch_availability()
        conflicts = {}

        for day in selected_days:
            advisors = []
            for entry in data.values():
                if day in entry.get("days", []):
                    advisors.append(entry["advisor"])
            if len(advisors) >= 2:
                conflicts[day] = advisors

        return conflicts

    def load_existing_data(self, *args):
        """Load existing availability data for the advisor."""
        data = self.fetch_availability()
        advisor = self.manager.get_screen("advisor_login").username_input.text.strip()

        for entry in data.values():
            if entry["advisor"] == advisor:
                days = entry.get("days", [])
                for day in days:
                    if day in self.buttons:
                        self.buttons[day].background_color = (0, 0.7, 0.3, 1)
                        self.buttons[day].color = (1, 1, 1, 1)
                break

    def go_back(self, instance):
        self.manager.current = "advisor_login"

    def save_to_firebase(self, data):
        try:
            # Delete existing entry for the advisor (if any)
            advisor = data["advisor"]
            existing_data = self.fetch_availability()
            for key, entry in existing_data.items():
                if entry["advisor"] == advisor:
                    requests.delete(f"{FIREBASE_URL}/availability/{key}.json")
                    break

            # Save new data
            requests.post(f"{FIREBASE_URL}/availability.json", data=json.dumps(data))
        except Exception as e:
            self.show_popup("Error", f"Failed to save data: {str(e)}")

    def fetch_availability(self):
        try:
            response = requests.get(f"{FIREBASE_URL}/availability.json")
            return response.json() or {}
        except Exception as e:
            self.show_popup("Error", f"Failed to fetch availability: {str(e)}")
            return {}

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        popup.open()


class CoachLogin(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout()

        title = Label(
            text="🏆 Welcome Ayni", font_size=48, bold=True, color=(0.1, 0.5, 0.8, 1),
            size_hint=(None, None), size=(500, 100), pos_hint={"center_x": 0.5, "top": 0.95}
        )

        self.password_input = TextInput(
            font_size=30, hint_text="Enter Password", multiline=False, password=True,
            size_hint=(None, None), size=(450, 90), pos_hint={"center_x": 0.5, "top": 0.85}
        )

        self.show_password_btn = Button(
            text="👁 Show Password", font_size=28, size_hint=(None, None), size=(450, 80),
            background_color=(0.5, 0.7, 0.9, 1), pos_hint={"center_x": 0.5, "top": 0.75}
        )
        self.show_password_btn.bind(on_release=self.toggle_password)

        login_btn = Button(
            text="✅ Login", font_size=30, size_hint=(None, None), size=(450, 100),
            background_color=(0.1, 0.7, 0.3, 1), pos_hint={"center_x": 0.5, "top": 0.65}
        )
        login_btn.bind(on_release=self.validate_login)

        forgot_btn = Button(
            text="🔄 Forgot Password?", font_size=28, size_hint=(None, None), size=(450, 90),
            background_color=(0.9, 0.4, 0.3, 1), pos_hint={"center_x": 0.5, "top": 0.50}
        )
        forgot_btn.bind(on_release=self.forgot_password)

        back_btn = Button(
            text="⬅ Back", font_size=28, size_hint=(None, None), size=(450, 90),
            background_color=(0.5, 0.5, 0.5, 1), pos_hint={"center_x": 0.5, "top": 0.35}
        )
        back_btn.bind(on_release=self.go_back)

        layout.add_widget(title)
        layout.add_widget(self.password_input)
        layout.add_widget(self.show_password_btn)
        layout.add_widget(login_btn)
        layout.add_widget(forgot_btn)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def validate_login(self, instance):
        if self.password_input.text == COACH_PASSWORD:
            self.manager.current = "coach_page"
            self.check_unfilled_advisors()
        else:
            self.show_popup("Error", "Incorrect password.")

    def check_unfilled_advisors(self):
        """Check for unfilled advisors on weekends."""
        today = datetime.today().weekday()  # Monday is 0, Sunday is 6
        if today == 5 or today == 6:  # Saturday (5) or Sunday (6)
            data = self.fetch_availability()
            unfilled_advisors = []

            for advisor in ADVISORS:
                filled = False
                for entry in data.values():
                    if entry["advisor"] == advisor:
                        filled = True
                        break
                if not filled:
                    unfilled_advisors.append(advisor)

            if unfilled_advisors:
                message = "The following advisors have not filled their availability for next week:\n"
                message += "\n".join(unfilled_advisors)
                self.show_popup("Reminder", message)

    def go_back(self, instance):
        self.manager.current = "home"

    def toggle_password(self, instance):
        self.password_input.password = not self.password_input.password

    def forgot_password(self, instance):
        self.show_popup("Forgot Password", "Please contact Eskinder or call 0920003516.")

    def fetch_availability(self):
        try:
            response = requests.get(f"{FIREBASE_URL}/availability.json")
            return response.json() or {}
        except Exception as e:
            self.show_popup("Error", f"Failed to fetch availability: {str(e)}")
            return {}

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        popup.open()


class CoachPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # Title
        title = Label(
            text="🏆 Welcome Ayni",
            font_size=50,
            bold=True,
            color=(0, 0.4, 0.7, 1),
            size_hint=(None, None),
            size=(650, 100),
            pos_hint={"center_x": 0.5, "top": 0.98},
        )

        # Subtitle
        subtitle = Label(
            text="These advisors are filled for next week",
            font_size=30,
            bold=True,
            color=(0.3, 0.3, 0.3, 1),
            size_hint=(None, None),
            size=(700, 60),
            pos_hint={"center_x": 0.5, "top": 0.90},
        )

        # Dynamic Grid Layout (adjust rows based on the number of advisors)
        self.advisors = ADVISORS
        num_advisors = len(self.advisors)
        
        grid = GridLayout(
            cols=8,  # 1 for advisor names, 7 for days (Mon-Sun)
            rows=num_advisors + 1,  # Add 1 for the header row (days)
            spacing=5,
            size_hint=(None, None),
            size=(1000, 600),
            pos_hint={"right": 1.38, "top": 0.85},  # Right-shifted
        )

        # Days Row (Horizontal)
        days = ["Advisor", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in days:
            label = Label(
                text=day,
                font_size=20,
                bold=True,
                color=(1, 1, 1, 1),
                size_hint=(None, None),
                size=(80, 60),
            )
            grid.add_widget(label)

        # Advisor Names (Vertical) and Buttons for Availability
        self.availability_buttons = {}  # Store button references

        for advisor in self.advisors:
            # Advisor Name Column (Vertical)
            advisor_label = Label(
                text=advisor,
                font_size=18,
                bold=True,
                color=(1, 1, 1, 1),  # White color for advisor names
                size_hint=(None, None),
                size=(120, 50),  # Increased width for advisor names
                halign="center",  # Center the text
                valign="middle",  # Vertically align the text
            )
            grid.add_widget(advisor_label)

            # Buttons for Each Day
            self.availability_buttons[advisor] = []
            for _ in range(7):  # 7 Days
                btn = Button(
                    text="",  # Initially empty
                    font_size=15,
                    size_hint=(None, None),
                    size=(60, 30),  # Reduced button size to fit all columns
                    background_color=(0.9, 0.9, 0.9, 1),  # Default Light Gray
                    color=(0, 0, 0, 1),
                )
                self.availability_buttons[advisor].append(btn)
                grid.add_widget(btn)

        # Back Button
        back_btn = Button(
            text="⬅ Back",
            font_size=32,
            size_hint=(None, None),
            size=(250, 80),
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5, "top": 0.12},
        )
        back_btn.bind(on_release=self.go_back)

        # Summary Titles for Total Days Filled and Percentage
        total_days_title = Label(
            text="Total Days Filled",
            font_size=20,
            bold=True,
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(250, 40),
            pos_hint={"left": 0.15, "bottom": 0.05},
        )

        percentage_title = Label(
            text="Percentage",
            font_size=20,
            bold=True,
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={"left": 0.55, "bottom": 0.05},
        )

        # Summary values
        self.total_days_filled_label = Label(
            text="0",  # Initially 0
            font_size=20,
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={"left": 0.3, "bottom": 0.05},
        )

        self.percentage_label = Label(
            text="0%",  # Initially 0%
            font_size=20,
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={"left": 0.7, "bottom": 0.05},
        )

        # Add elements to layout
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(grid)
        layout.add_widget(back_btn)
        layout.add_widget(total_days_title)
        layout.add_widget(percentage_title)
        layout.add_widget(self.total_days_filled_label)
        layout.add_widget(self.percentage_label)

        self.add_widget(layout)

        # Fetch data from Firebase and update UI
        self.fetch_availability()

    def fetch_availability(self):
        """Fetch availability data from Firebase and update the UI."""
        try:
            response = requests.get(f"{FIREBASE_URL}/availability.json")
            data = response.json() or {}

            for entry in data.values():
                advisor = entry["advisor"]
                days = entry.get("days", [])

                for day in days:
                    day_index = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(day)
                    self.availability_buttons[advisor][day_index].text = "AL"
                    self.availability_buttons[advisor][day_index].background_color = (0, 0.7, 0.3, 1)  # Green

            self.update_summary()
        except Exception as e:
            self.show_popup("Error", f"Failed to fetch data: {str(e)}")

    def update_summary(self):
        """Update the summary with total days filled and percentage."""
        total_filled_days = sum(1 for advisor in self.availability_buttons for btn in self.availability_buttons[advisor] if btn.text == "AL")
        total_days = 7 * len(self.advisors)  # Total days (7 days * number of advisors)
        percentage_filled = (total_filled_days / total_days) * 100 if total_days > 0 else 0

        # Update the labels with total days filled and percentage
        self.total_days_filled_label.text = f"{total_filled_days} / {total_days}"
        self.percentage_label.text = f"{percentage_filled:.2f}%"

    def go_back(self, instance):
        self.manager.current = "home"  # Back to Home Page

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        popup.content = Label(text=message)
        popup.open()


class RoadmapApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(FirstPage(name="home"))
        sm.add_widget(AdvisorLogin(name="advisor_login"))
        sm.add_widget(WeeklyRoadmap(name="weekly_roadmap"))
        sm.add_widget(CoachLogin(name="coach_login"))
        sm.add_widget(CoachPage(name="coach_page"))
        return sm


if __name__ == "__main__":
    RoadmapApp().run()