import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- [1. 개인 설정] ---
MY_COMPANY_INFO = {
    "name": "씨엠",
    "type": "제조/IT/스마트공장 관심기업",
    "interest": "스마트공장 구축, 자율형공장, 해외시장 개척, 장비 지원",
    "target_email": "cm2407@naver.com"
}

genai.configure(api_key="AIzaSyA40kKTWXCl__udh224ydOatLhEo7yfKiA")
EMAIL_ID = "cm2407"
APP_PASSWORD = "BGBKWDZEFKP5"

def run_automation():
    print("🚀 경북테크노파크 공고 정밀 수집 시작...")
    # 이미지 153135135.jpg에 나온 정확한 주소
    list_url = "https://www.gbtp.or.kr/user/board/list?menu=231"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(list_url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('table.table tbody tr')
        
        collected_data = []
        # 최신 5개 공고 상세 분석
        for row in rows[:5]:
            title_el = row.select_one('td.subject a')
            if title_el:
                title = title_el.get_text(strip=True)
                link = "https://www.gbtp.or.kr" + title_el['href']
                
                # 상세 페이지 접속하여 본문 요약 (PDF 대신 텍스트 수집)
                print(f"🔎 상세 분석 중: {title}")
                d_res = requests.get(link, headers=headers, timeout=15)
                d_soup = BeautifulSoup(d_res.text, 'html.parser')
                detail_text = d_soup.select_one('.board_view_area').get_text(strip=True)[:1500]
                
                collected_data.append({"title": title, "link": link, "content": detail_text})

        if not collected_data:
            print("⚠️ 수집된 공고가 없습니다.")
            return

        # 3. AI 맞춤형 분석 및 리포트 생성
        print("🤖 AI가 맞춤형 리포트 작성 중...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        context = "\n".join([f"제목: {d['title']}\n내용: {d['content']}\n---" for d in collected_data])
        
        prompt = f"""
        당신은 경북 지역 기업 컨설턴트입니다. 
        우리 회사({MY_COMPANY_INFO['name']})의 관심분야({MY_COMPANY_INFO['interest']})를 바탕으로 공고를 분석하세요.
        
        분석할 공고:
        {context}

        조건: 
        1. 적합도가 있는 사업을 추천하고, 왜 추천하는지 회사 상황에 맞춰 1줄로 설명하세요.
        2. 적합한게 없다면 가장 최신 공고 2개를 요약해서 '참고용'으로 보내주세요.
        """
        
        report = model.generate_content(prompt).text
        send_email(report)

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def send_email(content):
    msg = MIMEMultipart()
    msg['Subject'] = f"🚀 [맞춤형 분석] {MY_COMPANY_INFO['name']}님을 위한 지원사업 소식"
    msg['From'] = f"{EMAIL_ID}@naver.com"
    msg['To'] = MY_COMPANY_INFO['target_email']
    msg.attach(MIMEText(content, 'plain'))

    with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
        server.login(EMAIL_ID, APP_PASSWORD)
        server.send_message(msg)
    print("✅ 메일 발송 성공!")

if __name__ == "__main__":
    run_automation()
