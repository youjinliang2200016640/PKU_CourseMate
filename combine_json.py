import pandas as pd
import os
import json

csv_files={
    "专业课":"专业课.csv",
    "英语课":"英语课.csv",
    "体育课":"体育课.csv",
    "通识课":"通识课.csv",
    "公选课":"公选课.csv"
}
all_courses=[]
for category, filename in csv_files.items():
    if not os.path.exists(filename):
        print(f"文件未找到：{filename}")
        continue
    df=pd.read_csv(filename, dtype={"课程号": str})
    df["课程类别"]=category
    all_courses.extend(df.to_dict(orient="records"))
with open("all_courses.json", "w", encoding="utf-8") as f:
    json.dump(all_courses, f, ensure_ascii=False, indent=2)
