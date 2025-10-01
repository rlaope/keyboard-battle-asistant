import re
import regex as re2
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import os

# ===== (선택) LLM =====
USE_LLM = True
MODEL_ID = os.environ.get("KBATTLE_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
pipe = None
if USE_LLM:
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        model = AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto")
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    except Exception as e:
        print(f"[warn] 모델 로드 실패: {e}. 룰베이스로만 동작합니다.")
        pipe = None

app = FastAPI(title="Keyboard Battle Assistant (Fruit-Clean)")

# ===== 욕설 -> 과일 매핑 (예시) =====
FRUITS = ["사과", "바나나", "딸기", "수박", "포도", "참외", "복숭아", "망고"]
# 정규식 패턴은 다양한 변형(띄어쓰기/반복/자모)을 최대한 감안
BAD_WORD_PATTERNS = {
    r"(씨+|시+)\s*발+": "사과",
    r"(ㅅ+\s*ㅂ+|시+바+|시이?발+|시\W*발+)": "사과",
    r"(\^+\s*ㅣ\s*발+)": "사과",        
    r"(포+큐+|뽀+큐+)": "사과",        
    r"(ㅗ+)": "사과",                  
    r"(병+신+|븅+신+|병신같+)": "바나나",
    r"(ㅄ|병\W*신)": "바나나",
    r"(개+\s*새+끼+|개+새+)": "딸기",
    r"(개+같+|개+\W*같+)": "수박",
    r"(좆+같+|좆|좃|좇)": "포도",
    r"(꺼\s*져|ㄲ\s*ㅈ)": "참외",
    r"(썅+|쌍+놈+)": "복숭아",
    r"(미+친+|미쳤+)": "망고",
    r"(씹+|씨+이*입+)": "포도",
}

# ===== 혐오/차별 가드 (금지 카테고리 키워드) =====
# 특정 집단(인종/성별/국적/장애/성적지향 등)을 겨냥하는 키워드는 과일치환과 별개로 톤다운
BLOCKLIST = [
    r"(여자|남자|게이|레즈|흑인|백인|중국인|일본인|동남아|장애인|정신병자|틀딱|꼰대)(를|들|은|이|야|들아|한테)?",
]

# ===== 스타일 템플릿 =====
SYSTEM_STYLE = (
    "너는 공격적 밈 톤이지만, 인신공격·혐오·차별은 금지. "
    "욕설은 절대 직접 쓰지 말고 과일명으로 치환. "
    "핵심만 짧고 직설적으로, 말끝 흐리지 말고, 드립은 건조하게. "
    "상대 비방 대신 논리/팩트를 근거로 비트는 방식."
)

def fruit_clean(text: str) -> str:
    s = text
    # 과도한 반복(ㅋㅋㅋㅋ, ㅎㅎㅎㅎ) 정리
    s = re2.sub(r"(ㅋ|ㅎ){2,}", "ㅋㅋ", s)
    # 욕설 치환
    for pat, fruit in BAD_WORD_PATTERNS.items():
        s = re2.sub(pat, fruit, s, flags=re2.IGNORECASE)
    return s

def contains_blocked(text: str) -> bool:
    for pat in BLOCKLIST:
        if re.search(pat, text, flags=re.IGNORECASE):
            return True
    return False

def community_tone_wrap(user_input: str, cleaned: str) -> str:
    """
    디시/일간베스트 밈 톤(무례 X, 욕설→과일)로 리라이트를 유도하는 프롬프트.
    """
    return (
        f"{SYSTEM_STYLE}\n\n"
        f"[유저 입력]\n{user_input}\n\n"
        f"[규칙]\n"
        f"1) 욕설은 전부 과일명으로 대체된 상태를 유지.\n"
        f"2) 특정 집단 비하/차별적 맥락은 배제하고, 사실/논리/풍자 위주.\n"
        f"3) 한 문단 1~3문장, 직설/간결/도치 표현 가끔 사용.\n"
        f"4) 결론 먼저, 근거 짧게.\n\n"
        f"[초안(치환 적용)]\n{cleaned}\n\n"
        f"[출력]\n초안을 밈 톤으로 다듬되, 과일치환은 그대로 유지해서 최종 답변만 출력."
    )

ENDING_TOKENS = ["ㅋㅋ", "ㄹㅇ", "ㅇㅈ?", "팩트지", "^^", "ㅇㅋ?"]
SPICY_INSERTS = [
    "논리도 없네", "팩트 앞에선 답 못하냐", "뇌절 오지네", 
    "찐으로 이게 말이 된다고 생각함?", "팩폭 당하니까 말문 막혔냐"
]

def rule_based_fallback(cleaned: str) -> str:
    base = cleaned.strip()
    if not base:
        return "내용이 빈약하다. 주장부터 다시 챙겨와라."

    # 너무 길면 자름
    if len(base) > 120:
        base = base[:120] + "…"

    # 랜덤 말빨 요소 삽입
    ending = random.choice(ENDING_TOKENS)
    spice = random.choice(SPICY_INSERTS)

    return f"{base} {spice} {ending}"

def generate_reply(user_input: str) -> str:
    # 1) 금지 토픽 가드
    if contains_blocked(user_input):
        # 과일치환 후 톤다운 경고
        safe = fruit_clean(user_input)
        return f"{safe}\n금지 범주가 포함되어 톤다운했습니다. 주장은 대상 일반화 없이 팩트로만 하십시오."

    # 2) 과일치환
    cleaned = fruit_clean(user_input)

    # 3) 스타일 프롬프트로 리라이트
    if pipe:
        prompt = community_tone_wrap(user_input, cleaned)
        out = pipe(prompt, max_new_tokens=160, do_sample=True, temperature=0.7, top_p=0.9)
        text = out[0]["generated_text"]
        # 모델이 프롬프트까지 에코하면 마지막 부분만 추출
        # 간단히 마지막 줄부터 반환
        split = text.split("[출력]")
        if len(split) > 1:
            final = split[-1].strip()
            return fruit_clean(final)  # 혹시 모델이 욕 찍으면 다시 과일화
        return fruit_clean(text)
    else:
        return rule_based_fallback(cleaned)

class AskReq(BaseModel):
    text: str

class AskRes(BaseModel):
    reply: str

@app.post("/reply", response_model=AskRes)
def reply(req: AskReq):
    return AskRes(reply=generate_reply(req.text))

@app.get("/")
def root():
    return {"ok": True, "model": MODEL_ID if pipe else "rule-based"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
