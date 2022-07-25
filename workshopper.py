from crawler import *
import meu
import csv


def montar_lista_de_itens_inscritos(id_steam):
    """
    Percorre a lista de itens inscritos do jogador no site da Steam e cria uma planilha com o nome do item,
    o link da sua página na oficina e o link da miniatura (thumbnail) de todos os itens.
    """

    nome_do_arquivo = "Itens inscritos da Workshop_rascunho.csv"
    with open(nome_do_arquivo, "w", encoding="utf-8", newline="") as planilha:

        def percorrer_paginas_da_lista_de_itens_inscritos():
            """
            Acessa a página da Steam que lista todos os itens atualmente inscritos. Em seguida, copia nome,
            url da página e url da miniatura de cada item para uma planilha. Por fim, visita a página de cada item e
            copia mais dados como: nome de quem criou o item, url de sua oficina, coleção, categoria...
            """

            print("Abrindo Meus Itens Inscritos")
            meus_itens_inscritos = "https://steamcommunity.com/id/{}/myworkshopfiles/?appid=255710" \
                                   "&browsefilter=mysubscriptions" \
                                   "&sortmethod=alpha" \
                                   "&numperpage=30".format(id_steam)
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

                        def preencher_linha_com_esses_dados(dados, arquivo=planilha):
                            csv.writer(arquivo).writerow(dados)

                        preencher_linha_com_esses_dados([imagem, nome, link])

                        print("• {}".format(nome))

                        item_atual += 1

                def ir_para_proxima_pagina():
                    try:
                        botao_de_proxima_pagina = "div.workshopBrowsePagingControls :last-child"
                        proxima_pagina = find(botao_de_proxima_pagina).get_attribute("href")

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

                copiar_infos_da_lista()
                ir_para_proxima_pagina()

        percorrer_paginas_da_lista_de_itens_inscritos()


def abrir_pagina_do_item_e_copiar_seus_dados():
    """
    Abre a página de cada item na oficina e copia dados para a planilha: nome do autor, link de sua oficina,
    coleções e categorias.
    """

    nome_da_planilha_de_leitura = "Itens inscritos da Workshop_rascunho.csv"
    nome_da_planilha_de_escrita = "Itens inscritos da Workshop_csv.csv"
    with open(nome_da_planilha_de_leitura, "r", encoding="utf-8", newline="") as planilha_simples_itens_inscritos, \
            open(nome_da_planilha_de_escrita, "w", encoding="utf-8", newline="") as planilha_final_itens_inscritos:
        reader = csv.reader(planilha_simples_itens_inscritos)
        writer = csv.writer(planilha_final_itens_inscritos)
        print("Adicionando autor, categoria e coleções dos itens:")

        for row in reader:

            nome_do_item = row[1]
            link_do_item = row[2]
            nome_do_autor = ""
            link_da_oficina_do_autor = ""
            categorias_e_colecoes = []
            item_encontrado = True  # seria melhor algo pra confirmar se o link foi mesmo encontrado

            def abrir_pagina_do_item_na_oficina():
                abrir_pagina(link_do_item)

                def copiar_nome_do_autor_e_link_de_sua_oficina():
                    for tentativa in range(3):
                        try:
                            nome_do_autor_e_link_de_sua_oficina = "div.breadcrumbs > a:nth-child(5)"
                            oficina_de_fulano = find(nome_do_autor_e_link_de_sua_oficina).text

                            fulano = oficina_de_fulano.split(" ")[2:]
                            nonlocal nome_do_autor
                            nome_do_autor = " ".join(fulano)

                            nonlocal link_da_oficina_do_autor
                            link_da_oficina_do_autor = find(nome_do_autor_e_link_de_sua_oficina).get_attribute("href")

                        except NoSuchElementException:
                            atualizar_pagina()

                        else:
                            break

                    else:
                        nonlocal item_encontrado
                        item_encontrado = False
                        print("Impossível carregar a página do item \"" + nome_do_item +
                              "\" ou localizar o autor e sua oficina")

                copiar_nome_do_autor_e_link_de_sua_oficina()

            abrir_pagina_do_item_na_oficina()

            if item_encontrado:
                def copiar_categorias_do_item():
                    try:
                        css_selector_categoria_do_item = ".rightDetailsBlock a"
                        categoria_do_item = find(css_selector_categoria_do_item)

                        if categoria_do_item.text == "Mod":
                            nonlocal categorias_e_colecoes
                            categorias_e_colecoes.append("Mod")

                        else:
                            css_selector_categoria_do_item_se_for_asset = ".workshopTags a"
                            lista_de_categorias_do_item_se_for_um_asset = finds(
                                css_selector_categoria_do_item_se_for_asset)

                            for categoria in lista_de_categorias_do_item_se_for_um_asset:
                                # noinspection PyUnboundLocalVariable
                                categorias_e_colecoes.append(categoria.text)

                    except NoSuchElementException:
                        subcategorias_de_assets = finds(".rightDetailsBlock > div > a")
                        for categoria in subcategorias_de_assets:
                            # noinspection PyUnboundLocalVariable
                            categorias_e_colecoes.append(categoria.text)

                def copiar_colecoes_do_item():
                    try:
                        botao_adicionar_a_colecao = find("#AddToCollectionBtn")
                        botao_adicionar_a_colecao.click()
                        lista_de_colecoes = find_if_visible("add_to_collection_dialog_checkbox")
                        for colecao in lista_de_colecoes:
                            if colecao.is_selected():
                                nome_da_colecao = colecao.get_attribute("data-title")
                                categorias_e_colecoes.append(nome_da_colecao)

                    except NoSuchElementException:
                        atualizar_pagina()

                    except TimeoutException:
                        atualizar_pagina()

                def ordenar_categorias_e_colecoes():
                    nonlocal categorias_e_colecoes
                    categorias_e_colecoes = sorted(set(categorias_e_colecoes))

                copiar_categorias_do_item()
                copiar_colecoes_do_item()
                ordenar_categorias_e_colecoes()

                # row[0] = row[0] I have no idea of what is this but thankfully it seems it makes no difference lol
                # row[1] = row[1]
                # row[2] = row[2]
                row.append(nome_do_autor)
                row.append(link_da_oficina_do_autor)
                row.extend(categorias_e_colecoes)
                writer.writerow(row)
                print("• " + row[1])
            else:
                pass


montar_lista_de_itens_inscritos(meu.steam_ID)
abrir_pagina_do_item_e_copiar_seus_dados()
input("Pressione qualquer tecla para encerrar.")
driver.quit()
