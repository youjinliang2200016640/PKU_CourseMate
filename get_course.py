import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import pandas as pd
async def main():
    browser = await launch(headless=False, slowMo=30)
    page = await browser.newPage()
    await page.goto("https://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/help/HelpController.jpf", {'waitUntil': 'networkidle2'})
    await asyncio.sleep(60)
    all_html = []
    while True:
        html = await page.content()
        all_html.append(html)
        next_btn = await page.querySelector('a.nextLink')
        if next_btn:
            try:
                await next_btn.click()
                await page.waitForTimeout(3000)
            except:
                break
        else:
            break

    await browser.close()

    course_data = []
    for html in all_html:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table.datagrid tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 12:
                continue
            course_data.append({
                "课程号": cols[0].get_text(strip=True).zfill(8),
                "课程名": cols[1].get_text(strip=True),
                "课程类别": cols[2].get_text(strip=True),
                "学分": cols[3].get_text(strip=True),
                "教师": cols[4].get_text(strip=True),
                "班号": cols[5].get_text(strip=True),
                "开课单位": cols[6].get_text(strip=True),
                "专业": cols[7].get_text(strip=True),
                "年级": cols[8].get_text(strip=True),
                "上课时间及教室": cols[9].get_text(strip=True),
                "限数/已选": f'"{cols[10].get_text(strip=True)}"',
                "备注": cols[11].get_text(strip=True)
            })
    df = pd.DataFrame(course_data)
    df.to_csv("课程列表.csv", index=False, encoding="utf-8-sig")
    print("所有页已抓取完成，保存为课程列表.csv")
asyncio.run(main())
