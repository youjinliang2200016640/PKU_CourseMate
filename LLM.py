import os, csv, textwrap
from pathlib import Path
import pandas as pd
from openai import OpenAI
import os
from pathlib import Path

os.environ["DEEPSEEK_API_KEY"]="sk-f52246e1729c4dc8a4110f9f0c051068"
MODEL_NAME="deepseek-reasoner"# deepseek-chat / deepseek-reasoner
MAX_TOKENS=8096
TEMPERATURE=0.5
client=OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),base_url="https://api.deepseek.com")
DATASET_ROOT=Path("dataset")
if not DATASET_ROOT.exists():
    raise FileNotFoundError("未找到 dataset 目录")

SYS_PROMPT="你是一名善于提炼课程测评要点的北大学生课程助手"
USER_PROMPT_TEMPLATE=textwrap.dedent("""
任务说明
    你将看到：
    (1)课程基本信息（CSV 转为 Markdown 表格形式）
    (2)若干条学生测评（可能为空）\
学生测评的格式是
1.xxx
...
2.xxx
...
表示不同同学发表的测评。在同一个文本中的一定是同一门课程（不保证是同一个任课老师）。
                                     
请你按照：课程难度与任务量、课程听感与收获、给分好坏、总结这四个模块给出该门课程的总结。下面对各部分你要输出的内容进行具体解释。注意，你不一定需要严格按照解释来（因为可能有信息缺失）完成每部分，甚至你不一定需要把五个部分都写，因为可能有信息缺失。有多少信息，就请尽可能完成多少部分。另外，由于不同学生有不同的能力、目的，因此同一门课程可能会给出截然相反的评价，因此你需要综合考虑这些评价，给出全面而客观的总结。\
（1）课程难度与任务量：一门课程需要的先修知识，容不容易听懂，每周大概需要花多少时间写作业/论文/lab，考试难度如何等。\
（2）课程听感与收获：老师授课节奏与内容质量分别如何，到场听课是否有明显帮助，PPT/板书/讲义质量如何等。\
（3）给分好坏：给分如何（是否容易拿高分），总评成绩构成，有无签到，是否调分等。\
（4）总结：该课程适合什么样的学生选择，是否推荐非必修的学生选课，如果选课了最好按照什么样的方法学习，以及对（1）-（3）部分的概括，对课程总体的总结。\

请注意：对于英语课、体育课，由于这类课程不一定是统考，老师对课程有很大的影响，且在选择的时候有较强的选择性，请你在输出以上内容时，按不同的授课教师进行讨论。对于专业课、通识课、公选课，由于一般只有一个班级没得选，因此不需要分类讨论。

测评文章中可能有一些名词，是北大学生特有的“网络黑话”，下面我会尽可能详细的给你解释（注意这些解释仅供你理解测评文本中可能不好理解的名词，但是请不要原封不动呈现这些解释）：
a.正态：北京大学规定，除非老师申请超优秀率，否则一门课85分以上的学生不得超过40%。因此，有些老师为了满足优秀率规定，会把本来高于85分的学生给强行降到84分或者84.5分，此即为“正态分布”，后学生常称为“正态”或者“正太”。不过，如果一名学生恰好拿了84分，也有可能说自己的成绩是“正态”，这是语义的推广。
b.PF：Pass/Fail制，是一种特殊的成绩记载方式，只记录合格/不合格，且不参与GPA计算。在2020-2022年的部分课程，由于中国大陆的疫情政策限制，部分课程被迫线上。有些课程推出了自选PF制/强制PF制。在如今管制结束后，仍有部分课程保留了这一制度，但大多是一开始就说清楚PF制还是百分制，而不可以自选。PF制的课程由于不参与GPA计算，因此很多学生投入精力较少。
c.彩虹/🌈：指课程总评拿到了100分。
d.两/三个看似无意义的英文字母：一般是授课老师中文名的拼音首字母。例如，“陈向群”简写为cxq，“冯硕”简写为fs。
e.A级/B级/C级/C+级：北京大学英语分级体制。入学时同学们会参加一场英语分级考试，根据结果选择不同学分和难度的英语课。从A到C+需要的学分数减少，难度增加。
f.地震概论：有两个含义。第一个含义是，地震概论本身是地球与空间科学学院开设的一门通识课，因其不签到、容易得满分高分、任务量小而著名，被人称为“北大第一水课”。另一种含义是一种形容词，因为本课程实在太著名，所以有人拿“地震概论”来形容一门课，可能在表示这么课事少课水给分好。
g.一些学院的简称：xk=信科=信息科学技术学院，sms=school of mathematical science=数院=数学科学学院，gy=工学院，wy=物理学院 或 外国语学院（可能有歧义，需要你根据context理解，因为两个学院拼音首字母都是wy），ccme=化学与分子工程学院，sky=生命科学学院，gsm=光华管理学院，jy=经济学院，nsd=国家发展研究院。
h.dz：指“洞主”，相当于百度贴吧中的贴主，指发帖人自己。
i.肥猴/赛艇：指北大学生常用于获取往年题与课程资料的两个平台。\
                                     
输出要求：请使用 Markdown 输出一段300-800字的中文总结，格式如下：
### 课程名称（然后在这个括号内写上开课院系与学分数）

#### 课程难度与任务量  
...

#### 课程听感与收获  
...

#### 给分好坏  
...

#### 总结与建议  
...

若测评为空，请根据课程基本信息合理推测，结尾加上：“提示：以上内容基于课程基本信息由LLM推测得到，并非来自学生测评，请谨慎参考！”
若为英语课/体育课，请按不同授课教师分别讨论；其他课程无需。
禁止逐句复制原文，可归纳引用。若信息严重不足可适当省略部分模块。
                                     
###课程基本信息
    {INFO_MD}
###学生测评
    {EVAL_TEXT}""")

