import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
import random_module
import time

# UI File 불러오기
ui_file = uic.loadUiType("rockscissorpaper.ui")[0]


# UI 관련 처리
class WindowClass(QMainWindow, ui_file):
    def __init__(self):
        super().__init__()

        # Window 기본 설정
        self.setupUi(self)
        self.setWindowTitle("Rock-Scissor-Paper!")

        # Computer 결과 관련 이미지
        self.computerResultImg = QPixmap()
        self.computerResultImg.load("images/empty.png")
        self.computerResultImg = self.computerResultImg.scaledToWidth(350)
        self.computerResultImg = self.computerResultImg.scaledToHeight(350)

        self.rockImg = QPixmap()
        self.rockImg.load("images/rock.png")
        self.rockImg = self.rockImg.scaledToWidth(350)
        self.rockImg = self.rockImg.scaledToHeight(350)
        self.scissorImg = QPixmap()
        self.scissorImg.load("images/scissor.png")
        self.scissorImg = self.scissorImg.scaledToWidth(350)
        self.scissorImg = self.scissorImg.scaledToHeight(350)
        self.paperImg = QPixmap()
        self.paperImg.load("images/paper.png")
        self.paperImg = self.paperImg.scaledToWidth(350)
        self.paperImg = self.paperImg.scaledToHeight(350)

        # 최종 결과 관련 이미지
        self.humanWinImg = QPixmap()
        self.humanWinImg.load("images/win.png")
        self.humanWinImg = self.humanWinImg.scaledToWidth(620)
        self.humanWinImg = self.humanWinImg.scaledToHeight(90)
        self.humanDrawImg = QPixmap()
        self.humanDrawImg.load("images/draw.png")
        self.humanDrawImg = self.humanDrawImg.scaledToWidth(620)
        self.humanDrawImg = self.humanDrawImg.scaledToHeight(90)
        self.humanLoseImg = QPixmap()
        self.humanLoseImg.load("images/lose.png")
        self.humanLoseImg = self.humanLoseImg.scaledToWidth(620)
        self.humanLoseImg = self.humanLoseImg.scaledToHeight(90)

        # 초기 이미지 설정
        self.loadInitialImage()

        self.initUI()

    def initUI(self):
        # 카메라 쓰레드 생성
        camThread = CameraThread(self)
        # Thread의 함수 변화 값에 따라 setImage 함수 호출하도록 연결
        camThread.changePixelMap.connect(self.setImage)

        # 쓰레드 시작
        camThread.start()

    # pyqtSlot을 이용해 외부 값을 받아들일 수 있도록 설정
    @pyqtSlot(QPixmap, str, int)
    def setImage(self, image, uiComputerResult, uiGameResult):
        # 영상을 배치할 Label에 Pixmap 형태의 Image 파일 설정
        self.humanCamera.setPixmap(image)

        # uiComputerResult 결과에 따라 ui 적용 함수 연결
        if uiComputerResult == "ROCK":
            self.rock()
        elif uiComputerResult == "SCISSOR":
            self.scissor()
        elif uiComputerResult == "PAPER":
            self.paper()
        else:
            self.loadInitialImage()

        # uiGameResult 결과에 따라 ui 적용 함수 연결
        if uiGameResult == 1:
            self.win()
        elif uiGameResult == 0:
            self.draw()
        elif uiGameResult == -1:
            self.lose()
        else:
            self.loadInitialImage()

    # Computer의 결과를 ui에 띄우기 위한 코드
    def loadInitialImage(self):
        self.computerResult.setPixmap(self.computerResultImg)

    def rock(self):
        self.computerResult.setPixmap(self.rockImg)

    def scissor(self):
        self.computerResult.setPixmap(self.scissorImg)

    def paper(self):
        self.computerResult.setPixmap(self.paperImg)

    # 최종 결과에 따른 사람의 승패 결과 ui 적용
    def win(self):
        self.result.setPixmap(self.humanWinImg)

    def draw(self):
        self.result.setPixmap(self.humanDrawImg)

    def lose(self):
        self.result.setPixmap(self.humanLoseImg)


