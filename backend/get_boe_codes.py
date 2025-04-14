import json
import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

BOE_URL = "https://www.boe.es/biblioteca_juridica/index.php?tipo=C&modo=1"

def get_consolidated_codes():
    options = uc.ChromeOptions()
    options.add_argument("--headless")  # sin ventana
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = uc.Chrome(options=options)

    print("🔍 Cargando la web del BOE...")
    driver.get(BOE_URL)
    time.sleep(3)

    codes = []
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='buscar/act.php?id=BOE-'][href*='tn=1']")
    for link in links:
        href = link.get_attribute("href")
        title = link.text.strip()
        if href and title:
            codes.append({"title": title, "url": href})

    driver.quit()
    return codes

def main():
    os.makedirs("data", exist_ok=True)
    codes = get_consolidated_codes()
    print(f"📚 Encontrados {len(codes)} códigos legales.")
    with open("data/boe_codigos_consolidados.json", "w", encoding="utf-8") as f:
        json.dump(codes, f, ensure_ascii=False, indent=2)
    print("✅ Guardado en 'data/boe_codigos_consolidados.json'")

if __name__ == "__main__":
    main()
