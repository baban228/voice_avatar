import tkinter as tk
from PIL import Image, ImageTk
import threading

class Avatar(tk.Tk):
    def __init__(self):
        super().__init__()

        # Убираем заголовок окна и границы
        self.overrideredirect(True)
        self.attributes('-transparentcolor', 'white')  # Устанавливаем белый цвет как прозрачный
        self.attributes('-topmost', True)  # Окно всегда поверх других

        self.animations = {
            'default': "default.gif",
            'anger': "anger.gif",
            'move_right_arm': "move_right_arm.gif",
            'jump': "jump.gif",
        }
        self.frames = {}
        for key in self.animations:
            self.frames[key] = self.load_gif_frames(self.animations[key])

        self.current_animation = 'default'
        self.current_frame = 0
        self.label = tk.Label(self, bg='white')
        self.label.pack()

        # Запускаем анимацию GIF
        self.update_gif()

        # Привязываем события мыши
        self.label.bind("<ButtonPress-1>", self.on_start_drag)
        self.label.bind("<B1-Motion>", self.on_drag)

        # Начальные координаты окна
        self.x_offset = 0
        self.y_offset = 0

        # Запускаем поток для обработки терминального ввода
        self.input_thread = threading.Thread(target=self.process_input, daemon=True)
        self.input_thread.start()

    def load_gif_frames(self, file_path):
        """Загружает кадры из файла GIF."""
        img = Image.open(file_path)
        frames = []
        try:
            while True:
                frames.append(ImageTk.PhotoImage(img.copy()))
                img.seek(len(frames))
        except EOFError:
            pass
        return frames

    def update_gif(self):
        """Обновляет кадр GIF."""
        if self.frames[self.current_animation]:
            self.label.config(image=self.frames[self.current_animation][self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.frames[self.current_animation])
        self.after(250, self.update_gif)

    def on_start_drag(self, event):
        """Начинает перетаскивание окна."""
        self.x_offset = event.x
        self.y_offset = event.y

    def on_drag(self, event):
        """Перетаскивает окно."""
        x = self.winfo_x() + event.x - self.x_offset
        y = self.winfo_y() + event.y - self.y_offset
        self.geometry(f"+{x}+{y}")

    def set_animation(self, animation_name):
        """Устанавливает текущую анимацию."""
        if animation_name in self.frames:
            self.current_animation = animation_name
            self.current_frame = 0
        else:
            print(f"Анимация '{animation_name}' не найдена.")

    def process_input(self):
        """Обрабатывает терминальный ввод."""
        while True:
            animation_name = input("Введите имя анимации (или 'exit' для выхода): ")
            if animation_name.lower() == 'exit':
                self.destroy()
                break
            self.set_animation(animation_name)

# Пример использования
if __name__ == "__main__":
    avatar = Avatar()
    avatar.mainloop()