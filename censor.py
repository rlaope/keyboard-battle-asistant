from collections import Counter

BAD_WORD_MAP = {
    "사과": ["시발", "씨발", "시바", "ㅅㅂ"],
    "바나나": ["병신", "븅신", "ㅄ"],
    "딸기": ["개새끼", "개새"],
    "수박": ["개같네", "개같은"],
    "포도": ["좆", "좆같네", "씹"],
    "참외": ["꺼져", "ㄲㅈ"],
    "복숭아": ["썅놈", "쌍놈"],
    "망고": ["미친놈", "미쳤네"],
    "악마의열매": ["김희망", "희僖망이", "케이홉", "행복맨", "행복희망", "가재맨"],
}

FRUIT_TO_BAD = {fruit: bad_list[0] for fruit, bad_list in BAD_WORD_MAP.items()}

def restore_swears(censored_text: str):
    """검열된 문장을 욕설로 복원하고 빈도 카운트"""
    restored = censored_text
    counts = Counter()
    for fruit, bad_word in FRUIT_TO_BAD.items():
        if fruit in restored:
            restored = restored.replace(fruit, bad_word)
            counts[bad_word] += censored_text.count(fruit)
    return restored, counts
