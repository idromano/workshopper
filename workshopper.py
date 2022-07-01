from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
import time
import csv

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


def abrir_pagina(endereco):
    driver.get(endereco)


def atualizar_pagina():
    driver.refresh()


def esperar_tantos_segundos(tempo_em_segundos):
    time.sleep(tempo_em_segundos)


def pegar_lista_de_itens_inscritos():
    """Cria uma planilha com nome, link e link da foto de cada item inscrito na oficina"""

    with open("Itens inscritos da Workshop_rascunho.csv", "w", encoding="utf-8", newline="") as planilha:
        meus_itens_inscritos = "https://steamcommunity.com/id/ikromano/myworkshopfiles/?appid=255710" \
                               "&browsefilter=mysubscriptions" \
                               "&sortmethod=alpha" \
                               "&numperpage=30"
        print("Abrindo Meus Itens Inscritos")
        abrir_pagina(meus_itens_inscritos)
        ultima_pagina = False
        while not ultima_pagina:
            def copiar_infos_da_lista():
                print("Copiando itens para a planilha")
                item_atual = 0
                total_de_itens_na_pagina = len(finds(".itemContents"))

                nomes = finds(".itemContents .workshopItemTitle")
                links = finds(".workshopItemSubscriptionDetails > a")
                imagens = finds(".workshopItemPreviewImage")

                while item_atual < total_de_itens_na_pagina:
                    nome = nomes[item_atual].text
                    link = links[item_atual].get_attribute("href")
                    imagem = imagens[item_atual].get_attribute("src")

                    writer = csv.writer(planilha)
                    writer.writerow([imagem, nome, link])

                    print("• {}".format(nome))

                    item_atual += 1

            def copiar_info_de_cada_item():
                print("Copiando itens para a planilha")
                itens_inscritos = finds(".itemContents")
                for item in itens_inscritos:
                    nome = find(".workshopItemTitle").text
                    link = find(".workshopItemSubscriptionDetails > a").get_attribute("href")
                    imagem = find(".workshopItemPreviewImage").get_attribute("src")

                    writer = csv.writer(planilha)
                    writer.writerow([imagem, nome, link])

                    print("• {}".format(nome))

            def ir_para_proxima_pagina():
                try:
                    proxima_pagina = find("div.workshopBrowsePagingControls :last-child").get_attribute("href")
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

            # copiar_info_de_cada_item()
            copiar_infos_da_lista()
            ir_para_proxima_pagina()


def adicionar_dados_dos_itens():
    with open("Itens inscritos da Workshop_rascunho.csv", "r", encoding="utf-8", newline="") as in_file, open(
            "Itens inscritos da Workshop_csv.csv", "w", encoding="utf-8", newline="") as out_file:
        reader = csv.reader(in_file)
        writer = csv.writer(out_file)
        print("Adicionando autor, categoria e coleções dos itens:")

        for row in reader:
            abrir_pagina(row[2])
            item_encontrado = True
            for tentativa in range(3):
                try:
                    autor = find("div.breadcrumbs > a:nth-child(5)").text
                    autor = " ".join(autor.split(" ")[2:])
                    oficina_do_autor = find("div.breadcrumbs > a:nth-child(5)").get_attribute("href")
                    categorias_e_colecoes = []
                except NoSuchElementException:
                    atualizar_pagina()
                else:
                    break
            else:
                item_encontrado = False
                print("Impossível carregar a página do item \"" + row[1] + "\" ou localizar o autor e sua oficina")

            # noinspection PyUnboundLocalVariable,PyTypeChecker
            def adicionar_categorias_do_item():
                try:
                    nonlocal categorias_e_colecoes
                    categorias_e_colecoes.append(find(".rightDetailsBlock > a").text)
                except NoSuchElementException:
                    subcategorias_de_assets = finds(".rightDetailsBlock > div > a")
                    for categoria in subcategorias_de_assets:
                        categorias_e_colecoes.append(categoria.text)

            def adicionar_colecoes_do_item():
                try:
                    botao_adicionar_a_colecao = find("#AddToCollectionBtn")
                    botao_adicionar_a_colecao.click()
                    esperar = WebDriverWait(driver, 10)
                    lista_de_colecoes = esperar.until(EC.visibility_of_all_elements_located(
                        (By.CLASS_NAME, "add_to_collection_dialog_checkbox")))  # não me parece muito legível mas ok
                    for colecao in lista_de_colecoes:
                        if colecao.is_selected():
                            categorias_e_colecoes.append(colecao.get_attribute("data-title"))
                except NoSuchElementException:
                    atualizar_pagina()
                except TimeoutException:
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


# pegar_lista_de_itens_inscritos()
# adicionar_dados_dos_itens()
# input("Pressione qualquer tecla para encerrar.")
# driver.quit()
