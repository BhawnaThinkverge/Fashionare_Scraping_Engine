from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os

options = Options()
options.add_argument("--headless=new")
options.add_argument("window-size=1920,1080")

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(
    service=service,
    options=options
)

driver.maximize_window()

wait = WebDriverWait(driver, 20)

def get_text(parent, by, selector):
    try:
        return parent.find_element(by, selector).text.strip()
    except:
        return ""

def get_attribute(parent, by, selector, attribute):
    try:
        return parent.find_element(by, selector).get_attribute(attribute)
    except:
        return ""

driver.get(
    "https://www.elle.com/fashion/trend-reports/"
)

wait.until(
    EC.presence_of_all_elements_located(
        (
            By.CSS_SELECTOR,
            "a[data-theme-key='custom-item']"
        )
    )
)


cards = driver.find_elements(
    By.CSS_SELECTOR,
    "a[data-theme-key='custom-item']"
)

blogs = []

for card in cards:
    title = get_text(
        card,
        By.TAG_NAME,
        "h3"
    )

    image = get_attribute(
        card,
        By.TAG_NAME,
        "img",
        "src"
    )

    url = card.get_attribute("href")

    author = get_text(
        card,
        By.CSS_SELECTOR,
        "address"
    )

    blogs.append({
        "Title": title,
        "Author": author,
        "Image": image,
        "URL": url
    })

    print(f"Collected {len(blogs)} articles")

for blog in blogs:
    driver.get(blog["URL"])

    try:
        wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div[data-journey-body='standard-article']"

                )
            )
        )

        container = driver.find_element(
            By.CSS_SELECTOR,
            "div[data-journey-body='standard-article']"
        )

        paragraphs = container.find_elements(
            By.TAG_NAME,
            "p"
        )

        content = []

        for p in paragraphs:
            text = p.text.strip()

            if text:
                content.append(text)

        article_text = "\n\n".join(content)
        blog["Full Article"]= article_text

    except:
        blog["Full Article"] = ""


df = pd.DataFrame(blogs)
os.makedirs("scraped_data", exist_ok=True)
df.to_excel(
    "scraped_data/Elle_Fashion_Data.xlsx",
    index=False
)

print("Data Scraped Sucessfully")
driver.quit()