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

def get_ai_summary(text_content):
    api_key = os.getenv("AI_API_KEY")
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": f"总结以下内容：{text_content}"}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        
        # 如果返回了正常结果
        if 'choices' in res_json:
            return res_json['choices'][0]['message']['content']
        # 如果 API 返回了错误信息，把错误信息显示出来
        else:
            return f"AI 接口报错了：{res_json.get('error', {}).get('message', '未知错误')}"
            
    except Exception as e:
        return f"网络请求失败：{str(e)}"

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
