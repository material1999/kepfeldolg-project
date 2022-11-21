from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QMessageBox, QPushButton, QHBoxLayout, QVBoxLayout, QStyle, QSlider, QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QIcon, QPalette
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt, QMutex, QWaitCondition
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import cv2
import sys
import numpy as np

# CONSTANTS
font = cv2.FONT_HERSHEY_DUPLEX
fontScale = 1
fontColor = (255, 255, 255)
thickness = 2
lineType = 2

# FUNCTIONS


def find_balls(frame):
    return cv2.HoughCircles(
        frame, cv2.HOUGH_GRADIENT, 1.2, 10, param1=70, param2=15, minRadius=5, maxRadius=10)


def classify_balls(balls, frame):
    red, black, pink, blue, yellow, brown, green = ([] for i in range(7))

    if balls is None:
        return red, black, pink, blue, yellow, brown, green

    balls = np.uint16(np.around(balls))
    for ball in balls[0, :]:
        (x, y, r) = ball

        # Hibakezelés arra az esetre, ha a detektált "golyó" kilógna a képből
        x = int(x)
        y = int(y)
        r = int(r)
        if x - r < 0 or x + r + 1 > frame.shape[1] or y - r < 0 or y + r + 1 > frame.shape[0]:
            continue

        # Kör formájú mask
        mask = np.zeros((2 * r + 1, 2 * r + 1), np.uint8)
        cv2.circle(mask, (r, r), r, 255, cv2.FILLED)

        # A kört befoglaló négyzet kivágása
        cropped_frame = frame[y - r:y + r + 1, x - r:x + r + 1]

        # Színek maskjai a kivágott képrészleten
        X = 15
        dark_red = (0, 0, 120)
        light_red = (50 + X, 50 + X, 255)
        red_mask = cv2.inRange(cropped_frame, dark_red, light_red)
        red_mask = cv2.bitwise_and(mask, red_mask)

        dark_black = (0, 0, 0)
        light_black = (15, 70, 15)
        black_mask = cv2.inRange(cropped_frame, dark_black, light_black)
        black_mask = cv2.bitwise_and(mask, black_mask)

        #dark_pink = (90, 140, 230)
        dark_pink = (90, 140, 255)
        #light_pink = (125 + X, 170 + X, 255)
        light_pink = (180 + X, 150 + X, 255)

        pink_mask = cv2.inRange(cropped_frame, dark_pink, light_pink)
        pink_mask = cv2.bitwise_and(mask, pink_mask)

        dark_blue = (110, 110, 0)
        light_blue = (160 + X, 130 + X, 15 + X)
        blue_mask = cv2.inRange(cropped_frame, dark_blue, light_blue)
        blue_mask = cv2.bitwise_and(mask, blue_mask)

        dark_yellow = (0, 200, 245)
        light_yellow = (30 + X, 255, 255)
        yellow_mask = cv2.inRange(cropped_frame, dark_yellow, light_yellow)
        yellow_mask = cv2.bitwise_and(mask, yellow_mask)

        dark_brown = (0, 90, 90)
        light_brown = (15 + X, 95 + X, 140 + X)
        brown_mask = cv2.inRange(cropped_frame, dark_brown, light_brown)
        brown_mask = cv2.bitwise_and(mask, brown_mask)

        dark_green = (50, 115, 0)
        light_green = (75 + X, 130 + X, 15 + X)
        green_mask = cv2.inRange(cropped_frame, dark_green, light_green)
        green_mask = cv2.bitwise_and(mask, green_mask)

        # Ha bizonyos számú pixel van az adott színből a detektált körben, akkor az adott szín listájához hozzáadódik
        MIN = 35
        if np.sum(red_mask == 255) > MIN:
            red.append(ball)
        elif np.sum(black_mask == 255) > MIN:
            black.append(ball)
        elif np.sum(pink_mask == 255) > MIN:
            pink.append(ball)
        elif np.sum(blue_mask == 255) > MIN:
            blue.append(ball)
        elif np.sum(yellow_mask == 255) > MIN:
            yellow.append(ball)
        elif np.sum(brown_mask == 255) > MIN:
            brown.append(ball)
        elif np.sum(green_mask == 255) > MIN:
            green.append(ball)

    return red, black, pink, blue, yellow, brown, green


def draw_circles(circles, color, frame):
    if circles is not None:
        detected_circles = np.uint16(np.around(circles))
        for (x, y, r) in detected_circles:
            cv2.circle(frame, (x, y), r, color, 2)
            # cv2.circle(frame, (x, y), 2, (0, 255, 255), 3)


def draw_points(circles, number, frame):
    if circles is not None:
        detected_circles = np.uint16(np.around(circles))
        for (x, y, r) in detected_circles:
            cv2.putText(frame, number, (x, y), font, fontScale,
                        fontColor, thickness, lineType)


def draw_counter(point, frame):
    cv2.putText(frame, "Points: " + str(point), (50, 50), font,
                fontScale, fontColor, thickness, lineType)


