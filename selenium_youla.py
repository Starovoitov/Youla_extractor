# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import logging
import time
import traceback


def do_search(string, time_range="За 24 часа"):
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


def specify_location(location, radius=50):
    location_ref_path = "//div[contains(text(), 'Местоположение')]/span"
    location_input_path = "//div[@class='modal_map__content scrollable modal_map__content modal_map_container']" \
                          "/div/div/div/div/div/div/div/div/div/div/input"
    location_button_path = "//span[contains(text(), 'Закрепить')][1]"
    search_radius_path = "//label[contains(text(), '" + str(radius) + " км')]"

    location_ref = wait.until(ec.presence_of_element_located((
        By.XPATH, location_ref_path)))
    location_ref.click()

    location_input = wait.until(ec.presence_of_element_located((
        By.XPATH, location_input_path)))
    location_input.clear()
    location_input.send_keys(location)

    location_input.send_keys(Keys.ARROW_DOWN + Keys.ENTER)
    wait.until(ec.presence_of_element_located((By.XPATH, location_button_path)))
    wait.until(ec.presence_of_element_located((By.XPATH, search_radius_path)))
    time.sleep(5)

    actions = ActionChains(driver)

    search_radius = driver.find_elements_by_xpath(search_radius_path)[1]
    search_radius.click()

    location_button = driver.find_elements_by_xpath(location_button_path)[1]
    actions.move_to_element(location_button)

    location_button.click()

    time.sleep(5)


def is_element_exist(xpath):
    try:
        driver.implicitly_wait(0)
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    finally:
        set_driver_wait_conditins()
    return True


def get_items_names_on_page():
    elements = driver.find_elements_by_class_name('product_item__title')
    return [title.text for title in elements]


def get_items_ids_on_page():
    try:
        if is_element_exist("//div[contains(text(), 'Ничего не найдено')]"):
            return []
        elements = driver.find_elements_by_class_name('product_item')
        return [title.get_attribute("data-id") for title in elements]
    except NoSuchElementException:
        return []


def get_item_date():
    try:
        item_date = driver.find_element_by_xpath("//th[contains(text(), 'Размещено')]/../td")
        return item_date.get_attribute('textContent')
    except NoSuchElementException:
        return


def get_phone_by_item(item_element):
    show_number_path = "//span[contains(text(), 'Показать номер')]"
    number_path = "//a[contains(text(), '+7')]"

    item_element.click()
    item_date = get_item_date()

    show_number = wait.until(ec.presence_of_element_located((
        By.XPATH, show_number_path)))
    show_number.click()

    number = wait.until(ec.presence_of_element_located((
        By.XPATH, number_path)))

    return number.text, item_date


def more():
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
    f.write(visible_name + "," + visible_name + "," + visible_name + "," + visible_name +
            ",,,,,,,,,,,,,,,,,,,,,,,,,* myContacts,," + str(data) + '\r')
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


def set_driver_wait_conditins():
    driver.implicitly_wait(300)
    wait = WebDriverWait(driver, 600)
    return wait


logging.basicConfig(handlers=[logging.FileHandler("selenium_log.log", 'w', 'utf-8')], level=logging.INFO,
                    format='[%(asctime)s] %(levelname).1s %(message)s',
                    datefmt='%Y.%m.%d %H:%M:%S')

logging.info("New start")

destinations = read_destinations("destinations.txt")

driver = webdriver.Chrome()
driver.get("https://youla.ru/")

wait = set_driver_wait_conditins()

logging.info("Chrome driver has been set up")

csv_file = "output.csv"
create_new_file(csv_file)

sought_for = "детский гардероб, город"
count = 1

for location in destinations:

    driver.get("https://youla.ru/")
    driver.implicitly_wait(300)
    wait = WebDriverWait(driver, 600)

    specify_location(location=location, radius=50)
    do_search(sought_for, time_range="За 24 часа")

    item_id_list = show_all_suitable()

    logging.info("Item list: %s" % item_id_list)
    logging.info("Total items: %d" % len(item_id_list))
    phones = []
    try:
        for item_id in item_id_list:
            item = wait.until(ec.element_to_be_clickable((By.XPATH, "//li[@data-id='" + item_id + "']")))
            phone, date = get_phone_by_item(item)

            if phone not in phones:
                add_to_csv(csv_file, count, phone)
                logging.info(str(count) + ',' + str(phone) + '.' + str(date))
                phones.append(phone)
            count += 1
            driver.back()
    except Exception as ex:
        logging.exception("Something awful happened!")
        logging.exception(traceback.print_exc())

logging.info("Processing has been ended")
time.sleep(5)
driver.quit()
