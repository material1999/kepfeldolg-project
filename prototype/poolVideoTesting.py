import sys
import numpy as np
import cv2

# in vs code for pylint: pylint --generate-rcfile > .pylintrc

#FUNCTIONS

def find_circles(frame):
    return cv2.HoughCircles(
            frame, cv2.HOUGH_GRADIENT, 1.2, 10, param1=100, param2=30, minRadius=5, maxRadius=30)

def draw_circles(circles, frame):
    if circles is not None:
        detected_circles = np.uint16(np.around(circles))
        for (x, y, r) in detected_circles[0, :]:
            cv2.circle(frame, (x, y), r, (0, 0, 0), 3)
            cv2.circle(frame, (x, y), 2, (0, 255, 255), 3)

def transform_frame(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    return gray_frame
    
#MAIN

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

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            break

        # Our operations on the frame come here
        
        #hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        
        #blured_grey_frame= cv2.GaussianBlur(gray_frame, (7, 7), 0)
        
        # reds
        dark_red = (0, 0, 120)
        light_red = (50, 50, 255)
        red_mask = cv2.inRange(frame, dark_red, light_red)
        
        red_masked_frame = cv2.bitwise_and(frame, frame, mask=red_mask)
        
        gray_masked_frame = cv2.cvtColor(red_masked_frame, cv2.COLOR_BGR2GRAY)
        blur_masked_frame = cv2.GaussianBlur(gray_masked_frame, (13, 13), 0)
        
        #sharpen
        #kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        #sharepened_frame = cv2.filter2D(blur_frame, -1, kernel)

        gray_frame=transform_frame(frame)
        
        circles = find_circles(gray_frame)

        draw_circles(circles, frame)

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
