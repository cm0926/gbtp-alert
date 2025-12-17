import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# 1. 설정 (아이디와 비번만 정확히 넣어주세요)
NAVER_ID = "cm2407"
NAVER_PW = "BGBKWDZEFKP5"
RECEIVER = "cm2407@naver.com"

def start_task():
    # 질문자님이 주신 100% 정확한 주소
    target_url = "https://www.gbtp.or.kr/user/board.do?bbsId=BBSMSTR_000000000021&searchTerm=ing"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 페이지 내의 모든 링크(a 태그)를 다 가져옵니다.
        all_links = soup.find_all('a')
        notices = []

        for a in all_links:
            title = a.get_text(strip=True)
            link = a.get('href', '')
            
            # 제목이 길고(공고문일 확률 높음) 링크에 'view'가 포함된 것만 골라냅니다.
            if len(title) > 10 and 'view' in link:
                full_link = "https://www.gbtp.or.kr" + link if not link.startswith('http') else link
                notices.append(f"📌 {title}\n🔗 {full_link}")

        # 중복 제거
        notices = list(set(notices))

        if notices:
            result_text = "🎯 수집 성공! 아래는 현재 접수 중인 공고입니다.\n\n" + "\n\n".join(notices[:10])
        else:
            result_text = "접수 중인 공고를 찾지 못했습니다. 사이트 구조를 다시 확인해야 합니다."

        # 메일 발송
        msg = MIMEText(result_text)
        msg['Subject'] = "🚀 [최종 확인] 경북TP 공고 수집 결과"
        msg['From'] = f"{NAVER_ID}@naver.com"
        msg['To'] = RECEIVER

        with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
            server.login(NAVER_ID, NAVER_PW)
            server.send_message(msg)
        print("✅ 모든 작업 완료! 메일함을 확인하세요.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    start_task()
