import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.aljazeera.net/where/palestine"

browser = webdriver.Chrome()
browser.get(URL)

articles = []

# Wait for the "See More" button to be clickable
see_more = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'اعرض المزيد')]")))

while len(articles) < 60:
    # Scroll to the bottom of the page
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # Wait a bit for new articles to load
    time.sleep(3)
    
    # Find all articles on the page
    page_articles = browser.find_elements(By.XPATH, "//article")
    
    # here check if i reached or exceeded the desired count of articles
    if len(articles) >= 60:
        break
    
    # Extend the list of articles
    articles.extend(page_articles)
    
    # Click "See More" if available
    try:
        see_more.click()
        time.sleep(3)  # Wait after clicking "See More"
    except Exception as e:
        print("See More button not found or error clicking:", e)
        break

# Limit to the first 60 articles
final_articles = articles[:60]

articles_data = []

for article in final_articles:
    # Extract article data
    title = article.find_element(By.XPATH, ".//a/span").text
    #url = URL + article.find_element(By.XPATH, ".//</a>").get_attribute("href") #error on this line
    url = URL + article.find_element(By.XPATH, ".//a").get_attribute("href") #here error fixed, remember link attribute
    date = article.find_element(By.XPATH, ".//div/span[2]").text
    text = article.text.split("Published On")[0]

    articles_data.append({"title": title, "url": url, "date": date, "text": text})

df = pd.DataFrame(articles_data)
df.to_csv("articles.csv", index=False, encoding='utf-8-sig')

browser.quit()
