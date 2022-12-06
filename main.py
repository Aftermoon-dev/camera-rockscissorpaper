import sys
import cv2
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
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

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
