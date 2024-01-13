import re
import time
import sqlite3
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException



print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
profile_path = "path/to/your/chrome/profile" # Add your chrome profile path here. If not, YouTube will not provide any content.



#Connect to database
conn = sqlite3.connect('youtube.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS youtube_views (id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE, title TEXT, views INTEGER, duration INTEGER)")


#Add data to database
def add_to_db(list_of_titles, list_of_views, list_of_durations):
    """
    Add the scraped YouTube video data to the database.

    Args:
        list_of_titles (list): A list of video titles.
        list_of_views (list): A list of video views.
        list_of_durations (list): A list of video durations.

    Returns:
        None
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    data = [(current_time, title, int(view), int(duration)) for title, view, duration in zip(list_of_titles, list_of_views, list_of_durations)]
    print(type(data))
    c.executemany("INSERT INTO youtube_views (date, title, views, duration) VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()


#Extract data from YouTube
def extract_data(url):
    """
    Extracts viewer counts in string format from YouTube

    Parameters:
    url (str): URL of any YouTube front page

    Returns:
    list[str]: A list of text items extracted from the specified span elements.

    This function initializes a WebDriver to load the given URL, waits for
    metadata elements to load, and extracts text from specific span elements.
    It handles NoSuchElementException to ensure robust scraping.
    """
    # Initialize the WebDriver
    driver = webdriver.Chrome()  # or use any other browser/driver
    driver.get(url)

    time.sleep(2)

    accept_button = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button/yt-touch-feedback-shape/div/div[2]')
    accept_button.click()

    time.sleep(2)

    zoom_out_script = "document.body.style.zoom='30%'"  # Adjust '50%' to the desired zoom level

    driver.execute_script(zoom_out_script)
    scroll_pause_time = 0.5  # You can set your own pause time. Use 2 sec if internet connection is bad.
    screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
    i = 1

    while True:
        # scroll one screen height each time
        driver.execute_script(f"window.scrollTo(0, {screen_height * i});")
        i += 0.5
        time.sleep(scroll_pause_time)
        # check if the bottom reached
        scroll_height = driver.execute_script("return document.documentElement.scrollHeight;")
        if (screen_height * i) > scroll_height:
            break

    # Scroll to the top of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    time.sleep(10)

    # Wait for the metadata elements to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'metadata')))
    
    # Locate the 'metadata' divs
    content_dict = {}
    content_divs = driver.find_elements(By.ID, 'content')
    for n, data in enumerate(content_divs):
        try:

            video_title = data.find_element(By.ID, 'video-title').text

            metadata_div = data.find_element(By.ID, 'metadata')
            spans = metadata_div.find_elements(By.TAG_NAME, 'span')[::2]
            for view_span in spans:
                view_span = view_span.text[5:]
                view_span = view_span[:-7]
                print(view_span)

            relative_xpath_duration = ".//span[@id='text']"
            duration_span = data.find_element(By.XPATH, relative_xpath_duration).text


            print(duration_span)    
            content_dict[f"{video_title}{[n]}"] = {
                "views": view_span,
                "duration": duration_span
            }

        except NoSuchElementException:
            pass

    # Close the driver
    driver.quit()

    return content_dict

#Process view data
def str_to_n_views(view_str):
    """
       Convert a string representation of a number, possibly with units 'k' or 'mill.', to a float.

       This function is designed to parse strings that represent numbers, potentially followed by
       a unit ('k' for thousand or 'mill.' for million), and convert them into their numerical value.

       Parameters:
       view_str (str): A string representing the number. This can include commas or periods as
                       decimal separators and optionally a 'k' (for thousands) or 'mill.' (for millions)
                       as a unit. Example inputs: "1,5k", "2.3mill.", "1234".

       Returns:
       float: The numerical value represented by the input string. Returns None if the string
              does not contain a valid number or format. For example, "1,5k" returns 1500.0,
              "2.3mill." returns 2300000.0.

       Raises:
       ValueError: If the input is not a string or if the format is incorrect.

       Examples:
       >>> str_to_float("1,5k")
       1500.0
       >>> str_to_float("2.3mill.")
       2300000.0
       >>> str_to_float("1234")
       1234.0

       Notes:
       - This function uses regular expressions for parsing.
       - The function assumes that commas are used as decimal separators and periods for thousands.
         This is common in some European countries.
       """
    # Regular expression to match the number and the unit (k or mill)
    match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?)(\s*)(k|mill\.)?', view_str, re.IGNORECASE)

    if not match:
        pass
    else:
        # Extract the number and the unit
        number_str = match.group(1).replace(',', '.')
        number = float(number_str)
        unit = match.group(3) if match.group(3) else ''

        # Convert the number based on the unit
        if unit:
            if unit.lower() == 'k':
                number *= 1000
            elif unit.lower() == 'mill.':
                number *= 1000000
        return number

#Process duration data
def str_to_s_duration(durations_string):
    """
       Convert a string representation of a duration to a number of seconds.

       This function is designed to parse strings that represent a duration in the format
       "HH:MM:SS" and convert them into the number of seconds. For example, "1:23:45" returns
       5025.

       Parameters:
       durations_string (str): A string representing the duration in the format "HH:MM:SS".
                               Example inputs: "1:23:45", "0:03:21", "1234".

       Returns:
       int: The number of seconds represented by the input string. Returns None if the string
            does not contain a valid duration or format. For example, "1:23:45" returns 5025,
            "0:03:21" returns 201, "1234" returns None.

       Raises:
       ValueError: If the input is not a string or if the format is incorrect.

       Examples:
       >>> str_to_seconds("1:23:45")
       5025
       >>> str_to_seconds("0:03:21")
       201
       >>> str_to_seconds("1234")
       None

       Notes:
       - This function uses regular expressions for parsing.
       """
    # Regular expression to match the duration

    if durations_string.count(":") == 2:
        match = re.search(r'(\d+):(\d+):(\d+)', durations_string)
        # Extract the hours, minutes and seconds
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        return hours * 3600 + minutes * 60 + seconds

    elif durations_string.count(":") == 1:
        match = re.search(r'(\d+):(\d+)', durations_string)
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        return minutes * 60 + seconds

    else:
        pass

# Test the function with some examples
url = "https://youtube.com/"

content_dict = extract_data(url=url)


#Create a dictionary for easy access to the data
data_dict = {}
first_key = next(iter(content_dict))

for key in content_dict.keys():
    if key == first_key:
        continue  # Skip the first element (it is redundant)

    title = key
    views = str_to_n_views(content_dict[key]["views"])
    duration = str_to_s_duration(content_dict[key]["duration"])

    # Add to data_dict only if both views and duration are not None
    if views is not None and duration is not None:
        data_dict[title] = {"views": views, "duration": duration}



#Add data to database
add_to_db(list_of_titles=list(data_dict.keys()),
          list_of_views=[item["views"] for item in data_dict.values()],
          list_of_durations=[item["duration"] for item in data_dict.values()])
