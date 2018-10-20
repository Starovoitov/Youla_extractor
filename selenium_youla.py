# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import logging
import time
import traceback
import sys
import getopt

options = Options()
# headless option shouldn't be used
# options.add_argument("--headless")
options.add_argument("--disable-extensions")
driver = None
wait = None


def do_search(string, time_range="За 24 часа"):
    global driver, wait
    searchbox_path = "//input[@id='downshift-0-input']"
    searchbox_button_path = "//span[contains(text(), 'Найти')]"
    data_range_path = "//label[contains(text(), '" + time_range + "')]"
    data_range_button_path = "//span[contains(text(), 'Применить')]"

    searchbox = wait.until(ec.presence_of_element_located((
        By.XPATH, searchbox_path)))
    searchbox.send_keys(string + Keys.ENTER)

    searchbox_button = wait.until(ec.presence_of_element_located((
        By.XPATH, searchbox_button_path)))
    searchbox_button.click()

    date_range = wait.until(ec.presence_of_element_located((
        By.XPATH, data_range_path)))
    date_range.click()

    date_range_button = wait.until(ec.presence_of_element_located((
        By.XPATH, data_range_button_path)))
    date_range_button.click()

    time.sleep(5)


def specify_location(location_name, radius=50):
    global driver, wait
    location_ref_path = "//div[contains(text(), 'Местоположение')]/span"
    location_input_css_selector = "._yjs_geolocation-map"
    location_button_css_selector = "._yjs_geolocation-select__button_apply"
    search_radius_path = "//label[text()= '" + str(radius) + " км']"

    location_ref = wait.until(ec.presence_of_element_located((By.XPATH, location_ref_path)))
    location_ref.click()

    time.sleep(2)
    location_input = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, location_input_css_selector))).\
        find_element_by_xpath(".//input")

    location_input.clear()
    location_input.send_keys(location_name)
    time.sleep(5)
    location_input.send_keys(Keys.ARROW_DOWN + Keys.ENTER)

    search_radius = wait.until(ec.presence_of_element_located((By.XPATH, search_radius_path)))
    search_radius.click()

    location_button = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, location_button_css_selector)))
    location_button.click()

    time.sleep(5)


def is_element_exist(xpath):
    global driver, wait
    exist = True
    try:
        driver.implicitly_wait(0)
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        exist = False
    finally:
        set_driver_wait_conditins()
        return exist


def get_items_names_on_page():
    global driver, wait
    elements = driver.find_elements_by_class_name('product_item__title')
    return [title.text for title in elements]


def get_items_ids_on_page():
    global driver, wait
    try:
        if is_element_exist("//div[contains(text(), 'Ничего не найдено')]"):
            return []
        elements = driver.find_elements_by_class_name('product_item')
        return [title.get_attribute("data-id") for title in elements]
    except NoSuchElementException:
        return []


def get_item_date():
    global driver, wait
    try:
        item_date = driver.find_element_by_xpath("//th[contains(text(), 'Размещено')]/../td")
        return item_date.get_attribute('textContent')
    except NoSuchElementException:
        return


def get_phone_by_item(item_element):
    global driver, wait
    show_number_path = "//span[contains(text(), 'Показать номер')]"
    number_path = "//a[contains(text(), '+7')]"
    number_card_css_selector = "._yjs_user-card"

    item_element.click()

    show_number = wait.until(ec.presence_of_element_located((
        By.XPATH, show_number_path)))
    show_number.click()

    wait.until(ec.presence_of_element_located((
        By.CSS_SELECTOR, number_card_css_selector)))

    if is_element_exist(number_path):
        return driver.find_element_by_xpath(number_path).text
    else:
        return


def more():
    global driver, wait
    driver.find_element_by_xpath("//span[contains(text(), 'Показать еще')]/..").click()
    time.sleep(5)


def show_all_suitable():
    id_list = get_items_ids_on_page()

    while len(id_list) % 60 == 0 and len(id_list) > 0:
        more()
        id_list = get_items_ids_on_page()
    return id_list


def normalize_phone(phone_number):
    normalized = ""

    for char in phone_number:
        if char in ('(', ')'):
            continue
        normalized += char
    return normalized


def add_to_csv(filename, line, data):
    f = open(filename, "a+")
    visible_name = "T" + str(line)
    f.write(visible_name + ",,,,,,,,,,,,,,,,,,,,,,,,,,,,* myContacts,,,," + str(data) + '\r')
    f.close()


def create_new_file(filename):
    f = open(filename, "w")
    f.write("Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional Name "
            "Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,Maiden Name,Birthday,"
            "Gender,Location,Billing Information,Directory Server,Mileage,Occupation,Hobby,Sensitivity,Priority,"
            "Subject,Notes,Language,Photo,Group Membership,E-mail 1 - Type,E-mail 1 - Value,Phone 1 - Type,Phone "
            "1 - Value\r")
    f.close()


