#!/usr/bin/env python3
"""
彩色分形生成器 - 使用Turtle图形库

此脚本生成各种经典分形图案，带有丰富多彩的设计
使用Python turtle模块。
"""

import turtle
import random
from math import cos, sin, radians
import colorsys

# Global counters for color gradient
SEG_IDX = 0  # 当前绘制到的线段序号
TOTAL_SEGMENTS = 1  # 总线段数，将在绘制开始前设置

# Set up the screen
def setup_screen():
    screen = turtle.Screen()
    screen.title("彩色分形图案")
    screen.bgcolor("black")
    screen.setup(width=800, height=800)
    screen.colormode(255)  # Enable full RGB color range
    # Use a lower tracer value to see some animation while not being too slow
    screen.tracer(0)  # Turn off animation for faster drawing
    return screen

# Set up the turtle
def create_turtle():
    t = turtle.Turtle()
    t.speed(0)  # Fastest speed
    t.hideturtle()
    t.pensize(3)  # Slightly thicker lines for better visibility
    return t

# 固定的彩虹颜色列表
RAINBOW_COLORS = [
    "#FF0000",  # 红色
    "#FF7F00",  # 橙色
    "#FFFF00",  # 黄色
    "#00FF00",  # 绿色 
    "#0000FF",  # 蓝色
    "#4B0082",  # 靛蓝
    "#9400D3"   # 紫罗兰
]

# 根据递归级别生成颜色
def rainbow_color(level, max_level):
    # 按递归级别直接选择颜色
    index = level % len(RAINBOW_COLORS)
    return RAINBOW_COLORS[index]

# 循环使用彩虹颜色列表
COLOR_INDEX = 0

def next_rainbow_color():
    """返回下一个彩虹颜色，每次调用循环前进"""
    global COLOR_INDEX
    color = RAINBOW_COLORS[COLOR_INDEX % len(RAINBOW_COLORS)]
    COLOR_INDEX += 1
    return color

# Generate a bright, random color for more visible contrast
def random_bright_color():
    # Use bright colors with high saturation
    r = random.randint(150, 255)
    g = random.randint(150, 255)
    b = random.randint(150, 255)
    return f"#{r:02x}{g:02x}{b:02x}"

# Koch雪花分形 - 彩色变体
def koch_snowflake(t, length, level, max_level):
    if level == 0:
        # 在最底层段落设置颜色并绘制
        global SEG_IDX, TOTAL_SEGMENTS
        h = SEG_IDX / TOTAL_SEGMENTS
        r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
        t.pencolor(int(r * 255), int(g * 255), int(b * 255))
        SEG_IDX += 1
        t.forward(length)
    else:
        koch_snowflake(t, length/3, level-1, max_level)
        t.left(60)
        koch_snowflake(t, length/3, level-1, max_level)
        t.right(120)
        koch_snowflake(t, length/3, level-1, max_level)
        t.left(60)
        koch_snowflake(t, length/3, level-1, max_level)

# 绘制完整的Koch雪花
def draw_koch_snowflake(t, size, levels):
    global SEG_IDX, TOTAL_SEGMENTS
    SEG_IDX = 0
    TOTAL_SEGMENTS = 3 * (4 ** levels)  # 递归后总线段数
    # 为三个边设置不同的起始颜色
    for _ in range(3):
        
        koch_snowflake(t, size, levels, levels)
        t.right(120)

# 谢尔宾斯基三角形分形 - 带颜色
def sierpinski_triangle(t, points, level, max_level):
    # 绘制填充三角形
    t.penup()
    t.goto(points[0][0], points[0][1])
    t.pendown()
    
    # 根据级别选择颜色
    color = RAINBOW_COLORS[level % len(RAINBOW_COLORS)]
    t.fillcolor(color)
    t.pencolor(color)
    t.begin_fill()
    
    for x, y in points[1:] + [points[0]]:
        t.goto(x, y)
    
    t.end_fill()
    
    # 如果级别 > 0，绘制三个更小的三角形
    if level > 0:
        # 计算中点
        mid1 = ((points[0][0] + points[1][0]) / 2, (points[0][1] + points[1][1]) / 2)
        mid2 = ((points[1][0] + points[2][0]) / 2, (points[1][1] + points[2][1]) / 2)
        mid3 = ((points[2][0] + points[0][0]) / 2, (points[2][1] + points[0][1]) / 2)
        
        # 对三个更小的三角形递归调用
        sierpinski_triangle(t, [points[0], mid1, mid3], level-1, max_level)
        sierpinski_triangle(t, [mid1, points[1], mid2], level-1, max_level)
        sierpinski_triangle(t, [mid3, mid2, points[2]], level-1, max_level)

# 龙曲线分形
def dragon_curve(t, length, level, angle, max_level):
    # 根据级别设置颜色
    color = RAINBOW_COLORS[level % len(RAINBOW_COLORS)]
    t.pencolor(color)
    
    if level == 0:
        t.forward(length)
    else:
        t.right(angle)
        dragon_curve(t, length, level-1, -angle, max_level)
        t.left(angle * 2)
        dragon_curve(t, length, level-1, angle, max_level)
        t.right(angle)

# Main function to select and draw fractals
def main():
    screen = setup_screen()
    t = create_turtle()
    
    # 创建多彩的分形图案 - 彩色Koch雪花
    t.penup()
    t.goto(-300, 100)  # 移动到左上方
    t.pendown()
    
    # 增加层级以使分形效果更明显
    levels = 4  # 保持在4层，但确保颜色清晰可见
    draw_koch_snowflake(t, 600, levels)  # 大小, 层级
    
    # 如果你想尝试其他分形，取消下面的注释
    
    # 选项2: 谢尔宾斯基三角形
    # t.clear()  # 清除之前的图案
    # size = 350
    # points = [
    #     (-size, -size * 0.866),  # 左下角
    #     (size, -size * 0.866),    # 右下角
    #     (0, size * 0.866)         # 顶部
    # ]
    # sierpinski_triangle(t, points, 6, 6)  # 顶点, 层级, 最大层级
    
    # 选项3: 龙曲线
    # t.clear()  # 清除之前的图案
    # t.penup()
    # t.goto(-100, 0)
    # t.pendown()
    # dragon_curve(t, 8, 12, 45, 12)  # 长度, 层级, 角度, 最大层级
    
    screen.update()
    turtle.done()

if __name__ == "__main__":
    main()
