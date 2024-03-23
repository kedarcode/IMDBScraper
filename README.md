# IMDB Scraper

## Overview

IMDB Scraper is a Python script designed to scrape movie data from IMDb based on user-defined queries. This tool utilizes the tkinter library to provide a user-friendly graphical interface for ease of use. Users can specify a search query, limit the number of records to scrape, control the number of threads for improved performance, and manage browser visibility. Additionally, the script includes a text area to display logs and errors during the scraping process.

## Installation

To use IMDB Scraper, follow these steps:

1. Ensure you have Python installed on your system.
2. Install the required dependencies by running:

pip install -r requirements.txt


![UI](https://github.com/kedarcode/IMDBScraper/assets/98396591/9bc318b7-b079-44f0-8d8b-c34957b7d6f9)


## Usage

1. Run the script.
2. Input your search query in the "Query" field. This should be the title of a movie or TV show.
3. Specify the limit for the number of records to scrape in the "Limit" field.
4. Adjust the number of threads in the "Thread" field. Increasing the number of threads can improve scraping speed but may consume more system resources.
5. Check the "Visible" checkbox to make the browser window visible during scraping. Unchecking it will run the scraper in headless mode.
6. View logs and errors in the text area provided.

## Note

- Ensure that the search query is precise and corresponds to a single movie or TV show title.
- Use caution when increasing the number of threads as it may impact system performance.
- The visibility of the browser window can affect the scraping process. Adjust as needed.
- Logs and errors will be displayed in real-time in the designated text area.

## Example

Below is an example of how to use IMDB Scraper:

1. Input "The Dark Knight" in the "Query" field.
2. Set the "Limit" to 10 to scrape information for the first 10 results.
3. Adjust the "Thread" to 4 for faster scraping.
4. Check the "Visible" checkbox to monitor the scraping process.
5. Click on the "Scrape" button to initiate the scraping process.

## Author

IMDB Scraper was developed by Kedar.

