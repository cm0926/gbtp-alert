import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io
from PyPDF2 import PdfReader

# ==========================================
# 1. 개인 설정 (이 부분을 꼭 수정하세요!)
# ==========================================
GEMINI_API_KEY = "AIzaSyA40kKTWXCl__udh224ydOatLhEo7yfKiA"
EMAIL_ID = "cm2407@naver.com"
APP_PASSWORD = "BGBKWDZEFKP5" # 공백없이 입력
RECEIVER_EMAIL = EMAIL_ID  # 나에게 보내기

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# 공고 사이트 주소
BASE_URL = "https://www.gbtp.or.kr"
LIST_URL = f"{BASE_URL}/home/main.do?menuPos=3" # 경북TP 사업공고 페이지

def get_latest_posts():
    """게시판에서 공고 목록을 가져옵니다."""
    response = requests.get(LIST_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 경북TP 게시판 구조에 맞게 제목과 링크 추출 (사이트 구조에 따라 수정될 수 있음)
    posts = []
    table = soup.select_one('table.board_list')
    if table:
        for row in table.select('tbody tr'):
            title_cell = row.select_one('td.subject a')
            if title_cell:
                title = title_cell.get_text(strip=True)
                link = BASE_URL + title_cell['href']
                posts.append({'title': title, 'link': link})
    return posts

def extract_pdf_text(post_link):
    """공고 상세 페이지에서 PDF를 찾아 텍스트를 추출합니다."""
    res = requests.get(post_link)
    soup = BeautifulSoup(res.text, 'html.parser')
    # 첨부파일 중 PDF 링크 찾기
    pdf_link_tag = soup.find('a', href=lambda href: href and '.pdf' in href.lower())
    
    if not pdf_link_tag:
        return "첨부된 PDF 파일을 찾을 수 없습니다."

    pdf_url = BASE_URL + pdf_link_tag['href']
    pdf_res = requests.get(pdf_url)
    
    with io.BytesIO(pdf_res.content) as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages[:3]: # 앞쪽 3페이지만 분석 (속도 및 토큰 절약)
            text += page.extract_text()
    return text

def summarize_with_gemini(text):
    """Gemini를 사용하여 내용을 요약합니다."""
    prompt = f"""
    다음은 정부지원사업 공고문 내용이다. 
    이 내용을 분석해서 아래 양식으로 정리해줘.
    
    1. 사업명:
    2. 지원대상:
    3. 지원예산:
    4. 접수마감일:
    5. 핵심 요약(3줄):
    6. 사업담당자 

    내용:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

def send_email(subject, body):
    """네이버 SMTP를 통해 메일을 발송합니다."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ID
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"[신규 공고 알림] {subject}"
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
            server.login(EMAIL_ID, APP_PASSWORD)
            server.sendmail(EMAIL_ID, RECEIVER_EMAIL, msg.as_string())
        print(f"메일 발송 성공: {subject}")
    except Exception as e:
        print(f"메일 발송 실패: {e}")

def run_monitor():
    """메인 실행 함수"""
    print("경북TP 공고 모니터링 시작...")
    
    # 히스토리 불러오기
    if os.path.exists("history.txt"):
        with open("history.txt", "r", encoding="utf-8") as f:
            history = f.read().splitlines()
    else:
        history = []

    posts = get_latest_posts()
    new_posts_found = False

    for post in posts:
        if post['title'] not in history:
            print(f"새 공고 발견! 분석 중: {post['title']}")
            
            # 1. PDF 텍스트 추출
            pdf_text = extract_pdf_text(post['link'])
            
            # 2. Gemini 요약
            summary = summarize_with_gemini(pdf_text)
            
            # 3. 이메일 발송
            email_content = f"공고 제목: {post['title']}\n링크: {post['link']}\n\n[AI 요약 내용]\n{summary}"
            send_email(post['title'], email_content)
            
            # 4. 히스토리 저장
            with open("history.txt", "a", encoding="utf-8") as f:
                f.write(post['title'] + "\n")
            
            new_posts_found = True
    
    if not new_posts_found:
        print("새로운 공고가 없습니다.")

if __name__ == "__main__":

    run_monitor()
