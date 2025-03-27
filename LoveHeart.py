import random
from math import sin, cos, pi, log
from tkinter import *

# 配置参数区 ====================================================
CANVAS_WIDTH = 640  # 画布宽度
CANVAS_HEIGHT = 480  # 画布高度
HEART_COLOR = "#FF69B4"  # 爱心颜色 (粉红色)
TEXT_COLOR = "#FFD700"  # 文字颜色 (金色)
FONT_NAME = "楷体"  # 字体名称
IMAGE_ENLARGE = 11  # 基础放大倍数
FRAME_RATE = 160  # 帧率 (毫秒)

# 计算画布中心坐标
CANVAS_CENTER_X = CANVAS_WIDTH // 2
CANVAS_CENTER_Y = CANVAS_HEIGHT // 2


# 爱心函数 ======================================================
def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    """爱心形状生成函数
    Args:
        t: 参数(弧度)
        shrink_ratio: 放大比例
    Returns:
        (x, y): 坐标元组
    """
    # 基础爱心函数
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))

    # 调整比例和位置
    x *= shrink_ratio
    y *= shrink_ratio
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y

    return int(x), int(y)


# 辅助函数 ======================================================
def scatter_inside(x, y, beta=0.15):
    """生成扩散效果坐标
    Args:
        beta: 扩散强度系数
    """
    ratio_x = -beta * log(random.random())
    ratio_y = -beta * log(random.random())
    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def shrink(x, y, ratio):
    """生成收缩效果坐标"""
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def curve(p):
    """跳动周期曲线函数"""
    return 2 * (2 * sin(4 * p)) / (2 * pi)


# 爱心类 ========================================================
class Heart:
    """爱心动画类"""

    def __init__(self, generate_frame=20):
        self.all_points = {}  # 帧缓存
        self._init_points()
        self.generate_frame = generate_frame
        self._generate_animation_frames()

    def _init_points(self):
        """初始化爱心点集"""
        # 基础点集
        self._points = set()
        for _ in range(2000):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self._points.add((x, y))

        # 边缘扩散点集
        self._edge_diffusion_points = set()
        for x, y in self._points:
            for _ in range(3):
                self._edge_diffusion_points.add(scatter_inside(x, y, 0.05))

        # 中心扩散点集
        self._center_diffusion_points = set()
        for _ in range(4000):
            x, y = random.choice(list(self._points))
            self._center_diffusion_points.add(scatter_inside(x, y, 0.17))

    def _generate_animation_frames(self):
        """生成动画帧数据"""
        for frame in range(self.generate_frame):
            self._calc_frame(frame)

    def _calc_frame(self, frame):
        """计算单帧数据"""
        ratio = 10 * curve(frame / 10 * pi)  # 动态比例系数
        halo_radius = int(4 + 6 * (1 + curve(frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(frame / 10 * pi) ** 2))

        frame_points = []

        # 生成光晕效果
        halo_points = set()
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, 11.6)  # 光晕爱心稍大
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in halo_points:
                halo_points.add((x, y))
                frame_points.append((
                    x + random.randint(-14, 14),
                    y + random.randint(-14, 14),
                    random.choice((1, 2, 2))
                ))

        # 添加各类点集
        for point_set in [self._points,
                          self._edge_diffusion_points,
                          self._center_diffusion_points]:
            for x, y in point_set:
                x, y = self._calc_position(x, y, ratio)
                frame_points.append((x, y, random.randint(1, 3)))

        self.all_points[frame] = frame_points

    @staticmethod
    def _calc_position(x, y, ratio):
        """计算动态位置"""
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.520)
        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)
        return x - dx, y - dy

    def render(self, canvas, frame):
        """渲染当前帧"""
        for x, y, size in self.all_points[frame % self.generate_frame]:
            canvas.create_rectangle(
                x, y,
                x + size, y + size,
                width=0,
                fill=HEART_COLOR
            )


# 主程序 ========================================================
def main():
    # 初始化窗口
    root = Tk()
    root.title("跳动爱心")

    # 创建画布
    canvas = Canvas(
        root,
        bg="black",
        height=CANVAS_HEIGHT,
        width=CANVAS_WIDTH
    )
    canvas.pack()

    # 添加文字
    canvas.create_text(
        CANVAS_CENTER_X, 50,
        text="爱心",
        fill=TEXT_COLOR,
        font=(FONT_NAME, 48, "bold")
    )

    # 初始化爱心动画
    heart = Heart()

    # 动画循环
    def draw(frame):
        canvas.delete("all")
        heart.render(canvas, frame)
        root.after(FRAME_RATE, draw, frame + 1)

    draw(0)  # 启动动画
    root.mainloop()


if __name__ == "__main__":
    main()