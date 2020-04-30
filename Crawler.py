from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import csv

my_chrome_profile = "Default"
path_to_my_chrome_profile = r"C:\Users\irdam\AppData\Local\Google\Chrome\User Data"
path_to_chromedriver = r"C:\Users\irdam\Google Drive\Programação\Selenium webdriver\chromedriver.exe"
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir={}".format(path_to_my_chrome_profile))
options.add_argument("--profile-directory={}".format(my_chrome_profile))
options.add_argument("headless")
driver = webdriver.Chrome(executable_path=path_to_chromedriver, options=options)


def abrir_pagina(endereco):
    print("Abrindo {}".format(endereco))
    driver.get(endereco)


def esperar_tantos_segundos(tempo_em_segundos):
    time.sleep(tempo_em_segundos)


def listar_itens_inscritos():
    """Cria uma planilha com nome, link e link da foto de cada item inscrito na oficina"""

    meus_itens_inscritos = "https://steamcommunity.com/id/damacenikos/myworkshopfiles/?appid=255710" \
                           "&browsefilter=mysubscriptions" \
                           "&sortmethod=alpha" \
                           "&numperpage=30"
    abrir_pagina(meus_itens_inscritos)
    proxima_pagina = True

    with open("Meus itens da oficina.csv", "w", encoding="utf-8", newline="") as planilha:
        writer = csv.writer(planilha)
        writer.writerow(["IMAGEM", "NOME", "LINK"])
        while proxima_pagina:
            itens_inscritos = driver.find_elements_by_class_name("itemContents")
            for item in itens_inscritos:
                nome = item.find_element_by_class_name("workshopItemTitle").text
                link = item.find_element_by_css_selector("div.workshopItemSubscriptionDetails > a").get_attribute(
                    "href")
                imagem = item.find_element_by_class_name("workshopItemPreviewImage").get_attribute("src")  # miniatura
                writer.writerow([imagem, nome, link])
            esperar_tantos_segundos(1)
            try:
                botao_de_proxima_pagina = driver.find_elements_by_class_name("pagebtn")[-1]
                botao_de_proxima_pagina.click()
            except NoSuchElementException:
                proxima_pagina = False

#  Próximo passo: função para abrir cada item da lista, coletar dados e adicionar à planilha
