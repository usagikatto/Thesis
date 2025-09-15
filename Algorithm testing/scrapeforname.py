from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)
url = "https://form.jotform.com/gracecateringsvcs/made-to-order-menu-form"
driver.get(url)

time.sleep(6)

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

data = []
current_category = "Uncategorized"
product_id_counter = 1000

container = soup.find("div", {"data-wrapper-react": "true"})
if not container:
    print("Container not found.")
else:
    for element in container.find_all(["span"], recursive=True):
        classes = element.get("class", [])

        if "form-product-category-item" in classes:
            b_tag = element.find("b")
            if b_tag:
                current_category = b_tag.text.strip()

        if "form-product-item" in classes:
            item = {"Category": current_category}

            product_id = product_id_counter
            item["Product ID"] = product_id

            product_id_counter += 1

            name_tag = element.find("span", class_="form-product-name")
            price_tag = element.find("span", class_="form-product-details")

            item["Menu Name"] = name_tag.text.strip() if name_tag else "Unknown"
            item["Price"] = price_tag.text.strip() if price_tag else "N/A"

            data.append(item)

df = pd.DataFrame(data)

df.to_csv(r"D:\Documents\Thesis\data\menu_data.csv", index=False)

