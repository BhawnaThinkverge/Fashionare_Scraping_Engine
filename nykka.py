from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import os

options = Options()
options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(
    service=service,
    options=options
)

wait = WebDriverWait(driver, 20)

def get_text(parent, by, selector):
    try:
        return parent.find_element(
            by,
            selector
        ).text.strip()
    except:
        return ""

def get_attribute(parent, by, selector, attribute):
    try:
        return parent.find_element(
            by,
            selector
        ).get_attribute(attribute)

    except:
        return ""

driver.get(
    "https://www.nykaafashion.com/style-files?srsltid=AfmBOor9qqyrhvfc5PNSulhEb_4DSoEQtynrVbQr9v7dUTbx8H_C-Te-"
)

time.sleep(5)

wait.until(
    EC.presence_of_all_elements_located(
        (
            By.CSS_SELECTOR,
            "a.block.no-underline"
        )
    )
)

cards = driver.find_elements(
    By.CSS_SELECTOR,
    "a.block.no-underline"
)

print(f"Total Blog Cards Found: {len(cards)}")

blogs = []

for card in cards:
    title = get_text(
        card,
        By.CSS_SELECTOR,
        "div.text-xl"
    )

    summary = get_text(
        card,
        By.CSS_SELECTOR,
        "div.text-sm"
    )

    date = get_text(
        card,
        By.CSS_SELECTOR,
        "div.text-xs span"
    )

    image = get_attribute(
        card,
        By.TAG_NAME,
        "img",
        "src"
    )

    url = card.get_attribute("href")
    if url.startswith("/"):
        url = "https://www.nykaafashion.com" + url

    blogs.append({
        "Title": title,
        "Summary": summary,
        "Date": date,
        "Image URL": image,
        "URL": url
    })

for blog in blogs:
    print(f"Opening: {blog["Title"]}")
    driver.get(
        blog["URL"]
    )

    selectors = [
        "section.article-wrapper",
        "div.article-box",
        "div.article-content",
        "article",
        "main"
    ]

    container = None

    for selector in selectors:
        try:
            container = driver.find_element(
                By.CSS_SELECTOR,
                selector
            )

            print("Found", selector)
            break

        except:
            continue

        
    content = []
    if container:
        elements = container.find_elements(
            By.CSS_SELECTOR,
            "h1,h2,h3,p,li"
        )

        for element in elements:
            text = element.text.strip()
            if text:
                content.append(text)

    else:
        print("No content container found")

    blog["Full Article"] = "\n\n".join(content)


df = pd.DataFrame(blogs)

os.makedirs("scraped_data", exist_ok=True)

df.to_excel(
    "scraped_data/Nykaa_Fashion_Data.xlsx",
    index = False
)

print("Data Scraped Sucessfully")
driver.quit()