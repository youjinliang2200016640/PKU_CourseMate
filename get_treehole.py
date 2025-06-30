from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
import json

def fetch_with_firefox(keyword):
    options = Options()
    options.set_preference(
        "profile", 
        "/Users/dfzx/Library/Application Support/Firefox/Profiles/0qxsskaq.default-release"
    )

    driver = webdriver.Firefox(options=options)
    driver.get("https://treehole.pku.edu.cn/")

    input("请确保你已登录成功并能看到树洞内容，然后回车继续...")

    search_url = f"https://treehole.pku.edu.cn/api/pku_hole?keyword={keyword}&page=1&limit=25"
    driver.get(search_url)
    time.sleep(2)

    try:
        text = driver.find_element("tag name", "pre").text
        return json.loads(text)
    except Exception as e:
        print("数据解析失败：", e)
        return {}

profile_path = "/Users/你的用户名/Library/Application Support/Firefox/Profiles/abcd1234.default-release"

keyword = input("请输入课程关键词（例如：线性代数 测评）：").strip()
data = fetch_with_firefox(keyword)

print(f"共获取 {len(data.get('data', []))} 条测评：\n")
for post in data.get("data", []):
    print(f"[#{post['pid']}] {post['text']}\n")
