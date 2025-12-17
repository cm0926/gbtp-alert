import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- [1. 정보 설정] ---
NAVER_ID = "cm2407"
NAVER_PW = "BGBKWDZEFKP5"
RECEIVER_EMAIL = "cm2407@naver.com"

def run_final_mission():
    print("🚀 경북테크노파크 데이터 서버 직접 타격 시작...")
    
    # 캡처 화면의 데이터가 실제로 오가는 통로 (POST 방식 주소)
    url = "https://www.gbtp.or.kr/user/board/list?menu=231"
    
    # 서버에 보낼 '접수중' 검색 조건 데이터
    payload = {
        'bbsId': 'BBSMSTR_000000000021',
        'searchTerm': 'ing',
        'searchCondition': '1'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Origin': 'https://www.gbtp.or.kr',
        'Referer': 'https://www.gbtp.or.kr/user/board/list?menu=231'
    }
    
    try:
        # POST 방식으로 '접수중'인 공고만 요청
        res = requests.post(url, data=payload, headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 15151513.jpg 화면의 표 구조를 정밀 조준
        rows = soup.select('table.table tbody tr')
        notice_list = []

        for row in rows:
            # 제목이 들어있는 'td.subject' 클래스를 찾습니다.
            title_tag = row.select_one('td.subject a')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = "https://www.gbtp.or.kr" + title_tag['href']
                
                # 접수 상태 확인 (빨간색 '접수중' 버튼 유무)
                status = row.select_one('.btn_red')
                status_text = status.get_text(strip=True) if status else "상태미상"
                
                notice_list.append(f"✅ [{status_text}] {title}\n🔗 {link}")

        # --- 메일 내용 구성 ---
        if notice_list:
            print(f"🎯 수집 대성공! {len(notice_list)}개의 공고를 찾았습니다.")
            content = "🔥 [성공] 경북TP 현재 접수 중인 공고 리스트입니다:\n\n" + "\n\n".join(notice_list)
        else:
            print("❌ 구조 분석 재시도 중...")
            # 비상용: 모든 a 태그 중 공고 패턴 수집
            all_a = soup.find_all('a', href=lambda x: x and 'bbsId=BBSMSTR' in x)
            notice_list = [f"📌 {a.get_text(strip=True)}\n🔗 https://www.gbtp.or.kr{a['href']}" for a in all_a if len(a.get_text(strip=True)) > 10]
            content = "✅ [백업 로직] 수집된 공고입니다:\n\n" + "\n\n".join(notice_list[:5]) if notice_list else "현재 수집 가능한 공고가 없습니다."

        # --- 메일 전송 (이 부분은 이미 검증됨) ---
        msg = MIMEMultipart()
        msg['Subject'] = "📢 [경북TP] 실시간 공고 수집 리포트"
        msg['From'] = f"{NAVER_ID}@naver.com"
        msg['To'] = RECEIVER_EMAIL
        msg.attach(MIMEText(content, 'plain'))

        with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
            server.login(NAVER_ID, NAVER_PW)
            server.send_message(msg)
        print("📧 메일함 확인해 주세요! 전송 완료!")

    except Exception as e:
        print(f"❌ 시스템 오류: {e}")

if __name__ == "__main__":
    run_final_mission()
