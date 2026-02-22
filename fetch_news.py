import os
import requests
import feedparser
import json
from datetime import datetime

# 1. 设定新闻源
SOURCES = [
    {"name": "金融时政", "url": "https://www.hkma.gov.hk/chi/rss/news-releases/"},
    {"name": "政府新闻", "url": "https://www.info.gov.hk/gia/rss/general/ctoday.xml"}
]

def get_ai_summary(text):
    api_key = os.getenv("AI_API_KEY")
    # --- 关键修改点：SiliconFlow 的 API 地址 ---
    url = "https://api.siliconflow.cn/v1/chat/completions"
    
    if not api_key:
        return "错误：未配置 AI_API_KEY"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # --- 关键修改点：SiliconFlow 的模型名称 ---
    # 推荐使用 deepseek-ai/DeepSeek-V3 (性价比极高) 
    # 或者 deepseek-ai/DeepSeek-R1 (推理能力更强)
    payload = {
        "model": "deepseek-ai/DeepSeek-V3", 
        "messages": [
            {"role": "system", "content": "你是一位香港金融与HR专家。"},
            {"role": "user", "content": f"请简要总结以下香港资讯，突出HR案例和金融热点，使用繁体中文：\n{text}"}
        ],
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        res_json = response.json()
        
        if 'choices' in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            # 这样写可以帮你捕获 SiliconFlow 返回的具体错误（如余额不足）
            error_info = res_json.get('error', {}).get('message', '未知错误')
            return f"SiliconFlow 报错：{error_info}"
            
    except Exception as e:
        return f"请求失败：{str(e)}"

# 执行逻辑
collected = []
for s in SOURCES:
    try:
        feed = feedparser.parse(s['url'])
        for e in feed.entries[:5]:
            collected.append(f"[{s['name']}] {e.title}")
    except:
        pass

full_text = "\n".join(collected)
report = get_ai_summary(full_text)

# 保存数据
with open("data.json", "w", encoding="utf-8") as f:
    json.dump({
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"), 
        "report": report
    }, f, ensure_ascii=False, indent=2)
