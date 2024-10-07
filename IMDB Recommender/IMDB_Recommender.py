import json
import math
import shutil
import sys
import os
import webbrowser
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import random
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QComboBox, QDialog, QLineEdit, QDialogButtonBox, QFileDialog, QMessageBox, QMenu, QAction, \
    QTableWidget, QHeaderView, QTableWidgetItem, QSlider, QGridLayout, QListWidget, QScrollArea, QAbstractItemView
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QPalette, QColor, QFont
from PyQt5.QtSvg import QSvgRenderer
import re
import mechanize
import time
import matplotlib.pyplot as plt
import numpy as np
import zipfile

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47',
    'Referer': 'https://www.imdb.com/'}

browser = mechanize.Browser()
browser.set_handle_robots(False)
browser.addheaders = [headers]

# Check the last login time from the user_preferences.txt file
def check_last_update():
    with open("user_preferences.txt", "r") as file:
        if os.stat("user_preferences.txt").st_size == 0:
            return ""

        try:
            preferences = file.read()
            preferences = preferences.split("\n")
            print(preferences)
            last_update = preferences[0].split(": ")[1].strip("\"")
            print(last_update)

            # If the last update time is longer than 7 days ago, pop up a message box and ask the user
            # if they want to update their watchlist, ratings list, or other custom lists
            days_since_last_update = (datetime.now() - datetime.strptime(last_update, "%Y-%m-%d")).days
            if (days_since_last_update) >= 7:
                message_box = QMessageBox()
                message_box.setWindowTitle("Update")
                message_box.setText(
                    f"It has been more than {days_since_last_update} days since you updated your lists.\n"
                    f"Would you like to update your watchlist, ratings list, or any other custom lists?")
                message_box.setIcon(QMessageBox.Question)
                message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                message_box.setDefaultButton(QMessageBox.Yes)
                message_box.buttonClicked.connect(ModernApp.create_preferences_file)
                message_box.exec_()

            return last_update

        except:
            message_box = QMessageBox()
            message_box.setWindowTitle("Update")
            message_box.setText(
                f"It looks like there is a problem and we do not know the last time you have updated your lists.\n"
                f"Would you like to update your watchlist, ratings list, or any other custom lists?")
            message_box.setIcon(QMessageBox.Question)
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.Yes)
            message_box.buttonClicked.connect(ModernApp.create_preferences_file)
            message_box.exec_()
            return ""

def smooth_color_change(image):
    # Get the image dimensions
    width = image.width()
    height = image.height()

    # Create a dictionary to store the colors and their counts
    color_counts = {}

    # If the image is too big, resize it
    if width > 1000 or height > 1000:
        image = image.scaled(1000, 1000, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        width = image.width()
        height = image.height()

    # Iterate through the image and add the colors to the list
    # (Similar colors should be counted as one color)
    # (The more centered the pixel is, the more important it is)
    # (Use Gaussian distribution to calculate the importance of the pixel)
    # (Similarity threshold: 10)
    similarity_threshold = 10

    # Iterate through the image and add the colors to the dictionary
    for x in range(width):
        for y in range(height):
            # Get the color at the current pixel
            color = QColor(image.pixel(x, y))

            # Convert QColor to tuple of RGBA values
            color_tuple = (color.red(), color.green(), color.blue(), color.alpha())

            # Calculate the importance of the pixel using Gaussian distribution
            importance = math.exp(-(x - width / 2) ** 2 / (2 * similarity_threshold ** 2)) * \
                         math.exp(-(y - height / 2) ** 2 / (2 * similarity_threshold ** 2))

            # Add the color to the dictionary, considering its importance
            if color_tuple in color_counts:
                color_counts[color_tuple] += importance
            else:
                color_counts[color_tuple] = importance

    # Find the color with the highest count
    dominant_color_tuple = max(color_counts, key=color_counts.get)

    # Find the color with second highest count
    second_dominant_color_tuple = max(color_counts, key=lambda x: color_counts[
        x] if x != dominant_color_tuple else 0)

    # Convert the tuples back to a QColor object
    dominant_color = QColor(*dominant_color_tuple)
    second_dominant_color = QColor(*second_dominant_color_tuple)

    print("Dominant Color:", dominant_color.name())
    print("Dominant Color RGB:", dominant_color.red(), dominant_color.green(),
          dominant_color.blue())
    print("Second Dominant Color:", second_dominant_color.name())
    print("Second Dominant Color RGB:", second_dominant_color.red(),
          second_dominant_color.green(),
          second_dominant_color.blue())

    # Find the average color
    average_color_tuple = (0, 0, 0, 0)
    for color_tuple in color_counts:
        average_color_tuple = tuple(map(sum, zip(average_color_tuple, color_tuple)))
    average_color_tuple = tuple(
        [int(color / len(color_counts)) for color in average_color_tuple])
    average_color = QColor(*average_color_tuple)
    print("Average Color:", average_color.name())
    print("Average Color RGB:", average_color.red(), average_color.green(),
          average_color.blue())

    # Check if we are in dark mode
    if window.theme == "dark":
        new_window_color = QColor(int(25 * 0.8 + average_color.red() * 0.2),
                                  int(25 * 0.8 + average_color.green() * 0.2),
                                  int(25 * 0.8 + average_color.blue() * 0.2))
        print("New Window Color:", new_window_color.name())
        dark_palette.setColor(QPalette.Window, new_window_color)

        # Check if the dominant color is too dark
        if (dominant_color.lightness() < QColor(100, 100,
                                                100).lightness() < second_dominant_color.lightness()):
            # Use the second dominant color instead
            dominant_color = second_dominant_color

        elif (dominant_color.lightness() < QColor(100, 100, 100).lightness()
              and second_dominant_color.value() < QColor(100, 100, 100).lightness()):
            # Lighten the dominant color
            dominant_color = dominant_color.lighter(500)

        else:
            # Lighten the dominant color until it is light enough
            while dominant_color.lightness() < QColor(100, 100, 100).lightness():
                dominant_color = dominant_color.lighter(150)

        print("New Dominant Color:", dominant_color.name())
        print("New Dominant Color RGB:", dominant_color.red(), dominant_color.green(),
              dominant_color.blue())

        dark_palette.setColor(QPalette.Link, dominant_color)
        window.dark_theme()

    elif window.theme == "light":
        new_window_color = QColor(int(255 * 0.8 + average_color.red() * 0.2),
                                  int(255 * 0.8 + average_color.green() * 0.2),
                                  int(255 * 0.8 + average_color.blue() * 0.2))
        print("New Window Color:", new_window_color.name())
        light_palette.setColor(QPalette.Window, new_window_color)

        # Check if the dominant color is too light
        if (dominant_color.lightness() > QColor(200, 200,
                                                200).lightness() > second_dominant_color.lightness()):
            # Use the second dominant color instead
            dominant_color = second_dominant_color

        elif (dominant_color.lightness() > QColor(200, 200, 200).lightness()
              and second_dominant_color.lightness() > QColor(200, 200, 200).lightness()):
            # Darken the dominant color
            dominant_color = dominant_color.darker(500)

        else:
            # Darken the dominant color until it is dark enough
            while dominant_color.lightness() > QColor(200, 200, 200).lightness():
                dominant_color = dominant_color.darker(150)

        print(" New Dominant Color:", dominant_color.name())
        print("New Dominant Color RGB:", dominant_color.red(), dominant_color.green(),
              dominant_color.blue())

        light_palette.setColor(QPalette.Link, dominant_color)
        window.light_theme()

# Custom QDialog class for the Preferences dialog
class PreferencesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferences")
        # Ask the user to enter their IMDb user page link
        self.user_list_file_label = QLabel("Want to add a custom list?", self)
        self.user_list_file_name_label = QLineEdit("Enter the name of the list", self)
        self.user_list_file_input = QPushButton("Select File", self)

        # Add a button to select the watchlist.csv file
        self.watchlist_file_label = QLabel("IMDb Watchlist File Path:", self)
        self.watchlist_file_input = QPushButton("Select File", self)

        # Add a button to select the ratings.csv file
        self.ratings_file_label = QLabel("IMDb Ratings File Path:", self)
        self.ratings_file_input = QPushButton("Select File", self)

        # Add a button to select the Letterboxd data .zip file
        self.letterboxd_file_label = QLabel("Letterboxd Data File Path:", self)
        self.letterboxd_file_input = QPushButton("Select File", self)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.user_list_file_label)
        layout.addWidget(self.user_list_file_name_label)
        layout.addWidget(self.user_list_file_input)
        layout.addWidget(self.watchlist_file_label)
        layout.addWidget(self.watchlist_file_input)
        layout.addWidget(self.ratings_file_label)
        layout.addWidget(self.ratings_file_input)
        layout.addWidget(self.letterboxd_file_label)
        layout.addWidget(self.letterboxd_file_input)
        layout.addWidget(button_box)
        self.setLayout(layout)

        # Connect the ratings_file_input button to the select_ratings_file function
        self.ratings_file_input.clicked.connect(self.select_ratings_file)

        # Connect the watchlist_file_input button to the select_watchlist_file function
        self.watchlist_file_input.clicked.connect(self.select_watchlist_file)

        # Connect the user_lists_file_input button to the select_user_lists_file function
        self.user_list_file_input.clicked.connect(self.select_user_list_file)

        # Connect the letterboxd_file_input button to the select_letterboxd_file function
        self.letterboxd_file_input.clicked.connect(self.select_letterboxd_file)

    # Ask user to select the directory for their ratings.csv file
    def select_ratings_file(self):
        # Open a file dialog to select the ratings.csv file
        ratings_file_path = QFileDialog.getOpenFileName(self, 'Select ratings.csv', '', 'CSV files (*.csv)')[0]

        # Check if the user selected a file
        if ratings_file_path:
            # Check if the ratings.csv file is in the same directory as the script or executable
            if not os.path.dirname(os.path.realpath(__file__)) + "ratings.csv" == ratings_file_path:
                # If not, copy the ratings.csv file to the same directory as the script
                shutil.copy(ratings_file_path, "ratings.csv")

            # Update the ratings_file_input text with the ratings.csv file path
            self.ratings_file_input.setText(ratings_file_path)

    # Ask user to select the directory for their watchlist.csv file
    def select_watchlist_file(self):
        # Open a file dialog to select the watchlist.csv file
        watchlist_file_path = QFileDialog.getOpenFileName(self, 'Select watchlist.csv', '', 'CSV files (*.csv)')[0]

        # Check if the user selected a file
        if watchlist_file_path:
            # Check if the watchlist.csv file is in the same directory as the script or executable
            if not os.path.dirname(os.path.realpath(__file__)) + "watchlist.csv" == watchlist_file_path:
                # If not, copy the watchlist.csv file to the same directory as the script
                shutil.copy(watchlist_file_path, "watchlist.csv")

            # Update the watchlist_file_input text with the watchlist.csv file path
            self.watchlist_file_input.setText(watchlist_file_path)

    # Ask user to select the directory for a custom exported user list
    def select_user_list_file(self):
        self.list_name = self.user_list_file_name_label.text()
        # Open a file dialog to select the user_lists.csv file
        user_lists_file_path = QFileDialog.getOpenFileName(self, 'Select a user list to import', '', 'CSV files (*.csv)')[0]

        # Check if the user selected a file
        if user_lists_file_path:
            # Check if the user_lists.csv file is in the same directory as the script or executable
            if not os.path.dirname(os.path.realpath(__file__)) + f"{self.list_name}.csv" == user_lists_file_path:
                # If not, copy the user_lists.csv file to the same directory as the script
                shutil.copy(user_lists_file_path, f"{self.list_name}.csv")

            # Update the user_lists_file_input text with the user_lists.csv file path
            self.user_list_file_input.setText(user_lists_file_path)

    # Ask user to select the directory for their Letterboxd data .zip file
    def select_letterboxd_file(self):
        # Open a file dialog to select the Letterboxd data .zip file
        letterboxd_file_path = QFileDialog.getOpenFileName(self, 'Select Letterboxd data .zip file', '', 'ZIP files (*.zip)')[0]

        # Check if the user selected a file
        if letterboxd_file_path:
            # Check if the Letterboxd data .zip file is in the same directory as the script or executable
            if not os.path.dirname(os.path.realpath(__file__)) + "letterboxd_data.zip" == letterboxd_file_path:
                # If not, copy the Letterboxd data .zip file to the same directory as the script
                shutil.copy(letterboxd_file_path, "letterboxd_data.zip")

                # Extract the contents of the Letterboxd data .zip file
                with zipfile.ZipFile("letterboxd_data.zip", 'r') as zip_ref:
                    zip_ref.extractall("letterboxd_data")

            # Update the letterboxd_file_input text with the Letterboxd data .zip file path
            self.letterboxd_file_input.setText(letterboxd_file_path)

