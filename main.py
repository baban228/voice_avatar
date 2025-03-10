import tkinter as tk
from PIL import Image, ImageTk
import sys
import threading
import queue

class HumanFigure:
    def __init__(self, root):
        self.root = root
        self._offset_x = 0
        self._offset_y = 0

        # Загрузка изображений
        self.idle_image = Image.open("idle.png")
        self.raise_hand_image = Image.open("raise_hand.png")
        self.nod_image = Image.open("nod.png")

        # Преобразование в PhotoImage
        self.idle_photo = ImageTk.PhotoImage(self.idle_image)
        self.raise_hand_photo = ImageTk.PhotoImage(self.raise_hand_image)
        self.nod_photo = ImageTk.PhotoImage(self.nod_image)

        # Настройка Canvas
        width, height = self.idle_image.size
        self.canvas = tk.Canvas(root, width=width, height=height, bg='white', highlightthickness=0)
        self.canvas.pack()

        # Отображение начального изображения
        self.image_on_canvas = self.canvas.create_image(0, 0, image=self.idle_photo, anchor=tk.NW)

        # Настройки окна
        root.overrideredirect(True)  # Убрать рамку
        root.attributes('-topmost', True)  # Окно поверх всех
        root.attributes('-transparentcolor', 'white')  # Белый фон прозрачный

        # Позиция окна (например, 100x100)
        root.geometry(f"{width}x{height}+100+100")

        # Добавляем обработчики для перетаскивания
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def on_mouse_down(self, event):
        """Запомнить позицию мыши при нажатии"""
        self._offset_x = event.x
        self._offset_y = event.y

    def on_mouse_move(self, event):
        """Переместить окно при движении мыши"""
        x = self.root.winfo_pointerx() - self._offset_x
        y = self.root.winfo_pointery() - self._offset_y
        self.root.geometry(f"+{x}+{y}")

    def on_mouse_up(self, event):
        """Сбросить смещение при отпускании кнопки"""
        self._offset_x = 0
        self._offset_y = 0

    def update_image(self, image_name):
        if image_name == 'raise_hand':
            new_photo = self.raise_hand_photo
        elif image_name == 'nod':
            new_photo = self.nod_photo
        else:
            new_photo = self.idle_photo
        self.current_image = new_photo
        self.canvas.itemconfig(self.image_on_canvas, image=new_photo)
        self.root.update_idletasks()

def main():
    q = queue.Queue()

    root = tk.Tk()
    human = HumanFigure(root)

    def process_commands():
        while True:
            command = q.get()
            if command in ['raise_hand', 'nod', 'idle']:
                human.update_image(command)
            q.task_done()

    def stdin_listener():
        for line in sys.stdin:
            command = line.strip()
            if command:
                q.put(command)
        q.join()

    # Запуск потоков
    threading.Thread(target=process_commands, daemon=True).start()
    threading.Thread(target=stdin_listener, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()