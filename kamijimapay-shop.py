from datetime import datetime
from time import sleep
import tkinter
import json
import requests

import cv2
from PIL import Image, ImageTk
from pyzbar import pyzbar
import numpy as np
import simpleaudio as sa

frequency = 3500
fs = 48000
seconds = 0.1
t = np.linspace(0, seconds, seconds * fs, False)
note = np.sin(frequency * t * 2 * np.pi)
audio = note * (2**15 - 1) / np.max(np.abs(note))
audio = audio.astype(np.int16)


while True:
    print("金額入力")
    price = input()
    if price.isdigit() == True:
        break
    print("正しい入力ではありません")

root = tkinter.Tk()
root.title("QR reader")
root.geometry("640x480")
CANVAS_X = 640
CANVAS_Y = 480
# Canvas作成
canvas = tkinter.Canvas(root, width=CANVAS_X, height=CANVAS_Y)
canvas.pack()


# VideoCaptureの引数にカメラ番号を入れる。
# デフォルトでは0、ノートPCの内臓Webカメラは0、別にUSBカメラを接続した場合は1を入れる。
cap = cv2.VideoCapture(0)


def show_frame():
    global CANVAS_X, CANVAS_Y

    ret, frame = cap.read()
    if ret == False:
        print('カメラから画像を取得できませんでした')

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGRなのでRGBに変換
    image_pil = Image.fromarray(image_rgb)  # RGBからPILフォーマットへ変換
    image_tk = ImageTk.PhotoImage(image_pil)  # ImageTkフォーマットへ変換
    # image_tkがどこからも参照されないとすぐ破棄される。
    # そのために下のようにインスタンスを作っておくかグローバル変数にしておく
    canvas.image_tk = image_tk
    # global image_tk

    # ImageTk 画像配置　画像の中心が指定した座標x,yになる
    canvas.create_image(CANVAS_X / 2, CANVAS_Y / 2, image=image_tk)
    # Canvasに現在の日時を表示
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    canvas.create_text(CANVAS_X / 2, 30, text=now_time, font=("Helvetica", 18, "bold"))

    # 画像からQRコードを読み取る
    decoded_objs = pyzbar.decode(frame)

    # pyzbar.decode(frame)の返値
    # ('Decoded', ['data', 'type', 'rect', 'polygon'])
    # [0][0]->.data, [0][1]->.type, [0][2]->rect, [0][3]->polygon

    # 配列要素がある場合
    if decoded_objs != []:
        # [0][0]->.data, [0][1]->.type, [0][2]->rect
        # example
        # for obj in decoded_objs:
        #     print('Type: ', obj.type)

        str_dec_obj = decoded_objs[0][0].decode('utf-8', 'ignore')
        print('QR cord: {}'.format(str_dec_obj))
        left, top, width, height = decoded_objs[0][2]
        play_obj = sa.play_buffer(audio, 1, 2, fs)
        # 取得したQRコードの範囲を描画
        
        canvas.create_rectangle(left, top, left + width, top + height, outline="green", width=5)
        # 取得したQRの内容を表示
        canvas.create_text(left + (width / 2), top - 30, text=str_dec_obj, font=("Helvetica", 20, "bold"))

        
        userID = str_dec_obj.split("=")
        
        if userID[0] == 'userID':
            print("yes/no?", end="")
            var = input()
            #prin(":{}".format(var))
            if var == 'yes':
                #userdata = {"data":str_dec_obj}
                url ="http://52.156.45.138/~db2019/kamijimapay/api/recieve.php"
                
                SendData = {"userID": userID[1], "shopID": "shop01", "productID": "000001", "price": price}
                response = requests.post(url,json=SendData)
                resDatas = response.json()
                print(resDatas)

            if var=='no':
                pass
            else:
                root.quit()






        # QRコードを取得して、その内容をTextに書き出し、そのままTKのプログラムを終了するコード
        # with open('QR_read_data.txt', 'w') as exportFile:
        #    exportFile.write(str_dec_obj)
        # sleep(1)
        # cap.release()
        #root.quit()


    # 10msごとにこの関数を呼び出す
    canvas.after(10, show_frame)

show_frame()
root.mainloop()