# Custom QDialog class for the Favorites dialog
class MyFavoritesDialog(QDialog):
    def __init__(self, favorites_data):
        super().__init__()
        self.setWindowTitle("Favorites")

        layout = QVBoxLayout()

        # Set the window size to a reasonable size so that the table is visible
        self.resize(800, 500)

        # If there are any favorites, show them in a table
        if favorites_data:
            table = QTableWidget()
            table.setRowCount(len(favorites_data))
            table.setColumnCount(3)  # Add an extra column for the delete button
            table.setHorizontalHeaderLabels(["Title", "URL", "Delete"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setEditTriggers(QTableWidget.NoEditTriggers)

            for row in range(len(favorites_data)):
                for column in range(2):
                    table.setItem(row, column, QTableWidgetItem(favorites_data[row][column]))

                # Create a delete button for each row
                delete_button = QPushButton("X")
                delete_button.clicked.connect(self.delete_row)
                delete_button.setProperty("row_index", row)  # Store the row index as a property
                table.setCellWidget(row, 2, delete_button)

            layout.addWidget(table)

        else:
            no_favorites_label = QLabel("You have no favorited movies/series.")
            layout.addWidget(no_favorites_label)

        self.setLayout(layout)

    def delete_row(self):
        # Get the clicked button and the associated row index
        sender = self.sender()
        row_index = sender.property("row_index")
        print(f"Row index: {row_index}")

        # Read the content of the favorites.csv file into a list
        with open('favorites.csv', 'r') as file:
            lines = file.readlines()
            print(lines)

        if 0 <= row_index < len(lines) - 1:
            # Remove the identified row from the list
            lines.pop(row_index + 1)
            print(lines)

            # Write the updated list back to the favorites.csv file (open mode read and write so that we can update lines again)
            with open('favorites.csv', 'w') as file:
                file.writelines(lines)

            # Remove the row from the table
            table = self.findChild(QTableWidget)
            if table is not None:
                table.removeRow(row_index)

            # Update row_index property of the delete buttons
            for row in range(row_index, table.rowCount()):
                button = table.cellWidget(row, 2)
                button.setProperty("row_index", row)

# Custom QDialog class for the Statistics dialog
class StatisticsWindow(QDialog):
    def __init__(self, ratings_data):
        super().__init__()
        self.setWindowTitle("Statistics")

        # Set the window size to a reasonable size
        self.resize(700, 400)

        layout = QGridLayout()

        # Your favorite director/creator based on the average rating you have given to their movies/series
        favorite_director_label = QLabel("<h3>Your Favorite Movie Directors</h3>")
        favorite_director_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_director_label, 0, 0, 1, 2)   # Row 0, Col 0-1

        # Get the favorite director/creator
        favorite_directors = self.get_favorite_director(ratings_data)

        # Create a QVBoxLayout to add QLabel widgets
        director_labels_layout = QVBoxLayout()

        # Iterate through the favorite directors and add them to QLabel widgets
        for director, info in favorite_directors[:5]:
            director_label = QLabel(f"<b>{director}:</b> {info[0]:.2f}/10 ({info[1]} titles) with {info[2]:.2f} ❤️")
            director_label.setAlignment(Qt.AlignCenter)
            director_labels_layout.addWidget(director_label)

        # Add "See All" button
        director_see_all = QPushButton("See All")
        # Connect the button click to see_all_directors function
        director_see_all.clicked.connect(lambda: self.see_all_directors( favorite_directors))
        director_labels_layout.addWidget(director_see_all)

        # Create a QWidget to hold the QLabel widgets
        director_labels_widget = QWidget()
        director_labels_widget.setLayout(director_labels_layout)

        # Add the director_labels_widget to your main layout
        layout.addWidget(director_labels_widget, 1, 0)  # Row 1, Col 0

        # Your favorite actor/actress based on the average rating you have given to their movies/series
        favorite_actor_label = QLabel("<h3>Your Favorite Actors/Actresses</h3>")
        favorite_actor_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_actor_label, 2, 0, 1, 2) # Row 2, Col 0-1

        # Get the favorite actor/actress
        favorite_actors = self.get_favorite_actor()

        # Create a QVBoxLayout to add QLabel widgets
        actor_labels_layout = QVBoxLayout()

        try:
            # Iterate through the favorite actors and add them to QLabel widgets
            for actor, info in favorite_actors[:5]:
                actor_label = QLabel(f"<b>{actor}:</b> {info[0]:.2f}/10 ({info[1]} titles) with {info[2]:.2f} ❤️")
                actor_label.setAlignment(Qt.AlignCenter)
                actor_labels_layout.addWidget(actor_label)

        except:
            actor_label = QLabel(favorite_actors)
            actor_label.setAlignment(Qt.AlignCenter)
            actor_labels_layout.addWidget(actor_label)

        # Add "See All" button
        actor_see_all = QPushButton("See All")
        # Connect the button click to see_all_actors function
        actor_see_all.clicked.connect(lambda: self.see_all_actors(favorite_actors))
        actor_labels_layout.addWidget(actor_see_all)

        # Create a QWidget to hold the QLabel widgets
        actor_labels_widget = QWidget()
        actor_labels_widget.setLayout(actor_labels_layout)

        # Add the actor_labels_widget to your main layout
        layout.addWidget(actor_labels_widget, 3, 0)  # Row 3, Col 0

        # Your favorite genre based on the average rating you have given to movies/series of that genre
        favorite_genre_label = QLabel("<h3>Your Favorite Genres</h3>")
        favorite_genre_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_genre_label, 0, 2, 1, 2)  # Row 0, Col 2-3

        # Get the favorite genre
        favorite_genres = self.get_favorite_genre(ratings_data)

        # Create a QVBoxLayout to add QLabel widgets
        genre_labels_layout = QVBoxLayout()

        # Iterate through the favorite genres and add them to QLabel widgets
        for genre, info in favorite_genres[:5]:
            genre_label = QLabel(f"<b>{genre}:</b> {info[0]:.2f}/10 ({info[1]} titles) with {info[2]:.2f} ❤️")
            genre_label.setAlignment(Qt.AlignCenter)
            genre_labels_layout.addWidget(genre_label)

        # Add "See All" button
        genre_see_all = QPushButton("See All")
        # Connect the button click to see_all_genres function
        genre_see_all.clicked.connect(lambda: self.see_all_genres(favorite_genres))
        genre_labels_layout.addWidget(genre_see_all)

        # Create a QWidget to hold the QLabel widgets
        genre_labels_widget = QWidget()
        genre_labels_widget.setLayout(genre_labels_layout)

        # Add the genre_labels_widget to your main layout
        layout.addWidget(genre_labels_widget, 1, 2)  # Row 1, Col 2

        # Your favorite TV series based on the average rating you have given to its episodes
        favorite_tv_series_label = QLabel("<h3>Your Favorite TV Shows</h3>")
        favorite_tv_series_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_tv_series_label, 4, 0, 1, 2)  # Row 4, Col 0-1

        # Get the favorite TV series
        favorite_tv_series = self.get_favorite_tv_series(ratings_data)

        # Create a QVBoxLayout to add QLabel widgets
        tv_labels_layout = QVBoxLayout()

        # Iterate through the favorite series and add them to QLabel widgets
        for tv, info in favorite_tv_series[:5]:
            tv_label = QLabel(f"<b>{tv}:</b> {info[0]}/10 ({info[1]:.2f}/10 average episode rating in {info[2]} episodes) with {info[-1]:.2f} ❤️")
            tv_label.setAlignment(Qt.AlignCenter)
            tv_labels_layout.addWidget(tv_label)

        # Add "See All" button
        tv_see_all = QPushButton("See All")
        # Connect the button click to see_all_tv_series function
        tv_see_all.clicked.connect(lambda: self.see_all_tv_series(favorite_tv_series))
        tv_labels_layout.addWidget(tv_see_all)

        # Create a QWidget to hold the QLabel widgets
        tv_labels_widget = QWidget()
        tv_labels_widget.setLayout(tv_labels_layout)

        # Add the tv_labels_widget to main layout
        layout.addWidget(tv_labels_widget, 5, 0)    # Row 5, Col 0

        # Your favorite years based on the average rating you have given to movies/series released in that year
        favorite_year_label = QLabel("<h3>Your Favorite Years</h3>")
        favorite_year_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(favorite_year_label, 2, 2, 1, 2)  # Row 2, Col 2-3

        # Get the favorite years
        chronological_years, year_stats = self.get_favorite_year(ratings_data)
        print(chronological_years)

        # Create a QVBoxLayout to add QLabel widgets
        year_labels_layout = QVBoxLayout()

        # Iterate through the favorite years and add them to QLabel widgets
        for year, info in year_stats[:5]:
            year_label = QLabel(f"<b>{year}:</b> {info[0]:.2f}/10 ({info[1]} titles) with {info[2]:.2f} ❤️")
            year_label.setAlignment(Qt.AlignCenter)
            year_labels_layout.addWidget(year_label)

        # Add "See All" button
        year_see_all = QPushButton("See All")

        # Connect the button click to see_all_years function
        year_see_all.clicked.connect(lambda: self.see_all_years(chronological_years, year_stats))
        year_labels_layout.addWidget(year_see_all)

        # Create a QWidget to hold the QLabel widgets
        year_labels_widget = QWidget()
        year_labels_widget.setLayout(year_labels_layout)

        # Add the year_labels_widget to main layout
        layout.addWidget(year_labels_widget, 3, 2, 1, 2)  # Row 3, Col 2

        # Watchlist statistics
        watchlist_stats_label = QLabel("<h3>Your Watchlist Statistics</h3><br>"
                                       "<b>Top Title Types</b><br>")
        watchlist_stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(watchlist_stats_label, 4, 2, 1, 2)  # Row 4, Col 2-3

        # Get the watchlist statistics
        watchlist_type_stats, watchlist_genre_stats = self.get_watchlist_stats()

        # Create a QVBoxLayout to add QLabel widgets
        watchlist_stats_layout = QVBoxLayout()

        # Iterate through the watchlist statistics and add them to QLabel widgets
        for stat in watchlist_type_stats[:5]:
            watchlist_type_stat_label = QLabel(f"<b>{stat[0]}:</b> {stat[1][0]} ({stat[1][1]:.2f}%)")
            watchlist_type_stat_label.setAlignment(Qt.AlignCenter)
            watchlist_stats_layout.addWidget(watchlist_type_stat_label)

        watchlist_stats_layout.addWidget(QLabel("<br><center><b>Top Genres</b></center><br>"))

        for stat in watchlist_genre_stats[:5]:
            watchlist_genre_stat_label = QLabel(f"<b>{stat[0]}:</b> {stat[1][0]} ({stat[1][1]:.2f}%)")
            watchlist_genre_stat_label.setAlignment(Qt.AlignCenter)
            watchlist_stats_layout.addWidget(watchlist_genre_stat_label)


        # Add "See All" button
        watchlist_stats_see_all = QPushButton("See All")
        # Connect the button click to see_all_watchlist_stats function
        watchlist_stats_see_all.clicked.connect(lambda: self.see_all_watchlist_stats(watchlist_type_stats, watchlist_genre_stats))
        watchlist_stats_layout.addWidget(watchlist_stats_see_all)

        # Create a QWidget to hold the QLabel widgets
        watchlist_stats_widget = QWidget()
        watchlist_stats_widget.setLayout(watchlist_stats_layout)

        # Add the watchlist_stats_widget to your main layout
        layout.addWidget(watchlist_stats_widget, 5, 2)  # Row 5, Col 2

        self.setLayout(layout)

        # Change the cursor back to the default cursor
        QApplication.restoreOverrideCursor()

    def get_favorite_year(self, ratings_data):
        window.update_result_label("Calculating your favorite years...")
        app.processEvents()
        time.sleep(1.5)

        # Create a dictionary to hold the year stats
        year_ratings = {}
        year_title_count = {}

        # Loop through the ratings_data list
        for item in ratings_data:
            # Check if the title type is not empty
            if item['Title Type'] != "":
                print(item['Original Title'])
                print(item['Year'])
                # Extract year and rating
                try:
                    year = int(item['Year'])
                    rating = float(item['Your Rating'])
                except:
                    continue

                # Check if the year is already in the dictionary
                if year in year_ratings:
                    # Add the rating to the existing year
                    year_ratings[year] += rating
                    year_title_count[year] += 1

                else:
                    # Add the year and rating to the dictionary
                    year_ratings[year] = rating
                    year_title_count[year] = 1

        # Check if there are any ratings
        if year_ratings:
            # Calculate the average rating for each year
            for year in year_ratings:
                year_ratings[year] /= year_title_count[year]

            # Calculate the love formula for each year
            year_love_formulas = {
                year: (avg_rating, year_title_count[year],
                       ((avg_rating ** 5) * (year_title_count[year] ** 1.2)))
                for year, avg_rating in year_ratings.items()
            }

            # Sort the years by ascending order (earliest to latest)
            chronological_years = sorted(year_love_formulas.items(), key=lambda x: x[0])

            # Sort the years by the love_formula in descending order
            best_years = sorted(year_love_formulas.items(), key=lambda x: x[1][2], reverse=True)

            # Choose a random year
            random_year = random.choice(best_years)

            if random_year[0] < 1900:
                jokes_list = [f"{random_year[0]}? You are definitely a time traveler.",
                              f"You are a vampire. This is the only way you could have watched a movies from {random_year[0]}.",
                              f"Wow, you are old. You watched movies from {random_year[0]}.",
                              f"Did they even have cameras in {random_year[0]}? How did you watch a movie from that year?",
                              f"Did you know that {random_year[0]} is the year that the first movie was made?<br><br>Well, I lied, but it must be close."]
            if random_year[0] >= 1900 and random_year[0] < 1930:
                jokes_list = [f"Do you sometimes watch movies in library? Because you watched a movie from {random_year[0]}. You probably needed a silent film or something.",
                              f"{random_year[0]}? You are either a cinephile or a historian. Or both."]
            if random_year[0] >= 1930 and random_year[0] < 1960:
                jokes_list = [f"Some people think {random_year[0]} is a legendary year for movies. You probably agree with them.",
                              f"There are a lot of arguments about whether {random_year[0]} is a good or bad year for cinema, you seem to like it.",
                              f"Quick! What is the first movie that comes to your mind when you think of {random_year[0]}?"]
            if random_year[0] >= 1960 and random_year[0] < 1980:
                jokes_list = [f"Ah, {random_year[0]}: golden age of sci-fi...",
                              f"I have a question: How did you watched that one movie from {random_year[0]}?<br>In the cinema? On VHS? From your laptop?",
                              f"Surely when I hear {random_year[0]}, I think of Blockbuster. Good times."]
            if random_year[0] >= 1980 and random_year[0] < 2000:
                jokes_list = [f"I see {random_year[0]} here. Wonder what did you watch from that year, Disney Renaissance?",
                              f"Ah, {random_year[0]}: golden age of action movies...",
                              f"{random_year[0]} means Spielberg or Tarantino to me. Let's see what you've got."]
            if random_year[0] >= 2000 and random_year[0] < 2010:
                jokes_list = [f"Ah, {random_year[0]}: the very beginnings of quality standalone superhero movies.",
                              f"Hmm, I bet {random_year[0]} in your ratings history means some indie cinema.",
                              f"{random_year[0]}? I'm guessing Nolan or Fincher."]
            if random_year[0] >= 2010 and random_year[0] < 2020:
                jokes_list = [f"{random_year[0]} can be a lot of things. I'm guessing you watched some Marvel movies, though.",
                              f"{random_year[0]} is like a box of chocolates. You never know what you're gonna get.",
                              f"Oh, boy. Half of {random_year[1][1]} titles you've watched from {random_year[0]} are the greatest cinema ever and the other half are otter dogshit."]
            if random_year[0] >= 2020:
                jokes_list = [f"I see {random_year[0]} here. You seem to be pretty up to date with the latest watchables.",
                              f"{random_year[0]}? Pandemic cinema, huh?",
                              f"{random_year[0]}? You must go to the cinema a lot. Or you have a lot of streaming services."]

            # Choose a random joke
            random_joke = random.choice(jokes_list)

            # Update the result label
            window.update_result_label(f"{random_joke}")
            app.processEvents()
            time.sleep(1.5)

            # Return the sorted year stats
            return chronological_years, best_years

        else:
            return "N/A"    # Return "N/A" if there are no ratings

    def see_all_years(self, chronological_years, year_stats):
        # Create a new QDialog to show all years
        dialog = QDialog()
        dialog.setWindowTitle("All Years")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(1400, 800)

        layout = QVBoxLayout()

        # If there are too many directors, show them in a table
        if year_stats:
            table = SortableTable(len(year_stats), 4)
            table.setHorizontalHeaderLabels(["Year", "Average Rating", "Rated Titles", "Your Love For The Year"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row, (year, info) in enumerate(year_stats):
                # Convert data to strings
                year_str = str(year)
                avg_rating_str = f"{info[0]:.2f}"
                title_count_str = str(info[1])
                your_love_str = f"{info[2]:.4f}"

                # Create QTableWidgetItem objects from the strings
                table.setItem(row, 0, QTableWidgetItem(year_str))
                table.setItem(row, 1, QTableWidgetItem(avg_rating_str))
                table.setItem(row, 2, QTableWidgetItem(title_count_str))
                table.setItem(row, 3, QTableWidgetItem(your_love_str))

            layout.addWidget(table)

            # Create 3 buttons to see graphs: average rating, title count, love formula
            graph_buttons_layout = QVBoxLayout()

            # Love formula graph
            love_formula_graph_button = QPushButton("Your Favorite Years Graph")
            love_formula_graph_button.clicked.connect(lambda: self.show_years_graph(chronological_years))
            graph_buttons_layout.addWidget(love_formula_graph_button)

            layout.addLayout(graph_buttons_layout)

        else:
            no_years_label = QLabel("You have no favorite years.")
            layout.addWidget(no_years_label)

        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

    def show_years_graph(self, chronological_years):
        # Create a new QDialog to show all the directors
        dialog = QDialog()
        dialog.setWindowTitle("All Years")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(1400, 800)

        layout = QVBoxLayout()
        self.setLayout(layout)

        graph_text_label = QLabel("Hover over the bars to see how much you love each year.")

        # If there are any years, show them in a graph
        if chronological_years:
            # Create a list of years and love formulas
            title_counts = [year[1][1] for year in chronological_years]
            avg_ratings = [year[1][0] for year in chronological_years]
            love_formulas = [year[1][2] for year in chronological_years]

            years = [year[0] for year in chronological_years]

            # Fill in the missing years
            for year in range(min(years), max(years) + 1):
                if year not in years:
                    years.append(year)
                    title_counts.append(0)
                    avg_ratings.append(0)
                    love_formulas.append(0)

            # Sort newly added years and normalized values
            years, title_counts, avg_ratings, love_formulas = zip(*sorted(zip(years, title_counts, avg_ratings, love_formulas)))

            # Normalize title_counts, avg_ratings and love_formulas to be between 0 and 10 (for better visualization)
            normalized_title_counts = [10 * (title_count / max(title_counts)) for title_count in title_counts]
            normalized_avg_ratings = [10 * (avg_rating / max(avg_ratings)) for avg_rating in avg_ratings]
            normalized_love_formulas = [10 * (love_formula / max(love_formulas)) for love_formula in love_formulas]

            # Set up the figure and axes
            fig, ax = plt.subplots()

            # Set the title
            ax.set_title("Your Favorite Years")

            # Set the x and y labels
            ax.set_xlabel("Year")
            ax.set_ylabel("Your Year Statistics")

            # Find the maximum value of the normalized values
            max_value = max(max(normalized_title_counts), max(normalized_avg_ratings), max(normalized_love_formulas))

            # Set the x and y ticks
            ax.set_xticks(years)
            ax.set_yticks(np.arange(0, 10.5, 0.5))

            # Plot average rating as a dotted line, love formula as a solid line and title count as bars
            ax.plot(years, normalized_avg_ratings, color="#4fbeff", linestyle="--", linewidth=2.5, label="Average Rating")
            ax.plot(years, normalized_love_formulas, color="#940000", linewidth=2.5, label="Your Love For the Year")
            ax.bar(years, normalized_title_counts, color="#fcba03", label="Rated Titles")

            # Rotate the x ticks
            plt.xticks(rotation=60)

            # Add legend
            ax.legend(loc="best")

            # Embed the plot in the dialog
            canvas = plt.gcf().canvas
            canvas.draw()
            plt.close(fig)
            plt.show()
            # Extend into the whole row
            layout.addWidget(canvas)
            # Stretch the canvas to the whole row and column
            layout.setStretch(0, 1)

            # Hover over the bars to see the love formula
            def hover(event):
                # If the mouse is over a bar
                if event.xdata is not None and event.ydata is not None:
                    # Get the position of the cursor
                    cursor_pos = (event.x, event.y)

                    # Get the index of the bar
                    year = int(event.xdata)

                    # Check if the hovered year is in the years list, if yes, get the index of the year in years
                    if year in years:
                        year_index = years.index(year)

                        # Get the title count of the year
                        title_count = title_counts[year_index]

                        # Get the average rating of the year
                        avg_rating = avg_ratings[year_index]

                        # Get the love formula of the year
                        love_formula = love_formulas[year_index]

                        print(f"years[year_index]: {years[year_index]}\thovered: {year}\tlove_formula: {love_formula}")
                        print(f"years[year_index]: {years[year_index]}\thovered: {year}\tavg_rating: {avg_rating}")
                        print(f"years[year_index]: {years[year_index]}\thovered: {year}\ttitle_count: {title_count}")

                    # If not, set the love formula, average rating and title count to 0
                    else:
                        love_formula = 0
                        avg_rating = 0
                        title_count = 0


                    graph_text_label.setText(f"<h3>{year}:</h3>\t<b>Your Love:</b> {love_formula:.2f}\t<b>Average Rating:</b> {avg_rating:.2f}\t<b>Rated Titles:</b> {title_count}")
                    app.processEvents()

            # Connect the hover function to the mouse move event
            canvas.mpl_connect("motion_notify_event", hover)

        else:
            no_years_label = QLabel("You have no favorite years.")
            layout.addWidget(no_years_label)

        layout.addWidget(graph_text_label)
        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

    def get_watchlist_stats(self):
        window.update_result_label("Calculating your watchlist statistics...")
        app.processEvents()
        time.sleep(1.5)

        # Read the watchlist.csv file into a list
        with open('watchlist.csv', 'r', encoding='utf-8') as file:
            watchlist_data = list(csv.DictReader(file))

        # Calculate the number of movies and series in the watchlist
        movie_count = 0
        series_count = 0
        episode_count = 0
        mini_series_count = 0
        short_count = 0
        tv_movie_count = 0
        tv_special_count = 0
        video_count = 0
        video_game_count = 0
        podcast_count = 0
        podcast_episode_count = 0
        tv_miniseries_count = 0
        tv_short_count = 0
        documentary_count = 0
        music_video_count = 0

        for item in watchlist_data:
            if item['Title Type'] == "Movie":
                movie_count += 1
            elif item['Title Type'] == "TV Series":
                series_count += 1
            elif item['Title Type'] == "TV Episode":
                episode_count += 1
            elif item['Title Type'] == "TV Mini Series":
                mini_series_count += 1
            elif item['Title Type'] == "Short":
                short_count += 1
            elif item['Title Type'] == "TV Movie":
                tv_movie_count += 1
            elif item['Title Type'] == "TV Special":
                tv_special_count += 1
            elif item['Title Type'] == "Video":
                video_count += 1
            elif item['Title Type'] == "Video Game":
                video_game_count += 1
            elif item['Title Type'] == "Podcast Series":
                podcast_count += 1
            elif item['Title Type'] == "Podcast Episode":
                podcast_episode_count += 1
            elif item['Title Type'] == "TV Mini Series":
                tv_miniseries_count += 1
            elif item['Title Type'] == "TV Short":
                tv_short_count += 1
            elif item['Title Type'] == "Documentary":
                documentary_count += 1
            elif item['Title Type'] == "Music Video":
                music_video_count += 1

        title_count = len(watchlist_data)

        # Create a dictionary of title types, their counts and percentages to return
        type_stats = { "Movies": (movie_count, movie_count / title_count * 100),
                          "Series": (series_count, series_count / title_count * 100),
                          "Episodes": (episode_count, episode_count / title_count * 100),
                          "Mini-Series": (mini_series_count, mini_series_count / title_count * 100),
                          "Short Films": (short_count, short_count / title_count * 100),
                          "TV Movies": (tv_movie_count, tv_movie_count / title_count * 100),
                          "TV Specials": (tv_special_count, tv_special_count / title_count * 100),
                          "Videos": (video_count, video_count / title_count * 100),
                          "Video Games": (video_game_count, video_game_count / title_count * 100),
                          "Podcasts": (podcast_count, podcast_count / title_count * 100),
                          "Podcast Episodes": (podcast_episode_count, podcast_episode_count / title_count * 100),
                          "TV Mini-Series": (tv_miniseries_count, tv_miniseries_count / title_count * 100),
                          "TV Shorts": (tv_short_count, tv_short_count / title_count * 100),
                          "Documentaries": (documentary_count, documentary_count / title_count * 100),
                          "Music Videos": (music_video_count, music_video_count / title_count * 100)}

        # Sort the title types by the percentage in descending order
        sorted_types = sorted(type_stats.items(), key=lambda x: x[1][1], reverse=True)

        # Get the count of each individual genre in the watchlist
        genre_count = {}
        for item in watchlist_data:
            if item['Title Type'] == "Movie" or item['Title Type'] == "TV Series" or item['Title Type'] == "TV Episode"\
                    or item['Title Type'] == "TV Mini Series" or item['Title Type'] == "Short"\
                    or item['Title Type'] == "TV Movie" or item['Title Type'] == "TV Special"\
                    or item['Title Type'] == "Video" or item['Title Type'] == "Video Game"\
                    or item['Title Type'] == "Podcast Series" or item['Title Type'] == "Podcast Episode"\
                    or item['Title Type'] == "TV Mini Series" or item['Title Type'] == "TV Short"\
                    or item['Title Type'] == "Documentary" or item['Title Type'] == "Music Video":

                genres = item['Genres'].split(", ")

                for genre in genres:
                    if genre in genre_count:
                        genre_count[genre] += 1
                    else:
                        genre_count[genre] = 1

                # Create a dictionary of genres, their counts and percentages to return
                genre_stats = {genre: (genre_count[genre], genre_count[genre] / title_count * 100) for genre in genre_count}

                # Sort the genres by the percentage in descending order
                sorted_genres = sorted(genre_stats.items(), key=lambda x: x[1][1], reverse=True)

        random_genre = random.choice(sorted_genres)[0]
        random_type = random.choice(sorted_types)[0]
        random_title = random.choice(watchlist_data)['Title']

        jokes_list = [f"Looks like you wanna watch an unhealthy amount of {sorted_genres[0][0]} {sorted_types[0][0]}.",
                      f"{random_genre} {random_type}? An interesting combination.",
                      f"Do you really wanna watch {random_title}? I wouldn't."]

        # Make a joke if there are any titles in the watchlist other than movies, series, episodes and mini-series
        if short_count > 0:
            jokes_list.append(f"You have {short_count} short films in your watchlist.<br><br>You must be a busy person if you want to watch shorts.")
        if tv_movie_count > 0:
            jokes_list.append(f"You have {tv_movie_count} TV movies in your watchlist.<br><br>I hope you know that they are not real movies.")
        if tv_special_count > 0:
            jokes_list.append(f"TV SPECIALS? REALLY? You really have {tv_special_count} TV specials in your watchlist.<br><br>Wow.")
        if video_count > 0:
            jokes_list.append(f"You have {video_count} videos in your watchlist.<br><br>What even is a video? Go on YouTube or whatever if you want to watch videos, dude.")
        if video_game_count > 0:
            jokes_list.append(f"You have {video_game_count} video games in your watchlist. Why do you use IMDB to keep track of your video games?")
        if podcast_count > 0:
            jokes_list.append(f"You have {podcast_count} podcasts in your watchlist.<br><br>I don't know what to say, just don't listen to Andrew Tate and we are good.")
        if podcast_episode_count > 0:
            jokes_list.append(f"You have {podcast_episode_count} podcast episodes in your watchlist.<br><br>I don't know what to say, just don't listen to Andrew Tate and we are good.")
        if documentary_count > 0:
            jokes_list.append(f"You have {documentary_count} documentaries in your watchlist. I hope you are not a flat earther.")
        if music_video_count > 0:
            jokes_list.append(f"You have {music_video_count} music videos in your watchlist. Spotify is just over there, mate.")
        if tv_short_count > 0:
            jokes_list.append(f"You have {tv_short_count} TV shorts in your watchlist.<br><br>Let me guess, you are a busy person and you don't have time to watch full episodes, right?")


        if 'Adult' in genre_count and genre_count['Adult'] > 0:
            jokes_list.append(f"You have {genre_count['Adult']} adult titles in your watchlist.<br><br>Pervert.")
        if 'Reality-TV' in genre_count and genre_count['Reality-TV'] > 0:
            jokes_list.append(f"You have {genre_count['Reality-TV']} reality TV shows in your watchlist.<br><br>"
                              f"I hope you know that they are not real.")
        if 'Talk-Show' in genre_count and genre_count['Talk-Show'] > 0:
            jokes_list.append(f"You have {genre_count['Talk-Show']} talk shows in your watchlist.<br><br>Why?")
        if 'News' in genre_count and genre_count['News'] > 0:
            jokes_list.append(f"You have {genre_count['News']} news shows in your watchlist.<br><br>"
                              f"My brother, you are not missing out on anything, trust me.")
        if 'Game-Show' in genre_count and genre_count['Game-Show'] > 0:
            jokes_list.append(f"You have {genre_count['Game-Show']} game shows in your watchlist.<br><br>"
                              f"I don't know what a game show is, but I am sure it is not a real show.")
        if 'Film-Noir' in genre_count and genre_count['Film-Noir'] > 0:
            jokes_list.append(f"You have {genre_count['Film-Noir']} film noir titles in your watchlist.<br><br>Not everything is black and white, you know??")
        if 'Musical' in genre_count and genre_count['Musical'] > 0:
            jokes_list.append(f"You have {genre_count['Musical']} musicals in your watchlist.<br><br>Are you a theater kid?")
        if 'Music' in genre_count and genre_count['Music'] > 0:
            jokes_list.append(f"You have {genre_count['Music']} music titles in your watchlist.<br><br>")
        if 'Sport' in genre_count and genre_count['Sport'] > 0:
            jokes_list.append(f"You have {genre_count['Sport']} sports titles in your watchlist.<br><br>Okay, I guess?")
        if 'Drama' in genre_count and genre_count['Drama'] > 0:
            jokes_list.append(f"You have {genre_count['Drama']} drama titles in your watchlist.<br><br>Are you a drama queen?")
            jokes_list.append(f"You have {genre_count['Drama']} drama titles in your watchlist.<br><br>"
                              f"Having 'drama' as a genre in your IMDb watchlist is like having 'food' as a cuisine in your restaurant menu: "
                              f"everything is a food and every goddamn movie is a drama.")

        window.update_result_label(random.choice(jokes_list))
        app.processEvents()
        time.sleep(5)

        return sorted_types, sorted_genres

    def see_all_watchlist_stats(self, type_stats, genre_stats):
        # Create a new QDialog to show all the watchlist statistics
        dialog = QDialog()
        dialog.setWindowTitle("Watchlist Statistics")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(800, 500)

        layout = QVBoxLayout()

        # If there are any watchlist statistics, show them in two tables in a QHBoxLayout
        if type_stats and genre_stats:
            # Create a QHBoxLayout to add the two tables
            tables_layout = QHBoxLayout()

            # Create a QTableWidget to show the title type statistics
            type_table = QTableWidget()
            type_table.setRowCount(len(type_stats))
            type_table.setColumnCount(2)
            type_table.setHorizontalHeaderLabels(["Title Type", "Count"])
            type_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            type_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            type_table.setEditTriggers(QTableWidget.NoEditTriggers)

            # Iterate through the title type statistics and add them to the table
            for row, stat in enumerate(type_stats):
                type_table.setItem(row, 0, QTableWidgetItem(stat[0]))
                type_table.setItem(row, 1, QTableWidgetItem(f"{stat[1][0]} ({stat[1][1]:.2f}%)"))

            # Add the table to the QHBoxLayout
            tables_layout.addWidget(type_table)

            # Create a QTableWidget to show the genre statistics
            genre_table = QTableWidget()
            genre_table.setRowCount(len(genre_stats))
            genre_table.setColumnCount(2)
            genre_table.setHorizontalHeaderLabels(["Genre", "Count"])
            genre_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            genre_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            genre_table.setEditTriggers(QTableWidget.NoEditTriggers)

            # Iterate through the genre statistics and add them to the table
            for row, stat in enumerate(genre_stats):
                genre_table.setItem(row, 0, QTableWidgetItem(stat[0]))
                genre_table.setItem(row, 1, QTableWidgetItem(f"{stat[1][0]} ({stat[1][1]:.2f}%)"))

            # Add the table to the QHBoxLayout
            tables_layout.addWidget(genre_table)

            # Add the QHBoxLayout to the QVBoxLayout
            layout.addLayout(tables_layout)

        else:
            no_stats_label = QLabel("You have no titles in your watchlist.")
            layout.addWidget(no_stats_label)

        dialog.setLayout(layout)
        dialog.exec_()

    def get_favorite_director(self, ratings_data):
        window.update_result_label("Calculating your favorite directors...")
        app.processEvents()
        time.sleep(1.5)

        director_ratings = {}
        director_title_counts = {}
        director_titles = {}

        # Loop through the ratings_data list
        for item in ratings_data:
            # Check if the title type is "Movie"
            if item['Title Type'] == "Movie" or item['Title Type'] == "Short" or item['Title Type'] == "TV Movie":
                # Extract director and rating
                director = item['Directors']
                rating = float(item['Your Rating'])

                # Check if the director is already in the dictionary
                if director in director_ratings:
                    # Add the rating to the existing director
                    director_ratings[director] += rating
                    director_title_counts[director] += 1
                    director_titles[director].append(item['Original Title'])
                else:
                    # Add the director to the dictionary
                    director_ratings[director] = rating
                    director_title_counts[director] = 1
                    director_titles[director] = [item['Original Title']]


        # Check if there are any ratings
        if director_ratings:
            # Calculate the average rating for each director
            director_average_ratings = {
                director: director_ratings[director] / director_title_counts[director]
                for director in director_ratings
            }

            # Calculate the love_formula for each director
            director_love_formulas = {
                director: (avg_rating, director_title_counts[director], ((avg_rating ** 5) * (director_title_counts[director] ** 1.2)) / 1000)
                for director, avg_rating in director_average_ratings.items()
            }

            # Sort the directors by the love_formula in descending order
            sorted_directors = sorted(director_love_formulas.items(), key=lambda x: x[1][2], reverse=True)

            # Select a random director from the dictionary and show it
            random_director = random.choice(list(director_ratings.keys()))

            jokes_list = [f"You have rated {len(director_ratings)} directors.<br><br>That's a lot of directors.",
                          f"I see {random_director} here.<br><br>I wonder if you really like them or you're just pretentious.",
                          f"{random_director}? That's a weird name.",
                          f"{random_director}? We've got a cinephile here, folks!",
                          f"{sorted_directors[0][0]}? I don't know who that is.<br><br>Oops, sorry! They were your favorite director.",
                          f"Do I see {random_director} here? Interesting...",
                          f"{random_director}?! Do you even watch cinema?!",
                          f"Ladies and gentlemen, {random_director}!",
                          f"Do you ever think that your life would be better if {random_director} directed it?<br><br>Me neither."]

            random_title = random.choice(director_titles[random_director])

            jokes_list.extend([f"Do you love {random_director} because of {random_title}?",
                               f"Are you really telling me that you love {random_director} who directed the abomination that is {random_title}?",
                               f"I believe {random_director} is a national treasure and {random_title} is a masterpiece. I am tired of pretending it's not.",
                               f"{random_director} is a great director, but {random_title} is a terrible movie. I am sorry.",
                               f"{random_director} is a terrible director, but {random_title} is a great movie. I am not sorry."])


            if len(director_titles[random_director]) > 1:
                random_title_2 = random.choice([title for title in director_titles[random_director] if title != random_title])
                jokes_list.extend([f"Between {random_title} and {random_title_2}, {random_director} has definitely been kidnapped and replaced by a doppelganger.",
                                   f"Did you know that {random_director} directed both {random_title} and {random_title_2}?<br><br>This isn't a trick question, it's true.",
                                   f"You have 5 seconds: which {random_director} movie is better, {random_title} or {random_title_2}?"])

            if len(director_ratings) > 1:
                random_director_2 = random.choice([director in director_ratings.keys()])

                while(random_director_2 == random_director):
                    random_director_2 = random.choice([director in director_ratings.keys()])

                jokes_list.extend([f"Did you know that {random_director} and {random_director_2} are siblings?<br><br>No, you did not! Because they are not. Probably...",
                                   f"Seems like your dream movie would be directed by {random_director} and {random_director_2}.<br><br>That would be an interesting collab.",
                                   f"Seems like you are a fan of {random_director} and {random_director_2}.<br><br>That's a weird combination, and I love it.",
                                   f"Your range is amazing. You love {random_director} and {random_director_2}.<br><br>That's like loving salt on pineapple. You have to try it to understand."])

            if random_director == "Christopher Nolan":
                nolan_list = ["time", "Hans Zimmer", "Michael Caine", "practical effects"]
                window.update_result_label(f"Seems like you are obsessed with Christopher Nolan as much as Christopher Nolan is obsessed with {random.choice(nolan_list)}.")

            elif random_director == "Quentin Tarantino":
                tarantino_list = ["feet", "N-word", "Uma Thurman", "violence", "70s"]
                window.update_result_label(f"Seems like you are obsessed with Quentin Tarantino as much as Quentin Tarantino is obsessed with {random.choice(tarantino_list)}.")

            elif random_director == "Martin Scorsese":
                scorcese_list = ["gangsters", "Robert De Niro", "Leonardo DiCaprio"]
                window.update_result_label(f"Seems like you are obsessed with Martin Scorsese as much as Martin Scorsese is obsessed with {random.choice(scorcese_list)}.")

            elif random_director == "Stanley Kubrick":
                kubrick_list = ["symmetry", "colors", "the number 42", "the moon"]
                window.update_result_label(f"Seems like you are obsessed with Stanley Kubrick as much as Stanley Kubrick is obsessed with {random.choice(kubrick_list)}.")

            elif random_director == "David Fincher":
                fincher_list = ["the color green", "Trent Reznor"]
                window.update_result_label(f"Seems like you are obsessed with David Fincher as much as David Fincher is obsessed with {random.choice(fincher_list)}.")

            elif random_director == "Steven Spielberg":
                spielberg_list = ["aliens", "John Williams", "the 80s", "dinosaurs", "sharks", "Tom Hanks", "the military"]
                window.update_result_label(f"Seems like you are obsessed with Steven Spielberg as much as Steven Spielberg is obsessed with {random.choice(spielberg_list)}.")

            elif random_director == "Alfred Hitchcock":
                hitchcock_list = ["blondes", "suspense"]
                window.update_result_label(f"Seems like you are obsessed with Alfred Hitchcock as much as Alfred Hitchcock is obsessed with {random.choice(hitchcock_list)}.")

            elif random_director == "Tim Burton":
                burton_list = ["Johnny Depp", "Helena Bonham Carter", "the color black", "stop motion", "Danny Elfman"]
                window.update_result_label(f"Seems like you are obsessed with Tim Burton as much as Tim Burton is obsessed with {random.choice(burton_list)}.")

            elif random_director == "Wes Anderson":
                anderson_list = ["symmetry", "pastel colors", "ensemble casts"]
                window.update_result_label(f"Seems like you are obsessed with Wes Anderson as much as Wes Anderson is obsessed with {random.choice(anderson_list)}.")

            else:
                window.update_result_label(random.choice(jokes_list))
                app.processEvents()
                time.sleep(5)

            return sorted_directors
        else:
            return "N/A"  # Return "N/A" and 0.0 for average rating when there are no ratings

    def see_all_directors(self, favorite_directors):
        # Create a new QDialog to show all the directors
        dialog = QDialog()
        dialog.setWindowTitle("All Directors")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(800, 500)

        layout = QVBoxLayout()

        # If there are too many directors, show them in a table
        if favorite_directors:
            table = SortableTable(len(favorite_directors), 4)
            table.setHorizontalHeaderLabels(["Director", "Average Rating", "Rated Movies", "Your Love For Them"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row, (director, info) in enumerate(favorite_directors):
                # Convert data to strings
                director_str = str(director)
                avg_rating_str = f"{info[0]:.2f}"
                title_count_str = str(info[1])
                your_love_str = f"{info[2]:.4f}"

                # Create QTableWidgetItem objects from the strings
                table.setItem(row, 0, QTableWidgetItem(director_str))
                table.setItem(row, 1, QTableWidgetItem(avg_rating_str))
                table.setItem(row, 2, QTableWidgetItem(title_count_str))
                table.setItem(row, 3, QTableWidgetItem(your_love_str))

            layout.addWidget(table)


        else:
            no_directors_label = QLabel("You have no favorite directors.")
            layout.addWidget(no_directors_label)

        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

    def get_favorite_actor(self):
        """
        window.update_result_label("Calculating your favorite actors/actresses...")
        app.processEvents()
        time.sleep(1.5)

        actor_ratings = {}
        actor_title_counts = {}
        actor_titles = {}

        # Get the user lists page from user_preferences.txt
        lists_link = checkPreferences()
        ratings_link = lists_link.replace("lists", "ratings")

        # Send an HTTP GET request to fetch the ratings page
        try:
            # Open the URL
            response = browser.open(ratings_link)

            html_content = response.read()

            # Get the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract the movie or TV series details from the list
            movie_details = soup.select('.lister-item-content')

            # Check how many titles are there in the list
            list_details = soup.select(".lister-list-length")
            number_of_titles_str = list_details[0].text.strip()

            # Use a regular expression to extract the integer
            match = re.search(r'\d+', number_of_titles_str)

            if match:
                # The group(0) will contain the first matched integer
                number_of_titles = int(match.group(0))
                window.update_result_label(f"Oh, boy.<br><br>"
                                           f"Found {number_of_titles} titles in your ratings list. That's AT LEAST {number_of_titles} actors/actresses for me to analyze.<br><br>"
                                           f"I may be a robot, but come on...")
                app.processEvents()
                time.sleep(5)

            # Calculate the page count
            page_count = math.ceil(number_of_titles / 100)

            # Append all pages to movie_details
            for page in range(2, page_count + 1):
                window.update_result_label(f"I am {page} layers deep in your ratings and I am too afraid to turn back now!")
                app.processEvents()

                # Find the "NEXT" button at the bottom of the page and extract the link
                next_button = soup.select_one(".lister-page-next")
                next_button_link = next_button['href']

                # Update the ratings_link with the next page link
                ratings_link = f"https://www.imdb.com{next_button_link}"

                try:
                    # Open the URL
                    response = browser.open(ratings_link)

                    # Get the HTML content
                    html_content = response.read()

                    soup = BeautifulSoup(html_content, 'html.parser')

                    # Extract the movie or TV series details from the list
                    movie_details += soup.select('.lister-item-content')

                except mechanize.URLError as e:
                    print(f"An error occurred: {e}")


            # Check if there are any movie details
            if movie_details:
                # Loop through the movie details
                for movie in movie_details:
                    # Get the title
                    title_element = movie.select_one(".lister-item-header a")
                    title = title_element.text.strip()

                    # Extract the title type
                    isEpisode_element = movie.find("small", class_="text-primary")
                    if isEpisode_element:
                        isEpisode = isEpisode_element.text.strip()
                    else:
                        isEpisode = ""

                    # Check if the title type is not an episode
                    if "Episode:" not in isEpisode:
                        # Extract actors and rating
                        # Find the <p> element with directors and actors
                        p_element = movie.select("p.text-muted.text-small a")

                        # Extract the actors from the text of each item in the list
                        actors = [actor.text.strip() for actor in p_element if "dir" not in actor['href']]

                        # Get the rating and directors from ratings.csv and remove directors from actors
                        with open('ratings.csv', 'r') as file:
                            ratings_data = list(csv.DictReader(file))

                            # Loop through the ratings_data list
                            for item in ratings_data:
                                # Check if the title type is "Movie"
                                if item['Title Type'] == "Movie":
                                    # Extract title and rating
                                    rating = int(item['Your Rating'])

                                    # Check if the title is the same as the current title
                                    if title == item['Original Title']:
                                        # Extract directors
                                        directors = item['Directors'].split(", ")

                                        # Remove directors from actors
                                        actors = [actor for actor in actors if actor not in directors]

                                        break

                        # Loop through the actors
                        for actor in actors:
                            # Check if the actor is already in the dictionary
                            if actor in actor_ratings:
                                # Add the rating to the existing actor
                                actor_ratings[actor] += rating
                                actor_title_counts[actor] += 1
                                actor_titles[actor].append(title)
                            else:
                                # Add the actor to the dictionary
                                actor_ratings[actor] = rating
                                actor_title_counts[actor] = 1
                                actor_titles[actor] = [title]

                # Select a random actor from the dictionary and show it
                random_actor = random.choice(list(actor_ratings.keys()))
                # Select a random title from the actor's titles
                random_title = random.choice(actor_titles[random_actor])

                # Select a random_actor_2 and random_actor_3 from the dictionary that is different than each other and random_actor
                random_actor_2 = random.choice([actor for actor in actor_ratings.keys() if actor != random_actor])
                random_actor_3 = random.choice([actor for actor in actor_ratings.keys() if actor != random_actor and actor != random_actor_2])


                jokes_list = [
                    f"Are you {random_actor}? Because only a narcissist would rate themselves {actor_ratings[random_actor] / actor_title_counts[actor]}/10 high...",
                    f"I get {random_actor}, but {random_actor} in {random_title}? Really?",
                    f"I can see why you like {random_actor} so much. I mean, I don't, but I can see why you do...",
                    f"I found {random_actor} in your ratings. Should I call the police?",
                    f"Do you have a crush on {random_actor}? I won't tell anyone...",
                    f"I am not sure if I should be impressed or disgusted by your love for {random_actor}...",
                    f"You watched {random_actor} in {actor_title_counts[random_actor]} titles and I don't know what to do with this information...",
                    f"Seems like you have a thing for {random_actor}...",
                    f"Quick, {random_actor} is coming! Act natural!",
                    f"Fuck, Marry, Kill: {random_actor}, {random_actor_2}, {random_actor_3}<br><br>Waiting for your answer...",
                    f"You reaaally like {random_actor}, and you are objectively right!"]

                if len(actor_titles[random_actor]) > 1:
                    # Select random_title_2 from the actor's titles that is different than random_title
                    random_title_2 = random.choice([title for title in actor_titles[random_actor] if title != random_title])
                    jokes_list.extend([f"I loved {random_actor} in {random_title}, but I am not so sure about {random_title_2}...",
                                      f"Quick question: {random_actor} in {random_title} or {random_title_2}?"])

                # Check if the actor has any formal titles, if not take a random joke from the jokes_list
                has_formal_title = False
                for prefix in ["Sir", "Sire", "Dame", "Madam", "Mistress", "Gentleman", "Mistress",
                               "Mrs.", "Ms.", "Miss", "Lord", "Lady", "Esq.", "Esquire",
                               "Excellency", "Honour", "The Honourable"]:
                    if prefix in random_actor:
                        if random_actor == "Sir Ian McKellen":
                            window.update_result_label(f"{random_actor}? I am no Gandalf, but I approve!")
                        else:
                            # Perform your desired action when a match is found
                            window.update_result_label(f"{random_actor}? Looks royal enough for me...")
                            has_formal_title = True
                        break  # Exit the loop after the first match (optional)

                if not has_formal_title:
                    if "Dr." in random_actor:
                        window.update_result_label(f"{random_actor}? I should bring my apple with me to keep them away!")
                    elif "Prof." in random_actor:
                        window.update_result_label(f"{random_actor}? Why is a professor acting? Shouldn't they be teaching?")
                    elif random_actor == "Bryan Cranston":
                        window.update_result_label(f"{random_actor}? I am the one who rates!")
                    elif random_actor == "Bob Odenkirk":
                        window.update_result_label(f"You watch {random_actor} at Starbucks?<br><br>"
                                                   f"I don't get it, what's the kick? Why doncha do it at home like the rest of us, with a big flat-screen TV, 50 channels of pay-per-view?"
                                                   f"In a Starbucks, that's nice!")
                    elif random_actor == "Aaron Paul":
                        window.update_result_label(f"This is my own private {random_actor} and I will not be harassed... Bitch!")
                    elif random_actor == "Dean Norris":
                        window.update_result_label(f"{random_actor}? Sex gifs.")
                    elif random_actor == "Giancarlo Esposito":
                        window.update_result_label(f"I found here a \"{random_actor}\", but I think I can call him Gus.")
                    else:
                        window.update_result_label(random.choice(jokes_list))

                app.processEvents()
                time.sleep(5)

                # Check if there are any ratings
                if actor_ratings:
                    # Calculate the average rating for each actor
                    actor_average_ratings = {
                        actor: actor_ratings[actor] / actor_title_counts[actor]
                        for actor in actor_ratings
                    }

                    # Calculate the love_formula for each actor
                    actor_love_formulas = {
                        actor: (avg_rating, actor_title_counts[actor],
                                   ((avg_rating ** 5) * (actor_title_counts[actor] ** 1.3)) / 1000)
                        for actor, avg_rating in actor_average_ratings.items()
                    }

                    # Sort the actors by the love_formula in descending order
                    sorted_actors = sorted(actor_love_formulas.items(), key=lambda x: x[1][2], reverse=True)

                    return sorted_actors
                else:
                    return []

        except:
            sorted_actors = (f"An error occurred.\n"
                             f"Please check if your Ratings are public and try again.")
            return sorted_actors
        """

        return "This functionality is not available at the moment due to the changes IMDb made to their website."

    def see_all_actors(self, favorite_actors):
        """
        # Create a new QDialog to show all the actors
        dialog = QDialog()
        dialog.setWindowTitle("All Actors")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(800, 500)

        layout = QVBoxLayout()

        # If there are too many actors, show them in a table
        if favorite_actors:
            table = SortableTable(len(favorite_actors), 4)
            table.setHorizontalHeaderLabels(["Actor", "Average Rating", "Title Count", "Your Love For Them"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row, (actor, info) in enumerate(favorite_actors):
                # Convert data to strings
                actor_str = str(actor)
                avg_rating_str = f"{info[0]:.2f}"
                title_count_str = str(info[1])
                your_love_str = f"{info[2]:.4f}"

                # Create QTableWidgetItem objects from the strings
                table.setItem(row, 0, QTableWidgetItem(actor_str))
                table.setItem(row, 1, QTableWidgetItem(avg_rating_str))
                table.setItem(row, 2, QTableWidgetItem(title_count_str))
                table.setItem(row, 3, QTableWidgetItem(your_love_str))

            layout.addWidget(table)

        else:
            no_actors_label = QLabel("You have no favorite actors.")
            layout.addWidget(no_actors_label)

        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()
        """
        # Show an error pop up
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle("Error")
        error_dialog.setText("This functionality is not available at the moment due to the changes IMDb made to their website.")
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.exec_()


    # Get the favorite genre based on the average rating you have given to movies/series of that genre
    def get_favorite_genre(self, ratings_data):
        window.update_result_label("Calculating your favorite genres...")
        app.processEvents()
        time.sleep(1.5)

        genre_ratings = {}
        genre_title_counts = {}

        # Loop through the ratings_data list
        for item in ratings_data:
            # Check if the title type is not "TV Episode", since the genre of a TV episode is the genre of the TV series
            if item['Title Type'] != "TV Episode":
                # Extract genres and rating
                genres = item['Genres'].split(", ")
                rating = float(item['Your Rating'])

                # Loop through the genres
                for genre in genres:
                    # Check if the genre is already in the dictionary
                    if genre in genre_ratings:
                        # Add the rating to the existing genre
                        genre_ratings[genre] += rating
                        genre_title_counts[genre] += 1
                    else:
                        # Add the genre to the dictionary
                        genre_ratings[genre] = rating
                        genre_title_counts[genre] = 1

        # Select a random genre from the dictionary and show it
        random_genre = random.choice(list(genre_ratings.keys()))

        # Find out if the genre starts with a vowel or a consonant
        if random_genre[0].lower() in "aeiou":
            window.update_result_label(f"Seems like we found an {random_genre} lover...")
        else:
            window.update_result_label(f"Seems like we found a {random_genre} lover...")
        app.processEvents()
        time.sleep(5)

        # Check if there are any ratings
        if genre_ratings:
            # Calculate the average rating for each genre
            genre_average_ratings = {
                genre: genre_ratings[genre] / genre_title_counts[genre]
                for genre in genre_ratings
            }

            # Calculate the love_formula for each genre
            genre_love_formulas = {
                genre: (avg_rating, genre_title_counts[genre],
                           ((avg_rating ** 5) * (genre_title_counts[genre] ** 1.2)) / 1000)
                for genre, avg_rating in genre_average_ratings.items()
            }

            # Sort the genres by the love_formula in descending order
            sorted_genres = sorted(genre_love_formulas.items(), key=lambda x: x[1][2], reverse=True)

            return sorted_genres
        else:
            return "N/A"  # Return "N/A" and 0.0 for average rating when there are no ratings

    def see_all_genres(self, favorite_genres):
        # Create a new QDialog to show all the genres
        dialog = QDialog()
        dialog.setWindowTitle("All Genres")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(800, 500)

        layout = QVBoxLayout()

        # If there are too many genres, show them in a table
        if favorite_genres:
            table = SortableTable(len(favorite_genres), 4)
            table.setHorizontalHeaderLabels(["Genre", "Average Rating", "Title Count", "Your Love For Them"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row, (genre, info) in enumerate(favorite_genres):
                # Convert data to strings
                genre_str = str(genre)
                avg_rating_str = f"{info[0]:.2f}"
                title_count_str = str(info[1])
                your_love_str = f"{info[2]:.4f}"

                # Create QTableWidgetItem objects from the strings
                table.setItem(row, 0, QTableWidgetItem(genre_str))
                table.setItem(row, 1, QTableWidgetItem(avg_rating_str))
                table.setItem(row, 2, QTableWidgetItem(title_count_str))
                table.setItem(row, 3, QTableWidgetItem(your_love_str))

            layout.addWidget(table)

        else:
            no_genres_label = QLabel("You have no favorite genres.")
            layout.addWidget(no_genres_label)

        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

    # Get the favorite TV series based on the average rating you have given to its episodes
    def get_favorite_tv_series(self, ratings_data):
        window.update_result_label("Calculating your favorite TV series...")
        app.processEvents()
        time.sleep(1.5)

        tv_series_data = {}

        # Check the rewatch count of each TV series
        rewatched_series = self.get_rewatch_counts()

        # Loop through the ratings_data list
        for item in ratings_data:

            # Check if the title type is TV series
            if item['Title Type'] == "TV Series":
                series_name = item['Original Title']
                rating = float(item['Your Rating'])

                if series_name not in tv_series_data:
                    tv_series_data[series_name] = {
                        'Your Rating': 0,
                        'Average Episode Rating': 0.0,
                        'Love Formula': 0.0,
                        'Episode Count': 0,  # Initialize episode count
                        'Rewatch Count': 1  # Initialize rewatch count
                    }

                # Update TV series rating
                tv_series_data[series_name]['Your Rating'] = rating
                tv_series_data[series_name]['Average Episode Rating'] += 0.0
                tv_series_data[series_name]['Episode Count'] += 0

                if series_name in rewatched_series:
                    tv_series_data[series_name]['Rewatch Count'] = rewatched_series[series_name]

            # Check if the title type is "TV Episode"
            elif item['Title Type'] == "TV Episode":
                # Split the title into series name and episode name
                # There are four possibilities:
                # "Series Name: Episode Name",
                # "Series Name: 'Episode Name: Episode Part'",
                # "'IP Name: Series Name': Episode Name",
                # "'IP Name: Series Name': 'Episode Name: Episode Part'"
                title_split = item['Original Title'].split(":")

                # Determine how many colons are in the title and act accordingly
                num_colons = len(title_split)

                if num_colons == 2:
                    # Format: "Series Name: Episode Name"
                    series_name = title_split[0]
                elif num_colons == 3:
                    window.update_result_label(f"Checking out individual episodes such as:<br>"
                                               f"{item['Original Title']}")
                    app.processEvents()

                    # Check the known TV titles first (to avoid unnecessary requests)
                    known_tv_titles = []

                    # Check if the "known_tv_titles.txt" file exists
                    if os.path.exists("known_tv_titles.txt"):
                        # If the file exists, read the known TV titles from the file and add them to the list
                        with open("known_tv_titles.txt", "r") as file:
                            known_tv_titles = [line.strip() for line in file]

                    # Check if the title starts with a known TV series name (from the known_tv_titles dictionary)
                    if any(item['Original Title'].startswith(known_title) for known_title in known_tv_titles):
                        # Format: "Series Name: 'Episode Name: Episode Part'"
                        series_name = title_split[0]

                    else:
                        # Format: "Series Name: 'Episode Name: Episode Part'" or "'IP Name: Series Name': Episode Name"
                        # Check the URL to determine which format it is
                        title_url = item['URL']
                        print(title_url)

                        # Get the HTML content of the title URL
                        title_html = requests.get(title_url, headers=headers).text

                        # Create a BeautifulSoup object from the HTML content
                        title_soup = BeautifulSoup(title_html, 'html.parser')

                        # Get the title from the HTML content
                        series_name = title_soup.find("div", class_="sc-2a168135-0 flmBNm").a.text
                        print(series_name)

                        # Save the known TV titles to a new line in the "known_tv_titles.txt" file
                        with open("known_tv_titles.txt", "a") as file:
                            file.write(f"{series_name}\n")

                elif num_colons == 4:
                    # Format: "'IP Name: Series Name': 'Episode Name: Episode Part'"
                    series_name = title_split[0] + ":" + title_split[1]
                else:
                    # Handle unexpected formats
                    continue  # Skip this item

                if series_name not in tv_series_data:
                    tv_series_data[series_name] = {
                        'Your Rating': 0,
                        'Average Episode Rating': 0.0,
                        'Love Formula': 0.0,
                        'Episode Count': 0,  # Initialize episode count
                        'Rewatch Count': 1  # Initialize rewatch count
                    }

                # Update episode rating
                tv_series_data[series_name]['Your Rating'] += 0
                tv_series_data[series_name]['Average Episode Rating'] += float(item['Your Rating'])
                tv_series_data[series_name]['Episode Count'] += 1

                if series_name in rewatched_series:
                    tv_series_data[series_name]['Rewatch Count'] = rewatched_series[series_name]


        # Select a random TV series from the dictionary and show it
        random_series = random.choice(list(tv_series_data.keys()))

        jokes_list = [f"How many times have you binge-watched {random_series} already?",
                      f"You sure waste a lot of time watching {random_series}.",
                      f"{random_series}? That's a questionable choice but who am I to judge?",
                      f"I don't think the world is ready for another season of {random_series}.",
                      f"Just between us: I, too, love {random_series}.",
                      f"Apparently you have rated {tv_series_data[random_series]['Episode Count']} episodes of {random_series}.<br><br>That's not at all weird... At all...",
                      f"I am proud of you, unlike your friends who doesn't like {random_series}.",
                      f"I know you watch {random_series} when you are alone. I am always watching you.",
                      f"I know you watch {random_series} because of the nudity. But I'll keep your secret.",
                      f"I am pretty sure you really liked {random_series} since you rated it {tv_series_data[random_series]['Your Rating']}/10.<br><br>"
                      f"But I bet you don't even remember what it was about...",

                      f"I am pretty sure you really liked {random_series} since you rated it {tv_series_data[random_series]['Your Rating']}/10.<br><br>"
                      f"But it might be that you generally rate everything high...",

                      f"Today's kids would think {random_series} is from the history books or something, that's how old you are.",
                      f"Today's kids would think {random_series} is lame.<br><br>I mean it is, but they don't have to know that.",
                      f"If you were a character in {random_series}, you would be the guy walking in the background. You know, the one that no one cares about.",
                      f"I am pretty sure you are the only person in the world who likes {random_series}.",
                      f"I know you watched {random_series} illegally. I am calling the police.",
                      f"If your life was a TV series, it would be {random_series}: boring and uninteresting.",
                      f"If your life was a TV series, it would be {random_series}: horribly cliché and only going downhill after the first episode.<br><br>"
                      f"But I am sure you would rate it 10/10.",

                      f"If your life was a TV series, it would be {random_series}: a complete waste of time.",
                      f"If {random_series} was a person, I am afraid you would run away with them from your own wedding.",
                      f"If {random_series} was a person, I am sure they would kill you and cry at your funeral, that's how awful {random_series} is. But you still like it."]

        if len(tv_series_data.keys()) > 1:
            random_series_2 = random.choice([series for series in tv_series_data.keys() if series != random_series])
            jokes_list.extend([
                f"It's beyond me how you can enjoy BOTH {random_series} and {random_series_2}.",
                f"Quick question: {random_series} or {random_series_2}?",
                f"If {random_series} and {random_series_2} had a baby, it would be the worst thing ever.<br><br>You seem to like both, though...",

                f"Did you know that {random_series} and {random_series_2} were created by the same person?<br><br>"
                f"Well, they weren't. And if you said yes, you are a liar. Be better..."
            ])

        # Check if the title has a number in it
        if any(char.isdigit() for char in random_series):
            # Take the full number from the title
            number = re.search(r'\d+', random_series).group(0)
            window.update_result_label(f"{jokes_list[0]} {number}?!")

        else:
            # Take a random joke from the jokes_list
            joke = random.choice(jokes_list)
            window.update_result_label(f"{joke}")

        app.processEvents()
        time.sleep(5)

        # Calculate average episode ratings and love formulas
        for series_name, data in tv_series_data.items():
            # If the TV series has at least one episode, calculate the average episode rating
            if data['Episode Count'] > 0:
                data['Average Episode Rating'] /= data['Episode Count']

            if data['Episode Count'] != 0 and data['Your Rating'] != 0:
                if data['Episode Count'] > 1:
                    love_formula = (
                            # Weighted by the number of episodes rated by the user
                            math.pow((data['Average Episode Rating'] ** 3) *
                                      (data['Your Rating'] ** 5), 0.2) *
                            (data['Episode Count'] ** 0.2)
                    )
                else:
                    love_formula = (
                        # Weighted by the number of episodes rated by the user
                        math.pow((data['Average Episode Rating'] ** 3) *
                                 (data['Your Rating'] ** 5), 0.2) *
                        ((data['Episode Count'] + 0.5) ** 0.2)
                    )

            elif data['Episode Count'] != 0 and data['Your Rating'] == 0:
                love_formula = (
                        data['Average Episode Rating'] * data['Episode Count'] ** 0.2
                )

            elif data['Episode Count'] == 0 and data['Your Rating'] != 0:
                love_formula = (
                        (data['Your Rating'] ** 5) / 1000
                )

            if data['Rewatch Count'] > 0:
                love_formula *= math.pow(data['Rewatch Count'], 1.1)

            data['Love Formula'] = love_formula

        # Sort the TV series by love formula in descending order
        sorted_series = sorted(
            tv_series_data.items(),
            key=lambda x: x[1]['Love Formula'],
            reverse=True
        )

        # Return the sorted data in the desired format
        formatted_data = [(series_name, (data['Your Rating'], data['Average Episode Rating'], data['Episode Count'], data['Rewatch Count'], data['Love Formula'])) for
                          series_name, data in sorted_series]

        return formatted_data if formatted_data else "N/A"

    def see_all_tv_series(self, favorite_tv_series):
        # Create a new QDialog to show all the TV series
        dialog = QDialog()
        dialog.setWindowTitle("All TV Shows")

        # Set the window size to a reasonable size so that the table is visible
        dialog.resize(1000, 550)

        layout = QVBoxLayout()

        # If there are too many TV series, show them in a table
        if favorite_tv_series:
            self.table = SortableTable(len(favorite_tv_series), 6)
            self.table.setHorizontalHeaderLabels(["TV Show", "Series Rating", "Average Episode Rating", "Episodes Rated By You", "Watch Count", "Your Love For Them"])
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            # Make the column "Rewatch Count" editable
            self.table.setEditTriggers(QAbstractItemView.DoubleClicked)

            for row, (series, info) in enumerate(favorite_tv_series):
                # Convert data to strings
                series_str = str(series)
                series_rating_str = f"{int(info[0])}"
                avg_rating_str = f"{info[1]:.2f}"
                episode_count_str = str(info[2])
                rewatch_count_str = str(info[3])
                your_love_str = f"{info[4]:.4f}"

                # Create QTableWidgetItem objects from the strings
                self.table.setItem(row, 0, QTableWidgetItem(series_str))
                self.table.setItem(row, 1, QTableWidgetItem(series_rating_str))
                self.table.setItem(row, 2, QTableWidgetItem(avg_rating_str))
                self.table.setItem(row, 3, QTableWidgetItem(episode_count_str))
                self.table.setItem(row, 4, QTableWidgetItem(rewatch_count_str))
                self.table.setItem(row, 5, QTableWidgetItem(your_love_str))

            layout.addWidget(self.table)

        else:
            no_tv_series_label = QLabel("You have no favorite TV shows.")
            layout.addWidget(no_tv_series_label)

        # Add a button to save the rewatch counts
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_rewatch_counts)
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        # Connect the sorting function to the header labels
        dialog.exec_()

    # Save the rewatch counts to rewatch.csv
    def save_rewatch_counts(self):
        # Create a list to store the rewatch counts
        rewatch_counts = []

        # Loop through the rows in the table
        for row in range(self.table.rowCount()):
            # Get the title and rewatch count
            title = self.table.item(row, 0).text()
            rewatch_count = self.table.item(row, 4).text()

            # Add the title and rewatch count to the list
            rewatch_counts.append((title, rewatch_count))

        # Write the rewatch counts to rewatch.csv (separated by semicolon)
        with open("rewatch.csv", "w") as file:
            file.write("Original Title;Rewatch Count\n")
            for title, rewatch_count in rewatch_counts:
                file.write(f"{title};{rewatch_count}\n")

    # Get the rewatch counts for each title from rewatch.csv
    def get_rewatch_counts(self):
        # Check if rewatch.csv exists
        if os.path.exists("rewatch.csv"):
            # Open rewatch.csv and add the titles to the list (items are separated by semicolon)
            with open("rewatch.csv", "r") as file:
                rewatch_data = list(csv.DictReader(file, delimiter=";"))

            print(rewatch_data)

            # Create a dictionary to store the rewatch counts
            rewatch_counts = {}

            # Loop through the rewatch_data list
            for item in rewatch_data:
                # Extract title and rewatch count
                title = item['Original Title']
                rewatch_counts[title] = int(item['Rewatch Count'])

            return rewatch_counts
        else:
            return {}    # Return 0 for rewatch count when there are no rewatch counts


class NowWatchingWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Now Watching")
        self.resize(800, 500)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Create a top-level layout for the main content
        content_layout = QVBoxLayout()
        self.main_layout.addLayout(content_layout)

        # Show what the user is currently watching
        self.now_watching_label = QLabel("You are now watching:")
        self.now_watching_label.setAlignment(Qt.AlignCenter)
        self.now_watching_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        content_layout.addWidget(self.now_watching_label)

        # Create a list widget to show what the user is currently watching
        self.now_watching_list = QListWidget()
        self.check_now_watching_list()
        self.now_watching_list.setStyleSheet("font-size: 20px;")
        content_layout.addWidget(self.now_watching_list)

        # Create a button to remove the selected title from the list
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_title)
        content_layout.addWidget(self.remove_button)

        # Create a button to clear the list
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_list)
        content_layout.addWidget(self.clear_button)

        # Create a search bar
        self.search_bar = QLineEdit()

        # Create a search button next to the search bar
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search)

        # Create a horizontal layout for the search bar and the search button
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_button)
        content_layout.addLayout(search_layout)

        # Create a list widget to show the search results
        self.search_results_list = QListWidget()
        self.search_results_list.setStyleSheet("font-size: 20px;")
        content_layout.addWidget(self.search_results_list)

        # Create a button to add the selected title to the list
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_title)
        content_layout.addWidget(self.add_button)

    # Class Functions
    def check_now_watching_list(self):
        # Check if watching.csv exists
        if os.path.exists("watching.csv"):
            # Open watching.csv and add the titles to the list
            with open("watching.csv", "r") as file:
                for line in file:
                    # Do not add the title if it is "Title"
                    if line.strip("\n") == "Title":
                        continue

                    # Remove the newline character
                    line = line.strip("\n")

                    # Add the title to the list
                    self.now_watching_list.addItem(line)

    def remove_title(self):
        # Check if there are any selected items
        if self.now_watching_list.selectedItems():
            # Loop through the selected items
            for item in self.now_watching_list.selectedItems():
                # Remove the item from the list
                self.now_watching_list.takeItem(self.now_watching_list.row(item))

                # Remove the item from watching.csv, if it exists
                if os.path.exists("watching.csv"):
                    with open("watching.csv", "r") as file:
                        lines = file.readlines()

                    with open("watching.csv", "w") as file:
                        for line in lines:
                            if line.strip("\n") != item.text():
                                file.write(line)

        else:
            # Show a message
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Please select a title to remove.")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()

    def clear_list(self):
        # Clear the list
        self.now_watching_list.clear()

        # Clear watching.csv, if it exists
        if os.path.exists("watching.csv"):
            with open("watching.csv", "w") as file:
                file.write("Title\n")


    def search(self):
        # Clear the list
        self.search_results_list.clear()

        # Get the search query
        search_query = self.search_bar.text()

        # Check if the search query is not empty
        if search_query:
            # Perform an IMDB search
            try:
                # Open the URL
                response = browser.open(f"https://www.imdb.com/find?q={search_query}&ref_=nv_sr_sm")

                # Get the HTML content
                html_content = response.read()

                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract the titles and their respective links from the search results
                search_results = soup.select("div.sc-17bafbdb-2")
                print(search_results)
                search_results = search_results[0].select("li.ipc-metadata-list-summary-item")

                # Check if there are any search results
                if search_results:
                    # Loop through the search results
                    for result in search_results:
                        # Extract the title
                        title_element = result.select_one("a")
                        title = title_element.text.strip()

                        # Add the title to the list
                        self.search_results_list.addItem(title)

                else:
                    # Show a message
                    self.search_results_list.addItem("No search results found.")

            except mechanize.URLError as e:
                print(f"An error occurred: {e}")

        else:
            # Show a message
            self.search_results_list.addItem("Please enter a search query.")

    def add_title(self):
        # Check if there are any selected items
        if self.search_results_list.selectedItems():
            # Loop through the selected items
            for item in self.search_results_list.selectedItems():
                # Add the item to the list
                self.now_watching_list.addItem(item.text())

            # If watching.csv doesn't exist, create it
            if not os.path.exists("watching.csv"):
                with open("watching.csv", "w") as file:
                    file.write("Title\n")

            # Add the selected title to watching.csv
            with open("watching.csv", "a") as file:
                file.write(f"{item.text()}\n")

        else:
            # Show a message
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Please select a title to add.")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()


