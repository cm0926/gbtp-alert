import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# ==========================================
# 1. 개인 설정 (이 부분만 수정하세요)
# ==========================================
MY_COMPANY_INFO = {
    "name": "(주)씨엠",
    "type": "제조 및 IT 서비스", # 예: 자동차, 섬유, 신소재부품가공, 라이프케이소재, 첨단디지털부품, SW 개발 등
    "interest": "자금지원, 마케팅, 기술개발(R&D), 시제품제작, 제품고급화, 디자인",
    "target_email": "cm2407@naver.com"
}

GEMINI_API_KEY = "AIzaSyA40kKTWXCl__udh224ydOatLhEo7yfKiA"
NAVER_ID = "cm2407"
NAVER_APP_PW = "BGBKWDZEFKP5"

# ==========================================
# 2. 수집 대상 사이트 정의
# ==========================================
TARGET_SITES = [
    {"name": "경북테크노파크", "url": "https://www.gbtp.or.kr/user/board/list?menu=231", "base": "https://www.gbtp.or.kr"},
    {"name": "경북경제진흥원", "url": "https://www.gepa.kr/user/board/list?menu=131", "base": "https://www.gepa.kr"},
    {"name": "경북창조경제혁신센터", "url": "https://ccei.creativekorea.or.kr/gyeongbuk/custom/notice_list.do", "base": "https://ccei.creativekorea.or.kr"},
    {"name": "경북창업포털", "url": "https://www.g-startup.or.kr/user/board/list?menu=131", "base": "https://www.g-startup.or.kr"}
]

genai.configure(api_key=GEMINI_API_KEY)

def get_notices(site):
    """사이트별 공고 수집"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    notices = []
    try:
        res = requests.get(site['url'], headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 공통적인 게시판 제목 태그 탐색 (사이트마다 다를 수 있음)
        items = soup.select('td.subject a, td.title a, div.title a, a.subject_link')
        
        for item in items[:5]: # 최근 5개만
            title = item.get_text(strip=True)
            link = item['href']
            if not link.startswith('http'):
                link = site['base'] + link
            notices.append({"site": site['name'], "title": title, "link": link})
    except Exception as e:
        print(f"Error crawling {site['name']}: {e}")
    return notices

def analyze_with_ai(notice_list):
    """AI에게 맞춤형 분석 요청"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    notice_text = "\n".join([f"[{n['site']}] {n['title']}" for n in notice_list])
    
    prompt = f"""
    당신은 경북 지역 기업 컨설턴트입니다. 
    다음 [공고 목록] 중 [우리 회사 정보]에 적합한 사업을 골라 '맞춤형 보고서'를 작성하세요.
    
    [우리 회사 정보]
    - 회사명: {MY_COMPANY_INFO['name']}
    - 업종: {MY_COMPANY_INFO['type']}
    - 관심: {MY_COMPANY_INFO['interest']}

    [공고 목록]
    {notice_text}

    형식:
    - 연습중이니 모든 공고를 무조건 다 요약해서 메일로 보내주세요.
    - 각 공고마다 '추천 이유(우리 회사에 어떤 이득인가?)'를 1줄로 포함하세요.
    - 요약 형식: [기관명] 사업명 (링크) -> 추천 이유
    - 만약 적합한게 하나도 없다면 '새로운 맞춤형 공고가 없습니다.'라고만 답하세요.
    """
    
    response = model.generate_content(prompt)
    return response.text

def send_email(content):
    """분석 내용을 이메일로 발송"""
    if "없습니다" in content and len(content) < 50:
        return # 보낼 내용 없으면 종료

    msg = MIMEMultipart()
    msg['Subject'] = f"🚀 [맞춤형 알림] {MY_COMPANY_INFO['name']}님을 위한 지원사업 요약"
    msg['From'] = f"{NAVER_ID}@naver.com"
    msg['To'] = MY_COMPANY_INFO['target_email']
    msg.attach(MIMEText(content, 'plain'))

    with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
        server.login(NAVER_ID, NAVER_APP_PW)
        server.send_message(msg)

# --- 메인 실행 로직 ---
if __name__ == "__main__":
    print("🚀 공고 수집 시작...")
    all_collected = []
    for site in TARGET_SITES:
        all_collected.extend(get_notices(site))
    
    if all_collected:
        print("🤖 AI 분석 중...")
        report = analyze_with_ai(all_collected)
        
        print("📧 메일 발송 중...")
        send_email(report)
        print("✅ 완료!")

