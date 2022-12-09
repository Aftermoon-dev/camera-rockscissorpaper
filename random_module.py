import random

def computerResult():
    # 가위바위보 리스트
    result_list = ["rock", "scissor", "paper"] 

    # 랜덤 생성
    rand = random.randint(0,2)

    # 가위바위보 결과 반환
    return result_list[rand] 

result = computerResult()
print(result)