class ImageLoaderThread(QThread):
    image_loaded = pyqtSignal(QPixmap)

    def __init__(self, image_url):
        super().__init__()
        self.image_url = image_url

    def run(self):
        # Download the image
        image_data = requests.get(self.image_url).content

        # Convert the image data to QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)

        # Emit the signal with the loaded pixmap
        self.image_loaded.emit(pixmap)


class DetailsWindow(QDialog):
    def __init__(self, title_url):
        super().__init__()
        # Remove the referral from the URL
        title_url = title_url.split("?")[0]

        # Access the title's URL
        response = browser.open(title_url)

        if response.code == 200:
            # Get the HTML content
            html_content = response.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Get the number of awards and nominations (span.ipc-metadata-list-item__list-content-item ::before)
            awards = soup.select_one("div[data-testid='awards']")
            if awards:
                awards = awards.select_one("span", class_="ipc-metadata-list-item__list-content-item").text.strip()
            print(awards)
        else:
            # Get the title from result_label's text's first row
            print("An error occurred while getting the awards and nominations on title")
            awards = "An error occurred while getting the awards and nominations on title"

        # Get certificate ratings and parental guide
        response = browser.open(title_url + "parentalguide")

        if response.code == 200:
            # Get the HTML content
            html_content = response.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Get the certificate ratings
            certificate_ratings_list = []
            certificate_ratings = soup.select_one("section[id='certificates']")

            if certificate_ratings:
                certificate_ratings = certificate_ratings.find("ul" , class_="ipl-inline-list")
                if certificate_ratings:
                    for item in certificate_ratings:
                        item = item.text.strip().replace('\n', '').replace('  ', '')
                        certificate_ratings_list.append(item)

            certificate_ratings_list = [item for item in certificate_ratings_list if item]  # Remove empty strings
            print(certificate_ratings_list)

            # Get the parental guide
            sex_nudity_list = []
            sex_nudity = soup.select_one("section[id='advisory-nudity']")

            if sex_nudity:
                sn_severity = sex_nudity.find("span", class_="ipl-status-pill").text.strip()
                sex_nudity = sex_nudity.find_all("li", class_="ipl-zebra-list__item")
                for item in sex_nudity:
                    sex_nudity_list.append(item.text.strip().strip("\n\n     \n\n\n\n\n\nEdit"))
            else:
                sn_severity = "-"

            violence_gore_list = []
            violence_gore = soup.select_one("section[id='advisory-violence']")

            if violence_gore:
                violence_severity = violence_gore.find("span", class_="ipl-status-pill").text.strip()
                violence_gore = violence_gore.find_all("li", class_="ipl-zebra-list__item")
                for item in violence_gore:
                    violence_gore_list.append(item.text.strip().strip("\n\n     \n\n\n\n\n\nEdit"))
            else:
                violence_severity = "-"

            profanity_list = []
            profanity = soup.select_one("section[id='advisory-profanity']")

            if profanity:
                profanity_severity = profanity.find("span", class_="ipl-status-pill").text.strip()
                profanity = profanity.find_all("li", class_="ipl-zebra-list__item")
                for item in profanity:
                    profanity_list.append(item.text.strip().strip("\n\n     \n\n\n\n\n\nEdit"))
            else:
                profanity_severity = "-"

            alcohol_drugs_smoking_list = []
            alcohol_drugs_smoking = soup.select_one("section[id='advisory-alcohol']")

            if alcohol_drugs_smoking:
                ad_severity = alcohol_drugs_smoking.find("span", class_="ipl-status-pill").text.strip()
                alcohol_drugs_smoking = alcohol_drugs_smoking.find_all("li", class_="ipl-zebra-list__item")
                for item in alcohol_drugs_smoking:
                    alcohol_drugs_smoking_list.append(item.text.strip().strip("\n\n     \n\n\n\n\n\nEdit"))
            else:
                ad_severity = "-"

            frightening_intense_scenes_list = []
            frightening_intense_scenes = soup.select_one("section[id='advisory-frightening']")

            if frightening_intense_scenes:
                fis_severity = frightening_intense_scenes.find("span", class_="ipl-status-pill").text.strip()
                frightening_intense_scenes = frightening_intense_scenes.find_all("li", class_="ipl-zebra-list__item")
                for item in frightening_intense_scenes:
                    frightening_intense_scenes_list.append(item.text.strip().strip("\n\n     \n\n\n\n\n\nEdit"))
            else:
                fis_severity = "-"

        self.setWindowTitle("Details")
        self.resize(1400, 800)

        self.main_layout = QGridLayout(self, spacing=0)

        # Show parental guide: Nudity, Violence, Profanity, Alcohol, Drugs & Smoking, Frightening & Intense Scenes
        parental_guide_widget = QWidget()
        parental_guide_label_widget = QWidget()
        parental_guide_label = QLabel("<h2>Parental Guide</h2>")

        # Create a button to show/hide the parental guide
        parental_guide_button = QPushButton("| Show/Hide")
        parental_guide_button.clicked.connect(
            lambda: parental_guide_container.show() if parental_guide_container.isHidden() else parental_guide_container.hide())


        parental_guide_label_widget_layout = QHBoxLayout()
        parental_guide_label_widget_layout.addWidget(parental_guide_label)
        parental_guide_label_widget_layout.addWidget(parental_guide_button)
        parental_guide_label_widget_layout.setAlignment(Qt.AlignLeft)
        parental_guide_label_widget.setLayout(parental_guide_label_widget_layout)


        # Nudity
        sex_nudity_label = QLabel(f"<h3>Sex & Nudity ({sn_severity})</h3>")
        sex_nudity_list_label = QLabel(f"\t-" + "\n\n\t- ".join(sex_nudity_list))
        sex_nudity_list_label.setStyleSheet("font-size: 18px;")
        sex_nudity_list_label.setWordWrap(True)
        sex_nudity_list_label.hide()

        match(sn_severity):
            case "Severe":
                sex_nudity_label.setStyleSheet("color: red;")
            case "Moderate":
                sex_nudity_label.setStyleSheet("color: orange;")
            case "Mild":
                sex_nudity_label.setStyleSheet("color: yellow;")
            case _:
                sex_nudity_label.setStyleSheet("color: green;")

        sex_nudity_label_widget = QWidget()
        sex_nudity_button = QPushButton("| Show/Hide")
        sex_nudity_label_widget_layout = QHBoxLayout()
        sex_nudity_button.clicked.connect(lambda: sex_nudity_list_label.show() if sex_nudity_list_label.isHidden() else sex_nudity_list_label.hide())
        sex_nudity_label_widget_layout.addWidget(sex_nudity_label)
        sex_nudity_label_widget_layout.addWidget(sex_nudity_button)
        sex_nudity_label_widget_layout.setAlignment(Qt.AlignLeft)
        sex_nudity_label_widget.setLayout(sex_nudity_label_widget_layout)

        # Violence & Gore
        violence_gore_label = QLabel(f"<h3>Violence & Gore ({violence_severity})</h3>")
        violence_gore_list_label = QLabel("\t- " + "\n\n\t- ".join(violence_gore_list))
        violence_gore_list_label.setStyleSheet("font-size: 18px;")
        violence_gore_list_label.setWordWrap(True)
        violence_gore_list_label.hide()

        match(violence_severity):
            case "Severe":
                violence_gore_label.setStyleSheet("color: red;")
            case "Moderate":
                violence_gore_label.setStyleSheet("color: orange;")
            case "Mild":
                violence_gore_label.setStyleSheet("color: yellow;")
            case _:
                violence_gore_label.setStyleSheet("color: green;")

        violence_gore_label_widget = QWidget()
        violence_gore_button = QPushButton("| Show/Hide")
        violence_gore_label_widget_layout = QHBoxLayout()
        violence_gore_button.clicked.connect(
            lambda: violence_gore_list_label.show() if violence_gore_list_label.isHidden() else violence_gore_list_label.hide())
        violence_gore_label_widget_layout.addWidget(violence_gore_label)
        violence_gore_label_widget_layout.addWidget(violence_gore_button)
        violence_gore_label_widget_layout.setAlignment(Qt.AlignLeft)
        violence_gore_label_widget.setLayout(violence_gore_label_widget_layout)

        # Profanity
        profanity_label = QLabel(f"<h3>Profanity ({profanity_severity})</h3>")
        profanity_list_label = QLabel("\t- " + "\n\n\t- ".join(profanity_list))
        profanity_list_label.setStyleSheet("font-size: 18px;")
        profanity_list_label.setWordWrap(True)
        profanity_list_label.hide()

        match(profanity_severity):
            case "Severe":
                profanity_label.setStyleSheet("color: red;")
            case "Moderate":
                profanity_label.setStyleSheet("color: orange;")
            case "Mild":
                profanity_label.setStyleSheet("color: yellow;")
            case _:
                profanity_label.setStyleSheet("color: green;")

        profanity_label_widget = QWidget()
        profanity_button = QPushButton("| Show/Hide")
        profanity_label_widget_layout = QHBoxLayout()
        profanity_button.clicked.connect(
            lambda: profanity_list_label.show() if profanity_list_label.isHidden() else profanity_list_label.hide())
        profanity_label_widget_layout.addWidget(profanity_label)
        profanity_label_widget_layout.addWidget(profanity_button)
        profanity_label_widget_layout.setAlignment(Qt.AlignLeft)
        profanity_label_widget.setLayout(profanity_label_widget_layout)

        # Alcohol, Drugs & Smoking
        alcohol_drugs_smoking_label = QLabel(f"<h3>Alcohol, Drugs & Smoking ({ad_severity})</h3>")
        alcohol_drugs_smoking_list_label = QLabel("\t- " + "\n\n\t- ".join(alcohol_drugs_smoking_list))
        alcohol_drugs_smoking_list_label.setStyleSheet("font-size: 18px;")
        alcohol_drugs_smoking_list_label.setWordWrap(True)
        alcohol_drugs_smoking_list_label.hide()

        match(ad_severity):
            case "Severe":
                alcohol_drugs_smoking_label.setStyleSheet("color: red;")
            case "Moderate":
                alcohol_drugs_smoking_label.setStyleSheet("color: orange;")
            case "Mild":
                alcohol_drugs_smoking_label.setStyleSheet("color: yellow;")
            case _:
                alcohol_drugs_smoking_label.setStyleSheet("color: green;")

        alcohol_drugs_smoking_label_widget = QWidget()
        alcohol_drugs_smoking_button = QPushButton("| Show/Hide")
        alcohol_drugs_smoking_label_widget_layout = QHBoxLayout()
        alcohol_drugs_smoking_button.clicked.connect(
            lambda: alcohol_drugs_smoking_list_label.show() if alcohol_drugs_smoking_list_label.isHidden() else alcohol_drugs_smoking_list_label.hide())
        alcohol_drugs_smoking_label_widget_layout.addWidget(alcohol_drugs_smoking_label)
        alcohol_drugs_smoking_label_widget_layout.addWidget(alcohol_drugs_smoking_button)
        alcohol_drugs_smoking_label_widget_layout.setAlignment(Qt.AlignLeft)
        alcohol_drugs_smoking_label_widget.setLayout(alcohol_drugs_smoking_label_widget_layout)

        # Frightening & Intense Scenes
        frightening_intense_scenes_label = QLabel(f"<h3>Frightening & Intense Scenes ({fis_severity})</h3>")
        frightening_intense_scenes_list_label = QLabel("\t- " + "\n\n\t- ".join(frightening_intense_scenes_list))
        frightening_intense_scenes_list_label.setStyleSheet("font-size: 18px;")
        frightening_intense_scenes_list_label.setWordWrap(True)
        frightening_intense_scenes_list_label.hide()

        match(fis_severity):
            case "Severe":
                frightening_intense_scenes_label.setStyleSheet("color: red;")
            case "Moderate":
                frightening_intense_scenes_label.setStyleSheet("color: orange;")
            case "Mild":
                frightening_intense_scenes_label.setStyleSheet("color: yellow;")
            case _:
                frightening_intense_scenes_label.setStyleSheet("color: green;")

        frightening_intense_scenes_label_widget = QWidget()
        frightening_intense_scenes_button = QPushButton("| Show/Hide")
        frightening_intense_scenes_label_widget_layout = QHBoxLayout()
        frightening_intense_scenes_button.clicked.connect(
            lambda: frightening_intense_scenes_list_label.show() if frightening_intense_scenes_list_label.isHidden() else frightening_intense_scenes_list_label.hide())
        frightening_intense_scenes_label_widget_layout.addWidget(frightening_intense_scenes_label)
        frightening_intense_scenes_label_widget_layout.addWidget(frightening_intense_scenes_button)
        frightening_intense_scenes_label_widget_layout.setAlignment(Qt.AlignLeft)
        frightening_intense_scenes_label_widget.setLayout(frightening_intense_scenes_label_widget_layout)

        # Create a container widget for the parental guide
        parental_guide_container = QWidget()
        parental_guide_container_layout = QVBoxLayout()
        parental_guide_container.hide()

        # Make the parental guide scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(parental_guide_widget)

        parental_guide_container_layout.addWidget(sex_nudity_label_widget)
        parental_guide_container_layout.addWidget(sex_nudity_list_label)
        parental_guide_container_layout.addWidget(violence_gore_label_widget)
        parental_guide_container_layout.addWidget(violence_gore_list_label)
        parental_guide_container_layout.addWidget(profanity_label_widget)
        parental_guide_container_layout.addWidget(profanity_list_label)
        parental_guide_container_layout.addWidget(alcohol_drugs_smoking_label_widget)
        parental_guide_container_layout.addWidget(alcohol_drugs_smoking_list_label)
        parental_guide_container_layout.addWidget(frightening_intense_scenes_label_widget)
        parental_guide_container_layout.addWidget(frightening_intense_scenes_list_label)

        # Create another button at the end of the container in case the parental guide is too long
        parental_guide_button_inner = QPushButton("Show/Hide")
        parental_guide_button_inner.clicked.connect(
            lambda: parental_guide_container.show() if parental_guide_container.isHidden() else parental_guide_container.hide())

        parental_guide_container_layout.addWidget(parental_guide_button_inner)
        parental_guide_container.setLayout(parental_guide_container_layout)

        parental_guide_widget_layout = QVBoxLayout()
        parental_guide_widget_layout.addWidget(parental_guide_label_widget)
        parental_guide_widget_layout.addWidget(parental_guide_container)
        parental_guide_widget.setLayout(parental_guide_widget_layout)

        # Change the color of the parental guide container background according to levels of overall severity
        # There are 5 categories with 4 levels of severity each: None, Mild, Moderate, Severe
        # This adds up to 20, with each 4 levels having a different color
        # 0-4: Green, 5-9: Yellow, 10-14: Orange, 15-20: Red

        severity_levels = {
            "": 0,
            "None": 0,
            "Mild": 1,
            "Moderate": 2,
            "Severe": 3
        }

        overall_severity = severity_levels[sn_severity] + severity_levels[violence_severity] + severity_levels[profanity_severity] + severity_levels[ad_severity] + severity_levels[fis_severity]

        print(f"Sex & Nudity: {sn_severity}\n"
              f"Violence & Gore: {violence_severity}\n"
              f"Profanity: {profanity_severity}\n"
              f"Alcohol, Drugs & Smoking: {ad_severity}\n"
              f"Frightening & Intense Scenes: {fis_severity}\n"
              f"Overall Severity: {overall_severity}")

        if overall_severity <= 4:
            parental_guide_container.setStyleSheet("background-color: #003a00;")    # Dark Green
        elif overall_severity <= 9:
            parental_guide_container.setStyleSheet("background-color: #505900;")    # Dark Yellow
        elif overall_severity <= 14:
            parental_guide_container.setStyleSheet("background-color: #593a00;")    # Dark Orange
        else:
            parental_guide_container.setStyleSheet("background-color: #3b0101;")    # Dark Red

        self.main_layout.addWidget(scroll_area, 0, 0)

        # Show the awards and nominations
        awards_widget = QWidget()
        awards_label = QLabel(f"<h2>Awards: {awards}</h2>")

        # Create a button to open the awards page
        awards_button = QPushButton("Show Awards && Nominations")
        awards_button.clicked.connect(lambda: webbrowser.open(title_url + "awards"))

        awards_widget_layout = QVBoxLayout()
        awards_widget_layout.addWidget(awards_label)
        awards_widget_layout.addWidget(awards_button)
        awards_widget.setLayout(awards_widget_layout)

        self.main_layout.addWidget(awards_widget, 1, 0)

        # Show the plot
        # Get to summaries page
        response = browser.open(title_url + "plotsummary")

        if response.code == 200:
            # Get the HTML content
            html_content = response.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Get the plot
            plot = soup.select_one("div[data-testid='sub-section-summaries']")
            if plot:
                # Get the list of plot summaries
                plot = plot.select("li[data-testid='list-item']")

                # Get the longest plot summary
                plot = max(plot, key=lambda x: len(x.text.strip()))

                # Get the plot text
                plot = plot.text.strip()

        else:
            print("An error occurred while getting the plot summary")
            plot = "An error occurred while getting the plot summary"

        plot_widget = QWidget()
        plot_label = QLabel("<h2>Plot</h2>")
        plot_text = QLabel(plot)
        plot_text.setWordWrap(True)

        # Add the plot text to a scroll area
        plot_scroll_area = QScrollArea()
        plot_scroll_area.setWidgetResizable(True)
        plot_scroll_area.setWidget(plot_text)

        plot_widget_layout = QVBoxLayout()
        plot_widget_layout.addWidget(plot_label)
        plot_widget_layout.addWidget(plot_scroll_area)
        plot_widget.setLayout(plot_widget_layout)

        self.main_layout.addWidget(plot_widget, 0, 1)

        # Show the plot keywords
        # Get to plot keywords page
        response = browser.open(title_url + "keywords")

        if response.code == 200:
            # Get the HTML content
            html_content = response.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Get the plot keywords
            plot_keywords = soup.select_one("div[data-testid='sub-section']")
            if plot_keywords:
                # Get the list of plot keywords
                plot_keywords = plot_keywords.select("li[data-testid='list-summary-item']")

                # Get the plot keywords text
                plot_keywords = [keyword.text.strip() for keyword in plot_keywords]

        else:
            print("An error occurred while getting the plot keywords")
            plot_keywords = ["An error occurred while getting the plot keywords"]

        plot_keywords_widget = QWidget()
        plot_keywords_label = QLabel("<h2>Plot Keywords</h2>")
        try:
            plot_keywords_text = QLabel("\n".join(plot_keywords))
        except:
            plot_keywords_text = QLabel("An error occurred while getting the plot keywords")
        plot_keywords_text.setWordWrap(True)

        # Add the plot keywords text to a scroll area
        plot_keywords_scroll_area = QScrollArea()
        plot_keywords_scroll_area.setWidgetResizable(True)
        plot_keywords_scroll_area.setWidget(plot_keywords_text)

        plot_keywords_widget_layout = QVBoxLayout()
        plot_keywords_widget_layout.addWidget(plot_keywords_label)
        plot_keywords_widget_layout.addWidget(plot_keywords_scroll_area)
        plot_keywords_widget.setLayout(plot_keywords_widget_layout)

        self.main_layout.addWidget(plot_keywords_widget, 1, 1)
        self.main_layout.setColumnStretch(0, 1) # Make the first column stretchable
        self.main_layout.setColumnStretch(1, 1) # Make the second column stretchable
        self.main_layout.setRowStretch(0, 1) # Make the first row stretchable
        self.main_layout.setRowStretch(1, 1) # Make the second row stretchable


