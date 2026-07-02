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
options.add_argument("--window-size=1920, 1080")

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(
    service=service,
    options=options
)

driver.maximize_window()

wait = WebDriverWait(driver, 20)

def get_text(parent, by, selector):
    try:
        return parent.find_element(
            by,
            selector,
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
    "https://www.bewakoof.com/blog/category/fashion/"
)

wait.until(
    EC.presence_of_all_elements_located(
        (
            By.CSS_SELECTOR,
            "article.l-post"
        )
    )
)

articles = driver.find_elements(
    By.CSS_SELECTOR,
    "article.l-post"
)

print(f"Total Blogs Found: {len(articles)}")

blogs = []
for article in articles:
    title = get_text(
        article,
        By.CSS_SELECTOR,
        "h2 a"
    )

    url = get_attribute(
        article,
        By.CSS_SELECTOR,
        "h2 a",
        "href"
    )

    date = get_text(
        article,
        By.TAG_NAME,
        "time"
    )

    author = get_text(
        article,
        By.CSS_SELECTOR,
        ".post-author a"
    )

    image = get_attribute(
        article,
        By.CSS_SELECTOR,
        ".media span",
        "data-bgsrc"
    )

    if url == "":
        print("Skipping Invalid Card")
        continue

    blogs.append({
        "Title": title,
        "URL": url,
        "Date": date,
        "Author": author,
        "Image URL": image
    })

print(f"\nMetadata Collected: {len(blogs)} Blogs")

for blog in blogs:
    driver.get(blog["URL"])

    wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "div.post-content"
            )
        )
    )

    container = driver.find_element(
        By.CSS_SELECTOR,
        "div.post-content"
    )

    elements = container.find_elements(
        By.XPATH,
        ".//*[self::h1 or self::h2 or self::h3 or self::h4 or self::p or self::li]"
    )

    article = []
    seen = set()

    for element in elements:
        text = element.text.strip()
        if text != "" and text not in seen:
            seen.add(text)
            article.append(text)

    blog["Full Article"] = "\n\n".join(article)

print("\nAll Articles Scraped Sucessfully")

df = pd.DataFrame(blogs)

os.makedirs("scraped_data", exist_ok=True)
df.to_excel(
    "scraped_data/Bewakoof_Fashion_Data.xlsx",
    index = False
)

print("Data Scraped Sucessfully")
driver.quit()