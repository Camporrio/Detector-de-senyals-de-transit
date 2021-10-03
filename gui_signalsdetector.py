from tkinter import *
from PIL import ImageTk, Image
import os
import glob
import cv2

def gui_cicle():
    root = Tk()
    root.title('Detector de senyals de trànsit')

    mypathOrientacio = ".\hsv\*OrientacioBlue.jpg"
    mypathIndicacio = ".\hsv\*IndicacioBlue.jpg"
    mypathWhite = ".\hsv\*WhiteOrientacio.jpg"
    mypathdefault = "default.png"

    imagedefault = cv2.imread("default.png",cv2.IMREAD_UNCHANGED)

    cv2.imwrite("hsv/0_OrientacioBlue.jpg", imagedefault)
    cv2.imwrite("hsv/0_IndicacioBlue.jpg", imagedefault)
    cv2.imwrite("hsv/0_WhiteOrientacio.jpg", imagedefault)

    gui_orientacioblue = ImageTk.PhotoImage(Image.open(mypathdefault))
    gui_indicacioblue = ImageTk.PhotoImage(Image.open(mypathdefault))
    gui_white = ImageTk.PhotoImage(Image.open(mypathdefault))

    label_orientacioblue = Label(root, image = gui_orientacioblue)
    label_orientacioblue.grid(row=0,column=0,rowspan=2)
    label_indicacioblue= Label(root, image = gui_indicacioblue)
    label_indicacioblue.grid(row=0,column=1)
    label_white = Label(root, image = gui_white)
    label_white.grid(row=1,column=1)

    def updater():
        
        lastorientacio = max(glob.glob(mypathOrientacio), key=os.path.getmtime)
        lastindicacio = max(glob.glob(mypathIndicacio), key=os.path.getmtime)
        lastwhite =  max(glob.glob(mypathWhite), key=os.path.getmtime)

        gui_orientacioblue = ImageTk.PhotoImage(Image.open(lastorientacio))
        gui_indicacioblue = ImageTk.PhotoImage(Image.open(lastindicacio))
        gui_white = ImageTk.PhotoImage(Image.open(lastwhite))

        print("GUI -> mostrant: " + lastorientacio)
        print("GUI -> mostrant: " + lastindicacio)
        print("GUI -> mostrant: " + lastwhite)

        label_orientacioblue.configure(image = gui_orientacioblue)
        label_indicacioblue.configure(image = gui_indicacioblue)
        label_white.configure(image = gui_white)
        label_orientacioblue.image = gui_orientacioblue
        label_indicacioblue.image = gui_indicacioblue
        label_white.image = gui_white

        root.after(4000, updater)

    updater()


    root.mainloop()