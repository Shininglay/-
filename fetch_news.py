import os
import requests
import feedparser
import json
from datetime import datetime

# 1. 设置新闻源 (香港金融与政府公告)
RSS_URLS = [
    "https://www.hkma.gov.hk/chi/rss/news-releases/", # 金管局
    "https://www.sfc.hk/tc/RSS-Feeds/News-and-announcements", # 证监会
    "https://www.info.gov.hk/gia/rss/general/ctoday.xml" # 政府综合新闻(含HR案例)
]

def get_ai_summary(news_list):
    api_key = os.getenv("AI_API_KEY")
    # 这里使用的是 DeepSeek 的 API 地址，你也可以换成 OpenAI
    url = "https://api.deepseek.com/v1/chat/completions"
    
    combined_text = "\n".join([f"- {n['title']}: {n['link']}" for n in news_list[:15]])
    
    prompt = f"""
    你是一位专业的香港金融与HR顾问。请从以下新闻中筛选出：
    1. 与HR、劳工法律、人才政策相关的案例。
    2. 重要的金融时政热点。
    
    请用精炼的繁体中文总结，每条包含：【标题】、简短【核心内容】、以及【行业建议】。
    今日新闻内容：
    {combined_text}
    """
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "你是一个专业的资讯分析助手。"},
                     {"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 总结失败: {str(e)}"

# 2. 抓取逻辑
all_news = []
for url in RSS_URLS:
    feed = feedparser.parse(url)
    for entry in feed.entries[:5]:
        all_news.append({"title": entry.title, "link": entry.link})

summary = get_ai_summary(all_news)

# 3. 保存结果
output = {
    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "report": summary
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