class SortableTable(QTableWidget):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setHorizontalHeaderLabels([""])
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().sortIndicatorChanged.connect(self.sort_table)
        self.sorting_order = Qt.DescendingOrder  # Default sorting order

    def sort_table(self, logicalIndex):
        items = [(
                 self.item(row, logicalIndex).text(), [self.item(row, col).text() for col in range(self.columnCount())],
                 row) for row in range(self.rowCount())]

        if self.sorting_order == Qt.AscendingOrder:
            items.sort(key=lambda x: (float(x[0]) if x[0].replace(".", "", 1).isdigit() else x[0], x[1]))
        else:
            items.sort(key=lambda x: (float(x[0]) if x[0].replace(".", "", 1).isdigit() else x[0], x[1]), reverse=True)

        for row, (_, row_data, original_row) in enumerate(items):
            for col, value in enumerate(row_data):
                new_item = QTableWidgetItem(value)
                self.setItem(row, col, new_item)

        self.sorting_order = Qt.AscendingOrder if self.sorting_order == Qt.DescendingOrder else Qt.DescendingOrder

class YearReviewWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Year Review")
        self.resize(800, 500)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Create a top-level layout for the main content
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        # Detect the user's active years from ratings.csv
        self.active_years = self.detect_active_years()

        # Create a layout for combo box and show button
        combo_button_layout = QHBoxLayout()
        self.content_layout.addLayout(combo_button_layout)

        # Create a "Year" combo box and add the active years to it
        self.year_combo = QComboBox()
        self.year_combo.addItems(self.active_years)

        # Center every item in the combo box
        self.year_combo.setEditable(True)
        self.year_combo.lineEdit().setAlignment(Qt.AlignCenter)

        # Make the combo box searchable
        self.year_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.year_combo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        combo_button_layout.addWidget(self.year_combo)

        # Create a "Show" button
        self.review_button = QPushButton("Review My Year")
        self.review_button.clicked.connect(self.review)
        combo_button_layout.addWidget(self.review_button)

        # Create a header label
        self.header_label = QLabel("<h2>Welcome to your year review!</h2>"
                                   "<h3>Let's see what you watched, and how much you loved them.</h3>")
        self.header_label.setWordWrap(True)
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.content_layout.addWidget(self.header_label)

        # Create a horizontal layout for the image and the details
        self.year_details_layout = QHBoxLayout()
        self.content_layout.addLayout(self.year_details_layout)

        # Create a label to show the image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.year_details_layout.addWidget(self.image_label)

        self.description_label = QLabel("-")
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignCenter)
        # Enable rich text for the description label so that we can change the font size, boldness, etc.
        self.description_label.setOpenExternalLinks(True)
        self.description_label.setFixedHeight(500)
        self.description_label.setMinimumWidth(200)
        self.year_details_layout.addWidget(self.description_label)

        # Hide the image and the description label
        self.image_label.hide()
        self.description_label.hide()

        # Create a layout for previous and next buttons
        previous_next_layout = QHBoxLayout()
        self.content_layout.addLayout(previous_next_layout)

        # Create a "Previous" button
        self.previous_button = QPushButton("Previous")
        self.previous_button.setMinimumWidth(50)
        self.previous_button.clicked.connect(self.previous)
        previous_next_layout.addWidget(self.previous_button)

        # Make the "Previous" button disabled by default
        self.previous_button.setEnabled(False)

        # Create a "Next" button
        self.next_button = QPushButton("How many titles did you watch? >")
        self.next_button.setMinimumWidth(50)
        self.next_button.clicked.connect(self.next)
        previous_next_layout.addWidget(self.next_button)

        # Hide the previous and next buttons
        self.previous_button.hide()
        self.next_button.hide()
        self.page = 0

    # Class Functions
    def detect_active_years(self):
        # Open ratings.csv and add the years to the list (items are separated by semicolon)
        with open("ratings.csv", "r") as file:
            ratings_data = list(csv.DictReader(file, delimiter=","))

        # Create a list to store the years
        years = []

        # Using pandas, infer the date type of the "Date Rated" column
        ratings_data = pd.DataFrame(ratings_data)
        ratings_data['Date Rated'] = pd.to_datetime(ratings_data['Date Rated'])

        # Detect the years from the "Date Rated" column
        ratings_data['Date Rated'] = ratings_data['Date Rated'].dt.strftime('%Y')

        # Convert the "Date Rated" column to a list
        years = ratings_data['Date Rated'].tolist()

        # Remove duplicates from the list
        years = list(set(years))

        # Sort the list in descending order
        years.sort(reverse=True)

        return years

    def review(self):
        # Show the next button
        self.next_button.show()

        # Get the selected year
        self.year = int(self.year_combo.currentText())

        print(self.year)

        # Read the CSV file into a DataFrame
        df = pd.read_csv('ratings.csv')

        print("df")
        print(df)

        # Filter the data so that only the selected year remains in the Date Rated column
        self.filtered_data = df[df['Date Rated'].str.contains(f'{self.year}')]
        print("filtered_data")
        print(self.filtered_data)

        # Convert the 'Date Rated' column to datetime for easy comparison
        self.filtered_data['Date Rated'] = pd.to_datetime(self.filtered_data['Date Rated'], format='%Y-%m-%d')

        # Filter the data for the first three months of the year (January, February, March)
        self.first_three_months_data = self.filtered_data[(self.filtered_data['Date Rated'] >= pd.to_datetime(f'{self.year}-01-01', format='%Y-%m-%d'))
                                                & (self.filtered_data['Date Rated'] <= pd.to_datetime(f'{self.year}-03-31', format='%Y-%m-%d'))]

        # Filter the data for the last three months of the year (October, November, December)
        self.last_three_months_data = self.filtered_data[(self.filtered_data['Date Rated'] >= pd.to_datetime(f'{self.year}-10-01', format='%Y-%m-%d'))
                                               & (self.filtered_data['Date Rated'] <= pd.to_datetime(f'{self.year}-12-31', format='%Y-%m-%d'))]

        # Check if there are any titles in the last three months
        if not self.last_three_months_data.empty:
            # Display the title of one random selection
            selected_title = self.last_three_months_data.sample()['Title'].values[0]
            print(f"You ended the year with some good choices, such as: {selected_title}")
        else:
            print(f"No titles found in the last three months of {self.year}.")

        #####################################

        # Get the number of titles watched in each month
        self.titles_watched_in_each_month = self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Title'].count().to_dict()

        # Sort the dictionary by the keys (January, February, March, etc.)
        self.titles_watched_in_each_month = dict(sorted(self.titles_watched_in_each_month.items(), key=lambda x: datetime.strptime(x[0], "%B")))

        #####################################

        # Get the average rating for the year
        self.average_rating = self.filtered_data['Your Rating'].mean()

        # Get the genres and their counts, and store them in a dictionary
        self.genres = {}
        for index, row in self.filtered_data.iterrows():
            # Get the genres
            genres = row['Genres'].split(", ")

            # Get the rating
            rating = row['Your Rating']

            # Loop through the genres
            for genre in genres:
                # Check if the genre is already in the dictionary
                if genre in self.genres:
                    # Increment the count by 1
                    self.genres[genre][0] += 1

                    # Add the rating to the list of ratings
                    self.genres[genre][1].append(rating)

                else:
                    # Add the genre to the dictionary
                    self.genres[genre] = [1, [rating]]

        # Loop through the dictionary and get the average rating for each genre
        for key, value in self.genres.items():
            # Calculate the average rating
            self.genres[key][1] = sum(value[1]) / len(value[1])

        # Calculate the love formula for each genre (count^1.3 * average rating^5)
        for key, value in self.genres.items():
            self.genres[key] = (value[0], value[1], (value[0] ** 1.3 * value[1] ** 5) / 1000)

        # Sort the genres dictionary based on the love formula
        self.genres = dict(sorted(self.genres.items(), key=lambda x: x[1][2], reverse=True))

        #####################################

        # Get the title types and counts, and store them in a dictionary
        title_types = self.filtered_data['Title Type'].value_counts().to_dict()

        # Create a list of strings for title types and their counts
        self.title_types_list = [f"<b>{key}:</b> {value}" for key, value in title_types.items()]

        #####################################

        # Get the total runtime for the year
        self.total_runtime = self.filtered_data['Runtime (mins)'].sum()

        # Get the month with the highest runtime
        self.month_with_highest_runtime = self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Runtime (mins)'].sum().idxmax()

        # Get the month with the lowest runtime
        self.month_with_lowest_runtime = self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Runtime (mins)'].sum().idxmin()

        # Get the month with the most titles watched
        self.month_with_most_titles = self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Title'].count().idxmax()

        # Get the month with the least titles watched
        self.month_with_least_titles = self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Title'].count().idxmin()

        # Get the month with the highest and lowest average rating
        self.month_with_highest_average_rating = self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Your Rating'].mean().idxmax()
        self.month_with_lowest_average_rating = self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Your Rating'].mean().idxmin()

        #####################################

        # Update the page
        self.page = 1
        self.update_page()


    def previous(self):
        if self.page == 0:
            self.previous_button.setEnabled(False)
            return

        self.page -= 1
        self.update_page()

    def next(self):
        self.page += 1
        self.update_page()

    def update_page(self):
        match(self.page):
            case 0: # Welcome page
                self.previous_button.setEnabled(False)
                self.previous_button.hide()
                self.description_label.hide()
                self.header_label.setText("Welcome to your year review!\n"
                                          "Let's see what you watched, and how much you loved them.")
                self.previous_button.setText("-")
                self.next_button.setText("How many titles did you watch? >")

            case 1: # Titles watched in each genre
                self.next_button.show()
                self.description_label.show()
                self.previous_button.setEnabled(True)
                self.previous_button.show()
                self.header_label.setText(f"<h1>\"{len(self.filtered_data)}\"</h1>")
                self.previous_button.setText("< To the beginning")
                self.next_button.setText("Your activity throughout the year >")

                # Add the title types and their counts to the description label
                self.description_label.setText(f"You watched a total of <b>{len(self.filtered_data)}</b> titles in {self.year}:<br><br>"
                                               + "<br>".join(self.title_types_list))


                # Delete the plot widget if it exists
                try:
                    self.plot_widget.deleteLater()
                    self.plot_widget_layout.deleteLater()
                except:
                    pass

            case 2: # Titles watched in each month
                self.header_label.setText("<h1>Quite the busy year, huh?</h1>")
                self.previous_button.setText("< How many titles did you watch?")
                self.next_button.setText("Where did all the time go? >")
                self.description_label.hide()
                self.image_label.hide()

                # Graph the number of titles watched in each month and show it in the description label
                # Set up the figure and axes
                fig, ax = plt.subplots()

                # Set the title
                ax.set_title("Number of Titles Watched in Each Month")

                # Set the x and y labels
                ax.set_xlabel("Month")
                ax.set_ylabel("Number of Titles")

                # Plot the data
                ax.bar(self.titles_watched_in_each_month.keys(), self.titles_watched_in_each_month.values())

                # Rotate the x ticks
                plt.xticks(rotation=60)

                # Embed the plot in the dialog
                self.canvas = plt.gcf().canvas
                self.canvas.draw()
                plt.close(fig)
                plt.show()

                # Create a widget to contain the plot and add it to the layout
                self.plot_widget = QWidget()
                self.plot_widget_layout = QVBoxLayout()
                self.plot_widget_layout.addWidget(self.canvas)
                self.plot_widget.setLayout(self.plot_widget_layout)

                self.year_details_layout.addWidget(self.plot_widget)
                # Stretch the plot widget to fill the entire row and column
                self.year_details_layout.setStretch(0, 1)
                self.year_details_layout.setStretch(1, 1)

                # Set the header label maximum height to 100
                self.header_label.setMaximumHeight(100)

            case 3: # Busiest month, least busy month
                self.header_label.setText(f"<h1>\"{int(self.total_runtime)}\" minutes</h1>")
                self.previous_button.setText("< Your activity throughout the year")
                self.next_button.setText("When did you have your BEST and WORST times? >")
                self.description_label.show()

                # Delete the plot widget if it exists
                try:
                    self.plot_widget.deleteLater()
                    self.plot_widget_layout.deleteLater()
                except:
                    pass

                # Convert the total runtime to days, hours, and minutes
                if self.total_runtime >= 1440:
                    time_watched = f"{int(self.total_runtime // 1440)} days, {int(self.total_runtime % 1440 // 60)} hours, and {int(self.total_runtime % 1440 % 60)} minutes"
                elif self.total_runtime >= 60:
                    time_watched = f"{self.total_runtime // 60} hours and {self.total_runtime % 60} minutes"
                else:
                    time_watched = f"{self.total_runtime} minutes"

                self.description_label.setText(f"You spent a total of <b>{time_watched}</b> watching movies and TV in {self.year}.<br><br>"
                                               f"Your busiest month was <b>{self.month_with_highest_runtime}</b>, where you spent <b>{int(self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Runtime (mins)'].sum().max())}</b> minutes watching titles.<br><br>"
                                               f"Your least busy month was <b>{self.month_with_lowest_runtime}</b>, where you spent <b>{int(self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Runtime (mins)'].sum().min())}</b> minutes watching titles.<br><br>"
                                               f"Your favorite month was <b>{self.month_with_most_titles}</b>, where you watched <b>{int(self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Title'].count().max())}</b> titles.<br><br>"
                                               f"Your least favorite month was <b>{self.month_with_least_titles}</b>, where you watched <b>{int(self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Title'].count().min())}</b> titles.<br><br>")

            case 4: # Favorite and least favorite month
                self.header_label.setText(f"<h1>You had your ups and downs.</h1>")
                self.previous_button.setText("< Where did all the time go?")
                self.next_button.setText("How did you start the year? >")
                self.description_label.show()

                # Choose a random title from the favorite month
                favorite_month_titles = self.filtered_data[self.filtered_data['Date Rated'].dt.strftime('%B') == self.month_with_highest_average_rating]['Title'].tolist()
                favorite_month_title = random.choice(favorite_month_titles)

                # Get the URL of the selected title
                favorite_month_title_url = self.filtered_data[self.filtered_data['Title'] == favorite_month_title]['URL'].values[0]

                # Get the rating of the selected title
                favorite_month_title_rating = self.filtered_data[self.filtered_data['Title'] == favorite_month_title]['Your Rating'].values[0]

                # Get the poster URL of the selected title
                soup = BeautifulSoup(browser.open(favorite_month_title_url).read(), 'html.parser')

                # Get the movie poster URL from the IMDb page
                poster_image = soup.find('img', class_='ipc-image')

                if poster_image:
                    poster_url = poster_image['src']
                    print(poster_url)

                    # Get the biggest poster image by changing the url
                    # For example:
                    # - URL we get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@._V1_QL75_UX190_CR0,0,190,281_.jpg
                    # - URL we want to get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@.jpg
                    # Remove everything except ".jpg" after "@@"
                    if "@@" in poster_url:
                        poster_url = poster_url.split("@@")[0] + "@@.jpg"

                    else:
                        poster_url = poster_url.split("_")[0] + "jpg"

                    # Create a pixmap from the poster image URL
                    pixmap = QPixmap()
                    pixmap.loadFromData(requests.get(poster_url).content)

                    # Set the pixmap to the poster_label
                    self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
                    self.image_label.show()

                    # Find the majority color of the poster image
                    # Convert the pixmap to a QImage
                    image = pixmap.toImage()

                    smooth_color_change(image)


                self.description_label.setText(f"Your average rating for {self.year} was <b>{self.average_rating:.2f}</b>/10.<br><br>"
                                               f"You definitely loved <b>{self.month_with_highest_average_rating}</b>, which got an average rating of <b>{self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Your Rating'].mean().max():.2f}</b>/10 from you.<br>"
                                               f"Your least enjoyable period probably was <b>{self.month_with_lowest_average_rating}</b>, where your average rating was <b>{self.filtered_data.groupby(self.filtered_data['Date Rated'].dt.strftime('%B'))['Your Rating'].mean().min():.2f}</b>/10<br><br>"
                                               f"You watched <b>{favorite_month_title}</b> in {self.month_with_highest_average_rating}, and you rated it <b>{favorite_month_title_rating}</b>/10. Maybe you should watch it again?")


            case 5: # Start of the year
                self.header_label.setText("<h1>A lot can happen in three months.</h1>")
                self.previous_button.setText("< When did you have your BEST and WORST times?")
                self.next_button.setText("How did you end the year? >")
                self.description_label.show()

                # Check if there are any titles in the first three months
                if not self.first_three_months_data.empty:
                    # Display the title and url of one random selection
                    selected_title = self.first_three_months_data.sample()['Title'].values[0]

                    # Get the URL of the selected title
                    selected_title_url = \
                    self.first_three_months_data[self.first_three_months_data['Title'] == selected_title][
                        'URL'].values[0]

                    # Get the rating of the selected title
                    selected_title_rating = \
                    self.first_three_months_data[self.first_three_months_data['Title'] == selected_title][
                        'Your Rating'].values[0]

                    # Get the poster URL of the selected title
                    soup = BeautifulSoup(browser.open(selected_title_url).read(), 'html.parser')

                    # Get the movie poster URL from the IMDb page
                    poster_image = soup.find('img', class_='ipc-image')

                    if poster_image:
                        poster_url = poster_image['src']
                        print(poster_url)

                        # Get the biggest poster image by changing the url
                        # For example:
                        # - URL we get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@._V1_QL75_UX190_CR0,0,190,281_.jpg
                        # - URL we want to get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@.jpg
                        # Remove everything except ".jpg" after "@@"
                        if "@@" in poster_url:
                            poster_url = poster_url.split("@@")[0] + "@@.jpg"

                        else:
                            poster_url = poster_url.split("_")[0] + "jpg"

                        # Create a pixmap from the poster image URL
                        pixmap = QPixmap()
                        pixmap.loadFromData(requests.get(poster_url).content)

                        # Set the pixmap to the poster_label
                        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
                        self.image_label.show()

                        # Find the majority color of the poster image
                        # Convert the pixmap to a QImage
                        image = pixmap.toImage()

                        smooth_color_change(image)

                        self.description_label.setText(f"Do you remember watching <b>{selected_title}</b> at the start of {self.year}?<br>"
                                                       f"You rated it <b>{selected_title_rating}</b>/10.<br><br>"
                                                       f"Along with that, you watched <b>{len(self.first_three_months_data)} titles</b> in the first three months of {self.year}.")

                else:
                    self.description_label.setText("No titles found in the first three months of the year.")
                    self.image_label.hide()


            case 6: # End of the year
                self.header_label.setText("<h1>Cheers to the year that was.</h1>")
                self.previous_button.setText("< How did you start the year?")
                self.next_button.setText("What were your favorite genres? >")
                self.description_label.show()

                # Check if there are any titles in the last three months
                if not self.last_three_months_data.empty:
                    # Display the title and url of one random selection
                    selected_title = self.last_three_months_data.sample()['Title'].values[0]

                    # Get the URL of the selected title
                    selected_title_url = \
                    self.last_three_months_data[self.last_three_months_data['Title'] == selected_title][
                        'URL'].values[0]

                    # Get the rating of the selected title
                    selected_title_rating = \
                    self.last_three_months_data[self.last_three_months_data['Title'] == selected_title][
                        'Your Rating'].values[0]

                    # Get the poster URL of the selected title
                    soup = BeautifulSoup(browser.open(selected_title_url).read(), 'html.parser')

                    # Get the movie poster URL from the IMDb page
                    poster_image = soup.find('img', class_='ipc-image')

                    if poster_image:
                        poster_url = poster_image['src']
                        print(poster_url)

                        # Get the biggest poster image by changing the url
                        # For example:
                        # - URL we get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@._V1_QL75_UX190_CR0,0,190,281_.jpg
                        # - URL we want to get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@.jpg
                        # Remove everything except ".jpg" after "@@"
                        if "@@" in poster_url:
                            poster_url = poster_url.split("@@")[0] + "@@.jpg"

                        else:
                            poster_url = poster_url.split("_")[0] + "jpg"

                        # Create a pixmap from the poster image URL
                        pixmap = QPixmap()
                        pixmap.loadFromData(requests.get(poster_url).content)

                        # Set the pixmap to the poster_label
                        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
                        self.image_label.show()

                        # Find the majority color of the poster image
                        # Convert the pixmap to a QImage
                        image = pixmap.toImage()

                        smooth_color_change(image)

                        self.description_label.setText(f"Do you remember watching <b>{selected_title}</b> at the end of {self.year}?<br>"
                                                       f"You rated it <b>{selected_title_rating}</b>/10.<br><br>"
                                                       f"Along with that, you watched <b>{len(self.last_three_months_data)} titles</b> in the last three months of {self.year}.")

                else:
                    self.description_label.setText("No titles found in the last three months of the year.")
                    self.image_label.hide()

            case 7: # Favorite genres
                self.header_label.setText(f"<h1>The best genres of {self.year}, according to you.</h1>")
                self.previous_button.setText("< How did you end the year?")
                self.next_button.setText("What were your favorite TV shows? >")

                # Get the favorite genre and filter the data
                favorite_genre = list(self.genres.keys())[0]

                # Choose a random title from the favorite genre
                favorite_genre_titles = self.filtered_data[self.filtered_data['Genres'].str.contains(favorite_genre)]['Title'].tolist()
                favorite_genre_title = random.choice(favorite_genre_titles)

                # Get the URL of the selected title
                favorite_genre_title_url = self.filtered_data[self.filtered_data['Title'] == favorite_genre_title]['URL'].values[0]

                # Get the rating of the selected title
                favorite_genre_title_rating = self.filtered_data[self.filtered_data['Title'] == favorite_genre_title]['Your Rating'].values[0]

                # Get the poster URL of the selected title
                soup = BeautifulSoup(browser.open(favorite_genre_title_url).read(), 'html.parser')

                # Get the movie poster URL from the IMDb page
                poster_image = soup.find('img', class_='ipc-image')

                if poster_image:
                    poster_url = poster_image['src']

                    # Get the biggest poster image by changing the url
                    # For example:
                    # - URL we get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@._V1_QL75_UX190_CR0,0,190,281_.jpg
                    # - URL we want to get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@.jpg
                    # Remove everything except ".jpg" after "@@"
                    if "@@" in poster_url:
                        poster_url = poster_url.split("@@")[0] + "@@.jpg"

                    else:
                        poster_url = poster_url.split("_")[0] + "jpg"

                    # Create a pixmap from the poster image URL
                    pixmap = QPixmap()
                    pixmap.loadFromData(requests.get(poster_url).content)

                    # Set the pixmap to the poster_label
                    self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
                    self.image_label.show()

                    # Find the majority color of the poster image
                    # Convert the pixmap to a QImage
                    image = pixmap.toImage()

                    smooth_color_change(image)

                self.description_label.setText(f"Your favorite genre was <b>{favorite_genre}</b>, and you watched <b>{len(self.filtered_data)}</b> titles in that genre.<br>"
                                               f"<b>{favorite_genre_title}</b> was one of them, and you rated it <b>{favorite_genre_title_rating}</b>/10.<br><br>")

                # Add the genres, their counts, and their average ratings and the love formula to the description label (only the top 5)
                self.description_label.setText(self.description_label.text() + f"<br><br><b>Your Top 5 Genres for {self.year}:</b><br>"
                                               + "<br>".join([f"<b>{key}:</b> {value[0]} titles, {value[1]:.2f}/10 average rating, {value[2]:.2f} ❤️" for key, value in list(self.genres.items())[:5]]))

                self.description_label.show()

            case 8: # Favorite TV shows
                random_genres, favorite_tv_shows = self.favorite_tv_shows()

                if random_genres is None and favorite_tv_shows is None:
                    self.description_label.setText("No TV shows found in the selected year.")
                    self.image_label.hide()

                else:
                    self.header_label.setText(f"<h1>From {random_genres[0]} to {random_genres[1]}, these are the TV shows that you enjoyed the most this year.</h1>")
                    self.previous_button.setText("< What were your favorite genres?")
                    self.next_button.setText("Who was your favorite director? >")

                    # Get the average rating for the tv shows in the selected year
                    self.average_tv_shows_rating = self.tv_shows_data['Your Rating'].mean()

                    self.description_label.setText(f"You watched a total of <b>{len(favorite_tv_shows)} TV shows</b> in {self.year} "
                                                   f"with an average rating of {self.average_tv_shows_rating:.2f}.<br><br>")

                    # Add the TV shows, their average ratings, episode counts, and love formulas to the description label (only the top 5)
                    self.description_label.setText(
                        self.description_label.text() + f"<br><br><b>Your Top 5 TV Shows for {self.year}:</b><br>"
                        + "<br>".join([f"<b>{show['Name']}:</b> {show['Your Rating']}/10, {show['Episode Count']} episodes, "
                                       f"{show['Average Episode Rating']:.2f}/10 average episode rating, {show['Love Formula']:.2f} ❤️"
                                       for show in favorite_tv_shows[:5]]))

                    # Choose a random TV show from the list
                    random_tv_show = random.choice(favorite_tv_shows)

                    # Get the URL of the selected TV show, if it exists.
                    # If there are multiple URLs in the list, choose one randomly
                    random_tv_show_url = random.choice(random_tv_show['URL'])

                    if random_tv_show_url is not None:
                        self.image_label.show()
                        # Get the poster URL of the selected TV show
                        soup = BeautifulSoup(browser.open(random_tv_show_url).read(), 'html.parser')

                        # Get the movie poster URL from the IMDb page
                        poster_image = soup.find('img', class_='ipc-image')

                        if poster_image:
                            poster_url = poster_image['src']
                            print(poster_url)

                            # Get the biggest poster image by changing the url
                            # For example:
                            # - URL we get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@._V1_QL75_UX190_CR0,0,190,281_.jpg
                            # - URL we want to get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@.jpg
                            # Remove everything except ".jpg" after "@@"
                            if "@@" in poster_url:
                                poster_url = poster_url.split("@@")[0] + "@@.jpg"

                            else:
                                poster_url = poster_url.split("_")[0] + "jpg"

                            # Create a pixmap from the poster image URL
                            pixmap = QPixmap()
                            pixmap.loadFromData(requests.get(poster_url).content)

                            # Set the pixmap to the poster_label
                            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
                            self.image_label.show()

                            # Find the majority color of the poster image
                            # Convert the pixmap to a QImage
                            image = pixmap.toImage()

                            smooth_color_change(image)

            case 9: # Favorite director
                self.header_label.setText(f"<h1>These are the movie directors that inspired you in {self.year}.</h1>")
                self.previous_button.setText("< What were your favorite TV shows?")
                self.next_button.setText("Who was your favorite actor? >")
                self.next_button.show()

                # Get the favorite director and filter the data
                favorite_directors = self.favorite_directors()

                if favorite_directors is None:
                    self.description_label.setText("No directors found in the selected year.")
                    self.image_label.hide()

                else:
                    # Show the top 5 directors in the description label
                    self.description_label.setText(f"You watched a total of <b>{len(favorite_directors)} movies</b> in {self.year}.<br><br>"
                                                    f"<b>Your Top 5 Directors for {self.year}:</b><br>"
                                                    + "<br>".join([f"<b>{director['Name']}:</b> {director['Movie Count']} movies, "
                                                                   f"{director['Average Movie Rating']:.2f}/10 average movie rating, {director['Love Formula']:.2f} ❤️"
                                                                   for director in favorite_directors[:5]]))

                    # Choose the first director from the list
                    top_director = favorite_directors[0]

                    # If the director's name contains a comma, remove everything after the comma
                    if "," in top_director['Name']:
                        top_director['Name'] = top_director['Name'].split(",")[0]

                    # Replace spaces with %20 in the director's name
                    top_director['Name'] = top_director['Name'].replace(" ", "%20")

                    # Search on IMDB
                    search_url = f"https://www.imdb.com/find?q={top_director['Name']}&ref_=nv_sr_sm"
                    print(search_url)

                    # Get the HTML content of the search URL
                    search_html = requests.get(search_url, headers=headers).text

                    # Create a BeautifulSoup object from the HTML content
                    search_soup = BeautifulSoup(search_html, 'html.parser')

                    # Get the first result
                    first_result = search_soup.find("div", class_="ipc-metadata-list-summary-item__tc").a['href']

                    # Get the director's page URL
                    director_url = f"https://www.imdb.com{first_result}"

                    # Get the poster URL of the selected director
                    soup = BeautifulSoup(browser.open(director_url).read(), 'html.parser')

                    # Get the director's poster URL from the IMDb page
                    poster_image = soup.find('img', class_='ipc-image')

                    if poster_image:
                        poster_url = poster_image['src']
                        print(poster_url)

                        # Get the biggest poster image by changing the url
                        # For example:
                        # - URL we get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@._V1_QL75_UX190_CR0,0,190,281_.jpg
                        # - URL we want to get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@.jpg
                        # Remove everything except ".jpg" after "@@"
                        if "@@" in poster_url:
                            poster_url = poster_url.split("@@")[0] + "@@.jpg"

                        else:
                            poster_url = poster_url.split("_")[0] + "jpg"

                        # Create a pixmap from the poster image URL
                        pixmap = QPixmap()
                        pixmap.loadFromData(requests.get(poster_url).content)

                        # Set the pixmap to the poster_label
                        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
                        self.image_label.show()

                        # Find the majority color of the poster image
                        # Convert the pixmap to a QImage
                        image = pixmap.toImage()

                        smooth_color_change(image)


            case 10: # Favorite actor
                self.header_label.setText(f"<h1>Actors</h1>")
                self.description_label.setText(f"Calculating your favorite actors for {self.year}...")
                self.previous_button.setText("< Who was your favorite director?")
                self.next_button.setEnabled(False)
                self.next_button.setText("-")
                self.next_button.hide()
                app.processEvents()

                """
                actors = self.favorite_actors()
                print(actors)

                
                # Show the top 5 actors in the description label
                self.description_label.setText(f"You watched a total of <b>{len(actors)} movies</b> in {self.year}.<br><br>"
                                               f"<b>Your Top 5 Actors for {self.year}:</b><br>"
                                               + "<br>".join([f"<b>{actor[0]}:</b> {actor[1][1]} movies, "
                                                              f"{actor[1][0]:.2f}/10 average movie rating, {actor[1][2]:.2f} ❤️"
                                                              for actor in actors[:5]]))

                # Choose the first actor from the list
                top_actor = actors[0]
                print(top_actor)

                # If the actor's name contains a comma, remove everything after the comma
                if "," in top_actor[0]:
                    top_actor[0] = top_actor[0].split(",")[0]

                # Get the name of the actor
                actor_name = top_actor[0]

                # Replace spaces with %20 in the actor's name
                actor_name = actor_name.replace(" ", "%20")

                # Search on IMDB
                search_url = f"https://www.imdb.com/find?q={actor_name}&ref_=nv_sr_sm"
                print(search_url)

                # Get the HTML content of the search URL
                search_html = requests.get(search_url, headers=headers).text

                # Create a BeautifulSoup object from the HTML content
                search_soup = BeautifulSoup(search_html, 'html.parser')

                # Get the first result
                first_result = search_soup.find("div", class_="ipc-metadata-list-summary-item__tc").a['href']

                # Get the actor's page URL
                actor_url = f"https://www.imdb.com{first_result}"

                # Get the poster URL of the selected director
                soup = BeautifulSoup(browser.open(actor_url).read(), 'html.parser')

                # Get the actor's poster URL from the IMDb page
                poster_image = soup.find('img', class_='ipc-image')

                if poster_image:
                    poster_url = poster_image['src']
                    print(poster_url)

                    # Get the biggest poster image by changing the url
                    # For example:
                    # - URL we get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@._V1_QL75_UX190_CR0,0,190,281_.jpg
                    # - URL we want to get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@.jpg
                    # Remove everything except ".jpg" after "@@"
                    if "@@" in poster_url:
                        poster_url = poster_url.split("@@")[0] + "@@.jpg"

                    else:
                        poster_url = poster_url.split("_")[0] + "jpg"

                    # Create a pixmap from the poster image URL
                    pixmap = QPixmap()
                    pixmap.loadFromData(requests.get(poster_url).content)

                    # Set the pixmap to the poster_label
                    self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
                    self.image_label.show()

                    # Find the majority color of the poster image
                    # Convert the pixmap to a QImage
                    image = pixmap.toImage()

                    smooth_color_change(image)
                    """
                self.description_label.setText("This functionality does not work at the moment due to IMDb's changes to the site.")

    def favorite_tv_shows(self):
        # Filter the data so that only the TV shows remain (filtered_data is already filtered to the selected year)
        self.tv_shows_data = self.filtered_data[self.filtered_data['Title Type'] == "TV Series"]

        # Filter the data so that only the TV episodes remain (filtered_data is already filtered to the selected year)
        self.tv_episodes_data = self.filtered_data[self.filtered_data['Title Type'] == "TV Episode"]

        if self.tv_shows_data.empty and self.tv_episodes_data.empty:
            return None, None

        # Create a dictionary to store the TV show names, their average ratings, their episode counts, and their average episode ratings
        tv_shows = {}

        if not self.tv_shows_data.empty:
            # Loop through the TV shows
            for index, row in self.tv_shows_data.iterrows():
                # Get the TV show name
                tv_show = row['Title']

                # Get the TV show rating
                tv_show_rating = row['Your Rating']

                # Check if the TV show is already in the dictionary
                # If not, create a new entry
                if tv_show not in tv_shows:
                    tv_shows[tv_show] = {
                        'Name': tv_show,
                        'Your Rating': tv_show_rating,
                        'Episode Count': 0,
                        'Average Episode Rating': 0,
                        'Love Formula': 0,
                        'URL': [row['URL']]
                    }

        if not self.tv_episodes_data.empty:
            # Loop through the TV episodes
            for index, row in self.tv_episodes_data.iterrows():
                # Get the TV show name
                tv_show = row['Title']
                title_url = row['URL']

                # Split the title into series name and episode name
                # There are four possibilities:
                # "Series Name: Episode Name",
                # "Series Name: 'Episode Name: Episode Part'",
                # "'IP Name: Series Name': Episode Name",
                # "'IP Name: Series Name': 'Episode Name: Episode Part'"
                title_split = tv_show.split(":")

                # Determine how many colons are in the title and act accordingly
                num_colons = len(title_split)

                if num_colons == 2:
                    # Format: "Series Name: Episode Name"
                    tv_show = title_split[0]
                elif num_colons == 3:
                    print(title_split)
                    # Format: "Series Name: 'Episode Name: Episode Part'" or "'IP Name: Series Name': Episode Name"

                    # Get the HTML content of the title URL
                    title_html = requests.get(title_url, headers=headers).text

                    # Create a BeautifulSoup object from the HTML content
                    title_soup = BeautifulSoup(title_html, 'html.parser')

                    # Get the title from the HTML content
                    tv_show = title_soup.find("div", class_="sc-2a168135-0 flmBNm").a.text

                elif num_colons == 4:
                    # Format: "'IP Name: Series Name': 'Episode Name: Episode Part'"
                    tv_show = title_split[0] + ":" + title_split[1]
                else:
                    # Handle unexpected formats
                    continue  # Skip this item

                # Get the TV episode rating
                tv_episode_rating = row['Your Rating']

                # Check if the TV show is in the dictionary
                # If not, create a new entry
                if tv_show not in tv_shows:
                    tv_shows[tv_show] = {
                        'Name': tv_show,
                        'Your Rating': 0,
                        'Episode Count': 1,
                        'Average Episode Rating': tv_episode_rating,
                        'Love Formula': 0,
                        'URL': [row['URL']]
                    }

                else:
                    # Increment the episode count
                    tv_shows[tv_show]['Episode Count'] += 1

                    # Add the episode rating to the total
                    tv_shows[tv_show]['Average Episode Rating'] += tv_episode_rating

                    # Add the URL to the list
                    tv_shows[tv_show]['URL'].append(row['URL'])


        # Loop through the dictionary and get the average episode rating for each TV show
        for key, value in tv_shows.items():
            # Calculate the average episode rating if the episode count is not 0
            if value['Episode Count'] != 0:
                tv_shows[key]['Average Episode Rating'] /= value['Episode Count']

            # Calculate the love formula for each TV show (episode count^1.3 * average episode rating^5 / 1000)
            if value['Episode Count'] != 0 and value['Your Rating'] != 0:
                if value['Episode Count'] > 1:
                    tv_shows[key]['Love Formula'] = (math.sqrt((value['Average Episode Rating'] ** 5) *
                                                               (value['Your Rating'] ** 5)) *
                                                     (value['Episode Count'] ** 1.3) / 1000)
                else:
                    tv_shows[key]['Love Formula'] = (math.sqrt((value['Average Episode Rating'] ** 5) *
                                                               (value['Your Rating'] ** 5)) *
                                                     ((value['Episode Count'] + 0.5) ** 1.3) / 1000)

            elif value['Episode Count'] != 0 and value['Your Rating'] == 0:
                tv_shows[key]['Love Formula'] = (
                        (value['Average Episode Rating'] ** 2.5) *
                        (value['Episode Count'] ** 1.3) / 1000
                )

            elif value['Episode Count'] == 0 and value['Your Rating'] != 0:
                tv_shows[key]['Love Formula'] = (
                        (value['Your Rating'] ** 5) / 1000
                )

        # Sort the dictionary by the love formula
        tv_shows = dict(sorted(tv_shows.items(), key=lambda x: x[1]['Love Formula'], reverse=True))

        # Create a list of dictionaries from the dictionary
        tv_shows = [value for key, value in tv_shows.items()]

        # Get a list of unique genres from the 'Genres' columns of tv_shows_data and tv_episodes_data
        unique_genres = np.append(self.tv_shows_data['Genres'].unique(), self.tv_episodes_data['Genres'].unique())

        # If any of the genres have multiple genres, split them and add them to the list
        for genre in unique_genres:
            if "," in genre:
                unique_genres = np.append(unique_genres, genre.split(", "))
                unique_genres = np.delete(unique_genres, np.where(unique_genres == genre))


        # Remove the empty string from the list
        unique_genres = np.delete(unique_genres, np.where(unique_genres == ""))

        # Remove the duplicates from the list
        unique_genres = np.unique(unique_genres)

        # Choose two random genres from the list
        if len(unique_genres) >= 2:
            random_genres = np.random.choice(unique_genres, size=2, replace=False)

        if tv_shows:
            return random_genres, tv_shows
        else:
            return None, None

    def favorite_directors(self):
        # Filter the data so that only the movies remain (filtered_data is already filtered to the selected year)
        self.movies_data = self.filtered_data[self.filtered_data['Title Type'] == "Movie"]

        print(self.filtered_data)
        print(self.movies_data)

        # Create a dictionary to store the director names, their average ratings, and their movie counts
        directors = {}

        # Loop through the movies
        for index, row in self.movies_data.iterrows():
            # Get the director name
            director = row['Directors']

            # Get the movie rating
            movie_rating = row['Your Rating']

            # Check if the director is already in the dictionary
            # If not, create a new entry
            if director not in directors:
                directors[director] = {
                    'Name': director,
                    'Movie Count': 1,
                    'Average Movie Rating': movie_rating,
                    'Love Formula': 0
                }

            else:
                # Increment the movie count
                directors[director]['Movie Count'] += 1

                # Add the movie rating to the total
                directors[director]['Average Movie Rating'] += movie_rating

        # Loop through the dictionary and get the average movie rating for each director
        for key, value in directors.items():
            # Calculate the average movie rating if the movie count is not 0
            if value['Movie Count'] != 0:
                directors[key]['Average Movie Rating'] /= value['Movie Count']

            # Calculate the love formula for each director (movie count^1.3 * average movie rating^5 / 1000)
            directors[key]['Love Formula'] = (math.sqrt((value['Average Movie Rating'] ** 5)) *
                                              (value['Movie Count'] ** 1.3) / 1000)

        # Sort the dictionary by the love formula
        directors = dict(sorted(directors.items(), key=lambda x: x[1]['Love Formula'], reverse=True))

        # Create a list of dictionaries from the dictionary
        directors = [value for key, value in directors.items()]

        return directors if directors else None

    def favorite_actors(self):
        """
        actor_ratings = {}
        actor_title_counts = {}
        actor_titles = {}

        yearFound = False
        breakFlag = False

        lists_link = checkPreferences()
        print(lists_link)

        # Strip away the part after "?"
        lists_link = lists_link.split("?")[0]
        print(lists_link)

        ratings_link = lists_link.replace("lists", f"ratings?sort=date_added,desc&ratingFilter=0&mode=detail&ref_=undefined&lastPosition=0")
        print(ratings_link)

        # Send an HTTP GET request to fetch the ratings page
        try:
            # Open the URL
            response = browser.open(ratings_link)

            html_content = response.read()

            # Get the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract the movie or TV series details from the list
            movie_details = soup.select('.lister-item-content')

            # Check how many titles are there in the list
            list_details = soup.select(".lister-list-length")
            number_of_titles_str = list_details[0].text.strip()
            print(number_of_titles_str)

            # Use a regular expression to extract the integer
            match = re.search(r'\d+', number_of_titles_str)
            print(match)

            if match:
                # The group(0) will contain the first matched integer
                number_of_titles = int(match.group(0))
                print(number_of_titles)

            # Calculate the page count
            page_count = math.ceil(number_of_titles / 100)
            print(page_count)

            # Loop through the pages
            for page in range(0, page_count + 1):
                # Check if the breakFlag is set to True
                if breakFlag:
                    print("breakFlag is True")
                    break

                for movie in movie_details:
                    if breakFlag:
                        print("breakFlag is True")
                        break

                    # Get the title
                    title_element = movie.select_one(".lister-item-header")
                    title = title_element.text.strip()
                    print(title)

                    # Extract the title type
                    isEpisode_element = movie.find("small", class_="text-primary")
                    if isEpisode_element:
                        isEpisode = isEpisode_element.text.strip()
                    else:
                        isEpisode = ""

                    print(isEpisode)

                    # Find the <p> tag with the text 'Rated on'
                    rating_date_tag = movie.find('p', text=lambda t: t and 'Rated on' in t)
                    print(rating_date_tag)

                    # Extract the rating year from the tag
                    rating_year = int(rating_date_tag.text.split(" ")[-1])
                    print(rating_year)

                    # Check if the rating year is the same as the selected year
                    if rating_year == self.year:
                        # yearFound flag is set to True
                        yearFound = True
                        print("yearFound is True")

                        # Check if the title type is not an episode
                        if "Episode:" not in isEpisode:
                            # Extract actors and rating
                            # Find the <p> element with directors and actors
                            p_element = movie.select("p.text-muted a")
                            print(p_element)

                            # Extract the actors from the text of each item in the list
                            actors = [actor.text.strip() for actor in p_element if "dir" not in actor['href']]
                            print(actors)

                            # Get the rating and directors from ratings.csv and remove directors from actors
                            with open('ratings.csv', 'r') as file:
                                ratings_data = list(csv.DictReader(file))

                                # Loop through the ratings_data list
                                for item in ratings_data:
                                    # Check if the title type is "Movie"
                                    if item['Title Type'] == "Movie":
                                        # Extract title and rating
                                        rating = int(item['Your Rating'])

                                        # Check if the title is the same as the current title
                                        if title == item['Original Title']:
                                            # Extract directors
                                            directors = item['Directors'].split(", ")

                                            # Remove directors from actors
                                            actors = [actor for actor in actors if actor not in directors]

                                            break

                                # Loop through the actors
                                for actor in actors:
                                    # Check if the actor is already in the dictionary
                                    if actor in actor_ratings:
                                        # Add the rating to the existing actor
                                        actor_ratings[actor] += rating
                                        actor_title_counts[actor] += 1
                                        actor_titles[actor].append(title)
                                    else:
                                        # Add the actor to the dictionary
                                        actor_ratings[actor] = rating
                                        actor_title_counts[actor] = 1
                                        actor_titles[actor] = [title]

                    else:
                        if yearFound:
                            print("yearFound is True")
                            # This means we have found the year, and now we are in the previous year
                            breakFlag = True
                            break
                        break


                # Next page
                next_page = soup.find('a', class_='flat-button lister-page-next next-page')
                print(next_page)

                if next_page:
                    next_page_url = f'https://www.imdb.com{next_page["href"]}'
                    print(next_page_url)
                    response = browser.open(next_page_url)
                    html_content = response.read()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    movie_details = soup.select('.lister-item-content')

            # Check if there are any ratings
            if actor_ratings:
                # Calculate the average rating for each actor
                actor_average_ratings = {
                    actor: actor_ratings[actor] / actor_title_counts[actor]
                    for actor in actor_ratings
                }

                # Calculate the love_formula for each actor
                actor_love_formulas = {
                    actor: (avg_rating, actor_title_counts[actor],
                            (avg_rating ** 5) * (actor_title_counts[actor] ** 1.2) / 1000)
                    for actor, avg_rating in actor_average_ratings.items()
                }

                # Sort the actors by the love_formula in descending order
                sorted_actors = sorted(actor_love_formulas.items(), key=lambda x: x[1][2], reverse=True)

                return sorted_actors
            else:
                print("No ratings found")
                return []

        except mechanize.URLError as e:
            print("URL Error: ", e)
            return []
        """
        return ["This feature does not work at the moment due to IMDb's changes to their website.", "", ""]

class InsightsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insights")
        self.resize(800, 500)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Create a top-level layout for the main content
        content_layout = QVBoxLayout()
        self.main_layout.addLayout(content_layout)

        # Create a label to show the insights
        insights_label = QLabel("<h2>Insights</h2>")
        insights_label.setAlignment(Qt.AlignCenter)

        # Add the label to the content layout
        content_layout.addWidget(insights_label)

        self.user_ratings_vs_IMDB_ratings()
        self.user_watched_vs_release_date()


    # Class functions
    def previous(self):
        self.current_case -= 1
        self.updateUI()

    def next(self):
        self.current_case += 1
        self.updateUI()

    def updateUI(self):
        # Clear the layout
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)

        # Create a new widget based on the current case
        self.createWidget(self.current_case)

        # Add the widget to the content layout
        self.content_layout.addWidget(self.widget)

    def user_ratings_vs_IMDB_ratings(self):
        # Open the ratings.csv file
        with open('ratings.csv', 'r') as file:
            # Read the file as a dictionary
            ratings_data = list(csv.DictReader(file))

            # Create dictionaries to store the user ratings and the IMDB ratings
            ratings = {}

            # Loop through the ratings_data list
            for item in ratings_data:
                # Extract the title name, user rating and the IMDB rating for each title
                title = item['Original Title']
                user_rating = float(item['Your Rating'])
                imdb_rating = float(item['IMDb Rating'])

                # ratings dictionary will have the title as the key and a tuple of user rating and IMDB rating as the value
                ratings[title] = (user_rating, imdb_rating)

            # Calculate the average difference between the user ratings and the IMDB ratings
            average_difference = sum([(user_rating - imdb_rating) for user_rating, imdb_rating in ratings.values()]) / len(ratings)
            print("Average Difference: ", average_difference)

            # Calculate the average user rating and the average IMDB rating
            average_user_rating = sum([user_rating for user_rating, imdb_rating in ratings.values()]) / len(ratings)
            average_imdb_rating = sum([imdb_rating for user_rating, imdb_rating in ratings.values()]) / len(ratings)
            print("Average User Rating: ", average_user_rating)
            print("Average IMDB Rating: ", average_imdb_rating)

            # Calculate the maximum difference that user rated a title higher than the IMDB rating
            max_difference = max([user_rating - imdb_rating for user_rating, imdb_rating in ratings.values()])
            # Print the maximum difference and the title
            print("Max Diff: ", max_difference, [title for title, (user_rating, imdb_rating) in ratings.items() if user_rating - imdb_rating == max_difference])

            # Calculate the maximum difference that user rated a title lower than the IMDB rating
            min_difference = min([user_rating - imdb_rating for user_rating, imdb_rating in ratings.values()])
            # Print the minimum difference and the title
            print("Min Diff: ", min_difference, [title for title, (user_rating, imdb_rating) in ratings.items() if user_rating - imdb_rating == min_difference])

            # Calculate the percentage of titles that the user rated higher than the IMDB rating
            higher_than_imdb = len([user_rating for user_rating, imdb_rating in ratings.values() if user_rating > imdb_rating]) / len(ratings) * 100
            print(f"Higher than IMDB: {higher_than_imdb:.2f}%")

            # Calculate the percentage of titles that the user rated the same as the IMDB rating
            same_as_imdb = len([user_rating for user_rating, imdb_rating in ratings.values() if user_rating == imdb_rating]) / len(ratings) * 100
            print(f"Same as IMDB: {same_as_imdb:.2f}%")

            # Calculate the percentage of titles that the user rated lower than the IMDB rating
            lower_than_imdb = len([user_rating for user_rating, imdb_rating in ratings.values() if user_rating < imdb_rating]) / len(ratings) * 100
            print(f"Lower than IMDB: {lower_than_imdb:.2f}%")

    def user_watched_vs_release_date(self):
        # Open the ratings.csv file
        with open('ratings.csv', 'r') as file:
            # Read the file as a dictionary
            ratings_data = list(csv.DictReader(file))

            # Create a dictionary to store the release dates and user rated dates
            dates = {}

            # Loop through the ratings_data list
            for item in ratings_data:
                print(item)
                # Extract the release year and the user rating for each title
                release_date = item['Release Date']
                user_date = item['Date Rated']

                # Check if the release date and user date are not empty
                if release_date == "" or user_date == "":
                    continue
                # Check if the release date is in the expected format (YYYY-MM-DD)
                if not re.match(r"\d{4}-\d{2}-\d{2}", release_date):
                    continue

                # Convert the user date and release date from strings in YYYY-MM-DD format to datetime objects
                release_date = datetime.strptime(release_date, "%Y-%m-%d")
                user_date = datetime.strptime(user_date, "%Y-%m-%d")

                # Add the title name as the key and the user date and release date as the tuple value to the dictionary
                dates[item['Original Title']] = (release_date, user_date)

            # Calculate the average difference between the user rated dates and the release dates
            average_difference = sum([(user_date - release_date).days for release_date, user_date in dates.values()]) / len(dates)

            # Calculate the years, months and days
            years = f"{int(average_difference // 365)} years," if average_difference // 365 > 0 else ""
            months = f"{int((average_difference % 365) // 30)} months, and" if (average_difference % 365) // 30 > 0 else ""
            days = f"{(average_difference % 365) % 30} days" if (average_difference % 365) % 30 > 0 else ""
            print(f"Average Date Difference: {years} {months} {days} after release")

            # Calculate the maximum difference that user rated a title after the release date
            max_difference = max([(user_date - release_date).days for release_date, user_date in dates.values()])
            years = f"{int(max_difference // 365)} years," if max_difference // 365 > 0 else ""
            months = f"{int((max_difference % 365) // 30)} months, and" if (max_difference % 365) // 30 > 0 else ""
            days = f"{(max_difference % 365) % 30} days" if (max_difference % 365) % 30 > 0 else ""
            print(f"Max Diff: {years} {months} {days}", [title for title, (release_date, user_date) in dates.items() if (user_date - release_date).days == max_difference])

            # Calculate the minimum difference that user rated a title after the release date
            min_difference = min([(user_date - release_date).days for release_date, user_date in dates.values()])
            years = f"{int(min_difference // 365)} years," if min_difference // 365 > 0 else ""
            months = f"{int((min_difference % 365) // 30)} months, and" if (min_difference % 365) // 30 > 0 else ""
            days = f"{(min_difference % 365) % 30} days" if (min_difference % 365) % 30 > 0 else ""
            print(f"Min Diff: {years} {months} {days}", [title for title, (release_date, user_date) in dates.items() if (user_date - release_date).days == min_difference])
