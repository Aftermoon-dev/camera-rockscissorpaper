import random


# 컴퓨터 랜덤 가위바위보 생성
def computerResult():
    # 가위바위보 리스트
    result_list = ["ROCK", "SCISSOR", "PAPER"]

    # 랜덤 생성
    rand = random.randint(0, 2)

    # 가위바위보 결과 반환
    return result_list[rand]


# 사람 가위바위보랑 컴퓨터 가위바위보 비교
def compareResult(pResult):
    # 컴퓨터 가위바위보 받기
    cResult = computerResult()

    # 승패 판단 --> -1: 짐, 0: 비김, 1: 이김
    result: int

    if pResult == cResult:  # 비긴 경우
        result = 0
    else:
        if pResult == "ROCK":  # 사람이 바위
            if cResult == "SCISSOR":
                result = 1
            else:
                result = -1
        elif pResult == "SCISSOR":  # 사람이 가위
            if cResult == "PAPER":
                result = 1
            else:
                result = -1
        else:  # 사람이 보
            if cResult == "ROCK":
                result = 1
            else:
                result = -1

    finalResult = [pResult, cResult, result]
    print(f"Human = {pResult} / Computer = {cResult} / result = {result}")

    # 가위바위보 승패 결과 반환
    return finalResult
