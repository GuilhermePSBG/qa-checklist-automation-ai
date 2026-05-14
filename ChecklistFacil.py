from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google import genai
import pandas as pd
import os
import time
from selenium.webdriver.common.keys import Keys
import pyautogui
from dotenv import load_dotenv
# =========================
# CONFIGURAÇÕES
# =========================

load_dotenv()

api_key = os.getenv("API_KEY")

cliente = genai.Client(api_key=api_key)


email = os.getenv("EMAIL")
senha = os.getenv("SENHA")

PastaArqPy = r"C:\Users\Hydrostec\OneDrive\Documentos\Estudo (G)\Automação básica com Python (sem framework ainda)\Checklist"

usar_ia = False

# =========================
# IA
# =========================

def processar_com_ia():

    for arquivo in os.listdir(PastaArqPy):

        if arquivo.endswith(".xlsx") and not arquivo.startswith("resultado_"):

            caminho_completo = os.path.join(PastaArqPy, arquivo)

            print(f"Processando: {arquivo}")

            try:

                df = pd.read_excel(caminho_completo, skiprows=2)

                itens = df["DESCRIÇÃO"].dropna().tolist()

                texto_itens = "\n".join(
                    [f"{i+1}. {item}" for i, item in enumerate(itens)]
                )

                prompt = f"""
Classifique cada item abaixo em apenas uma categoria.

Categorias possíveis:
- Segurança
- Documentação
- Equipamentos
- Estrutura
- Elétrica

Itens:
{texto_itens}

Responda apenas neste formato:

Item - Categoria
"""

                resposta = None

                for tentativa in range(3):

                    try:

                        resposta = cliente.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt
                        )

                        break

                    except Exception as erro_ia:

                        print(f"Erro IA: {erro_ia}")

                        time.sleep(10)

                if resposta is None:
                    continue

                linhas = resposta.text.split("\n")

                dados = []

                for linha in linhas:

                    if " - " in linha:

                        item, categoria = linha.split(" - ", 1)

                        dados.append([
                            item.strip(),
                            categoria.strip()
                        ])

                resultado = pd.DataFrame(
                    dados,
                    columns=["Item", "Categoria"]
                )

                resultado.to_excel(
                    os.path.join(
                        PastaArqPy,
                        f"resultado_{arquivo}"
                    ),
                    index=False
                )

                print(f"Arquivo salvo: resultado_{arquivo}")

            except Exception as e:

                print(f"Erro: {e}")

# =========================
# ZOOM
# =========================

def ajustar_zoom():

    navegador.execute_script(
        "document.body.style.zoom='67%'"
    )

# =========================
# EXECUTAR IA
# =========================

if usar_ia:
    processar_com_ia()

else:
    print("Pulando IA")

# =========================
# NAVEGADOR
# =========================

navegador = webdriver.Chrome()

navegador.maximize_window()

navegador.get(
    "https://spa.checklistfacil.com.br/login?lang=pt-br"
)

# =========================
# LOGIN
# =========================

WebDriverWait(navegador, 10).until(
    EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "input[formcontrolname='username']")
    )
).send_keys(email)

navegador.find_element(
    By.XPATH,
    "//button[contains(., 'Continuar')]"
).click()

WebDriverWait(navegador, 10).until(
    EC.visibility_of_element_located(
        (By.NAME, "user-password")
    )
)

navegador.find_element(
    By.NAME,
    "user-password"
).send_keys(senha)

navegador.find_element(
    By.XPATH,
    "//button[@type='submit' and contains(., 'Entrar')]"
).click()

# =========================
# FECHAR MODAL
# =========================

botao = WebDriverWait(navegador, 20).until(
    EC.presence_of_element_located(
        (By.XPATH, "//button[contains(., 'Configurar depois')]")
    )
)

navegador.execute_script(
    "arguments[0].click();",
    botao
)

# =========================
# LOOP ARQUIVOS
# =========================

