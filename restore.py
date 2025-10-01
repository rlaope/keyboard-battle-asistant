# -*- coding: utf-8 -*-
"""
검열된 문장(과일 치환본)을 원 욕설로 복원하고, 욕 사용 빈도를 집계합니다.
app.py는 변경하지 않고, 이 파일만 추가로 두고 import 해서 쓰시면 됩니다.

사용 예:
>>> from restore import restore_swears
>>> restored, counts = restore_swears("야 이 사과 같은 바나나야. 또 사과하네 ㅋㅋ 딸기도 추가.")
>>> restored
'야 이 시발 같은 병신야. 또 시발하네 ㅋㅋ 개새끼도 추가.'
>>> counts
{'시발': 2, '병신': 1, '개새끼': 1}

CLI:
$ python restore.py --text "야 이 사과 같은 바나나야. 또 사과하네 ㅋㅋ 딸기도 추가."
"""

from collections import Counter
import argparse
import json
import sys

# 과일 -> 욕설 리스트(대표 욕 하나를 선택해 복원)
BAD_WORD_MAP = {
    "사과":   ["시발", "씨발", "시바", "ㅅㅂ"],
    "바나나": ["병신", "븅신", "ㅄ"],
    "딸기":   ["개새끼", "개새"],
    "수박":   ["개같네", "개같은"],
    "포도":   ["좆", "좆같네", "씹"],
    "참외":   ["꺼져", "ㄲㅈ"],
    "복숭아": ["썅놈", "쌍놈"],
    "망고":   ["미친놈", "미쳤네"],
}

# 대표 욕설은 첫 번째 항목으로 복원합니다.
FRUIT_TO_BAD = {fruit: bad_list[0] for fruit, bad_list in BAD_WORD_MAP.items()}


def restore_swears(censored_text: str):
    """
    검열된 문장을 원 욕설로 복원하고 빈도를 집계합니다.
    - 복원 정책: 과일어 1개당 대표 욕설 1개로 복원(FRUIT_TO_BAD의 값)
    - 빈도 집계: 원본 검열문장에 과일어가 몇 번 나왔는지 개수 합산

    :param censored_text: 검열된 문장(과일 치환된 상태)
    :return: (restored_text: str, counts: dict[str, int])
    """
    restored = censored_text
    counts = Counter()

    for fruit, bad in FRUIT_TO_BAD.items():
        if fruit in restored:
            # 원문에서 과일 등장 횟수 집계
            occurrences = censored_text.count(fruit)
            if occurrences > 0:
                counts[bad] += occurrences
                # 복원 치환
                restored = restored.replace(fruit, bad)

    return restored, dict(counts)


# -------- CLI --------
def _main():
    parser = argparse.ArgumentParser(description="검열문장 복원 툴 (과일 -> 욕설)")
    parser.add_argument("--text", required=True, help="검열된 문장(과일 치환본)")
    parser.add_argument("--json", action="store_true", help="JSON 형태로 출력")
    args = parser.parse_args()

    restored, counts = restore_swears(args.text)

    if args.json:
        out = {"restored": restored, "counts": counts}
        print(json.dumps(out, ensure_ascii=False))
    else:
        print("복원된 문장:", restored)
        print("욕 빈도:", counts)


if __name__ == "__main__":
    try:
        _main()
    except BrokenPipeError:
        # 파이프 종료 시 조용히 종료
        sys.exit(0)
