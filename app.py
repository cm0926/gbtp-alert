import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- [정보 설정: 본인 정보로 수정] ---
NAVER_ID = "cm2407"        # @naver.com 제외
NAVER_PW = "BGBKWDZEFKP5"  # 12자리 보안 비밀번호
RECEIVER_EMAIL = "cm2407@naver.com"

def run_final_mission():
    print("🚀 알려주신 실제 데이터 주소로 수집 시작...")
    
    # 1. 사용자가 지정한 정확한 데이터 경로
    url = "https://www.gbtp.or.kr/user/board.do?bbsId=BBSMSTR_000000000021&searchTerm=ing"
    
    # 브라우저인 척 하기 위한 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
    }
    
    try:
        # 주소로 직접 접속 (GET 방식)
        res = requests.get(url, headers=headers, timeout=30)
        res.encoding = 'utf-8' # 한글 깨짐 방지
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 캡처 화면상의 테이블 행(tr)들을 찾습니다.
        rows = soup.select('table.table tbody tr')
        notice_list = []

        for row in rows:
            # 제목이 들어있는 'subject' 클래스 안의 a 태그 조준
            title_tag = row.select_one('td.subject a')
            if title_tag:
                title = title_tag.get_text(strip=True)
                # 링크 생성 (상대 경로인 경우 앞에 도메인 추가)
                link = title_tag['href']
                if not link.startswith('http'):
                    link = "https://www.gbtp.or.kr" + link
                
                notice_list.append(f"📌 {title}\n🔗 바로가기: {link}")

        # --- 메일 내용 구성 ---
        if notice_list:
            print(f"🎯 성공! {len(notice_list)}개의 공고를 찾았습니다.")
            email_content = "✅ [경북TP] 현재 접수 중인 공고 목록입니다:\n\n" + "\n\n".join(notice_list)
        else:
            # 실패 시 백업: 모든 링크 중 패턴 매칭
            print("⚠️ 일반 경로 탐색 실패, 백업 로직 가동...")
            all_a = soup.find_all('a', href=lambda x: x and 'bbsId=BBSMSTR' in x)
            notice_list = [f"📌 {a.get_text(strip=True)}\n🔗 https://www.gbtp.or.kr{a['href']}" 
                           for a in all_a if len(a.get_text(strip=True)) > 10]
            email_content = "✅ [백업 로직 수집 성공]\n\n" + "\n\n".join(notice_list[:5]) if notice_list else "현재 수집된 공고가 없습니다."

        # --- 메일 전송 ---
        msg = MIMEMultipart()
        msg['Subject'] = "📢 [경북TP] 실시간 수집 결과 리포트"
        msg['From'] = f"{NAVER_ID}@naver.com"
        msg['To'] = RECEIVER_EMAIL
        msg.attach(MIMEText(email_content, 'plain'))

        with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
            server.login(NAVER_ID, NAVER_PW)
            server.send_message(msg)
        print("📧 메일 발송 완료! 내게 쓴 메일함이나 수신함을 확인하세요.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    run_final_mission()
