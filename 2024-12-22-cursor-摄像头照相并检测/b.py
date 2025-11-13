import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import numpy as np
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions

class CameraApp:
    def __init__(self, window):
        self.window = window
        self.window.title("智能相机识别系统")
        
        # 初始化模型
        self.model = MobileNetV2(weights='imagenet')
        
        # 创建界面元素
        self.frame = ttk.Frame(window)
        self.frame.pack(padx=10, pady=10)
        
        # 创建显示区域
        self.display = ttk.Label(self.frame)
        self.display.pack()
        
        # 创建按钮
        self.capture_btn = ttk.Button(self.frame, text="拍照", command=self.capture_image)
        self.capture_btn.pack(pady=5)
        
        # 创建结果显示区域
        self.result_label = ttk.Label(self.frame, text="识别结果将在这里显示")
        self.result_label.pack(pady=5)
        
        # 初始化摄像头
        self.camera = cv2.VideoCapture(0)
        self.update_camera()
        
    def update_camera(self):
        # 读取摄像头画面
        ret, frame = self.camera.read()
        if ret:
            # 转换颜色空间从BGR到RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 转换为PIL图像
            image = Image.fromarray(frame_rgb)
            # 调整大小
            image = image.resize((640, 480))
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # 更新显示
            self.display.configure(image=photo)
            self.display.image = photo
        
        # 每10毫秒更新一次
        self.window.after(10, self.update_camera)
    
    def capture_image(self):
        # 拍照
        ret, frame = self.camera.read()
        if ret:
            # 预处理图像用于模型识别
            image = cv2.resize(frame, (224, 224))
            image = np.expand_dims(image, axis=0)
            image = preprocess_input(image)
            
            # 进行预测
            predictions = self.model.predict(image)
            results = decode_predictions(predictions, top=3)[0]
            
            # 显示结果
            result_text = "识别结果：\n"
            for i, (imagenet_id, label, score) in enumerate(results):
                result_text += f"{i+1}. {label}: {score*100:.2f}%\n"
            
            self.result_label.configure(text=result_text)

def main():
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()