import random

# 컴퓨터 랜덤 가위바위보 생성
def computerResult():
    # 가위바위보 리스트
    result_list = ["rock", "scissor", "paper"] 

    # 랜덤 생성
    rand = random.randint(0,2)

    # 가위바위보 결과 반환
    return result_list[rand] 


# 사람 가위바위보랑 컴퓨터 가위바위보 비교
def compareResult():

    # 사람 가위바위보 받기
    pResult = "rock" # (임의)

    # 컴퓨터 가위바위보 받기
    cResult = computerResult()

    # 승패 판단 --> -1: 짐, 0: 비김, 1: 이김
    result : int

    if pResult == cResult: # 비긴 경우
        result = 0
    else: 
        if pResult == "rock": # 사람이 바위
            if cResult == "scissor":
                result = 1
            else:
                result = -1
        elif pResult == "scissor": # 사람이 가위
            if cResult == "paper":
                result = 1
            else:
                result = -1
        else: # 사람이 보
            if cResult == "rock":
                result = 1
            else:
                result = -1

    if result == 0:
        resultString = "비겼습니다!"
    elif result == 1:
        resultString = "이겼습니다!"
    else:
        resultString = "졌습니다!"

    # 결과 확인
    print("YOU: {}, COMPUTER: {}\n{}" .format(pResult, cResult, resultString))

    # 가위바위보 승패 결과 반환
    return result

compareResult()
