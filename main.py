import tkinter as tk
from PIL import Image, ImageTk
import sys
import threading
import queue
import time

class HumanFigure:
    def __init__(self, root):
        self.root = root
        self._offset_x = 0
        self._offset_y = 0
        self.animation_paused = False
        self.current_animation = None

        # Загрузка частей тела
        self.body_parts = {
            'body': Image.open("body.png"),
            'left_arm': Image.open("left_arm.png"),
            'right_arm': Image.open("right_arm.png"),
            'left_leg': Image.open("left_leg.png"),
            'right_leg': Image.open("right_leg.png")
        }

        # Преобразование в PhotoImage
        self.body_part_photos = {key: ImageTk.PhotoImage(img) for key, img in self.body_parts.items()}

        # Настройка Canvas
        body_width, body_height = self.body_parts['body'].size
        canvas_width = body_width * 4
        canvas_height = body_height * 4
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg='white', highlightthickness=0)
        self.canvas.pack()

        # Координаты частей тела
        self.positions = {
            'body': (canvas_width // 2, canvas_height // 2),
            'left_arm': (canvas_width // 4 - 6, canvas_height // 3 + 185),  # Рука левее и немного выше
            'right_arm': (3 * canvas_width // 4 + 7, canvas_height // 3 + 185),  # Рука правее и немного выше
            'left_leg': (canvas_width // 4 + 57, 2 * canvas_height // 3 + 83),  # Нога ниже
            'right_leg': (3 * canvas_width // 4 - 62, 2 * canvas_height // 3 + 80)  # Нога ниже
        }

        # Отображение частей тела
        self.body_part_ids = {
            key: self.canvas.create_image(x, y, image=self.body_part_photos[key], anchor=tk.CENTER)
            for key, (x, y) in self.positions.items()
        }

        # Настройки окна
        root.overrideredirect(True)
        root.attributes('-topmost', True)
        root.attributes('-transparentcolor', 'white')
        root.geometry(f"{canvas_width}x{canvas_height}+100+100")

        # Перетаскивание
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Анимации
        self.animations = {
            'idle': [
                {'left_arm': (canvas_width // 4 - 6, canvas_height // 3 + 185),
                 'right_arm': (3 * canvas_width // 4 + 7, canvas_height // 3 + 185),
                 'left_leg': (canvas_width // 4 + 57, 2 * canvas_height // 3 + 83),
                 'right_leg': (3 * canvas_width // 4 - 62, 2 * canvas_height // 3 + 80)}
            ],
            'raise_hand': [
                {'left_arm': (canvas_width // 4 - 6, canvas_height // 3 + 185),
                 'right_arm': (3 * canvas_width // 4 + 7, canvas_height // 3 + 135),
                 'left_leg': (canvas_width // 4 + 57, 2 * canvas_height // 3 + 83),
                 'right_leg': (3 * canvas_width // 4 - 62, 2 * canvas_height // 3 + 80)},

            ],
            'nod': [
                {'left_arm': (canvas_width // 4 - 6, canvas_height // 3 + 185),
                 'right_arm': (3 * canvas_width // 4 + 7, canvas_height // 3 + 185),
                 'left_leg': (canvas_width // 4 + 57, 2 * canvas_height // 3 + 83),
                 'right_leg': (3 * canvas_width // 4 - 62, 2 * canvas_height // 3 + 80)},
                {'left_arm': (canvas_width // 4 - 6, canvas_height // 3 + 185),
                 'right_arm': (3 * canvas_width // 4 + 7, canvas_height // 3 + 185),
                 'left_leg': (canvas_width // 4 + 57, 2 * canvas_height // 3 + 83),
                 'right_leg': (3 * canvas_width // 4 - 62, 2 * canvas_height // 3 + 80)},
                {'left_arm': (canvas_width // 4 - 6, canvas_height // 3 + 185),
                 'right_arm': (3 * canvas_width // 4 + 7, canvas_height // 3 + 185),
                 'left_leg': (canvas_width // 4 + 57, 2 * canvas_height // 3 + 83),
                 'right_leg': (3 * canvas_width // 4 - 62, 2 * canvas_height // 3 + 80)},
                {'left_arm': (canvas_width // 4 - 6, canvas_height // 3 + 185),
                 'right_arm': (3 * canvas_width // 4 + 7, canvas_height // 3 + 185),
                 'left_leg': (canvas_width // 4 + 57, 2 * canvas_height // 3 + 83),
                 'right_leg': (3 * canvas_width // 4 - 62, 2 * canvas_height // 3 + 80)}
            ],
            'move_right': [
                {'left_arm': (canvas_width // 4 - 6 + 100, canvas_height // 3 + 185),
                 'right_arm': (3 * canvas_width // 4 + 7 + 100, canvas_height // 3 + 185),
                 'left_leg': (canvas_width // 4 + 57 + 100, 2 * canvas_height // 3 + 83),
                 'right_leg': (3 * canvas_width // 4 - 62 + 100, 2 * canvas_height // 3 + 80)},
                {'left_arm': (canvas_width // 4 - 6 + 200, canvas_height // 3 + 185),
                 'right_arm': (3 * canvas_width // 4 + 7 + 200, canvas_height // 3 + 185),
                 'left_leg': (canvas_width // 4 + 57 + 200, 2 * canvas_height // 3 + 83),
                 'right_leg': (3 * canvas_width // 4 - 62 + 200, 2 * canvas_height // 3 + 80)}
            ],
            'move_left': [
                {'left_arm': (canvas_width // 4 - 6 - 100, canvas_height // 3 + 185),
                 'right_arm': (3 * canvas_width // 4 + 7 - 100, canvas_height // 3 + 185),
                 'left_leg': (canvas_width // 4 + 57 - 100, 2 * canvas_height // 3 + 83),
                 'right_leg': (3 * canvas_width // 4 - 62 - 100, 2 * canvas_height // 3 + 80)},
                {'left_arm': (canvas_width // 4 - 6 - 200, canvas_height // 3 + 185),
                 'right_arm': (3 * canvas_width // 4 + 7 - 200, canvas_height // 3 + 185),
                 'left_leg': (canvas_width // 4 + 57 - 200, 2 * canvas_height // 3 + 83),
                 'right_leg': (3 * canvas_width // 4 - 62 - 200, 2 * canvas_height // 3 + 80)}
            ],
            'move_up': [
                {'left_arm': (canvas_width // 4 - 6, canvas_height // 3 + 185 - 100),
                 'right_arm': (3 * canvas_width // 4 + 7, canvas_height // 3 + 185 - 100),
                 'left_leg': (canvas_width // 4 + 57, 2 * canvas_height // 3 + 83 - 100),
                 'right_leg': (3 * canvas_width // 4 - 62, 2 * canvas_height // 3 + 80 - 100)},
                {'left_arm': (canvas_width // 4 - 6, canvas_height // 3 + 185 - 200),
                 'right_arm': (3 * canvas_width // 4 + 7, canvas_height // 3 + 185 - 200),
                 'left_leg': (canvas_width // 4 + 57, 2 * canvas_height // 3 + 83 - 200),
                 'right_leg': (3 * canvas_width // 4 - 62, 2 * canvas_height // 3 + 80 - 200)}
            ],
            'move_down': [
                {'left_arm': (canvas_width // 4 - 6, canvas_height // 3 + 185 + 100),
                 'right_arm': (3 * canvas_width // 4 + 7, canvas_height // 3 + 185 + 100),
                 'left_leg': (canvas_width // 4 + 57, 2 * canvas_height // 3 + 83 + 100),
                 'right_leg': (3 * canvas_width // 4 - 62, 2 * canvas_height // 3 + 80 + 100)},
                {'left_arm': (canvas_width // 4 - 6, canvas_height // 3 + 185 + 200),
                 'right_arm': (3 * canvas_width // 4 + 7, canvas_height // 3 + 185 + 200),
                 'left_leg': (canvas_width // 4 + 57, 2 * canvas_height // 3 + 83 + 200),
                 'right_leg': (3 * canvas_width // 4 - 62, 2 * canvas_height // 3 + 80 + 200)}
            ]
        }

    def on_mouse_down(self, event):
        self._offset_x = event.x
        self._offset_y = event.y
        # При нажатии на окно останавливаем текущую анимацию
        if self.current_animation:
            self.root.after_cancel(self.current_animation)
            self.current_animation = None

    def on_mouse_move(self, event):
        x = self.root.winfo_pointerx() - self._offset_x
        y = self.root.winfo_pointery() - self._offset_y
        self.root.geometry(f"+{x}+{y}")

    def on_mouse_up(self, event):
        self._offset_x = 0
        self._offset_y = 0

    def play_animation(self, animation_name, frame=0):
        if self.animation_paused:
            return
        if frame < len(self.animations[animation_name]):
            for part, (x, y) in self.animations[animation_name][frame].items():
                self.canvas.coords(self.body_part_ids[part], x, y)
            self.current_animation = self.root.after(100, self.play_animation, animation_name, frame + 1)
        else:
            # После завершения анимации возвращаемся в idle
            self.current_animation = None
            self.update_image('idle')

    def update_image(self, image_name):
        if self.current_animation:
            self.root.after_cancel(self.current_animation)
            self.current_animation = None
        if image_name in self.animations:
            if len(self.animations[image_name]) > 1:
                # Запускаем анимацию
                self.play_animation(image_name)
            else:
                # Показываем статичное изображение
                for part, (x, y) in self.animations[image_name][0].items():
                    self.canvas.coords(self.body_part_ids[part], x, y)

def main():
    q = queue.Queue()

    root = tk.Tk()
    human = HumanFigure(root)

    def process_commands():
        while True:
            command = q.get()
            if command in ['raise_hand', 'nod', 'idle', 'move_right', 'move_left', 'move_up', 'move_down']:
                human.update_image(command)
            q.task_done()

    def stdin_listener():
        for line in sys.stdin:
            command = line.strip()
            if command:
                q.put(command)
        q.join()

    threading.Thread(target=process_commands, daemon=True).start()
    threading.Thread(target=stdin_listener, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()