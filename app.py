import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- [정보 설정: 본인 정보로 꼭 수정하세요] ---
NAVER_ID = "cm2407"  # @naver.com 제외
NAVER_PW = "BGBKWDZEFKP5"  # 네이버 2단계 인증 시 발급받은 12자리 비번
RECEIVER_EMAIL = "cm2407@naver.com"

def run_final_test():
    print("🚀 경북테크노파크 강제 수집 시도 중...")
    
    # 사용자가 직접 준 주소 (접수중 필터링된 주소)
    url = "https://www.gbtp.or.kr/user/board/list?menu=231&searchTerm=ing"
    
    # 사람이 브라우저로 접속하는 것처럼 속이는 설정 (매우 중요)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # '접수중' 빨간 버튼이 있는 행(tr)을 모두 찾습니다.
        rows = soup.find_all('tr')
        notice_list = []

        for row in rows:
            # 줄 안에 '접수중' 글자가 있는지 확인
            status_tag = row.find('span', class_='btn_red') # 접수중 태그
            if status_tag and "접수중" in status_tag.get_text():
                link_tag = row.select_one('td.subject a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    link = "https://www.gbtp.or.kr" + link_tag['href']
                    notice_list.append(f"📌 {title}\n🔗 바로가기: {link}")

        if not notice_list:
            print("❌ 목록 추출 실패. 수동으로 데이터를 확인해야 합니다.")
            content = "사이트 구조가 크게 변경되었거나 접속이 차단되었습니다."
        else:
            print(f"✅ {len(notice_list)}개의 공고 수집 성공!")
            content = "🔥 [성공] 현재 경북TP에서 '접수 중'인 공고입니다:\n\n" + "\n\n".join(notice_list[:5])

        # 메일 발송 로직
        msg = MIMEMultipart()
        msg['Subject'] = "📢 [최종 확인] 경북TP 맞춤형 공고 리포트"
        msg['From'] = f"{NAVER_ID}@naver.com"
        msg['To'] = RECEIVER_EMAIL
        msg.attach(MIMEText(content, 'plain'))

        with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
            server.login(NAVER_ID, NAVER_PW)
            server.send_message(msg)
        print("📧 메일 전송이 완료되었습니다!")

    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    run_final_test()
