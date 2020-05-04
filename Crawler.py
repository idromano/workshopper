import csv
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

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


def adicionar_dados_dos_itens():
    with open("Itens inscritos da Workshop.csv", "r", encoding="utf-8", newline="") as in_file, open(
            "Itens inscritos da Workshop_completo.csv", "w", encoding="utf-8", newline="") as out_file:
        reader = csv.reader(in_file)
        writer = csv.writer(out_file)
        print("Adicionando autor, categoria e coleções dos itens:")

        for row in reader:
            abrir_pagina(row[2])
            item_encontrado = True
            for tentativa in range(3):
                try:
                    autor = driver.find_element_by_css_selector(
                        "div.breadcrumbs > a:nth-child(3)").text
                    autor = " ".join(autor.split(" ")[2:])
                    oficina_do_autor = driver.find_element_by_css_selector(
                        "div.breadcrumbs > a:nth-child(3)").get_attribute(
                        "href")
                    categorias_e_colecoes = []
                except NoSuchElementException:
                    atualizar_pagina()
                else:
                    break
            else:
                item_encontrado = False
                print("Impossível carregar a página do item \"" + row[1] + "\" ou localizar o autor e sua oficina")

            # noinspection PyUnboundLocalVariable
            def adicionar_categorias_do_item():
                try:
                    nonlocal categorias_e_colecoes
                    categorias_e_colecoes.append(
                        driver.find_element_by_css_selector(".rightDetailsBlock > a").text)
                except NoSuchElementException:
                    subcategorias_de_assets = driver.find_elements_by_css_selector(
                        ".rightDetailsBlock > div > a")
                    for categoria in subcategorias_de_assets:
                        categorias_e_colecoes.append(categoria.text)

            def adicionar_colecoes_do_item():
                try:
                    botao_adicionar_a_colecao = driver.find_element_by_id("AddToCollectionBtn")
                    botao_adicionar_a_colecao.click()
                    esperar = WebDriverWait(driver, 10)
                    lista_de_colecoes = esperar.until(ec.visibility_of_all_elements_located(
                        (By.CLASS_NAME, "add_to_collection_dialog_checkbox")))  # não me parece muito legível mas ok
                    for colecao in lista_de_colecoes:
                        if colecao.is_selected():
                            categorias_e_colecoes.append(colecao.get_attribute("data-title"))
                except NoSuchElementException:
                    atualizar_pagina()

            def ordenar_categorias_e_colecoes():
                nonlocal categorias_e_colecoes
                categorias_e_colecoes = sorted(set(categorias_e_colecoes))

            if item_encontrado:
                adicionar_categorias_do_item()
                adicionar_colecoes_do_item()
                ordenar_categorias_e_colecoes()

                row[0] = row[0]
                row[1] = row[1]
                row[2] = row[2]
                row.append(autor)
                row.append(oficina_do_autor)
                row.extend(categorias_e_colecoes)
                writer.writerow(row)
                print("• " + row[1])
            else:
                pass


pegar_lista_de_itens_inscritos()
adicionar_dados_dos_itens()
input("Pressione qualquer tecla para encerrar.")
driver.quit()
