import json
import time
import requests
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# 设置ChromeDriver路径
driver_path = 'C:/software/chrome/chromedriver-win64/chromedriver.exe'
service = Service(driver_path)

# 配置ChromeOptions
options = webdriver.ChromeOptions()
# 初始化ChromeDriver
driver = webdriver.Chrome(service=service, options=options)

# 创建保存目录
save_dir = 'papers'
os.makedirs(save_dir, exist_ok=True)

progress_file = 'download_progress.json'
checkpoint_file = 'checkpoint.txt'
pdf_urls_file = 'pdf_urls.txt'
failed_urls_file = 'failed_urls.txt'

def human_like_delay(min_delay=8, max_delay=20):
    time.sleep(random.uniform(min_delay, max_delay))

def save_pdf_url(pdf_url, filename):
    with open(filename, 'a') as f:
        f.write(f"{pdf_url}\n")
    print(f"Saved PDF URL to {filename}")

def load_paper_urls(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f]

def load_download_progress(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f]
        except IOError:
            print(f"Error reading {filename}. Starting with an empty list.")
            return []
    return []

def save_download_progress(downloaded_papers, filename):
    with open(filename, 'w') as f:
        for paper in downloaded_papers:
            f.write(f"{paper}\n")
    print(f"Saved download progress to {filename}")

def save_failed_url(paper_url, filename):
    with open(filename, 'a') as f:
        f.write(f"{paper_url}\n")
    print(f"Saved failed URL to {filename}")

def save_checkpoint(index, filename):
    with open(filename, 'w') as f:
        f.write(str(index))
    print(f"Saved checkpoint: {index}")

def load_checkpoint(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return int(f.read())
    return 0

def download_paper(paper_url):
    driver.get(paper_url)
    print(f"full paper url: {paper_url}")
    human_like_delay()

    try:
        doi_element = driver.find_element(By.XPATH, '//a[contains(@href, "doi.org")]')
        doi_url = doi_element.get_attribute('href').replace("https://doi.org/", "")
        print(f'Found DOI: {doi_url}')
        
        title_element = driver.find_element(By.XPATH, '//h1[@data-test-id="paper-detail-title"]')
        title = title_element.text.replace('/', '_').replace('\\', '_')
        print(f'Found Title: {title}')
        
        sci_hub_url = f'https://sci-hub.se/{doi_url}'
        driver.get(sci_hub_url)
        human_like_delay()
        
        button_element = driver.find_element(By.XPATH, '//button[contains(@onclick, "location.href")]')
        onclick_attr = button_element.get_attribute('onclick')
        pdf_url = onclick_attr.split("location.href='")[1].split("'")[0]
        if pdf_url.startswith("//"):
            pdf_url = f'https:{pdf_url}'
        elif pdf_url.startswith("/"):
            pdf_url = f'https://sci-hub.se{pdf_url}'
        print(f"pdf url: {pdf_url}")

        #保存pdf url
        save_pdf_url(pdf_url, pdf_urls_file)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': sci_hub_url
        }

        response = requests.get(pdf_url, headers=headers)
        time.sleep(10)
        if response.status_code == 200:
            paper_name = f"{title}.pdf"
            save_path = os.path.join(save_dir, paper_name)
            with open(save_path, 'wb') as f:
                start_time = time.time()
                for chunk in response.iter_content(chunk_size=256*1024):  # 增大块大小到1MB
                    f.write(chunk)
                    chunk_time = time.time() - start_time
                    print(f"Chunk downloaded in {chunk_time:.2f} seconds")
                    time.sleep(1)  # 每次写入后增加延时
            print(f'Downloaded: {paper_name}')
            human_like_delay()
            # 检查下载文件大小
            downloaded_size = os.path.getsize(save_path)
            print(f'Downloaded file size: {downloaded_size} bytes')

            return True
        else:
            print(f'Failed to download PDF from {pdf_url}, status code: {response.status_code}')
            print(f'Content-Type: {response.headers.get("Content-Type")}')
            return False
    except Exception as e:
        print(f'Failed to download PDF from {paper_url}: {e}')
        save_failed_url(paper_url, failed_urls_file)
        return False


# 主函数
def main():
    all_paper_urls = load_paper_urls('Kai_Huang_Papers.json')
    print(f'Total papers found: {len(all_paper_urls)}')

    downloaded_papers = load_download_progress(progress_file)
    print(f'Total papers already downloaded: {len(downloaded_papers)}')

    start_index = load_checkpoint(checkpoint_file)
    print(f'Starting from index: {start_index}')

    for i, paper_url in enumerate(all_paper_urls[start_index:], start=start_index):
        if paper_url in downloaded_papers:
            print(f'Skipping already downloaded paper: {paper_url}')
            continue
        if download_paper(paper_url):
            downloaded_papers.append(paper_url)
            print(f"Attempting to save progress after downloading: {paper_url}")
            save_download_progress(downloaded_papers, progress_file)
            print("Progress JSON has updated")
            save_checkpoint(i + 1, checkpoint_file)
        else:
            print(f"Failed to download paper, skipping: {paper_url}")
        human_like_delay()  # 延时模拟人类行为

    driver.quit()
    print("下载完成。")

if __name__ == "__main__":
    main()
