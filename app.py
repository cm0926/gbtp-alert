import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- [1. 개인 설정] ---
MY_COMPANY_INFO = {
    "name": "(주)씨엠",
    "type": "제조 및 IT",
    "interest": "스마트공장, 신규시장 개척, 장비 지원, 시제품 제작",
    "target_email": "cm2407@naver.com"
}

genai.configure(api_key="AIzaSyA40kKTWXCl__udh224ydOatLhEo7yfKiA")
EMAIL_ID = "cm2407"
APP_PASSWORD = "BGBKWDZEFKP5"

def get_detailed_info(link):
    """상세 페이지에 접속하여 본문 및 첨부파일 확인"""
    try:
        res = requests.get(link, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 상세 페이지의 텍스트만 추출 (PDF를 직접 읽기 전 단계)
        content = soup.select_one('.board_view_area').get_text(strip=True)
        return content[:2000] # 분석을 위해 앞부분 2000자만 가져옴
    except:
        return "본문 내용을 가져오지 못했습니다."

def run_automation():
    # 1. 목록 페이지 수집
    list_url = "https://www.gbtp.or.kr/user/board/list?menu=231"
    res = requests.get(list_url, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 2. 공고 목록 추출 (이미지 주신 17번, 16번 등)
    rows = soup.select('table.table tbody tr')
    
    collected_data = []
    for row in rows[:3]: # 최신 공고 3개만 깊게 분석
        title_el = row.select_one('td.subject a')
        if title_el:
            title = title_el.get_text(strip=True)
            link = "https://www.gbtp.or.kr" + title_el['href']
            
            print(f"🔎 상세 분석 중: {title}")
            detail_text = get_detailed_info(link)
            collected_data.append({"title": title, "link": link, "content": detail_text})

    # 3. AI 맞춤형 분석
    if collected_data:
        model = genai.GenerativeModel('gemini-1.5-flash')
        context = "\n".join([f"제목: {d['title']}\n내용: {d['content']}\n---" for d in collected_data])
        
        prompt = f"""
        당신은 기업 컨설턴트입니다. 다음 공고들이 우리 회사({MY_COMPANY_INFO['name']})에 적합한지 분석하세요.
        우리 회사 분야: {MY_COMPANY_INFO['type']}, 관심사: {MY_COMPANY_INFO['interest']}

        [공고 데이터]
        {context}

        각 공고별로 다음 양식을 지켜주세요:
        1. 추천 여부: (적극추천/보통/해당없음)
        2. 이유: (회사 업종과 연관 지어 1줄 요약)
        3. 핵심내용: (지원금액, 마감일)
        4. 링크: (제공된 링크 그대로)
        
        *적합한 게 없더라도 공부 차원에서 가장 최신 것 1개는 반드시 분석해 주세요.
        """
        
        report = model.generate_content(prompt).text
        send_email(report)

def send_email(content):
    msg = MIMEMultipart()
    msg['Subject'] = f"🚀 [오늘의 맞춤공고] {MY_COMPANY_INFO['name']} 분석 리포트"
    msg['From'] = f"{EMAIL_ID}@naver.com"
    msg['To'] = MY_COMPANY_INFO['target_email']
    msg.attach(MIMEText(content, 'plain'))

    with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
        server.login(EMAIL_ID, APP_PASSWORD)
        server.send_message(msg)
    print("✅ 메일 발송 완료!")

if __name__ == "__main__":
    run_automation()
