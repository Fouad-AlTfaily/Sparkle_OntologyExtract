from selenium import webdriver
import pandas as pd  
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.aljazeera.net/where/palestine"

driver = webdriver.Chrome()
driver.get(URL)
   
see_more = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'اعرض المزيد')]")))

articles = []

while len(articles) < 50:

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  
    see_more.click()
    
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    
    for article in soup.find_all('article'):
       
        title = article.find('a').text
        url = URL + article.find('a')['href'] 
        date = article.find('div').findNext('span').text
        text = article.find('div', class_='gc__content').text
        
        articles.append({'title': title, 'url': url, 'date': date,'text': text})
        
df = pd.DataFrame(articles)
df.to_csv("articles.csv", index=False, encoding='utf-8-sig')  

driver.quit()