def csv_to_md_table(csv_path: Path)->str:
    df = pd.read_csv(csv_path)
    return df.to_markdown(index=False)
def read_txt(path: Path) -> str:
    return path.read_text("utf-8", errors="ignore").strip() if path.exists() else ""
def call_llm(info_md: str, eval_text: str)->str:
    prompt=USER_PROMPT_TEMPLATE.format(INFO_MD=info_md, EVAL_TEXT=eval_text or"（无）")
    resp=client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens =MAX_TOKENS,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system","content": SYS_PROMPT},
            {"role": "user","content": prompt}
        ],
        stream=False
    )
    return resp.choices[0].message.content.strip()
def process_course(course_dir:Path):
    info_csv=course_dir/"info.csv"
    pzxy_txt=course_dir/"evaluation_pzxy.txt"
    th_txt=course_dir/"evaluation_treehole.txt"
    out_md=course_dir/"AI_summary.md"
    if out_md.exists():
        content = out_md.read_text(encoding="utf-8").strip()
        if content:
            print(f"已有总结，跳过 {out_md.relative_to(DATASET_ROOT.parent)}")
            return
    info_md =csv_to_md_table(info_csv) if info_csv.exists() else "（缺少info.csv）"
    eval_txt="\n\n".join([read_txt(pzxy_txt), read_txt(th_txt)]).strip()
    try:
        summary=call_llm(info_md,eval_txt)
        out_md.write_text(summary,encoding="utf-8")
        print(f"生成 {out_md.relative_to(DATASET_ROOT.parent)}")
    except Exception as e:
        print(f"失败 {course_dir.name}—{e}")
for cat_dir in DATASET_ROOT.iterdir():
    if not cat_dir.is_dir(): continue
    for school_dir in cat_dir.iterdir():
        if not school_dir.is_dir(): continue
        for course_dir in school_dir.iterdir():
            if course_dir.is_dir():
                process_course(course_dir)
