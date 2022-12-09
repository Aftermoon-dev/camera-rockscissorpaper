import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic

# UI File 불러오기
ui_file = uic.loadUiType("rockscissorpaper.ui")[0]


# UI 관련 처리
class WindowClass(QMainWindow, ui_file):
    def __init__(self):
        super().__init__()

        # Window 기본 설정
        self.setupUi(self)
        self.setWindowTitle("Rock-Scissor-Paper!")

        self.initUI()

    def initUI(self):
        # 카메라 쓰레드 생성
        camThread = CameraThread(self)
        # Thread의 함수 변화 값에 따라 setImage 함수 호출하도록 연결
        camThread.changePixelMap.connect(self.setImage)

        # 쓰레드 시작
        camThread.start()

    # pyqtSlot을 이용해 외부 값을 받아들일 수 있도록 설정
    @pyqtSlot(QPixmap)
    def setImage(self, image):
        # 영상을 배치할 Label에 Pixmap 형태의 Image 파일 설정
        self.camPlayer.setPixmap(image)


# 한개의 손만 인식
max_num_hands = 1

# 11개의 제스쳐 데이터 
gesture = {
    0:'fist', 1:'one', 2:'two', 3:'three', 4:'four', 5:'five',
    6:'six', 7:'rock', 8:'spiderman', 9:'yeah', 10:'ok',
}

# 가위바위보 매칭
rps_gesture = {0:'rock', 5:'paper', 9:'scissors'}

# MediaPipe로 손 인식
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=max_num_hands,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

# 제스쳐 인식 모델
file = np.genfromtxt('data/gesture_train.csv', delimiter=',')
angle = file[:,:-1].astype(np.float32)
label = file[:, -1].astype(np.float32)
knn = cv2.ml.KNearest_create()
knn.train(angle, cv2.ml.ROW_SAMPLE, label)



# 카메라 쓰레드
class CameraThread(QThread):
    # pyqtSignal을 이용하여 변경 사항을 보낼 수 있는 변수 정의
    changePixelMap = pyqtSignal(QPixmap)

    def run(self):
        # Video Capture
        capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        while True:
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
                        v1 = joint[[0,1,2,3,0,5,6,7,0,9,10,11,0,13,14,15,0,17,18,19],:] # 관절1
                        v2 = joint[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],:] # 관절2
                        v = v2 - v1 # [20,3]

                        # v 정규화 - 크기 1짜리 벡터
                        v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]
                        
                        # 각도 구하기
                        angle = np.arccos(np.einsum('nt,nt->n',
                            v[[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18],:], 
                            v[[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19],:])) # [15,]
                        
                        angle = np.degrees(angle) # 라디안을 각도로 변환

                        # 제스쳐 추론하기
                        data = np.array([angle], dtype=np.float32)
                        ret, results, neighbours, dist = knn.findNearest(data, 3)
                        idx = int(results[0][0])
                        
                        # 제스쳐 결과 
                        if idx in rps_gesture.keys():
                            cv2.putText(img, text=rps_gesture[idx].upper(), org=(int(res.landmark[0].x * img.shape[1]), int(res.landmark[0].y * img.shape[0] + 20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)

                        mp_drawing.draw_landmarks(img, res, mp_hands.HAND_CONNECTIONS)

                # 이미지 크기 설정
                h, w, c = img.shape

                # QImage 형태로 변경
                qImg = QImage(img.data, w, h, w * c, QImage.Format_RGB888)

                # QImage에서 GUI에 띄울 수 있는 QPixmap 형태로 변환
                pixmap = QPixmap.fromImage(qImg)

                # pyqtSignal로 QPixmap 형태로 변환된 카메라 프레임 보내기
                self.changePixelMap.emit(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = WindowClass()
    mainWindow.show()
    sys.exit(app.exec_())
