
"""
根据五张课程 CSV，生成
dataset/课程类别/开课单位/课程名/
│-- info.csv
│-- evaluation_pzxy.txt
│-- evaluation_treehole.txt
└-- AI_summary.txt
"""

import csv
import os
import re
from pathlib import Path

course_files = {
    "专业课":  "专业课.csv",
    "英语课":  "英语课.csv",
    "体育课":  "体育课.csv",
    "通识课":  "通识课.csv",
    "公选课":  "公选课.csv",
}

DATASET_ROOT = Path("dataset")
DATASET_ROOT.mkdir(exist_ok=True)
_illegal = r'[\/:*?"<>|]'
def clean(name: str) -> str:
    return re.sub(_illegal, "_", name).strip()
for category, fname in course_files.items():
    path = Path(fname)
    if not path.exists():
        print(f"⚠️ 找不到文件：{fname}（跳过）")
        continue
    with path.open(encoding="utf-8") as f:
        sample = f.read(2048)
        dialect = csv.Sniffer().sniff(sample)
        f.seek(0)
        reader = csv.DictReader(f, dialect=dialect)

        missing = [k for k in ("开课单位", "课程名") if k not in reader.fieldnames]
        if missing:
            print(f"«{fname}» 缺少字段 {missing}，跳过该文件")
            continue

        for row in reader:
            school = clean(str(row.get("开课单位", "")))
            cname  = clean(str(row.get("课程名", "")))

            if not school or not cname:
                continue

            course_dir = DATASET_ROOT / category / school / cname
            course_dir.mkdir(parents=True, exist_ok=True)
            info_path = course_dir / "info.csv"
            with info_path.open("w", newline="", encoding="utf-8") as info_f:
                writer = csv.DictWriter(info_f, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerow({k: row.get(k, "") for k in reader.fieldnames})
            for fn in ("evaluation_pzxy.txt", "evaluation_treehole.txt", "AI_summary.txt"):
                (course_dir / fn).touch(exist_ok=True)

print("处理完毕！请查看 dataset/ 目录。")
