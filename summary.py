import asyncio
import aiohttp
import json
import xmltodict
import google.generativeai as genai

url = "http://apis.data.go.kr/B490001/sjbPrecedentInfoService/getSjbPrecedentNaeyongPstate"
params = {
    "serviceKey": "HL+Z1DVaoQ5w5vI/N1y1qA0pALQW7IcgLjf2XoNoq4ggQ0GtFiV1AoiXIXT55Q7hqxPa7OpeVdWPhZQFnDeCNg==",
    "pageNo": 1,
    "numOfRows": 10,
    "kindA": "기각",
    "kindB": "장해",
    "kindC": "업무상질병",
}

GOOGLE_API_KEY = "AIzaSyC1WSVud2tmNk5izNATKvdjyc5eoPZGu94"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

async def fetch_data(session, url, params):
    async with session.get(url, params=params) as response:
        return await response.text()

async def generate_summary(content):
    summary = await asyncio.to_thread(model.generate_content, content + "  를 요약해주고, 원고의 승패를 알려줘!git")
    return summary.text

async def main():
    async with aiohttp.ClientSession() as session:
        response_text = await fetch_data(session, url, params)
        response_dict = xmltodict.parse(response_text)
        
        jsonStr = json.dumps(response_dict, indent=4)
        dict_data = json.loads(jsonStr)

        total_count = dict_data['response']['body']['totalCount']
        items = dict_data['response']['body']['items'].values()

        tasks = []
        for i in items:
            for j in i:
                content = j['noncontent']
                tasks.append(generate_summary(content))

        summaries = await asyncio.gather(*tasks)

        for summary in summaries:
            print(summary)


asyncio.run(main())
