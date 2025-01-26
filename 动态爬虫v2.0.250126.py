'''
以下内容不得修改或删除!!!
# 版权声明：本代码由编写者：施云扬（复旦大学经济学院、国际金融学院）原创编写。
# 版本信息：动态爬虫2.0版本，2025年1月26日
# 许可声明：本代码仅供经编写者允许的许可者内部使用，以提高工作效率，未经许可不得使用。
# 注意事项：使用本代码时，请确保遵守相关法律法规和道德规范。
# 免责条款：若违反规定（包括但不限于违法使用、滥用导致网页禁止、网页反爬虫措施导致失败等），责任自负，编写者一律不负责。编写者保留一切权利。
'''
# 以下正文
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

def scrape_website(url, keywords, output_file_path):
    # 设置chromedriver的路径，根据你的实际路径进行修改
    chromedriver_path = '/Applications/chromedriver-mac-arm64/chromedriver'

    # 创建一个Service对象
    service = Service(executable_path=chromedriver_path)

    # 创建一个Chrome浏览器实例
    driver = webdriver.Chrome(service=service)

    # 打开网页
    driver.get(url)

    # 存储包含关键词的新闻标题、链接和额外元素内容
    results = []

    # 记录滚动开始时间
    start_time = time.time()

    while time.time() - start_time < 25:
        # 使用ActionChains模拟快速滚动
        ActionChains(driver).scroll_by_amount(0, 100).perform()
        time.sleep(0.5)  # 等待0.1秒，模拟快速滚动

    # 获取页面源代码
    page_source = driver.page_source

    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(page_source, 'html.parser')

    # 找到所有新闻标题和链接
    news_items = soup.find_all('a', class_='text-lg font-semibold text-gray-900 hover:text-primary dark:text-white')

    # 遍历每个新闻项
    for item in news_items:
        # 获取新闻标题
        title = item.get_text()

        # 检查标题是否包含任何关键词
        if any(keyword in title for keyword in keywords):
            # 获取文章链接
            link = item['href']

            # 获取额外的元素内容
            extra_element = item.find_next('div', class_='text-sm text-foreground/60')
            extra_content = extra_element.get_text() if extra_element else None

            # 将标题、链接和额外内容添加到结果列表中
            results.append((title, link, extra_content))

    # 关闭浏览器
    driver.quit()

    # 将结果保存到指定路径的.txt文件中
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for title, link, extra_content in results:
            file.write(f"标题: {title}\n")
            file.write(f"链接: {link}\n")
            file.write(f"额外内容: {extra_content}\n\n")

if __name__ == '__main__':
    # 定义要抓取的网页的URL
    url = 'https://www.dsb.cn/news'

    # 定义要查找的关键词列表
    keywords = ['京东', '腾讯', '快手']

    # 定义输出文件的路径，你需要根据实际情况填写
    output_file_path = '/Users/shiyunyang/Python进一步学习/dailynews.txt'

    # 调用scrape_website函数并将结果保存到指定路径的.txt文件中
    scrape_website(url, keywords, output_file_path)