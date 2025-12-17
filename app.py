import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- [1. 정보 설정: 꼭 확인하세요!] ---
NAVER_ID = "cm2407"        # @naver.com은 제외
NAVER_PW = "BGBKWDZEFKP5"  # 12자리 대문자 보안 비밀번호
RECEIVER_EMAIL = "cm2407@naver.com"

def run_ultimate_test():
    print("🚀 경북테크노파크 보안 우회 수집 시작...")
    
    # 이미지 153135135.jpg의 실제 데이터가 위치한 주소
    url = "https://www.gbtp.or.kr/user/board/list?menu=231&searchTerm=ing"
    
    # 진짜 사람 브라우저처럼 보이기 위한 고난도 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.gbtp.or.kr/',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        # 세션을 사용하여 연결 유지
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 153135135.jpg 이미지의 표 구조를 분석하여 데이터를 낚아챕니다.
        # 공고 제목은 보통 td 안의 a 태그에 있습니다.
        items = soup.select('table.table tbody tr')
        notice_list = []

        for item in items:
            title_tag = item.select_one('td.subject a')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = "https://www.gbtp.or.kr" + title_tag['href']
                notice_list.append(f"📌 {title}\n🔗 바로가기: {link}")

        if not notice_list:
            # 예외 케이스: 다른 태그 구조일 경우 재시도
            all_links = soup.find_all('a')
            for a in all_links:
                if "view" in a.get('href', '') and len(a.get_text(strip=True)) > 10:
                    notice_list.append(f"📌 {a.get_text(strip=True)}\n🔗 바로가기: https://www.gbtp.or.kr" + a['href'])

        # 결과물 생성
        if notice_list:
            print(f"✅ {len(notice_list)}개의 공고를 찾아냈습니다!")
            content = "🔥 [축하합니다!] 경북TP 수집에 성공했습니다.\n\n" + "\n\n".join(notice_list[:5])
        else:
            print("❌ 데이터 추출에 실패했습니다.")
            content = "사이트 접속은 성공했으나, 내용을 읽어오는 데 실패했습니다. 구조를 다시 확인해야 합니다."

        # 메일 발송
        msg = MIMEMultipart()
        msg['Subject'] = "📢 [성공] 경북TP 실시간 공고 리스트"
        msg['From'] = f"{NAVER_ID}@naver.com"
        msg['To'] = RECEIVER_EMAIL
        msg.attach(MIMEText(content, 'plain'))

        with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
            server.login(NAVER_ID, NAVER_PW)
            server.send_message(msg)
        print("📧 메일함으로 성공 리포트를 보냈습니다!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    run_ultimate_test()