class ModernApp(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.theme = "dark"
        self.star_color = "white"
        # Create a star icon at the top left corner on the movie poster
        star_icon = QIcon("star.svg")
        star_icon_renderer = QSvgRenderer("star.svg")
        self.star_icon_pixmap = QPixmap(20, 20)
        self.star_icon_pixmap.fill(Qt.transparent)
        self.star_icon_painter = QPainter(self.star_icon_pixmap)
        star_icon_renderer.render(self.star_icon_painter)
        self.star_icon_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        self.star_icon_painter.fillRect(self.star_icon_pixmap.rect(), QColor(255, 255, 255))
        self.star_icon_painter.end()
        self.star_icon_label = QLabel()
        self.star_icon_label.setPixmap(self.star_icon_pixmap)

        self.min_rating = 0.0
        self.max_runtime = 0
        self.selected_genre = "All Genres"
        self.selected_type = "All Types"
        self.max_episodes = 0

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Watchable: IMDB Recommender")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.resize(800, 500)

        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # Create a menu toolbar
        menu_bar = self.menuBar()
        options_menu = menu_bar.addMenu("Options")

        statistics_action = QAction("Your Statistics", self)
        statistics_action.triggered.connect(self.statistics)

        help_action = QAction("Help", self)
        help_action.triggered.connect(self.help)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)

        now_watching_action = QAction("Now Watching", self)
        now_watching_action.triggered.connect(self.now_watching)

        year_review_action = QAction("Year Review", self)
        year_review_action.triggered.connect(self.year_review)

        insights_action = QAction("Insights", self)
        insights_action.triggered.connect(self.insights)

        menu_bar.addAction(statistics_action)
        menu_bar.addAction(now_watching_action)
        menu_bar.addAction(year_review_action)
        menu_bar.addAction(insights_action)
        menu_bar.addAction(help_action)
        menu_bar.addAction(about_action)

        # Create a "User Preferences" action in the "Options" menu
        user_preferences_action = QAction("User Preferences", self)
        user_preferences_action.triggered.connect(self.create_preferences_file)
        options_menu.addAction(user_preferences_action)

        # Create a "Favorites" action in the "Options" menu
        favorites_action = QAction("Favorites", self)
        favorites_action.triggered.connect(self.favorites)
        options_menu.addAction(favorites_action)

        # Create a "Theme" submenu in the "Options" menu
        theme_menu = QMenu("Theme", self)
        options_menu.addMenu(theme_menu)

        # Create a "Light" action in the "Theme" submenu
        light_theme_action = QAction("Light", self)
        light_theme_action.triggered.connect(self.light_theme)
        theme_menu.addAction(light_theme_action)

        # Create a "Dark" action in the "Theme" submenu
        dark_theme_action = QAction("Dark", self)
        dark_theme_action.triggered.connect(self.dark_theme)
        theme_menu.addAction(dark_theme_action)

        # Check if the preferences file exists, and create it if not
        self.preferences_file = "user_preferences.txt"
        self.user_lists_link = ""

        # Create a combo box to select a list
        self.list_combo = QComboBox()
        self.list_combo.addItem("Watchlist")  # Add a default option

        # Find all the .csv files in the current directory except for ratings.csv, watchlist.csv, rewatch.csv, watching.csv, favorites.csv
        lists = [file for file in os.listdir() if
                 file.endswith(".csv") and file not in ["ratings.csv", "watchlist.csv", "rewatch.csv", "watching.csv",
                                                        "favorites.csv"]]

        # Add the list names to the combo box
        if lists:
            for list_name in lists:
                self.list_combo.addItem(list_name.split(".")[0])

        # Check if the preferences file exists or not empty
        if not self.check_preferences_file() or os.stat(self.preferences_file).st_size == 0:
            self.create_preferences_file()

        # Center every item in the combo box
        self.list_combo.setEditable(True)
        self.list_combo.lineEdit().setAlignment(Qt.AlignCenter)

        # Make the combo box searchable
        self.list_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.list_combo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        self.main_layout.addWidget(self.list_combo)

        # Create a "Filters" button
        filters_button = QPushButton("Filters", self)
        filters_button.clicked.connect(self.show_filters)
        self.main_layout.addWidget(filters_button)

        # Create a container widget to hold filter widgets
        self.filters_container = QWidget()
        self.filters_container.hide()
        self.main_layout.addWidget(self.filters_container)

        # Create a combo box to select a title type
        self.title_type_combo = QComboBox()
        self.title_type_combo.addItem("All Types")  # Add a default option
        self.title_type_combo.addItems(["Movies", "TV Series", "TV Episodes", "TV Mini-Series", "Shorts", "TV Movies", "TV Specials", "Videos", "Video Games", "Podcasts", "Podcast Episodes", "TV Mini-Series", "TV Shorts", "Documentaries", "Music Videos"])


        # Create a QSlider for selecting minimum IMDB rating
        self.rating_slider = QSlider(Qt.Horizontal)
        self.rating_slider.setMinimum(0)
        self.rating_slider.setMaximum(20)  # To allow 0.5 increments, use 20 instead of 10
        self.rating_slider.setValue(0)  # Default to 0.0
        self.rating_slider.setTickInterval(1)
        self.rating_slider.setTickPosition(QSlider.TicksAbove)

        # Create a QSlider for selecting maximum runtime
        self.runtime_slider = QSlider(Qt.Horizontal)
        self.runtime_slider.setMinimum(0)
        self.runtime_slider.setMaximum(180)  # Maximum runtime is 180 minutes
        self.runtime_slider.setValue(0)  # Default to 0
        self.runtime_slider.setTickInterval(1)
        self.runtime_slider.setTickPosition(QSlider.TicksAbove)

        # Create a QLabel to display the selected rating
        self.rating_label = QLabel("Minimum Rating: No Limit")

        # Create a QLabel to display the selected runtime
        self.runtime_label = QLabel("Maximum Runtime: No Limit")

        # Update the label when the slider value changes
        self.rating_slider.valueChanged.connect(self.update_rating_label)

        # Update the label when the slider value changes
        self.runtime_slider.valueChanged.connect(self.update_runtime_label)

        # Create a QComboBox for selecting genres
        self.genre_combo = QComboBox()
        self.genre_combo.addItem("All Genres")  # Add a default option
        # Add genre options to the combo box
        self.genre_combo.addItems(["Action", "Adult", "Adventure", "Animation",
                                   "Biography", "Comedy", "Crime", "Documentary",
                                   "Drama", "Family", "Fantasy", "Film Noir",
                                   "Game Show", "History", "Horror", "Musical",
                                   "Music", "Mystery", "News", "Reality-TV",
                                   "Romance", "Sci-Fi", "Short", "Sport",
                                   "Talk-Show", "Thriller", "War", "Western"])

        # Create a "Apply Filters" button
        apply_filters_button = QPushButton("Apply Filters")
        apply_filters_button.clicked.connect(self.apply_filters)

        # Create a layout for filter widgets
        filter_layout = QVBoxLayout()
        filter_layout.addWidget(self.title_type_combo)
        filter_layout.addWidget(self.genre_combo)
        filter_layout.addWidget(self.rating_label)
        filter_layout.addWidget(self.rating_slider)
        filter_layout.addWidget(self.runtime_label)
        filter_layout.addWidget(self.runtime_slider)
        filter_layout.addWidget(apply_filters_button)
        self.filters_container.setLayout(filter_layout)

        # Create a new QWidget for displaying the movie/series poster and details, horizontally
        self.poster_widget = QWidget()
        self.poster_layout = QHBoxLayout()
        self.poster_widget.setLayout(self.poster_layout)
        self.main_layout.addWidget(self.poster_widget)

        # Create a new QWidget for displaying the IMDb and Letterboxd logos on top, and the movie/series details below
        self.logo_poster_widget = QWidget()
        self.logo_poster_layout = QVBoxLayout()

        self.logo_poster_widget.setLayout(self.logo_poster_layout)

        self.poster_label = QLabel()
        self.poster_label.hide()
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setStyleSheet("padding: 10px;")
        self.poster_label.setMinimumWidth(300)
        self.poster_label.setMinimumHeight(450)
        self.poster_label.setMaximumWidth(500)
        self.poster_label.setMaximumHeight(750)

        self.poster_layout.addWidget(self.poster_label)
        self.poster_layout.addWidget(self.logo_poster_widget)

        self.logo_label = QLabel("Test")
        self.logo_label.setStyleSheet("padding: 10px;")
        self.logo_label.hide()

        self.result_label = QLabel("Welcome to Watchable!<br>Your recommendation will appear here.")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("padding: 10px;")
        # Enable rich text
        self.result_label.setOpenExternalLinks(True)
        self.result_label.setAlignment(Qt.AlignCenter)

        self.logo_poster_layout.addWidget(self.logo_label)
        self.logo_poster_layout.addWidget(self.result_label)

        # Create a new QLabel for displaying the movie/series description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setStyleSheet("padding: 10px;")
        self.description_label.hide()
        self.main_layout.addWidget(self.description_label)

        # Create scroll areas for the logo label and result label
        self.result_scroll_area = QtWidgets.QScrollArea()
        self.result_scroll_area.setWidgetResizable(True)
        self.result_scroll_area.setFixedHeight(450)
        self.result_scroll_area.setAlignment(Qt.AlignCenter)
        self.result_scroll_area.hide()

        self.logo_poster_layout.addWidget(self.result_scroll_area)

        # Add the description label to a scroll area
        self.description_scroll_area = QtWidgets.QScrollArea()
        self.description_scroll_area.setWidgetResizable(True)
        self.description_scroll_area.setFixedHeight(250)
        self.description_scroll_area.setAlignment(Qt.AlignCenter)
        self.description_scroll_area.hide()

        self.main_layout.addWidget(self.description_scroll_area)

        # Create a new QPushButton for displaying more details about the movie/series
        self.more_details_button = QPushButton("More About This Title")
        self.more_details_button.clicked.connect(self.more_details)
        self.more_details_button.hide()
        self.main_layout.addWidget(self.more_details_button)


        # Add both the QLineEdit and the button to a container widget
        self.container = QWidget()
        self.container_layout = QHBoxLayout()
        self.container.setLayout(self.container_layout)

        # Add the container to the main layout
        self.main_layout.addWidget(self.container)

        self.setLayout(self.main_layout)

        self.find_movie_button = QPushButton("Find Something to Watch!")
        self.find_movie_button.clicked.connect(self.apply_filters)
        self.find_movie_button.clicked.connect(self.find_random_movie)
        self.main_layout.addWidget(self.find_movie_button)

    def check_preferences_file(self):
        return os.path.isfile(self.preferences_file)

    # Create a new preferences file in a form of dictionary
    def create_preferences_file(self):
        dialog = PreferencesDialog() # Open the "User Preferences" dialog
        result = dialog.exec_()

        if result == QDialog.Accepted:
            with open("user_preferences.txt", "w") as file:
                file.write(f"\"Last Update\": \"{datetime.now().strftime('%Y-%m-%d')}\"")

            # Update the combo box with the new lists
            window.list_combo.clear()
            window.list_combo.addItem("Watchlist")  # Add a default option

            # Find all the .csv files in the current directory except for ratings.csv, watchlist.csv, rewatch.csv, watching.csv, favorites.csv
            lists = [file for file in os.listdir() if file.endswith(".csv") and file not in ["ratings.csv", "watchlist.csv", "rewatch.csv", "watching.csv", "favorites.csv"]]

            # Add the list names to the combo box
            if lists:
                for list_name in lists:
                    window.list_combo.addItem(list_name.split(".")[0])


    def find_random_movie(self):
        # Change the cursor to indicate that the program is working
        QApplication.setOverrideCursor(Qt.WaitCursor)
        selected_index = self.list_combo.currentIndex()

        if selected_index == 0:
            self.update_result_label(0)
            app.processEvents()

            # Randomly select if the title is from IMDb Watchlist or Letterboxd Watchlist (0 for IMDb, 1 for Letterboxd)
            random_site = random.randint(0, 1)

            if random_site == 0:
                # Change the logo label to display IMDb.png image with 40x50 size
                self.logo_label.setPixmap(QPixmap("IMDb.png").scaled(40, 40))
                self.logo_label.show()

                self.list_random(self.min_rating, self.selected_genre, self.max_runtime, self.selected_type)

            elif random_site == 1:
                # Change the logo label to display letterboxd.png image with 40x40 size
                self.logo_label.setPixmap(QPixmap("letterboxd.png").scaled(40, 40))
                self.logo_label.show()

                self.list_random_letterboxd()

        else:
            self.update_result_label(1)
            app.processEvents()
            self.list_random(self.min_rating, self.selected_genre, self.max_runtime, self.selected_type)

        # Change the cursor back to normal
        self.poster_label.show()
        self.result_label.setAlignment(Qt.AlignVCenter)
        self.description_label.show()
        self.more_details_button.show()
        QApplication.restoreOverrideCursor()

    ## IF AN IMDb WATCHLIST, READ CSV FILE AND SELECT A MOVIE/SERIES RANDOMLY (WITH USER FILTERS) ##
    def list_random(self, min_rating, selected_genre, max_runtime, selected_type):

        # Define the destination file path where you want to save the CSV file
        self.list_name = f"{self.list_combo.currentText()}.csv"

        # Read the CSV file and store its data in a list of dictionaries
        csv_data = []
        with open(self.list_name, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                csv_data.append(row)

        # Check if there's data in the CSV file
        if csv_data:
            print("\nSuccessfully read the CSV file.")
            self.update_result_label(3)
            app.processEvents()

            # Filter the CSV data by minimum rating, maximum runtime and selected genre
            csv_data = [item for item in csv_data if 'IMDb Rating' in item and item['IMDb Rating'] and float(item['IMDb Rating']) >= min_rating]
            print(f"Filtered by rating: {min_rating} ({len(csv_data)} titles match)")

            if selected_genre != "All Genres":
                csv_data = [item for item in csv_data if selected_genre in item['Genres']]

            if max_runtime != 0:
                csv_data = [item for item in csv_data if 'Runtime (mins)' in item and item['Runtime (mins)'] and int(item['Runtime (mins)']) <= max_runtime]
                print(f"Filtered by runtime: {max_runtime} ({len(csv_data)} titles match)")

            if selected_type != "All Types":
                csv_data = [item for item in csv_data if selected_type in item['Title Type']]
                print(f"Filtered by title type: {selected_type} ({len(csv_data)} titles match)")

            self.result_label.setText(f"Our chefs are adding filters to enhance your selection's flavor...<br><br>"
                                      f"({len(csv_data)} titles match your preferences)")
            app.processEvents()

            # Check if there's data in the CSV file after filtering
            if csv_data:
                self.result_label.setText(f"We're handpicking a special title for you...<br><br>"
                                          f"({len(csv_data)} titles match your preferences)")
                app.processEvents()

                # Randomly select a row from the CSV data
                random_item = random.choice(csv_data)

                # Check if the user has rated the movie/series before
                user_rating = self.checkRatings(random_item['Original Title'], random_item['Title Type'])

                # To get the title type and the poster, we need to scrape the movie's/series' own page
                # Send an HTTP GET request to fetch the list page
                second_response = requests.get(random_item['URL'], headers=headers)

                # Check if the request was successful
                if second_response.status_code == 200:
                    self.update_result_label(5)
                    app.processEvents()
                    # Parse the HTML content of the page
                    second_soup = BeautifulSoup(second_response.content, 'html.parser')

                    director_details = second_soup.select("div.ipc-metadata-list-item__content-container")
                    if director_details:
                        directors = random_item['Directors'] if random_item['Directors'] != "" else director_details[0].select_one("a.ipc-metadata-list-item__list-content-item--link").text.strip()

                    # If the title is not a TV series, do not get the number of episodes
                    if random_item["Title Type"] == "TV Series" or random_item["Title Type"] == "TV Mini Series":
                        episode_details = second_soup.find('span', class_='ipc-title__subtext')

                        if episode_details:
                            number_of_episodes = int(episode_details.text.strip())

                    else:
                        number_of_episodes = 0

                    # Get the movie poster URL from the IMDb page
                    poster_image = second_soup.find('img', class_='ipc-image')

                    if poster_image:
                        poster_url = poster_image['src']
                        print(poster_url)

                        # Get the biggest poster image by changing the url
                        # For example:
                        # - URL we get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@._V1_QL75_UX190_CR0,0,190,281_.jpg
                        # - URL we want to get: https://m.media-amazon.com/images/M/MV5BMTI3MzYxMTA4NF5BMl5BanBnXkFtZTcwMDE4ODg3Mg@@.jpg
                        # Remove everything except ".jpg" after "@@"
                        if "@@" in poster_url:
                            poster_url = poster_url.split("@@")[0] + "@@.jpg"

                        else:
                            poster_url = poster_url.split("_")[0] + "jpg"

                        # Create a pixmap from the poster image URL
                        pixmap = QPixmap()
                        pixmap.loadFromData(requests.get(poster_url).content)

                        # Set the pixmap to the poster_label
                        self.poster_label.setPixmap(pixmap.scaled(self.poster_label.size(), Qt.KeepAspectRatio))

                        # Find the majority color of the poster image
                        # Convert the pixmap to a QImage
                        image = pixmap.toImage()

                        smooth_color_change(image)

                        # Create a star icon at the top left corner on the movie poster
                        star_icon = QIcon("star.svg")
                        star_icon_renderer = QSvgRenderer("star.svg")
                        self.star_icon_pixmap = QPixmap(20, 20)
                        self.star_icon_pixmap.fill(Qt.transparent)
                        self.star_icon_painter = QPainter(self.star_icon_pixmap)
                        star_icon_renderer.render(self.star_icon_painter)
                        self.star_icon_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                        self.star_icon_painter.fillRect(self.star_icon_pixmap.rect(), QColor(255, 255, 255))
                        self.star_icon_painter.end()

                        # Change the color of the star icon to yellow if it is in the favorites list
                        if self.check_favorites(random_item['Original Title']):
                            self.star_color = "yellow"
                            self.change_star_color(self.star_color)

                        else:
                            # If not in the favorites list, change the color of the star icon to white or black depending on the theme
                            if self.theme == "light":
                                self.star_color = "black"
                                self.change_star_color(self.star_color)

                            elif self.theme == "dark":
                                self.star_color = "white"
                                self.change_star_color(self.star_color)

                        self.star_icon_label = QLabel(self.poster_label)
                        self.star_icon_label.setPixmap(self.star_icon_pixmap)
                        self.star_icon_label.move(10, 10)
                        self.star_icon_label.show()

                        # When clicked, save the movie/series' title and URL to a CSV file name "favorites.csv" and change the color of the star icon to yellow
                        # When clicked again, remove the movie/series from the CSV file and change the color of the star icon to white or black depending on the theme
                        self.star_icon_label.mousePressEvent = lambda event: self.save_favorite(random_item['Original Title'], random_item['URL'])

                    description_details = second_soup.select_one("span[data-testid='plot-xl']")

                    if description_details:
                        description = description_details.text.strip()
                        self.description_label.setText(f"{description}")

                    # Extract and print the desired columns
                    self.result_label.setText(f"<a href=\"{random_item['URL']}\"><h1>{random_item['Original Title']}</h1></a><br>"
                                              f"<b>Title Type:</b> {random_item['Title Type']}<br>"
                                              f"<b>IMDb Rating:</b> {random_item['IMDb Rating']}<br>"
                                              f"<b>Runtime:</b> {random_item['Runtime (mins)']}<br>"
                                              f"<b>Episode Count:</b> {number_of_episodes}<br>"
                                              f"<b>Year:</b> {random_item['Year']}<br>"
                                              f"<b>Genres:</b> {random_item['Genres']}<br>"
                                              # Use csv to get the directors, if empty, use the scraped data
                                              f"<b>Director/Creator:</b> {directors}<br><br>"
                                              f"{user_rating}")

                else:
                    print("\nFailed to retrieve the list. Check the URL and try again.")

            else:
                # If there are no filtered movie details, show an error message
                self.result_label.setText(f"No title matches your criteria. Try again with different filters.")

                # Reset the poster_label
                self.poster_label.clear()
                print("The CSV file is empty.")
                return

    ## IF A LETTERBOXD WATCHLIST, READ CSV FILE AND SELECT A MOVIE/SERIES RANDOMLY (WITHOUT FILTERS) ##
    def list_random_letterboxd(self):
        # Get the CSV file from unzipped letterboxd_data folder
        letterboxd_csv = "letterboxd_data/watchlist.csv"

        # Read the CSV file and store its data in a list of dictionaries
        csv_data = []

        with open(letterboxd_csv, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                csv_data.append(row)

        # Check if there's data in the CSV file
        if csv_data:
            print("\nSuccessfully read the CSV file.")
            self.update_result_label(3)
            app.processEvents()

            # Randomly select a row from the CSV data
            random_item = random.choice(csv_data)

            # Check if the user has rated the movie/series before
            # user_rating = self.checkRatings(random_item['Title'], random_item['Type'])

            # To get the title type and the poster, we need to scrape the movie's/series' own page
            # Send an HTTP GET request to fetch the list page
            response = requests.get(random_item['Letterboxd URI'], headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                self.update_result_label(5)
                app.processEvents()
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.content, 'html.parser')

                details = soup.select("div.col-17")
                if details:
                    director = soup.select_one("a.contributor")
                    film_details = soup.select_one("div.review")


                    tagline = film_details.select_one("h4.tagline")
                    print("Tagline:", tagline)

                    if tagline:
                        tagline = tagline.text.strip() + "<br><br>"
                    else:
                        tagline = ""

                    description = film_details.select_one("div.truncate")

                # Get the movie poster URL from the IMDb page
                script_w_data = soup.select_one('script[type="application/ld+json"]')
                poster_image = json.loads(script_w_data.text.split(' */')[1].split('/* ]]>')[0])
                print(poster_image['image'])


                if poster_image:
                    poster_url = poster_image['image']
                    print("Poster URL", poster_url)

                    # Create a pixmap from the poster image URL
                    pixmap = QPixmap()
                    pixmap.loadFromData(requests.get(poster_url).content)

                    # Set the pixmap to the poster_label
                    self.poster_label.setPixmap(pixmap.scaled(self.poster_label.size(), Qt.KeepAspectRatio))

                    # Find the majority color of the poster image
                    # Convert the pixmap to a QImage
                    image = pixmap.toImage()

                    smooth_color_change(image)

                    # Create a star icon at the top left corner on the movie poster
                    star_icon = QIcon("star.svg")
                    star_icon_renderer = QSvgRenderer("star.svg")
                    self.star_icon_pixmap = QPixmap(20, 20)
                    self.star_icon_pixmap.fill(Qt.transparent)
                    self.star_icon_painter = QPainter(self.star_icon_pixmap)
                    star_icon_renderer.render(self.star_icon_painter)
                    self.star_icon_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                    self.star_icon_painter.fillRect(self.star_icon_pixmap.rect(), QColor(255, 255, 255))

                    self.star_icon_painter.end()

                    # Change the color of the star icon to yellow if it is in the favorites list
                    if self.check_favorites(random_item['Name']):
                        self.star_color = "yellow"
                        self.change_star_color(self.star_color)

                    else:
                        # If not in the favorites list, change the color of the star icon to white or black depending on the theme
                        if self.theme == "light":
                            self.star_color = "black"
                            self.change_star_color(self.star_color)

                        elif self.theme == "dark":
                            self.star_color = "white"
                            self.change_star_color(self.star_color)

                    self.star_icon_label = QLabel(self.poster_label)

                    self.star_icon_label.setPixmap(self.star_icon_pixmap)
                    self.star_icon_label.move(10, 10)

                    self.star_icon_label.show()

                    # When clicked, save the movie/series' title and URL to a CSV file name "favorites.csv" and change the color of the star icon to yellow
                    # When clicked again, remove the movie/series from the CSV file and change the color of the star icon to white or black depending on the theme
                    self.star_icon_label.mousePressEvent = lambda event: self.save_favorite(random_item['Name'], random_item['Letterboxd URI'])

                # Extract and print the desired columns
                self.result_label.setText(f"<a href=\"{random_item['Letterboxd URI']}\"><h1>{random_item['Name']}</h1></a><br>"
                                          f"<i>{tagline}</i>"
                                          f"<b>Year:</b> {random_item['Year']}<br>"
                                          f"<b>Director:</b> {director.text.strip()}<br>")

                if description:
                    self.description_label.setText(f"{description.text.strip()}")


    ## SHOW USER IF THEY WATCHED AND RATED THIS MOVIE/SERIES BEFORE
    def checkRatings(self, title, title_type):


        # Define the destination file path where you want to save the CSV file
        self.ratings_csv = 'ratings.csv'

        # Check if ratings.csv exists
        try:
            # Read the CSV file and store its data in a list of dictionaries
            ratings_csv_data = []
            with open(self.ratings_csv, mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    ratings_csv_data.append(row)

        except FileNotFoundError:
            return f"Ratings file not found."

        # Check if there's data in the CSV file
        if ratings_csv_data:
            # Iterate through the CSV data to find a match for the provided title
            for item in ratings_csv_data:
                if item["Original Title"] == title:
                    your_rating = item["Your Rating"]
                    date_rated = item["Date Rated"]
                    # Convert the date to a more readable format (day number, month name, year)
                    date_rated = datetime.strptime(date_rated, "%Y-%m-%d").strftime("%d %B %Y")

                    rating_result = f"\nYou have rated this {title_type} with a rating of <b>{your_rating}/10</b> on <b>{date_rated}</b>."
                    return rating_result # Exit the function once a match is found

            # If no match is found, print a message
            rating_result = f"\nYou have not rated this {title_type}."
            return rating_result

        else:
            rating_result = f"\nYou have not rated this {title_type}."
            return rating_result

    # Get more details about the movie/series
    def more_details(self):
        try:
            # Get the title URL from the result_label
            title_url = self.result_label.text().split("<a href=\"")[1].split("\"><h1>")[0]

            # Create a new window to display the details
            self.details_window = DetailsWindow(title_url)
            self.details_window.show()
        except IndexError:
            print("No title URL found.")

    # Save the movie/series' title and URL to a CSV file name "favorites.csv"
    def save_favorite(self, title, url):
        # Define the destination file path where you want to save the CSV file
        favorites_csv = 'favorites.csv'

        # Initialize a list to store the favorites data
        favorites_data = []

        # Check if the file exists
        if os.path.isfile(favorites_csv):
            # If the file exists, load its data
            with open(favorites_csv, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                # Skip the header row (if present)
                next(csv_reader, None)
                # Read the CSV data into a list of dictionaries
                for row in csv_reader:
                    if len(row) == 2:
                        csv_title, csv_url = row
                        favorites_data.append({'Title': csv_title, 'URL': csv_url})

        favorite = self.check_favorites(title)

        # Check if the movie/series is already in the favorites data
        if favorite:
            # If it is, remove the movie/series from the favorites data
            favorites_data.remove(favorite)

            # Write the updated data (including the new addition and removal) to "favorites.csv"
            with open(favorites_csv, 'w', encoding='utf-8') as file:
                # Write the header row
                file.write("Title,URL\n")
                # Write the updated data
                for data in favorites_data:
                    file.write(f"{data['Title']},{data['URL']}\n")

            # Change the color of the star icon to white/black depending on the theme
            if self.theme == "light" and self.star_color == "yellow":
                self.star_color = "black"
                self.change_star_color(self.star_color)
            elif self.theme == "dark" and self.star_color == "yellow":
                self.star_color = "white"
                self.change_star_color(self.star_color)

            return

        # Append the new movie/series' title and URL to the favorites data
        favorites_data.append({'Title': title, 'URL': url})

        # Write the updated data (including the new addition and removal) to "favorites.csv"
        with open(favorites_csv, 'w', encoding='utf-8') as file:
            # Write the header row
            file.write("Title,URL\n")
            # Write the updated data
            for favorite in favorites_data:
                file.write(f"{favorite['Title']},{favorite['URL']}\n")

        # Change the color of the star icon to yellow
        self.star_color = "yellow"
        self.change_star_color(self.star_color)

    # Check if the movie/series is already in the favorites.csv file
    def check_favorites(self, title):
        # Define the destination file path where you want to save the CSV file
        self.favorites_csv = 'favorites.csv'

        # Check if the file exists
        if not os.path.isfile(self.favorites_csv):
            print("'favorites.csv' does not exist.")
            return False

        # Check if the movie/series is already in the favorites.csv file
        with open(self.favorites_csv, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if row["Title"] == title:
                    return row

        return False

    def show_filters(self):
        if self.filters_container.isHidden():
            self.filters_container.show()
        else:
            self.filters_container.hide()

    def apply_filters(self):
        # Retrieve selected minimum rating and genre
        self.min_rating = self.rating_slider.value() / 2.0
        self.selected_genre = self.genre_combo.currentText()
        self.max_runtime = self.runtime_slider.value()

        if self.title_type_combo.currentText() != "All Types":
            match(self.title_type_combo.currentText()):
                case "Movies":
                    self.selected_type = "Movie"
                case "TV Series":
                    self.selected_type = "TV Series"
                case "TV Episodes":
                    self.selected_type = "TV Episode"
                case "TV Mini-Series":
                    self.selected_type = "TV Mini Series"
                case "Shorts":
                    self.selected_type = "Short"
                case "TV Movies":
                    self.selected_type = "TV Movie"
                case "TV Specials":
                    self.selected_type = "TV Special"
                case "Videos":
                    self.selected_type = "Video"
                case "Video Games":
                    self.selected_type = "Video Game"
                case "Podcasts":
                    self.selected_type = "Podcast Series"
                case "Podcast Episodes":
                    self.selected_type = "Podcast Episode"
                case "TV Shorts":
                    self.selected_type = "TV Short"
                case "Documentaries":
                    self.selected_type = "Documentary"
                case "Music Videos":
                    self.selected_type = "Music Video"

        # Display the applied filters
        self.result_label.setText(f"<h3>Applied Filters:</h3><br>"
                                  f"Type: {self.title_type_combo.currentText()}<br>"
                                  f"Minimum Rating: {self.min_rating}<br>"
                                  f"Genre: {self.selected_genre}<br>"
                                  f"Maximum Runtime: {self.max_runtime}<br>")

        # Hide the filters container after applying filters
        self.filters_container.hide()

    # Update the rating label when the slider value changes
    def update_rating_label(self):
        if self.rating_slider.value() == 0:
            self.rating_label.setText(f"Minimum Rating: No Limit")
        else:
            self.rating_label.setText(f"Minimum Rating: {self.rating_slider.value() / 2.0}")

    # Update the runtime label when the slider value changes
    def update_runtime_label(self):
        if self.runtime_slider.value() == 0:
            self.runtime_label.setText(f"Maximum Runtime: No Limit")
        else:
            self.runtime_label.setText(f"Maximum Runtime: {self.runtime_slider.value()}")

    # Update the result label to inform the user that the program is working
    def update_result_label(self, flag):
        match(flag):
            case 0:
                self.result_label.setText("Our chefs are crafting a watchlist recommendation for you...<br><br>")
                return
            case 1:
                self.result_label.setText("We're preparing a delightful recommendation from your list...<br><br>")
                return
            case 2:
                self.result_label.setText("A custom recommendation is on its way, tailored just for you...<br><br>")
                return
            case 3:
                self.result_label.setText("Our chefs are adding filters to enhance your selection's flavor...<br><br>")
                return
            case 4:
                self.result_label.setText("We're handpicking a special title for you...<br><br>")
                return
            case 5:
                self.result_label.setText("Your perfect dish is ready to be served! Enjoy your meal!<br><br>")
                return
            case 6:
                self.result_label.setText("Creating a culinary masterpiece takes time. Please be patient!<br><br>")
                return
            case 7:
                self.result_label.setText("We're curating a special menu just for you...<br><br>")
                return
            case _:
                self.result_label.setText(flag)

    # Change the star icon color
    def change_star_color(self, color):
        star_painter = QPainter(self.star_icon_pixmap)
        if color == "yellow":
            star_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            star_painter.fillRect(self.star_icon_pixmap.rect(), QColor(255, 212, 59))
            star_painter.end()
            self.star_color = "yellow"

        elif color == "white":
            star_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            star_painter.fillRect(self.star_icon_pixmap.rect(), QColor(255, 255, 255))
            star_painter.end()
            self.star_color = "white"

        elif color == "black":
            star_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            star_painter.fillRect(self.star_icon_pixmap.rect(), QColor(0, 0, 0))
            star_painter.end()
            self.star_color = "black"

        # Update the star icon label with the new pixmap
        self.star_icon_label.setPixmap(self.star_icon_pixmap)

    # Change the theme to light
    def light_theme(self):
        app.setPalette(light_palette)

        # Delete existing scroll area widgets
        if hasattr(self, 'result_scroll_area'):
            self.result_scroll_area.deleteLater()
        if hasattr(self, 'description_scroll_area'):
            self.description_scroll_area.deleteLater()

        # Create scroll areas for the result label and description label
        self.result_scroll_area = QtWidgets.QScrollArea()
        self.result_scroll_area.setWidgetResizable(True)
        self.result_scroll_area.setFixedHeight(450)
        self.result_scroll_area.setWidget(self.logo_poster_widget)

        self.poster_layout.addWidget(self.result_scroll_area)

        # Add the description label to a scroll area
        self.description_scroll_area = QtWidgets.QScrollArea()
        self.description_scroll_area.setWidgetResizable(True)
        self.description_scroll_area.setFixedHeight(250)
        self.description_scroll_area.setWidget(self.description_label)

        self.main_layout.addWidget(self.description_scroll_area)

        # Move container widget and find book button to the bottom
        self.main_layout.removeWidget(self.container)
        self.main_layout.removeWidget(self.find_movie_button)
        self.main_layout.addWidget(self.container)
        self.main_layout.addWidget(self.find_movie_button)

        self.theme = "light"

        if self.star_color != "yellow" or self.star_color == "white":
            self.star_color = "black"
            self.change_star_color(self.star_color)

    # Change the theme to dark
    def dark_theme(self):
        app.setPalette(dark_palette)

        # Delete existing scroll area widgets
        if hasattr(self, 'result_scroll_area'):
            self.result_scroll_area.deleteLater()
        if hasattr(self, 'description_scroll_area'):
            self.description_scroll_area.deleteLater()

        # Create scroll areas for the result label and description label
        self.result_scroll_area = QtWidgets.QScrollArea()
        self.result_scroll_area.setWidgetResizable(True)
        self.result_scroll_area.setFixedHeight(450)
        self.result_scroll_area.setWidget(self.logo_poster_widget)

        self.poster_layout.addWidget(self.result_scroll_area)

        # Add the description label to a scroll area
        self.description_scroll_area = QtWidgets.QScrollArea()
        self.description_scroll_area.setWidgetResizable(True)
        self.description_scroll_area.setFixedHeight(250)
        self.description_scroll_area.setWidget(self.description_label)

        self.main_layout.addWidget(self.description_scroll_area)

        # Move container widget and find book button to the bottom
        self.main_layout.removeWidget(self.container)
        self.main_layout.removeWidget(self.find_movie_button)
        self.main_layout.addWidget(self.container)
        self.main_layout.addWidget(self.find_movie_button)

        self.theme = "dark"

        if self.star_color != "yellow" or self.star_color == "black":
            self.star_color = "white"
            self.change_star_color(self.star_color)

    # Show the statistics dialog
    def statistics(self):
        # Check if ratings.csv exists
        self.ratings_csv = "ratings.csv"

        try:
            # Read the CSV file and store its data in a list of dictionaries
            ratings_csv_data = []
            with open(self.ratings_csv, mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    ratings_csv_data.append(row)

        except FileNotFoundError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Statistics")
            msg.setText("You have not rated any movies/series yet.")
            msg.exec_()
            return

        # Change the cursor to a wait cursor
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Create and display the statistics dialog
        statistics_window = StatisticsWindow(ratings_csv_data)
        statistics_window.exec_()

        # Change the cursor back to the default cursor
        QApplication.restoreOverrideCursor()

    # Show the help dialog
    def help(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Help")
        msg.setText(
            "This program allows you to randomly select a movie or TV series from your IMDb watchlist or any of your IMDb lists.<br><br>"
            "For more information on how to use this program, please visit:<br><br>"
            "<a href='https://github.com/isonerinan/Python-Projects/tree/main/IMDB%20Recommender'>"
            "https://github.com/isonerinan/Python-Projects/tree/main/IMDB%20Recommender</a>")

        msg.exec_()

    # Show the about dialog
    def about(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About")
        msg.setText("<h1>Watchable: IMDB Recommender</h1>"
                    "<h3>Version 5.0</h3>"
                    "<b>Created by:</b> İbrahim Soner İNAN<br><br>"
                    "<a href='https://github.com/isonerinan'>GitHub</a><br><br>"
                    "<a href='https://www.linkedin.com/in/isonerinan'>LinkedIn</a><br><br>"
                    "<a href='https://www.instagram.com/isonerinan'>Instagram</a><br><br>"
                    "<a href='https://www.twitter.com/isonerinan'>Twitter</a>")
        msg.exec_()

    # Show the years summary review window
    def year_review(self):
        # Create and display the statistics dialog
        year_review_window = YearReviewWindow()
        year_review_window.exec_()

        # Change the cursor back to the default cursor
        QApplication.restoreOverrideCursor()

    def insights(self):
        # Create and display the insights dialog
        insights_window = InsightsWindow()
        insights_window.exec_()

        # Change the cursor back to the default cursor
        QApplication.restoreOverrideCursor()

    # Show the now watching dialog
    def now_watching(self):
        # Create and display the now watching dialog
        now_watching_window = NowWatchingWindow()
        now_watching_window.exec_()

        # Change the cursor back to the default cursor
        QApplication.restoreOverrideCursor()

    # Show the favorited movies/series from the favorites.csv file
    def favorites(self):
        favorites_csv = 'favorites.csv'
        favorites_data = []

        # Check if the file exists
        if not os.path.isfile(favorites_csv):
            # If the file doesn't exist, show a message that there are no favorites.
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Favorites")
            msg.setText("You have no favorited movies/series.")
            msg.exec_()
            return

        # Read the favorites from the CSV file
        with open(favorites_csv, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            # Skip the header row
            next(csv_reader, None)
            for row in csv_reader:
                if len(row) == 2:
                    title, url = row
                    favorites_data.append((title, url))

        # Create and display the favorites dialog
        favorites_dialog = MyFavoritesDialog(favorites_data)
        favorites_dialog.exec_()

    # def update_letterboxd_watchlist(self):




if __name__ == '__main__':
    # Create the application
    app = QApplication([])

    app.setStyle("Fusion")
    app.setFont(QFont("Roboto"))

    # Set the dark theme
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)

    # Set the light theme
    light_palette = QPalette()
    light_palette.setColor(QPalette.Window, QColor(255, 255, 255))
    light_palette.setColor(QPalette.WindowText, Qt.black)
    light_palette.setColor(QPalette.Base, QColor(240, 240, 240))
    light_palette.setColor(QPalette.AlternateBase, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ToolTipBase, Qt.black)
    light_palette.setColor(QPalette.ToolTipText, Qt.black)
    light_palette.setColor(QPalette.Text, Qt.black)
    light_palette.setColor(QPalette.Button, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ButtonText, Qt.black)
    light_palette.setColor(QPalette.BrightText, Qt.red)
    light_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    light_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    light_palette.setColor(QPalette.HighlightedText, Qt.white)

    # Initialize in dark mode
    app.setPalette(dark_palette)

    window = ModernApp()
    window.show()
    # Check the last time the user updated their lists
    check_last_update()
    sys.exit(app.exec_())

