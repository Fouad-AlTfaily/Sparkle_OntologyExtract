from datetime import datetime
import time
import pandas as pd   

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://www.aljazeera.net/where/palestine"  

STOP_DATE = datetime(2024, 3, 2)

options = Options() 
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")
options.set_capability("acceptInsecureCerts", True)

browser = webdriver.Chrome(options=options)  
browser.get(URL)  

articles = []
date_xpath = ".//div/span[contains(., '/')]"   

see_more = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'اعرض المزيد')]")))
    
while True:

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(3)   

    page_articles = browser.find_elements(By.XPATH, "//article")
    articles.extend(page_articles)

    # Click See More  
    see_more.click()
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//article")))

    last_date_str = articles[-1].find_element(By.XPATH, date_xpath).text.split("Published On")[0]  
    last_date = datetime.strptime(last_date_str, "%d/%m/%Y")
    
    if last_date < STOP_DATE:
        break

filtered_articles = []

for article in articles:
    date = datetime.strptime(article.find_element(By.XPATH, ".//div/span[2]").text, "%d/%m/%Y") 
    if date < STOP_DATE:
        filtered_articles.append(article)

articles_data = []

for article in filtered_articles:
   
    title = article.find_element(By.XPATH, ".//a/span").text  
    url = URL + article.find_element(By.XPATH, ".//a").get_attribute("href") 
    date = article.find_element(By.XPATH, ".//div/span[2]").text
    
    text = article.text.split("Published On")[0]
    
    articles_data.append({"title": title, "url": url, "date": date, "text": text})
    
df = pd.DataFrame(articles_data) 
df.to_csv("articles.csv", index=False, encoding='utf-8-sig')

browser.quit()