# 한개의 손만 인식
max_num_hands = 1

# 11개의 제스쳐 데이터 
gesture = {
    0: 'fist', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
    6: 'six', 7: 'rock', 8: 'spiderman', 9: 'yeah', 10: 'ok',
}

# 가위바위보 매칭
rps_gesture = {0: 'ROCK', 5: 'PAPER', 9: 'SCISSOR'}

# MediaPipe로 손 인식
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=max_num_hands,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

# 제스쳐 인식 모델
file = np.genfromtxt('data/gesture_train.csv', delimiter=',')
angle = file[:, :-1].astype(np.float32)
label = file[:, -1].astype(np.float32)
knn = cv2.ml.KNearest_create()
knn.train(angle, cv2.ml.ROW_SAMPLE, label)


# 카메라 쓰레드
class CameraThread(QThread):
    # pyqtSignal을 이용하여 변경 사항을 보낼 수 있는 변수 정의
    changePixelMap = pyqtSignal(QPixmap, str, int)

    def run(self):
        global humanFinalResult
        global computerFinalResult
        global gameFinalResult

        # Video Capture
        capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        while True:
            humanFinalResult = None
            computerFinalResult = None
            gameFinalResult = None

            # Video 읽기
            ret, frame = capture.read()

            # 정상적으로 Video가 넘어온 경우
            if ret:
                # BGR에서 RGB 형태로 이미지 변경
                img = cv2.flip(frame, 1)
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = hands.process(frame)
                img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                if result.multi_hand_landmarks is not None:
                    for res in result.multi_hand_landmarks:
                        joint = np.zeros((21, 3))
                        for j, lm in enumerate(res.landmark):
                            joint[j] = [lm.x, lm.y, lm.z]

                        # 손가락 관절 각도 비교
                        v1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 0, 13, 14, 15, 0, 17, 18, 19], :]  # 관절1
                        v2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], :]  # 관절2
                        v = v2 - v1  # [20,3]

                        # v 정규화 - 크기 1짜리 벡터
                        v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

                        # 각도 구하기
                        angle = np.arccos(np.einsum('nt,nt->n',
                                                    v[[0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18], :],
                                                    v[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19],
                                                    :]))  # [15,]

                        angle = np.degrees(angle)  # 라디안을 각도로 변환

                        # 제스쳐 추론하기
                        data = np.array([angle], dtype=np.float32)
                        ret, results, neighbours, dist = knn.findNearest(data, 3)
                        idx = int(results[0][0])

                        # 제스쳐 결과
                        if idx in rps_gesture.keys():
                            # 사람의 가위바위보 결과
                            result = rps_gesture[idx]
                            cv2.putText(img, text=result, org=(
                                int(res.landmark[0].x * img.shape[1]), int(res.landmark[0].y * img.shape[0] + 20)),
                                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255),
                                        thickness=2)
                            # random_module 을 이용해 computer의 랜덤 결과를 불러옴 + 사람의 결과를 보냄
                            # 이를 통해 결과 Return
                            finalResult = random_module.compareResult(result)

                            # 사람, 컴퓨터, 게임의 총 결과를 변수에 저장
                            humanFinalResult = finalResult[0]
                            computerFinalResult = finalResult[1]
                            gameFinalResult = finalResult[2]

                        mp_drawing.draw_landmarks(img, res, mp_hands.HAND_CONNECTIONS)

                # 이미지 크기 설정
                h, w, c = img.shape

                # QImage 형태로 변경
                qImg = QImage(img.data, w, h, w * c, QImage.Format_RGB888)

                # QImage에서 GUI에 띄울 수 있는 QPixmap 형태로 변환
                pixmap = QPixmap.fromImage(qImg)

                # pyqtSignal로 QPixmap 형태로 변환된 카메라 프레임 보내기
                # ComputerResult 및 GameResult 전달
                self.changePixelMap.emit(pixmap, computerFinalResult, gameFinalResult)

                if gameFinalResult != None:
                    time.sleep(3)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = WindowClass()
    mainWindow.show()
    sys.exit(app.exec_())
