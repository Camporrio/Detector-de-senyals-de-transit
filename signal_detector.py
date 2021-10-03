import numpy as np
import cv2
from pathlib import Path
import pytesseract
from PIL import ImageTk, Image
from multiprocessing import Process
import gui_signalsdetector as gui

def extractImages(pathOut,pathHsv):
    #en funcio dels frames que volem agafar si son d'un video o de la camera comentem i descomentem un o altre
    #video
    vidcap = cv2.VideoCapture('carvideo_22Trim.mp4')
    #càmera
    #vidcap = cv2.VideoCapture(0)

    #Inicialitzem el contador que sencarrega de portar un control dels frames extrets
    count = 0
    #Llegim els frames del video
    success,image = vidcap.read()
    success = True
    framecount = 0
    while success:
        
        vidcap.set(cv2.CAP_PROP_POS_MSEC,framecount)
        success,image = vidcap.read()
        print ('Reading frame -- ' + str(count))
        # guardem els frames en format jpg
        cv2.imwrite(pathOut + "/" + str(count) + ".jpg" , image)
        #Cridem a la funcio que aplicara lalgorisme HSV al frame
        image_to_hsv(pathOut,pathHsv,count)

        count = count + 1
        framecount = framecount + 3000

def image_to_hsv(pathOut,pathHsv, contador):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    crop_white = None
    crop_blue_ind = None
    crop_blue_or = None
    count = str(contador)    
    notblue = False
    notwhite = False
    loop = True 
    loop2 = True
    #Per a fer servir els frames de la camara:
    image_hsv1 = cv2.imread(pathOut + "/" + count + ".jpg", cv2.IMREAD_UNCHANGED)

    
    #Per a fer servir frames que afegim manualment:
    #image_hsv1 = cv2.imread("16.jpg", cv2.IMREAD_UNCHANGED)

    image_hsv = cv2.fastNlMeansDenoising(image_hsv1, None, 15,7,21)
    image_hsv2 = cv2.medianBlur(image_hsv, 11)
    #Busquem la mida de la imatge
    height, width= image_hsv.shape[:2]

    #********************ROI***********************************
    # __________
    #|          |X
    #L_____     |X
    #XXXXXX|____|X
    #XXXXXXXXXXXXX

    ROI = np.array([[(0,height/2),(0,0),(width,0),(width,height-(height/4)),(width-(width/4),height-(height/4)),(width-(width/4),(height-(height/3))),(width/2, height-(height/3)),(width/2,height/2)]], dtype= np.int32)
    
    #*******************************************************
    
    #Proces per printar el ROI del frame
    blank= np.zeros_like(image_hsv)
    regofint = cv2.fillPoly(blank, ROI, (255,255,255))
    regofintim =  cv2.bitwise_and(image_hsv2, regofint)
    
    hsv_frame = cv2.cvtColor(regofintim, cv2.COLOR_BGR2HSV)

    #*************BLUE MASK****************************************************************************************************
    #**************************************************************************************************************************
    #Rang del color blau
    aux1 = 0
    while loop == True:
        
        if notblue == True:
            low_blue = np.array([106, 80, 2])
            high_blue = np.array([130, 255, 255])
        if notblue == False:
            low_blue = np.array([78, 158, 124])
            high_blue = np.array([138, 255, 255])
        #Mascara del color blau
        blue_mask = cv2.inRange(hsv_frame, low_blue, high_blue)
        #Color blau aillat en el frame
        blue = cv2.bitwise_and(image_hsv, image_hsv, mask=blue_mask)
        #Frame en escala de grisos
        blue_gray = cv2.cvtColor(blue, cv2.COLOR_BGR2GRAY)
        blue_clean = cv2.fastNlMeansDenoising(blue_gray, None, 50,7,21)
        r,bluecropppp = cv2.threshold(blue_clean,50,255,cv2.THRESH_BINARY)
        contornblue, hierarchyblue = cv2.findContours(bluecropppp, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contornblue) == 0:
            notblue = True
            if aux1 < 1:
                aux1 = aux1 + 1
            else:
                loop = False
            
        if len(contornblue)>0:
                loop = False
                thresh1 = False
                i = 0
                for contorn in contornblue:
                    i = i+1
                    (xb,yb,wb,hb) = cv2.boundingRect(contorn)

                    if  40 < wb < width-(width/4) and 40 < hb < height/2:
                        #t1 = 145
                        crop_blue = image_hsv1[yb:yb+hb, xb:xb+wb]
                        areacontorn = cv2.contourArea(contorn)
                        heightcrop, widthcrop= crop_blue.shape[:2]
                        areacrop = heightcrop * widthcrop
                        leftarea = areacrop - areacontorn
                        if leftarea < areacrop/3:
                            if wb > hb:
                                t1 = 190
                                while thresh1 == False and t1 >=100:
                                    crop_blue_or = image_hsv1[yb:yb+hb, xb:xb+wb]
                                    imgresized_or = cv2.resize(crop_blue_or,(600,415),interpolation=cv2.INTER_AREA)
                                    blur_resized_or = cv2.GaussianBlur(imgresized_or, (3,3), 0)
                                    crop_blue_gray = cv2.cvtColor(imgresized_or, cv2.COLOR_BGR2GRAY)
                                    blur_blue = cv2.GaussianBlur(crop_blue_gray, (3,3), 0)
                                    ret,bluecrop_thresh = cv2.threshold(blur_blue,t1,255,cv2.THRESH_BINARY_INV)
                                    t1 = t1 - 15
                                    bluecrop_thresh1 = cv2.fastNlMeansDenoising(bluecrop_thresh, None, 50,7,21)
                                    text_blue = pytesseract.image_to_string(bluecrop_thresh1, lang = 'eng+spa')
                                    
                                    if text_blue != '\x0c' and text_blue != '\n' and text_blue != '\n\x0c' and text_blue != '' and text_blue != ' \n\x0c':
                                        thresh1 = True
                                        cv2.imwrite(pathHsv + "/" + count + "_OrientacioBlue.jpg" , blur_resized_or)
                                        print(text_blue)
                            if wb < hb:
                                crop_blue_ind = image_hsv1[yb:yb+hb, xb:xb+wb]
                                imgresized_ind = cv2.resize(crop_blue_ind,(315,500),interpolation=cv2.INTER_AREA)
                                blur_resized_ind = cv2.GaussianBlur(imgresized_ind, (3,3), 0)
                                cv2.imwrite(pathHsv + "/" + count + "_IndicacioBlue.jpg" , blur_resized_ind)

    #*************WHITE MASK***************************************************************************************************
    #**************************************************************************************************************************

    #Rang del color blanc
    aux2 = 0
    while loop2 == True:
        
        if notwhite == True:
            low_white = np.array([74, 0, 160])
            high_white = np.array([91, 37, 204])
        if notwhite == False:
            low_white = np.array([0, 0, 200])
            high_white = np.array([76, 14, 233])
        #Mascara del color blanc
        white_mask = cv2.inRange(hsv_frame, low_white, high_white)
        #Color blanc aillat en el frame
        white = cv2.bitwise_and(image_hsv, image_hsv, mask=white_mask)
        #Frame en escala de grisos
        white_gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)

        white_clean = cv2.fastNlMeansDenoising(white_gray, None, 50,7,21)
        r,whitecropppp = cv2.threshold(white_clean,210,255,cv2.THRESH_BINARY)
        
        contornwhite, hierarchywhite = cv2.findContours(whitecropppp, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        if len(contornwhite) == 0:
                notblue = True
                if aux2 < 1:
                    aux2 = aux2 + 1
                else:
                    loop2 = False
        
        if len(contornwhite)>0:
            loop2 = False
            i = 0
            thresh2 = False
            for contorn in contornwhite:
                i = i+1
                
                (xw,yw,ww,hw) = cv2.boundingRect(contorn)
                
                if  40 < ww < width-(width/4) and 40 < hw < height/2:
                    crop_white = image_hsv1[yw:yw+hw, xw:xw+ww]
                    areacontorn = cv2.contourArea(contorn)
                    heightcrop, widthcrop= crop_white.shape[:2]
                    areacrop = heightcrop * widthcrop
                    leftarea = areacrop - areacontorn
                    if leftarea < areacrop/3:
                        imgresized_white = cv2.resize(crop_white,(600,415),interpolation = cv2.INTER_AREA)
                        blur_resized_white = cv2.GaussianBlur(imgresized_white, (3,3), 0)
                        crop_white_gray = cv2.cvtColor(imgresized_white, cv2.COLOR_BGR2GRAY)
                        blur_white = cv2.GaussianBlur(crop_white_gray, (3,3), 0)
                        t2 = 255
                        while thresh2 == False and t2>= 100:
                            
                            ret,whitecrop_thresh = cv2.threshold(blur_white,t2,255,cv2.THRESH_BINARY)
                            t2 = t2 - 15
                            text_white = pytesseract.image_to_string(whitecrop_thresh, lang='eng+spa')
                            if text_white != '\x0c' and text_white != '\n' and text_white != ' \n\x0c' and text_white != ' ' and text_white != '\n\x0c' :
                                
                                thresh2 = True
                                cv2.imwrite(pathHsv + "/" + count + "_WhiteOrientacio.jpg" , blur_resized_white)
                                print(text_white)
        
    #cv2.imwrite(pathHsv + "/" + count + "_rectangle.jpg" , image_hsv1)
    
if __name__ == '__main__':
    
    pathOut = Path("frames")
    cspOut = str(Path(pathOut))
    pathHsv = Path("hsv")
    cspHsv = str(Path(pathHsv))
    
    p1 = Process(target= extractImages, args = (cspOut,cspHsv,)) 
    p2 = Process(target = gui.gui_cicle)

    p1.start()
    p2.start()

    p1.join()
    p2.join()