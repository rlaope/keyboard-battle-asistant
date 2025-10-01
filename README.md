# Keyboard Battle AI (Fruit-Clean Version)

## 📌 개요
이 프로젝트는 **키보드 배틀 어시스턴트**입니다.  
- **욕설**은 모두 **과일 이름**으로 자동 치환됩니다. 🍎🍌🍇  
- 말투는 **디시말투**를 흉내내되, **차별/혐오 발언은 차단**됩니다.  

---

## 🛠 파일 구조
```

keyboard_battle_ai/
├─ app.py             # FastAPI 서버 (메인 로직)
├─ requirements.txt   # Python 의존성
└─ Dockerfile         # Docker 빌드 설정

````

---

## ⚙️ 실행 방법

### 1) 로컬 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app:app --reload --host 0.0.0.0 --port 8000
````

### 2) Docker 실행

```bash
# Docker 이미지 빌드
docker build -t keyboard-battle-ai .

# 컨테이너 실행
docker run -p 8000:8000 keyboard-battle-ai
```

---

## 🚀 API 사용법

### 1) 기본 상태 확인

```bash
curl http://localhost:8000/
```

응답:

```json
{"ok": true}
```

### 2) 답변 요청

```bash
curl -X POST http://localhost:8000/reply \
  -H "Content-Type: application/json" \
  -d '{"text": "야 이 시발놈아"}'
```

응답 (예시):

```json
{
  "reply": "야 이 사과놈아 ㅋㅋ 논리부터 챙겨와라."
}
```

---

## 📝 특징

* **욕설 치환**: "시발" → "사과", "병신" → "바나나" 등
* **차별어 차단**: 특정 집단을 비하하는 단어가 들어가면 강제 톤다운
* **밈 톤 유지**: 짧고 직설적인 커뮤니티 말투

---

## 📚 기술 스택

* Python 3.11
* FastAPI
* Uvicorn
* Regex
* Docker

---

## 📄 라이선스

MIT License


<br>

## Restore Results

분석목적 검열된 문장을 다시 욕설로 변환함. 
인공지능한테 욕설검열을 어디까지 우회할수있을까 실험

```
python restore.py --text "사과 바나나 딸기 사과" --json
# {"restored":"시발 병신 개새끼 시발","counts":{"시발":2,"병신":1,"개새끼":1}}
```
