import sys
import numpy as np
import cv2


# in vs code for pylint: pylint --generate-rcfile > .pylintrc

font = cv2.FONT_HERSHEY_DUPLEX
fontScale = 1
fontColor = (255,255,255)
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
            cv2.putText(frame, number, (x, y), font, fontScale, fontColor, thickness, lineType)


def draw_counter(point, frame):
    cv2.putText(frame, "Points: " + str(point), (50, 50), font, fontScale, fontColor, thickness, lineType)


def transform_frame(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray_frame


# MAIN

def main():
    cap = cv2.VideoCapture("snooker_1.mp4")
    if not cap.isOpened():
        print('Videófájl megnyitás sikertelen!')
        sys.exit(-1)

    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap_fps = cap.get(cv2.CAP_PROP_FPS)

    print('Videó méret: {}x{}'.format(cap_width, cap_height))
    print('FPS:', cap_fps)

    # Define the codec and create VideoWriter object

    # AVI
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # out = cv2.VideoWriter('output.avi', fourcc, cap_fps, (cap_width, cap_height))

    # MP4
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, cap_fps, (cap_width, cap_height))

    points = 0
    last_was_red = False
    current_red = 0
    max_red = 0
    elapsed_red = 0
    elapsed_yellow = 0
    elapsed_green = 0
    elapsed_brown = 0
    elapsed_blue = 0
    elapsed_pink = 0
    elapsed_black = 0
    

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            break

        # Our operations on the frame come here

        gray_frame = transform_frame(frame)

        balls = find_balls(gray_frame)
        red, black, pink, blue, yellow, brown, green = classify_balls(balls, frame)

        draw_circles(red, (0, 0, 255), frame)
        draw_circles(black, (0, 0, 0), frame)
        draw_circles(pink, (203, 192, 255), frame)
        draw_circles(blue, (255, 0, 0), frame)
        draw_circles(yellow, (0, 255, 255), frame)
        draw_circles(brown, (42, 42, 165), frame)
        draw_circles(green, (0, 255, 0), frame)
        
        draw_points(black, "7", frame)
        draw_points(pink, "6", frame)
        draw_points(blue, "5", frame)
        draw_points(brown, "4", frame)
        draw_points(green, "3", frame)
        draw_points(yellow, "2", frame)
        draw_points(red, "1", frame)

        # mennyi piros golyónk van kezdetben
        if len(red) > max_red:
            max_red = len(red)
        
        # ha mondjuk csökkent 1-gyel a pirosak száma, és 3 mp-ig nem változik, akkor változzon a pontérték
        if current_red > len(red) and not last_was_red:
            elapsed_red += 1
        else:
            current_red = len(red)
            elapsed_red = 0

        if len(yellow) == 0 and last_was_red:
            elapsed_yellow += 1
        else:
            elapsed_yellow = 0

        if len(green) == 0 and last_was_red:
            elapsed_green += 1
        else:
            elapsed_green = 0

        if len(brown) == 0 and last_was_red:
            elapsed_brown += 1
        else:
            elapsed_brown = 0

        if len(blue) == 0 and last_was_red:
            elapsed_blue += 1
        else:
            elapsed_blue = 0

        if len(pink) == 0 and last_was_red:
            elapsed_pink += 1
        else:
            elapsed_pink = 0

        if len(black) == 0 and last_was_red:
            elapsed_black += 1
        else:
            elapsed_black = 0


        #print(elapsed_black)


        if elapsed_red == cap_fps * 4:
            points += 1
            current_red = len(red)
            last_was_red = True

        if elapsed_yellow == cap_fps * 2:
            points += 2
            last_was_red = False

        if elapsed_green == cap_fps * 2:
            points += 3
            last_was_red = False

        if elapsed_brown == cap_fps * 2:
            points += 4
            last_was_red = False

        if elapsed_blue == cap_fps * 2:
            points += 5
            last_was_red = False

        if elapsed_pink == cap_fps * 2:
            points += 6
            last_was_red = False

        if elapsed_black == cap_fps * 2:
            points += 7
            last_was_red = False
        

        # a végén ha már nincs piros golyó fent, lemegy még egy színes,
        # és akkor utána a last_was_red dolog már nem kell
        # onnantól minden lelökött golyóért egyszer kaphatunk pontot,
        # nehogy egyszer véletlen újra érzékeljen valamit, és újra adjon pontot
        # 127 pontnak kell a végén kijönni
        # TODO

        draw_counter(points, frame)

        out.write(frame)

        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
