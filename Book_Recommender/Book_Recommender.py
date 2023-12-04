# PyQT application to recommend books based on user input
import json
import math
# FEATURES:
# - "Read Later" QLineEdit to add books to a list of books to read later
# - "Search" QLineEdit to search for books
# - "Add to List" QPushButton to add books to a custom user list
# - "Delete List" QPushButton to delete a custom user list
# - "Recommend" QPushButton to recommend random books from "Read Later" or any other selected user list
# - "Read History" QPushButton to view books that have been read
# - "Delete" QPushButton to delete books from any selected user list
# - "Star Rating" QComboBox to rate books out of 10
# - "My Lists" QComboBox to select a user list to view the books in that list
# - Genre, Type, Maximum Page, and Author filters to filter books by
# - "Clear Filters" QPushButton to clear all filters
# - Goodreads API to get book information

import os
import random

import sys
import requests
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, \
    QMainWindow, QAction, QMenu, QSlider, QMessageBox
from bs4 import BeautifulSoup
import re

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47'}


class BookRecommendationApp(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.theme = "dark"
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Readable: Book Recommender")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.resize(800, 500)

        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # Create a top-level layout for the main content
        content_layout = QVBoxLayout()
        self.main_layout.addLayout(content_layout)

        # Create a menu toolbar
        menu_bar = self.menuBar()
        options_menu = menu_bar.addMenu("Options")

        help_action = QAction("Help", self)
        help_action.triggered.connect(self.help)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)

        menu_bar.addAction(help_action)
        menu_bar.addAction(about_action)

        # Create a "User Preferences" action in the "Options" menu
        user_preferences_action = QAction("User Preferences", self)
        user_preferences_action.triggered.connect(self.create_preferences_file)
        options_menu.addAction(user_preferences_action)

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
        self.to_read_link = ""

        # Create a combo box to select a list
        self.list_combo = QComboBox()
        self.list_names = []
        self.list_links = []

        # Check if the preferences file exists or not empty
        if not self.check_preferences_file() or os.stat(self.preferences_file).st_size == 0:
            self.create_preferences_file()

        # Check the preferences file and get the necessary links
        self.user_lists_link = self.checkPreferences()

        if not (self.user_lists_link == "" and self.to_read_link == ""):
            # Send an HTTP GET request to fetch the Goodreads user lists page
            response = requests.get(self.user_lists_link, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                list_items = soup.find_all('div', class_='stacked', id='paginatedShelfList')

                # Extract the list names and links
                for item in list_items:
                    lists = item.find_all('a', class_='actionLinkLite')
                    for list in lists:
                        self.list_names.append(list.text.strip())
                        self.list_links.append(list['href'])

                # Add the list names to the combo box
                self.list_combo.addItems(self.list_names)

        # Center every item in the combo box
        self.list_combo.setEditable(True)
        self.list_combo.lineEdit().setAlignment(Qt.AlignCenter)

        # Remove non-printable characters from list names
        self.list_names = [''.join(char for char in list_name if char.isprintable()) for list_name in self.list_names]
        self.list_names = [list_name.strip() for list_name in self.list_names]

        print(self.list_names)

        # If there is a "Want to Read" list, select it by default
        want_to_read_indices = [i for i, list_name in enumerate(self.list_names) if "Want to Read" in list_name]
        if want_to_read_indices:
            # If there are multiple occurrences, choose the first one.
            index = want_to_read_indices[0]
            print("Found at index:", index)
            self.list_combo.setCurrentIndex(index)
            print("True")
        else:
            print("String 'Want to Read' not found in any list.")

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

        # Create a QSlider for selecting minimum Goodreads rating
        self.rating_slider = QSlider(Qt.Horizontal)
        self.rating_slider.setMinimum(0)
        self.rating_slider.setMaximum(10)  # To allow 0.5 increments, use 10 instead of 5
        self.rating_slider.setValue(0)  # Default to 0.0
        self.rating_slider.setTickInterval(1)
        self.rating_slider.setTickPosition(QSlider.TicksAbove)

        # Create a QLabel to display the selected rating
        self.rating_label = QLabel("Minimum Rating: No Limit")

        # Update the label when the slider value changes
        self.rating_slider.valueChanged.connect(self.update_rating_label)

        # Create a QComboBox for selecting genres
        self.genre_combo = QComboBox()
        self.genre_combo.addItem("All Genres")  # Add a default option
        # Add genre options to the combo box
        self.genre_combo.addItems(["Art", "Biography", "Business", "Chick-lit",
                                   "Children's", "Christian", "Classics", "Comics",
                                   "Contemporary", "Cookbooks", "Crime", "Ebooks",
                                   "Fantasy", "Fiction", "Gay and Lesbian", "Graphic novels",
                                   "Historical Fiction", "History", "Horror", "Humor and Comedy",
                                   "Manga", "Memoir", "Music", "Mystery",
                                   "Non-fiction", "Paranormal", "Philosophy", "Poetry", "Psychology",
                                   "Religion", "Romance", "Science", "Science fiction", "Self help",
                                   "Suspense", "Spirituality", "Sports", "Thriller", "Travel", "Young-adult"])

        # Create a "Apply Filters" button
        apply_filters_button = QPushButton("Apply Filters")
        apply_filters_button.clicked.connect(self.apply_filters)

        # Create a layout for filter widgets
        filter_layout = QVBoxLayout()
        filter_layout.addWidget(self.genre_combo)
        filter_layout.addWidget(self.rating_label)
        filter_layout.addWidget(self.rating_slider)
        filter_layout.addWidget(apply_filters_button)
        self.filters_container.setLayout(filter_layout)

        # Create a new QWidget for displaying the movie/series poster and details, horizontally
        self.poster_widget = QWidget()
        self.poster_layout = QHBoxLayout()
        self.poster_widget.setLayout(self.poster_layout)
        self.main_layout.addWidget(self.poster_widget)

        self.poster_label = QLabel()
        self.poster_label.hide()
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_layout.addWidget(self.poster_label)

        # Create a new QLabel for displaying the movie/series title and details
        self.result_label = QLabel("Welcome to Readable!<br>Your recommendation will appear here.")
        self.result_label.setWordWrap(True)
        # Enable rich text
        self.result_label.setOpenExternalLinks(True)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.poster_layout.addWidget(self.result_label)

        # Create a new QLabel for displaying the movie/series description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.hide()
        self.main_layout.addWidget(self.description_label)

        # Create scroll areas for the result label and description label
        self.result_scroll_area = QtWidgets.QScrollArea()
        self.result_scroll_area.setWidgetResizable(True)
        self.result_scroll_area.setFixedHeight(450)
        self.result_scroll_area.hide()

        self.poster_layout.addWidget(self.result_scroll_area)

        # Add the description label to a scroll area
        self.description_scroll_area = QtWidgets.QScrollArea()
        self.description_scroll_area.setWidgetResizable(True)
        self.description_scroll_area.setFixedHeight(250)
        self.description_scroll_area.hide()

        self.main_layout.addWidget(self.description_scroll_area)

        # Create a QLineEdit for custom Goodreads list input
        self.custom_list = QLineEdit()
        self.custom_list.setPlaceholderText("Want to explore a custom list? Paste it here!")
        self.custom_list.setAlignment(Qt.AlignCenter)

        # Create a QPushButton
        search_button = QPushButton("Search")

        # Connect the button's clicked signal to the slot
        search_button.clicked.connect(self.apply_filters)
        search_button.clicked.connect(self.search_button_click)


        # Add both the QLineEdit and the button to a container widget
        self.container = QWidget()
        self.container_layout = QHBoxLayout()
        self.container_layout.addWidget(self.custom_list)
        self.container_layout.addWidget(search_button)
        self.container.setLayout(self.container_layout)

        # Add the container to the main layout
        self.main_layout.addWidget(self.container)

        self.setLayout(self.main_layout)

        self.find_book_button = QPushButton("Find Something to Read!")
        self.find_book_button.clicked.connect(self.apply_filters)
        self.find_book_button.clicked.connect(self.find_random_book)
        self.main_layout.addWidget(self.find_book_button)

    def check_preferences_file(self):
        return os.path.isfile(self.preferences_file)

    # Create a new preferences file in a form of dictionary
    def create_preferences_file(self):
        # Ask the user for their Goodreads user lists link
        user_lists_link, ok = QtWidgets.QInputDialog.getText(self, "User Lists Link", "Enter your Goodreads user lists link:")
        if ok:
            # Write the links to the preferences file
            with open(self.preferences_file, "w") as file:
                file.write(f"\"User Lists Link\": \"{user_lists_link}\"\n")

    def find_random_book(self):
        # Change the cursor to indicate that the program is working
        QApplication.setOverrideCursor(Qt.WaitCursor)
        selected_index = self.list_combo.currentIndex()

        # Get the selected list's name
        selected_list_name = self.list_names[selected_index]

        # Get the selected export link from the list of links
        # (example export link: https://www.goodreads.com/review_porter/export/171429787/goodreads_export.csv)
        # (example list link: https://www.goodreads.com/review/list/171429787?shelf=read-later)
        selected_list_link = "https://www.goodreads.com" + self.list_links[selected_index] + "&per_page=infinite"

        print(selected_list_link)

        # Send an HTTP GET request to fetch the Goodreads export link and download the CSV file
        response = requests.get(selected_list_link, headers=headers)

        # Check if the response is successful
        if response.status_code == 200:
            # Get the book details
            soup = BeautifulSoup(response.content, 'html.parser')
            book_details = soup.find_all('tr', class_='bookalike review')

            # If not empty, select a random book from the list
            if book_details:
                random_book = random.choice(book_details)

                # Get the book title
                book_title = random_book.find('td', class_='field title')
                book_title = book_title.find('a').text.strip()
                print("Title:", book_title)

                # Get the book author
                book_author = random_book.find('td', class_='field author')
                book_author = book_author.find('a').text.strip()

                # Author names are formatted as "Surname, Name", so we need to reverse them
                book_author = book_author.split(", ")
                book_author = book_author[1] + " " + book_author[0]
                print("Author:", book_author)

                # Get the book rating
                book_rating = random_book.find('td', class_='field avg_rating')
                book_rating = book_rating.find('div', class_='value').text.strip()
                print("Rating:", book_rating)

                # Get the book link
                book_link = "https://www.goodreads.com" + random_book.find('td', class_='field title').find('a')['href']
                print("Link:", book_link)

                # Get the book cover image link
                # List covers end with "._SY75_.jpg" or "._SX50_.jpg" etc.
                # Book covers are 283x475 pixels and end with ".jpg"
                book_cover_link = random_book.find('td', class_='field cover').find('img')['src']

                # Regular expression pattern
                pattern = re.compile(r'\._\w+_\.jpg')

                # Replace the pattern with ".jpg" in each cover link
                book_cover_link = re.sub(pattern, '.jpg', book_cover_link)
                print("New Cover Link:", book_cover_link)

                # Create a pixmap from the poster image URL
                pixmap = QPixmap()
                pixmap.loadFromData(requests.get(book_cover_link).content)

                # Scale the pixmap so it wouldn't be too big or too small
                pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)

                self.poster_label.setPixmap(pixmap)

                # Find the majority color of the poster image
                # Convert the pixmap to a QImage
                image = pixmap.toImage()

                # Get the image dimensions
                width = image.width()
                height = image.height()

                # Create a dictionary to store the colors and their counts
                color_counts = {}

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
                second_dominant_color_tuple = max(color_counts, key=lambda x: color_counts[x] if x != dominant_color_tuple else 0)

                # Convert the tuples back to a QColor object
                dominant_color = QColor(*dominant_color_tuple)
                second_dominant_color = QColor(*second_dominant_color_tuple)

                print("Dominant Color:", dominant_color.name())
                print("Dominant Color RGB:", dominant_color.red(), dominant_color.green(), dominant_color.blue())
                print("Second Dominant Color:", second_dominant_color.name())
                print("Second Dominant Color RGB:", second_dominant_color.red(), second_dominant_color.green(), second_dominant_color.blue())

                # Find the average color
                average_color_tuple = (0, 0, 0, 0)
                for color_tuple in color_counts:
                    average_color_tuple = tuple(map(sum, zip(average_color_tuple, color_tuple)))
                average_color_tuple = tuple([int(color / len(color_counts)) for color in average_color_tuple])
                average_color = QColor(*average_color_tuple)
                print("Average Color:", average_color.name())
                print("Average Color RGB:", average_color.red(), average_color.green(), average_color.blue())

                # Check if we are in dark mode
                if self.theme == "dark":
                    new_window_color = QColor(int(25 * 0.8 + average_color.red() * 0.2),
                                              int(25 * 0.8 + average_color.green() * 0.2),
                                              int(25 * 0.8 + average_color.blue() * 0.2))
                    print("New Window Color:", new_window_color.name())
                    dark_palette.setColor(QPalette.Window, new_window_color)

                    # Check if the dominant color is too dark
                    if dominant_color.lightness() < QColor(100, 100, 100).lightness() and second_dominant_color.lightness() > QColor(100, 100, 100).lightness():
                        # Use the second dominant color instead
                        dominant_color = second_dominant_color

                    elif dominant_color.lightness() < QColor(100, 100, 100).lightness() and second_dominant_color.lightness() < QColor(100, 100, 100).lightness():
                        # Lighten the dominant color
                        dominant_color = dominant_color.lighter(150)

                    dark_palette.setColor(QPalette.Link, dominant_color)
                    self.dark_theme()

                elif self.theme == "light":
                    new_window_color = QColor(int(255 * 0.8 + average_color.red() * 0.2),
                                              int(255 * 0.8 + average_color.green() * 0.2),
                                              int(255 * 0.8 + average_color.blue() * 0.2))
                    print("New Window Color:", new_window_color.name())
                    light_palette.setColor(QPalette.Window, new_window_color)

                    # Check if the dominant color is too light
                    if dominant_color.lightness() > QColor(200, 200, 200).lightness() and second_dominant_color.lightness() < QColor(200, 200, 200).lightness():
                        # Use the second dominant color instead
                        dominant_color = second_dominant_color

                    elif dominant_color.lightness() > QColor(200, 200, 200).lightness() and second_dominant_color.lightness() > QColor(200, 200, 200).lightness():
                        # Darken the dominant color
                        dominant_color = dominant_color.darker(150)

                    light_palette.setColor(QPalette.Link, dominant_color)
                    self.light_theme()


                # Get the book page count
                book_page_count = random_book.find('td', class_='field num_pages')
                book_page_count = book_page_count.find('nobr').text.strip()
                book_page_count = book_page_count.replace("pp", "")
                print("Page Count:", book_page_count)

                # Get more details about the book
                # Set up Chrome options for headless mode
                chrome_options = Options()
                chrome_options.add_argument('--headless')  # Run Chrome in headless mode

                # Specify the path to ChromeDriver
                chromedriver_path = 'chromedriver.exe'

                # Create ChromeOptions and set the executable path
                chrome_options.add_argument(f'--executable_path={chromedriver_path}')

                # Create a WebDriver instance
                driver = webdriver.Chrome(options=chrome_options)

                # Visit the book link
                driver.get(book_link)

                # Wait for the page to load
                wait = WebDriverWait(driver, 5)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'BookPageMetadataSection__genres')))
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'BookPageMetadataSection__description')))
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'BookDetails')))
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'FeaturedDetails')))
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'TruncatedContent')))

                # turn the page into soup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                print(soup.prettify())

                # Extract content of the script tag
                script_content = soup.select_one('script[type="application/ld+json"]').string

                # Convert the content to a dictionary
                script_content = json.loads(script_content)

                # Extract the book language
                book_language = script_content.get('inLanguage')

                # Extract the book genres
                genre_info = re.findall(r'{"__typename":"Genre","name":"(.*?)","webUrl":"(.*?)"}', str(soup))

                genre_names = [genre[0] for genre in genre_info]
                genre_urls = [genre[1] for genre in genre_info]

                # Join the genres into a string, separated by commas, and with <a> tags
                book_genres = ", ".join([f"<a href='{genre_url}'>{genre}</a>" for genre, genre_url in zip(genre_names, genre_urls)])

                # Extract the book ISBN
                isbn = script_content.get('isbn')

                # Extract the book author URL
                author_url = script_content.get('author', [{}])[0].get('url')

                # Extract the book type
                book_type = script_content.get('bookFormat')

                # Extract the book awards
                awards = script_content.get('awards')

                # Extract the book characters
                character_info = re.findall(r'\{"__typename":"Character","name":"(.*?)","webUrl":"(.*?)"\}', str(soup))

                character_names = [character[0] for character in character_info]
                character_urls = [character[1] for character in character_info]

                # Join the characters into a string, separated by commas, and with <a> tags
                characters = ", ".join([f"<a href='{character_url}'>{character}</a>" for character, character_url in zip(character_names, character_urls)])

                # Extract the book places
                place_info = re.findall(r'\{"__typename":"Places","name":(.*?),"countryName":(.*?),"webUrl":(.*?),"year":(.*?)\}', str(soup))

                place_names = [place[0].strip("\"") for place in place_info]
                place_countries = [place[1].strip("\"") for place in place_info]
                place_urls = [place[2].strip("\"") for place in place_info]
                place_years = [place[3].strip("\"") for place in place_info]

                # Join the places into a string, separated by commas, and with <a> tags
                places = ", ".join([f"<a href='{place_url}'>{place}</a> ({place_year})" for place, place_url, place_year in zip(place_names, place_urls, place_years)])

                # Print extracted values
                print(f'Language: {book_language}')
                print(f'ISBN: {isbn}')
                print(f'Author URL: {author_url}')
                print(f'Book Type: {book_type}')
                print(f'Awards: {awards}')
                print(f'Characters: {characters}')
                print(f'Places: {places}')

                # Get book details
                try:
                    book_details_element = driver.find_element(By.CLASS_NAME, 'BookDetails')
                    # Get the book publish date
                    try:
                        publish_date_element = book_details_element.find_element(By.CSS_SELECTOR,
                                                                                     'p[data-testid="publicationInfo"]')
                        book_publish_date = publish_date_element.text.strip().replace("First published", "")

                    except NoSuchElementException:
                        book_publish_date = None

                except NoSuchElementException:
                    print("Book details not found.")

                # Get the book description
                try:
                    description_element = driver.find_element(By.CLASS_NAME, 'BookPageMetadataSection__description')
                    description_container = description_element.find_element(By.CLASS_NAME, 'Formatted')
                    book_description = description_container.text.strip()

                except NoSuchElementException:
                    book_description = None

                # Close the browser window
                driver.quit()

                # Update the result label
                self.update_result_label(f"<h3><a href='{book_link}'>{book_title}</a></h3><br>"
                                         f"<b>Author: </b><a href='{author_url}'>{book_author}</a><br>"
                                         f"<b>Average Rating: </b>{book_rating}/5<br>"
                                         f"<b>Book Format: </b>{book_page_count}, {book_type}<br><br>"
                                         f"<b>Genres: </b>{book_genres}<br>"
                                         f"<b>Publish Date: </b>{book_publish_date}<br>"
                                         f"<b>Edition Language: </b>{book_language}<br><br>"
                                         f"<b>Literary Awards: </b>{awards}<br><br>"
                                         f"<b>Characters: </b>{characters}<br>"
                                         f"<b>Places: </b>{places}<br><br>")


                self.result_label.setAlignment(Qt.AlignVCenter)

                # Update the description label
                self.description_label.setText(f"{book_description}")

                # Check if result label is too long
                if len(self.result_label.text()) > 140:
                    # Add result label to the scroll area
                    self.result_scroll_area.setWidget(self.result_label)
                    self.result_scroll_area.show()

                # Check if the description label is too long
                if len(book_description) > 140:
                    # Add description label to the scroll area
                    self.description_scroll_area.setWidget(self.description_label)
                    self.description_scroll_area.show()

                # Add padding to the result label and description label
                self.result_label.setStyleSheet("padding: 10px")
                self.description_label.setStyleSheet("padding: 10px")




        # Change the cursor back to normal
        self.poster_label.show()
        self.result_label.setAlignment(Qt.AlignVCenter)
        self.description_label.show()
        QApplication.restoreOverrideCursor()

    # Check the preferences file for the user's IMDb user page link and watchlist export link
    def checkPreferences(self):
        with open(self.preferences_file, "r") as file:
            preferences = file.read()
            preferences = preferences.split("\n")

            user_lists_link = preferences[0].split(": ")[1].strip("\"")

            return user_lists_link


    # Search button logic for custom list input
    def search_button_click(self):
        self.update_result_label(2)
        app.processEvents()

        # Get the text from the QLineEdit
        list_link = self.custom_list.text()

        # Call the list_random function with the input


    def show_filters(self):
        if self.filters_container.isHidden():
            self.filters_container.show()
        else:
            self.filters_container.hide()

    def apply_filters(self):
        # Retrieve selected minimum rating and genre
        self.min_rating = self.rating_slider.value() / 2.0
        self.selected_genre = self.genre_combo.currentText()

        # Display the applied filters
        self.result_label.setText(f"<h3>Applied Filters:</h3><br>"
                                  f"Minimum Rating: {self.min_rating}<br>"
                                  f"Genre: {self.selected_genre}<br>")

        # Hide the filters container after applying filters
        self.filters_container.hide()

    # Update the rating label when the slider value changes
    def update_rating_label(self):
        if self.rating_slider.value() == 0:
            self.rating_label.setText(f"Minimum Rating: No Limit")
        else:
            self.rating_label.setText(f"Minimum Rating: {self.rating_slider.value() / 2.0}")

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

    # Change the theme to light
    def light_theme(self):
        app.setPalette(light_palette)
        self.theme = "light"

    # Change the theme to dark
    def dark_theme(self):
        app.setPalette(dark_palette)
        self.theme == "dark"

    # Show the help dialog
    def help(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Help")
        msg.setText(
            "This program allows you to randomly select a book from your Goodreads Read Later list or any other custom list.<br><br>"
            "For more information on how to use this program, please visit:<br><br>"
            "BOOK RECOMMENDER LINK HERE")

        msg.exec_()

    # Show the about dialog
    def about(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About")
        msg.setText("<h1>Readable: Book Recommender</h1>"
                    "<h3>Version 1.5</h3>"
                    "<b>Created by:</b> İbrahim Soner İNAN<br><br>"
                    "<a href='https://github.com/isonerinan'>GitHub</a><br><br>"
                    "<a href='https://www.linkedin.com/in/isonerinan'>LinkedIn</a><br><br>"
                    "<a href='https://www.instagram.com/isonerinan'>Instagram</a><br><br>"
                    "<a href='https://www.twitter.com/isonerinan'>Twitter</a>")
        msg.exec_()



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

    window = BookRecommendationApp()
    window.show()
    sys.exit(app.exec_())
