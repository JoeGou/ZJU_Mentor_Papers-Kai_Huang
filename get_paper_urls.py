from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import requests
import os
import time
import json

# 配置路径
driver_path = 'C:/software/chrome/chromedriver-win64/chromedriver.exe'
save_dir = 'papers'
url_file = 'Kai_Huang_Papers.json'
base_url = 'https://www.semanticscholar.org/author/Kai-Huang/144459093?sort=pub-date'

# 确保保存目录存在
os.makedirs(save_dir, exist_ok=True)

# 初始化ChromeDriver
service = Service(driver_path)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

def get_paper_urls(page_url):
    driver.get(page_url)
    time.sleep(10)  # 等待页面加载
    papers = driver.find_elements(By.XPATH, '//a[contains(@href, "/paper/") and not(contains(@href, "#citing-papers"))]')
    paper_urls = [paper.get_attribute('href') for paper in papers]
    print(f"paper_urls: {paper_urls}")
    return paper_urls

def save_paper_urls(urls, filename):
    with open(filename, 'w') as f:
        for url in urls:
            f.write(f"{url}\n")
    print(f"Saved paper URLs to {filename}")

def main():
    page_num = 1
    all_paper_urls = []

    while True:
        page_url = f'{base_url}&page={page_num}'
        paper_urls = get_paper_urls(page_url)
        if not paper_urls:
            break
        all_paper_urls.extend(paper_urls)
        page_num += 1

    print(f'Total papers found: {len(all_paper_urls)}')
    save_paper_urls(all_paper_urls, url_file)
    
   
    print("Paper Urls downloaded done")
    # for paper_url in all_paper_urls:
    #     download_paper(paper_url)

    # driver.quit()
    # print("下载完成。")

if __name__ == "__main__":
    main()
