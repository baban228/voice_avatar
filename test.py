import tkinter as tk
import numpy as np
from PIL import Image, ImageTk


# Функция для линейной интерполяции
def interpolate_linear(initial, final, t):
    return initial * (1 - t) + final * t


# Начальные и конечные позы для разных анимаций
initial_pose = np.array([
    [100, 100],  # голова
    [100, 150],  # шея
    [100, 200],  # таз
    [100, 250],  # левое плечо
    [150, 200],  # левый локоть
    [200, 150],  # левое запястье
    [100, 250],  # правое плечо
    [50, 200],  # правый локоть
    [0, 150],  # правое запястье
    [100, 300],  # правое бедро
    [150, 350],  # правое голенище
    [100, 300],  # левое бедро
    [50, 350]  # левое голенище
])

raise_right_arm_pose = np.array([
    [100, 100],  # голова
    [100, 150],  # шея
    [100, 200],  # таз
    [100, 250],  # левое плечо
    [150, 200],  # левый локоть
    [200, 150],  # левое запястье
    [100, 250],  # правое плечо
    [100, 200],  # правый локоть
    [100, 150],  # правое запястье
    [100, 300],  # правое бедро
    [150, 350],  # правое голенище
    [100, 300],  # левое бедро
    [50, 350]  # левое голенище
])

bend_left_knee_pose = np.array([
    [100, 100],  # голова
    [100, 150],  # шея
    [100, 200],  # таз
    [100, 250],  # левое плечо
    [150, 200],  # левый локоть
    [200, 150],  # левое запястье
    [100, 250],  # правое плечо
    [50, 200],  # правый локоть
    [0, 150],  # правое запястье
    [100, 300],  # правое бедро
    [150, 350],  # правое голенище
    [100, 300],  # левое бедро
    [50, 380]  # левое голенище
])


# Загрузка изображений
def load_image(filename, size):
    image = Image.open(filename)
    image = image.resize(size, Image.LANCZOS)  # Используем LANCZOS вместо ANTIALIAS
    return ImageTk.PhotoImage(image)


# Создание окна
root = tk.Tk()
root.title("Анимация человека")

# Создание холста
canvas = tk.Canvas(root, width=400, height=400, bg='white')
canvas.pack()

# Загрузка изображений для частей тела
head_image = load_image('head.png', (50, 50))
neck_image = load_image('neck.png', (10, 50))
body_image = load_image('body.png', (50, 100))
left_upper_arm_image = load_image('left_upper_arm.png', (50, 50))
left_lower_arm_image = load_image('left_lower_arm.png', (50, 50))
left_hand_image = load_image('left_hand.png', (50, 50))
right_upper_arm_image = load_image('right_upper_arm.png', (50, 50))
right_lower_arm_image = load_image('right_lower_arm.png', (50, 50))
right_hand_image = load_image('right_hand.png', (50, 50))
right_upper_leg_image = load_image('right_upper_leg.png', (50, 50))
right_lower_leg_image = load_image('right_lower_leg.png', (50, 50))
left_upper_leg_image = load_image('left_upper_leg.png', (50, 50))
left_lower_leg_image = load_image('left_lower_leg.png', (50, 50))


# Функция для обновления позы
def update_pose(pose):
    canvas.delete('all')  # Очистка холста

    # Позиционирование изображений
    head_x, head_y = pose[0]
    neck_x, neck_y = pose[1]
    body_x, body_y = pose[2]
    left_shoulder_x, left_shoulder_y = pose[3]
    left_elbow_x, left_elbow_y = pose[4]
    left_wrist_x, left_wrist_y = pose[5]
    right_shoulder_x, right_shoulder_y = pose[6]
    right_elbow_x, right_elbow_y = pose[7]
    right_wrist_x, right_wrist_y = pose[8]
    right_hip_x, right_hip_y = pose[9]
    right_knee_x, right_knee_y = pose[10]
    left_hip_x, left_hip_y = pose[11]
    left_knee_x, left_knee_y = pose[12]

    # Рисование головы
    canvas.create_image(head_x, head_y, image=head_image, anchor='center')

    # Рисование шеи
    canvas.create_image(neck_x, neck_y, image=neck_image, anchor='center')

    # Рисование тела
    canvas.create_image(body_x, body_y, image=body_image, anchor='center')

    # Рисование левой руки
    canvas.create_image(left_shoulder_x, left_shoulder_y, image=left_upper_arm_image, anchor='center')
    canvas.create_image(left_elbow_x, left_elbow_y, image=left_lower_arm_image, anchor='center')
    canvas.create_image(left_wrist_x, left_wrist_y, image=left_hand_image, anchor='center')

    # Рисование правой руки
    canvas.create_image(right_shoulder_x, right_shoulder_y, image=right_upper_arm_image, anchor='center')
    canvas.create_image(right_elbow_x, right_elbow_y, image=right_lower_arm_image, anchor='center')
    canvas.create_image(right_wrist_x, right_wrist_y, image=right_hand_image, anchor='center')

    # Рисование правой ноги
    canvas.create_image(right_hip_x, right_hip_y, image=right_upper_leg_image, anchor='center')
    canvas.create_image(right_knee_x, right_knee_y, image=right_lower_leg_image, anchor='center')

    # Рисование левой ноги
    canvas.create_image(left_hip_x, left_hip_y, image=left_upper_leg_image, anchor='center')
    canvas.create_image(left_knee_x, left_knee_y, image=left_lower_leg_image, anchor='center')


# Функция для анимации
def animate(initial_pose, final_pose, duration=30):
    for frame in range(duration):
        t = frame / (duration - 1)  # t изменяется от 0 до 1
        current_pose = interpolate_linear(initial_pose, final_pose, t)
        update_pose(current_pose)
        root.update()  # Обновление холста
        root.after(100)  # Пауза между кадрами


# Кнопки для выбора анимации
def start_raise_right_arm():
    animate(initial_pose, raise_right_arm_pose)


def start_bend_left_knee():
    animate(initial_pose, bend_left_knee_pose)


button_raise_right_arm = tk.Button(root, text="Поднять правую руку", command=start_raise_right_arm)
button_raise_right_arm.pack(side=tk.LEFT)

button_bend_left_knee = tk.Button(root, text="Согнуть левое колено", command=start_bend_left_knee)
button_bend_left_knee.pack(side=tk.RIGHT)

# Запуск главного цикла событий
root.mainloop()