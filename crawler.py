from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
# noinspection PyPep8Naming
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains  # I think I don't need this since there's no "send_keys" or wtv
from selenium.webdriver.common.by import By
# noinspection PyUnresolvedReferences
from selenium.common.exceptions import NoSuchElementException
# noinspection PyUnresolvedReferences
from selenium.common.exceptions import TimeoutException
import time


my_chrome_profile = "Default"
path_to_my_chrome_profile = r"C:\Users\irdam\AppData\Local\Google\Chrome\User Data"

options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir={}".format(path_to_my_chrome_profile))
options.add_argument("--profile-directory={}".format(my_chrome_profile))

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

key_combination = ActionChains(driver)


def open_new_tab(url):
    driver.execute_script('''window.open("{}","_blank");'''.format(url))
    time.sleep(1)
    current_handles = driver.window_handles
    current_handle = driver.current_window_handle
    current_handle_index = current_handles.index(current_handle)
    next_tab_index = current_handle_index - 1
    driver.switch_to.window(driver.window_handles[next_tab_index])


def find(css_selector):
    return driver.find_element(By.CSS_SELECTOR, css_selector)


def finds(css_selector):
    return driver.find_elements(By.CSS_SELECTOR, css_selector)


def find_if_visible(css_selector_by_class, seconds_to_wait=10):
    return WebDriverWait(driver, seconds_to_wait).\
        until(EC.visibility_of_all_elements_located((By.CLASS_NAME, css_selector_by_class)))


def abrir_pagina(endereco):
    driver.get(endereco)


def atualizar_pagina():
    driver.refresh()


def esperar_tantos_segundos(tempo_em_segundos):
    time.sleep(tempo_em_segundos)
