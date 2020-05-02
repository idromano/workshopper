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
driver = webdriver.Chrome(executable_path=path_to_chromedriver, options=options)


def abrir_pagina(endereco):
    driver.get(endereco)


def atualizar_pagina():
    driver.refresh()


def esperar_tantos_segundos(tempo_em_segundos):
    time.sleep(tempo_em_segundos)


def pegar_lista_de_itens_inscritos():
    """Cria uma planilha com nome, link e link da foto de cada item inscrito na oficina"""

    with open("Itens inscritos da Workshop.csv", "w", encoding="utf-8", newline="") as planilha:
        meus_itens_inscritos = "https://steamcommunity.com/id/damacenikos/myworkshopfiles/?appid=255710" \
                               "&browsefilter=mysubscriptions" \
                               "&sortmethod=alpha" \
                               "&numperpage=30"
        print("Abrindo Meus Itens Inscritos")
        abrir_pagina(meus_itens_inscritos)
        ultima_pagina = False
        while not ultima_pagina:
            def copiar_info_de_cada_item():
                print("Copiando itens para a planilha")
                itens_inscritos = driver.find_elements_by_class_name("itemContents")
                for item in itens_inscritos:
                    nome = item.find_element_by_class_name("workshopItemTitle").text
                    link = item.find_element_by_css_selector("div.workshopItemSubscriptionDetails > a").get_attribute(
                        "href")
                    imagem = item.find_element_by_class_name("workshopItemPreviewImage").get_attribute("src")
                    writer = csv.writer(planilha)
                    writer.writerow([imagem, nome, link])
                    print("• {}".format(nome))

            def ir_para_proxima_pagina():
                try:
                    proxima_pagina = driver.find_element_by_css_selector(
                        "div.workshopBrowsePagingControls :last-child").get_attribute("href")
                    if proxima_pagina is not None:
                        print("Próxima página")
                        esperar_tantos_segundos(1)
                        abrir_pagina(proxima_pagina)
                    else:
                        nonlocal ultima_pagina
                        ultima_pagina = True
                        print("Itens copiados!")
                except NoSuchElementException:
                    atualizar_pagina()

            copiar_info_de_cada_item()
            ir_para_proxima_pagina()


pegar_lista_de_itens_inscritos()
