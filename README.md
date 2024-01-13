# YouTubeViewScraper

## Description
This repository is an out-of-the-box demonstration of collecting publicly accessible data from sources containing dynamically loaded content, such as YouTube. It aims to display that Selenium provides viable solutions for large-scale web scraping on JavaScript-heavy websites.

For use with non-norwegian setups, adequate adjusting must be made:
1.  The formatting of the str_to_n_views() function is written for browsers displaying view count in Norwegian (e.g., sett 3,5 mill. ganger) and will hence require re-writing if this is not accommodated for.

To run this demo, follow the installation guide and run the main.py file.

## Installation
1.  Clone this repo (!git clone https://github.com/davidharket/YouTubeViewScraper)
2.  Install required packages (!pip install -r requirements.txt)
3.  Change the value of the profile_path variable on line 14.
4.  Install a Chrome Web Driver if not already acquired (download is available here: https://chromedriver.storage.googleapis.com/index.html?path=114.0.5735.90/).
5.  Run main.py

## Usage
This is just a demonstration, but in running the script, a database containing the date of data collection, title of the video investigated, view count associated with the corresponding video, and duration time (in seconds) associated with the corresponding video for all elements scraped will be produced.

Here is a screenshot of the collected data displayed in the DB Browser (SQLite) desktop application
![Screenshot of result](/images/screenshot.png)