def read_destinations(filename):
    f = open(filename, "r")
    destinations_ = f.readlines()
    f.close()
    return [x.strip() for x in destinations_]


def read_past_numbers(filename):
    f = open(filename, "r")
    f.readline()
    past_output = f.readlines()
    f.close()
    return [x.split(',')[-1].strip() for x in past_output]


def set_driver_wait_conditins():
    global driver, wait
    driver.implicitly_wait(300)
    WebDriverWait(driver, 300)
    return wait


def main(csv_file, sought_for, log, destinations_file, already_used_numbers_file, radius, time_range):
    global driver, wait
    logging.basicConfig(handlers=[logging.FileHandler(log, 'w', 'utf-8')], level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    logging.info("New start")

    try:
        destinations = read_destinations(destinations_file)
    except FileNotFoundError:
        print("No location for search is suggested, aborted")
        return
    try:
        already_used_numbers = read_past_numbers(already_used_numbers_file)
    except FileNotFoundError:
        already_used_numbers = []

    driver.get("https://youla.ru/")
    driver.maximize_window()
    logging.info("Web driver has been set up")

    create_new_file(csv_file)

    count = 1
    for location in destinations:

        driver.get("https://youla.ru/")
        set_driver_wait_conditins()

        specify_location(location_name=location, radius=radius)
        logging.info(location)

        do_search(sought_for, time_range=time_range)

        item_id_list = show_all_suitable()
        logging.info("Item list: %s" % item_id_list)
        logging.info("Total items: %d" % len(item_id_list))

        phones = []
        try:
            for item_id in item_id_list:

                try:
                    item = wait.until(ec.element_to_be_clickable((By.XPATH, "//li[@data-id='" + item_id + "']")))
                except TimeoutException:
                    continue

                phone = get_phone_by_item(item)

                if phone and phone not in phones and phone not in already_used_numbers:
                    add_to_csv(csv_file, count, phone)
                    logging.info(str(count) + ',' + str(phone))
                    phones.append(phone)

                count += 1
                driver.back()
        except Exception:
            logging.exception("Something awful happened!")
            logging.exception(traceback.print_exc())

    logging.info("Processing has been ended")
    time.sleep(5)
    driver.quit()


def print_help():
    """Prints a brief info about input parameters"""
    print("c, (--csv_file) - output csv file containing collected phone number by requested subject. "
          "The format is compatible to google contacts to be imported. Default name: output.csv")
    print("s, (--search) - subject to search on youla. Default value: детский гардероб, город")
    print("l, (--log) - log name of the script. Default name: youla.log")
    print("p, (--places) - file containing list of search locations (one pattern per line). Every pattern should be "
          "recognizable by youla so it can suggest matches. Default name: destinations.txt")
    print("u, (--already_used_numbers) - file-result of previous script launch. The script won't put here "
          "already used phones. If missed then it puts in output csv every finding")
    print("r, (--radius) - range of search Default value: 50 km. Any other suggested value should match values "
          "of ranges on youla's modal location window")
    print("t, (--time) - terms of new items appearing. Only items appeared in specified term are taken. "
          "Default value: За 24 часа"
          "Any other suggested value should PRECISELY match values suggested by youla's right side bar")


# default config
config = {
    "output_csv_file": "output.csv",
    "search": "детский гардероб, город",
    "log_name": "youla.log",
    "places_list": "destinations.txt",
    "already_used_numbers_file": "past_output.csv",
    "radius": 50,
    "time": "За 24 часа",
}


if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:c:l:p:u:r:t:h', ['search=', 'csv_file=', 'log=',
                                                                     'places=', 'already_used_numbers=', 'radius=',
                                                                     'time=', 'help'])

    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_help()
            sys.exit(2)
        elif opt in ('-c', '--csv_file'):
            config["output_csv_file"] = arg.strip('=')
        elif opt in ('-s', '--search'):
            config["search"] = arg.strip('=')
        elif opt in ('-l', '--log'):
            config["log_name"] = arg.strip('=')
        elif opt in ('-p', '--places'):
            config["places_list"] = arg.strip('=')
        elif opt in ('-u', '--already_used_numbers'):
            config["already_used_numbers "] = arg.strip('=')
        elif opt in ('-r', '--radius'):
            config["radius"] = int(arg.strip('='))
        elif opt in ('-t', '--time'):
            config["time"] = arg.strip('=')
        else:
            pass

    try:
        driver = webdriver.Chrome(chrome_options=options)
        wait = WebDriverWait(driver, 300)
        main(csv_file=config["output_csv_file"], sought_for=config["search"], log=config["log_name"],
             destinations_file=config["places_list"], already_used_numbers_file=config["already_used_numbers_file"],
             radius=config["radius"], time_range=config["time"])
    except KeyboardInterrupt:
        pass