def transform_frame(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray_frame

# GUI
# https://stackoverflow.com/questions/55306673/pyqt-crashes-when-trying-to-show-opencv-videostream
class VideoThread(QThread):
    changemap = pyqtSignal('QImage')

    def __init__(self, mutex, condition, video):
        super().__init__()
        self.mutex = mutex
        self.condition = condition
        self.video = video
        self.pause=False

        self.points = 0
        self.last_was_red = False
        self.current_red = 0
        self.elapsed_red = 0
        self.elapsed_yellow = 0
        self.elapsed_green = 0
        self.elapsed_brown = 0
        self.elapsed_blue = 0
        self.elapsed_pink = 0
        self.elapsed_black = 0

    def run(self):
        cap = cv2.VideoCapture("snooker_1.mp4")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap_fps = cap.get(cv2.CAP_PROP_FPS)
        while True:
            while self.pause:
                pass
            
            try:
                ret, img_rgb = cap.read()
                if ret:
                    # Our operations on the frame come here

                    gray_frame = transform_frame(img_rgb)

                    balls = find_balls(gray_frame)
                    red, black, pink, blue, yellow, brown, green = classify_balls(
                        balls, img_rgb)

                    draw_circles(red, (0, 0, 255), img_rgb)
                    draw_circles(black, (0, 0, 0), img_rgb)
                    draw_circles(pink, (203, 192, 255), img_rgb)
                    draw_circles(blue, (255, 0, 0), img_rgb)
                    draw_circles(yellow, (0, 255, 255), img_rgb)
                    draw_circles(brown, (42, 42, 165), img_rgb)
                    draw_circles(green, (0, 255, 0), img_rgb)

                    draw_points(black, "7", img_rgb)
                    draw_points(pink, "6", img_rgb)
                    draw_points(blue, "5", img_rgb)
                    draw_points(brown, "4", img_rgb)
                    draw_points(green, "3", img_rgb)
                    draw_points(yellow, "2", img_rgb)
                    draw_points(red, "1", img_rgb)

                    # ha mondjuk csökkent 1-gyel a pirosak száma, és 3 mp-ig nem változik, akkor változzon a pontérték
                    if self.current_red > len(red) and not self.last_was_red:
                        self.elapsed_red += 1
                    else:
                        self.current_red = len(red)
                        self.elapsed_red = 0

                    if len(yellow) == 0 and self.last_was_red:
                        self.elapsed_yellow += 1
                    else:
                        self.elapsed_yellow = 0

                    if len(green) == 0 and self.last_was_red:
                        self.elapsed_green += 1
                    else:
                        self.elapsed_green = 0

                    if len(brown) == 0 and self.last_was_red:
                        self.elapsed_brown += 1
                    else:
                        self.elapsed_brown = 0

                    if len(blue) == 0 and self.last_was_red:
                        self.elapsed_blue += 1
                    else:
                        self.elapsed_blue = 0

                    if len(pink) == 0 and self.last_was_red:
                        self.elapsed_pink += 1
                    else:
                        self.elapsed_pink = 0

                    if len(black) == 0 and self.last_was_red:
                        self.elapsed_black += 1
                    else:
                        self.elapsed_black = 0

                    if self.elapsed_red == cap_fps * 4:
                        self.points += 1
                        self.current_red = len(red)
                        self.last_was_red = True

                    if self.elapsed_yellow == cap_fps * 2:
                        self.points += 2
                        self.last_was_red = False

                    if self.elapsed_green == cap_fps * 2:
                        self.points += 3
                        self.last_was_red = False

                    if self.elapsed_brown == cap_fps * 2:
                        self.points += 4
                        self.last_was_red = False

                    if self.elapsed_blue == cap_fps * 2:
                        self.points += 5
                        self.last_was_red = False

                    if self.elapsed_pink == cap_fps * 2:
                        self.points += 6
                        self.last_was_red = False

                    if self.elapsed_black == cap_fps * 2:
                        self.points += 7
                        self.last_was_red = False

                    # a végén ha már nincs piros golyó fent, lemegy még egy színes,
                    # és akkor utána a last_was_red dolog már nem kell
                    # onnantól minden lelökött golyóért egyszer kaphatunk pontot,
                    # nehogy egyszer véletlen újra érzékeljen valamit, és újra adjon pontot
                    # 127 pontnak kell a végén kijönni
                    if self.current_red == 0:
                        self.last_was_red = True

                    draw_counter(self.points, img_rgb)

                    rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)

                    #any other image processing here

                    convert = QImage(
                        rgb.data, rgb.shape[1], rgb.shape[0], QImage.Format_RGB888)
                    p = convert.scaled(1280, 720, Qt.KeepAspectRatio)
                    self.changemap.emit(p)
                    self.condition.wait(self.mutex)

            except:
                print('error')
    def set_video(self, video):
        self.video=video
    
    def toggle_pause(self):
        self.pause=not self.pause


class App(QWidget):
    time = 0

    def __init__(self):
        super().__init__()
        self.title = "Pool score tracker"
        self.mutex = QMutex() 
        self.condition = QWaitCondition()
        self.initUI()

    @pyqtSlot('QImage')
    def setImage(self, image):
        self.mutex.lock()
        try:
            self.label.setPixmap(QPixmap.fromImage(image))
        finally:
            self.mutex.unlock()
            self.condition.wakeAll()

    def initUI(self):
        self.mutex.lock()
        self.setWindowIcon(QIcon("snooker_sport_icon.ico"))
        self.setWindowTitle("Pool score tracker")
        self.setGeometry(100, 100, 1280, 720)
        self.resize(1280, 720)
        self.label = QLabel(self)
        self.label.resize(1280, 720)
        
        self.vid_thr = VideoThread(mutex=self.mutex, condition=self.condition, video='')
        self.vid_thr.changemap.connect(self.setImage)

        self.openBtn = QPushButton('Open video')
        self.openBtn.clicked.connect(self.open_file)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.openBtn)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)

        hbox.addWidget(self.playBtn)

        # self.slider = QSlider(Qt.Horizontal)
        # self.slider.setRange(0, 0)
        # hbox.addWidget(self.slider)
        vbox.addWidget(self.label)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        
        if filename != '':
            if not self.vid_thr.isRunning():
                self.vid_thr.set_video(filename)
                self.playBtn.setEnabled(True)
            
    def play_video(self):
        if not self.vid_thr.isRunning():
            self.vid_thr.start()
        else:
            self.vid_thr.toggle_pause()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = App()
    win.show()
    app.exit(app.exec_())
