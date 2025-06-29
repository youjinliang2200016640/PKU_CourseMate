from .llm import *
from dotenv import load_dotenv
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
import re
import csv
import json
import numpy as np
from PIL import Image
from io import BytesIO
from collections import Counter, defaultdict

STOP_WORDS_PATH  = "hit_stopwords.txt"
ENV_PATH = ".env"
MIN_LEGTH = 2

load_dotenv(ENV_PATH)

deepseek_v3 = Deepseek_V3()
deepseek_v3.setup()

deepseek_r1 = Deepseek_R1()
deepseek_r1.setup()

with open(STOP_WORDS_PATH, encoding='utf-8') as file:
    stop_words = []
    for line in file:
        stop_words.append(line.strip())
        
stop_words.extend(["洞主", "dz"])

plt.rcParams['font.sans-serif'] = ['KaiTi']
plt.rcParams['axes.unicode_minus'] = False

# 绘制词云图
def wordcloud_draw(context : str, title = "WorldCloud", width = 1920, height = 1080, savepath = '', max_words_num = 100, max_font_size=100):
    cut_list = jieba.lcut(context)
    cut_list = [word for word in cut_list if len(word) >= MIN_LEGTH]
    cut_list = ' '.join(cut_list)
    cloud = WordCloud(
        font_path='C:/Windows/Fonts/STKAITI.TTF',
        width=width,
        height=height,
        background_color= 'rgba(255, 255, 255, 0)',
        mode="RGBA",
        max_words=max_words_num,
        max_font_size=max_font_size,
        stopwords=stop_words, 
        scale=3,
        collocations=False
    ).generate(
        cut_list
    )
    cloud_image = plt.imshow(cloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    if savepath:    
        plt.savefig(savepath, dpi=300, bbox_inches="tight", transparent=True)
    plt.clf()
    return cloud_image


def histogram_draw(scores : list[float], title : str = "得分情况"):
    custom_bins = [0, 60, 70, 75, 80, 85, 90, 95, 100]
    freq, _ = np.histogram(scores, bins=custom_bins)

    # 生成区间标签
    bin_labels = [
        f"{custom_bins[i]}-{custom_bins[i+1]}" 
        for i in range(len(custom_bins)-1)
    ]

    # 创建等宽柱状图
    graph = plt.figure(figsize=(10, 6))
    x_pos = np.arange(len(bin_labels))  # 生成0,1,2...序列作为x坐标
    width = 0.8  # 固定柱宽
    bars = plt.bar(
        x_pos, 
        freq,
        width=width,
        color='#2196F3',
        edgecolor='black',
        alpha=0.75,
        linewidth=1.2
    )

    # 设置图表元素
    plt.title(title, fontsize=14)
    plt.xlabel('分数区间', fontsize=12)
    plt.ylabel('频数', fontsize=12)
    plt.xticks(x_pos, bin_labels)  # 旋转标签
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # 添加频数标注
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, 
            height + 0.2,
            str(int(height)),
            ha='center', 
            va='bottom',
            fontsize=10
        )
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    img = Image.open(buf)
    return img

# 将抽取上课时间字符串中的信息，并以元组的形式返回(上课的周，星期几，时间)
def convert(item : str):
    items = item.split(" ")
    if len(items) == 3:
        week, times, room = items
    else:
        week, times, room = *items, None
    op = {
        "一" : 0,
        "二" : 1,
        "三" : 2,
        "四" : 3,
        "五" : 4,
        "六" : 5,
        "日" : 6,
    }
    rep = re.compile(r"(?:每|单|双)周周(\w)(\d+~\d+)节")
    match = rep.search(times)
    if match is None:
        print(times)
        raise ValueError("match error")
    else:
        times = match.groups()
        return week, op[times[0]], times[1], room
# 将原始数据读入为json对象
def readInfo(path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        key = next(reader)
        value = next(reader)
    data = {}
    regex = re.compile(r"\d+~\d+周 (?:每|单|双)周周\w\d+~\d+节(?: \w{2}\d{3})?", )
    for k,v in zip(key, value):
        if k == '上课时间及教室':
            if v:
                times =  regex.findall(v)
                if times:
                    data[k] = list(map(convert, times))
                else:
                    print(value)
                    data[k] = v
            else:
                data[k] = []
        elif k == "限数/已选":
            data[k] = v.replace("\"", "")
        elif k == "学分" or k == "年级":
            data[k] = None if not v else int(float(v))
        else:
            data[k] = v if v else None
    return data
# 数据处理
def processInfo(path):
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    regex = re.compile(r"\d+~\d+周 (?:每|单|双)周周\w\d+~\d+节(?: \w{2}\d{3})?", )
    for data in items:
        for k,v in data.items():
            if k == '上课时间及教室':
                if v:
                    times =  regex.findall(v)
                    if times:
                        data[k] = list(map(convert, times))
                    else:
                        data[k] = v
                else:
                    data[k] = []
            elif k == "限数/已选":
                data[k] = v.replace("\"", "")
            elif k == "学分" or k == "年级":
                data[k] = None if v is None else int(v)
            else:
                data[k] = v
    return items
def insertItem(path):
    with open(path, "r", encoding="utf-8") as f:
        key = f.readline()
        value = f.readline()
    keys = key.split(",")
    keys.insert(2, "级别")
    with open(path, "w", encoding="utf-8") as f:
        f.writelines([",".join(keys), value])

# 计算tf-idf，并将输入文本依据tf-idf处理为词云图的输入字符串
class WordConstructor:
    IDF_PATH = "idf.json"
    DOC_PATH = "dataset"
    def __init__(self):
        self.idf_dict : dict[str, float] | None = None
        
    def tf(self, context : str):
        words = [word for word in jieba.lcut(context) if len(word)>=MIN_LEGTH]
        return Counter(words)
        
    @property
    def idf(self):
        if self.idf_dict is not None:
            return self.idf_dict
        if os.path.exists(WordConstructor.IDF_PATH):
            with open(WordConstructor.IDF_PATH, "r", encoding="utf-8") as f:
                self.idf_dict = json.load(f)
        else:
            contexts = []
            for dir, subdir, files in os.walk(WordConstructor.DOC_PATH):
                if not subdir:
                    file_path = os.path.join(dir, "evaluation_treehole.txt")
                    with open(file_path, "r", encoding="utf-8") as f:
                        txt = f.read()
                        if txt:
                            contexts.extend(txt.split("\n\n"))
            D = len(contexts)
            count = Counter()
            for context in contexts:
                words = [word for word in jieba.lcut(context) if len(word) >=2]
                words = list(set(words))
                for word in words:
                    count[word] += 1
            idf = {}
            for k, v in count.items():
                idf[k] = np.log(D/(v+1))
            with open(WordConstructor.IDF_PATH, "w", encoding="utf-8") as f:
                json.dump(idf, f, ensure_ascii=False, indent=4)
            self.idf_dict = idf
        return self.idf_dict
    
    def tf_idf(self, context : str):
        tf = self.tf(context)
        idf = self.idf
        assert idf is not None
        tf_idf = {}
        for k in tf.keys():
            tf_idf[k] = tf[k] * idf[k]
        return tf_idf
    
    def process(self, context):
        tf_idf = self.tf_idf(context)
        content = []
        for k, v in tf_idf.items():
            content.extend([k]*int(10*v))
        return " ".join(content)