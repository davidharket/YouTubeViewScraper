import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


def extract_metadata_spans(url):
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

    # Wait for the metadata elements to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'metadata')))

    # Locate the 'metadata' divs
    metadata_divs = driver.find_elements(By.ID, 'metadata')

    # Find all span elements within the 'metadata-inline' div and extract text from each element
    list_spans = []
    for metadata_div in metadata_divs:
        try:
            spans = metadata_div.find_elements(By.TAG_NAME, 'span')[::2]
            for span in spans:
                span = span.text[5:]
                list_spans.append(span[:-7])
        except NoSuchElementException:
            pass
    # Close the driver
    driver.quit()
    return list_spans


def str_to_int(view_str):
    """
       Convert a string representation of a number, possibly with units 'k' or 'mill.', to an integer.

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
       >>> str_to_int("1,5k")
       1500.0
       >>> str_to_int("2.3mill.")
       2300000.0
       >>> str_to_int("1234")
       1234.0

       Notes:
       - This function uses regular expressions for parsing.
       - The function assumes that commas are used as decimal separators and periods for thousands.
         This is common in some European countries.
       """
    # Regular expression to match the number and the unit (k or mill)
    match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?)(\s*)(k|mill\.)?', view_str, re.IGNORECASE)

    if not match:
        return None

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


# Test the function with some examples
url = "https://youtube.com/"

converted_values = [str_to_int(s) for s in extract_metadata_spans(url=url)]
print(converted_values)