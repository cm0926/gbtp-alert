import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- [정보 설정] ---
EMAIL_ID = "cm2407"
APP_PASSWORD = "BGBKWDZEFKP5"
TARGET_EMAIL = "cm2407@naver.com"

def run_test():
    print("🚀 경북테크노파크 수집 시도...")
    # 이미지 153135135.jpg의 실제 게시판 주소
    url = "https://www.gbtp.or.kr/user/board/list?menu=231"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    res = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 공고 제목이 들어있는 태그를 더 넓게 잡습니다.
    items = soup.find_all('td', class_='subject')
    
    notice_list = []
    for item in items[:5]:
        title_a = item.find('a')
        if title_a:
            title = title_a.get_text(strip=True)
            link = "https://www.gbtp.or.kr" + title_a['href']
            notice_list.append(f"- {title}\n  (링크: {link})")

    if not notice_list:
        content = "⚠️ 사이트 구조가 바뀌어 목록을 가져오지 못했습니다. 로그를 확인하세요."
        print(content)
    else:
        content = "✅ 경북테크노파크 최신 공고 5개 수집 성공!\n\n" + "\n\n".join(notice_list)
        print("✅ 수집 성공! 메일을 보냅니다.")

    # 메일 발송
    msg = MIMEMultipart()
    msg['Subject'] = "🔥 [최종 테스트] 경북TP 공고 수집 결과"
    msg['From'] = f"{EMAIL_ID}@naver.com"
    msg['To'] = TARGET_EMAIL
    msg.attach(MIMEText(content, 'plain'))

    with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
        server.login(EMAIL_ID, APP_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    run_test()