for arquivo in os.listdir(PastaArqPy):

    if arquivo.endswith(".xlsx") and arquivo.startswith("resultado_"):

        caminho = os.path.join(PastaArqPy, arquivo)

        df = pd.read_excel(caminho)

        print(f"Usando arquivo: {arquivo}")

        ajustar_zoom()

        time.sleep(2)

        pyautogui.click(x=82, y=149)

        time.sleep(2)

        WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(),'Configurações')]")
            )
        ).click()

        WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[text()='Checklists']")
            )
        ).click()

        # =========================
        # CRIAR CHECKLIST
        # =========================

        nome_limpo = (
            arquivo
            .replace("resultado_", "")
            .replace(".xlsx", "")
        )

        botao = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'a[href="https://spa.checklistfacil.com.br/checklist/create"]'
                )
            )
        )

        botao.click()

        time.sleep(2)

        campo_nome = WebDriverWait(navegador, 20).until(
            EC.presence_of_element_located(
                (By.ID, "mat-input-0")
            )
        )

        campo_nome.clear()

        campo_nome.send_keys(nome_limpo)

        WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".mat-mdc-select-placeholder")
            )
        ).click()

        WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//span[contains(text(), 'Segurança do Trabalho')]"
                )
            )
        ).click()

        WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[.//span[contains(., 'Salvar')]]"
                )
            )
        ).click()

        areas_criadas = {}

        # =========================
        # LOOP ITENS
        # =========================

        for index, row in df.iterrows():

            item = str(row["Item"])

            categoria = str(row["Categoria"])

            print(f"Item: {item}")

            print(f"Categoria: {categoria}")

            # =========================
            # CRIAR ÁREA
            # =========================

            if categoria not in areas_criadas:
                try:

                    WebDriverWait(navegador, 10).until(
                        EC.invisibility_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                ".mat-mdc-snack-bar-container"
                            )
                        )
                    )

                except:
                    pass

                ajustar_zoom()

                # scroll para baixo antes
                navegador.execute_script("""
                    window.scrollTo(0, document.body.scrollHeight);
                """)

                time.sleep(1)

                botao_add_area = WebDriverWait(navegador, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//button[.//span[contains(., 'Adicionar área')]]"
                        )
                    )
                )

                navegador.execute_script("""
                    arguments[0].scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                """, botao_add_area)

                time.sleep(1)

                navegador.execute_script(
                    "arguments[0].click();",
                    botao_add_area
                )

                campo_area = WebDriverWait(navegador, 10).until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            "//input[@placeholder='Nome da área*']"
                        )
                    )
                )

                campo_area.click()

                campo_area.clear()

                campo_area.send_keys(categoria)

                # =========================
                # SCROLL PARA BOTÃO SALVAR
                # =========================

                navegador.execute_script("""
                    window.scrollTo(0, document.body.scrollHeight);
                """)

                time.sleep(1)

                botao_salvar_area = WebDriverWait(navegador, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//button[.//span[contains(., 'Salvar')]]"
                        )
                    )
                )

                navegador.execute_script("""
                    arguments[0].scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                """, botao_salvar_area)

                time.sleep(1)

                navegador.execute_script("""
                    window.scrollBy(0, 400);
                """)

                time.sleep(1)

                navegador.execute_script(
                    "arguments[0].click();",
                    botao_salvar_area
                )

                areas_criadas[categoria] = True

                print(f"Área criada: {categoria}")

                time.sleep(2)

            # =========================
            # ENCONTRAR ÁREA
            # =========================

            areas = WebDriverWait(navegador, 10).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'area')]"
                    )
                )
            )

            area_encontrada = False

            for area in areas:

                texto_area = area.text.strip()

                if categoria.lower() in texto_area.lower():

                    area_encontrada = True

                    botao_novo_item = area.find_element(
                        By.XPATH,
                        ".//button[.//span[normalize-space()='Novo item']]"
                    )

                    navegador.execute_script(
                        "arguments[0].click();",
                        botao_novo_item
                    )

                    print(f"Novo item clicado em {categoria}")

                    break

            if not area_encontrada:

                print(f"Área não encontrada: {categoria}")

                continue

            # =========================
            # CAMPO ITEM
            # =========================

            time.sleep(1)

            WebDriverWait(navegador, 10).until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,
                        "input.checklist-item-name-input"
                    )
                )
            )

            campos = navegador.find_elements(
                By.CSS_SELECTOR,
                "input.checklist-item-name-input"
            )

            campo_item = campos[-1]

            navegador.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            """, campo_item)

            time.sleep(1)

            campo_item.click()

            campo_item.clear()

            campo_item.send_keys(item)

            print(f"Texto enviado: {item}")

            # =========================
            # SCROLL
            # =========================

            navegador.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            """, campo_item)

            time.sleep(1)

            navegador.execute_script("""
                window.scrollBy(0, 500);
            """)

            time.sleep(1)

            # =========================
            # SALVAR ITEM
            # =========================

            try:

                WebDriverWait(navegador, 10).until(
                    EC.invisibility_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            ".mat-mdc-snack-bar-container"
                        )
                    )
                )

            except:
                pass

            botao_salvar = WebDriverWait(navegador, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[.//span[normalize-space()='Salvar']]"
                    )
                )
            )

            navegador.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            """, botao_salvar)

            time.sleep(1)

            navegador.execute_script(
                "arguments[0].click();",
                botao_salvar
            )

            print(f"Item salvo: {item}")

            time.sleep(2)

print("FINALIZADO")