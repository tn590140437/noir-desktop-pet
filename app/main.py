import sys
import math
import random

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QApplication, QMenu, QWidget


class NoirPet(QWidget):
    """Noir V0.02 — portable desktop-pet prototype.

    This version intentionally draws Noir with Qt instead of loading sprite
    files. The final silver-white chibi sprite animations can replace the
    paint routine later without changing the Windows build workflow.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Noir")
        self.setFixedSize(190, 190)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            screen.right() - self.width() - 35,
            screen.bottom() - self.height() - 25,
        )

        self.frame = 0
        self.look_direction = 0       # -1 left, 0 centre, 1 right
        self.blink_frames = 0
        self.sleeping = False
        self.drag_offset = None

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(50)     # ~20 FPS drawing timer

        self.behaviour_timer = QTimer(self)
        self.behaviour_timer.timeout.connect(self.choose_small_behaviour)
        self.behaviour_timer.start(2400)

    def animate(self):
        self.frame += 1
        if self.blink_frames > 0:
            self.blink_frames -= 1
        self.update()

    def choose_small_behaviour(self):
        if self.sleeping:
            return

        roll = random.random()
        if roll < 0.30:
            self.blink_frames = 3
        elif roll < 0.55:
            self.look_direction = -1
        elif roll < 0.80:
            self.look_direction = 1
        else:
            self.look_direction = 0
        self.update()

    # ---------- Mouse interaction ----------

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            if not self.sleeping:
                self.look_direction = 1
            event.accept()

    def mouseMoveEvent(self, event):
        if (
            self.drag_offset is not None
            and event.buttons() & Qt.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self.drag_offset
            )
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        look_action = menu.addAction("Noir，看這邊")
        sleep_action = menu.addAction(
            "叫醒 Noir" if self.sleeping else "讓 Noir 睡一下"
        )
        menu.addSeparator()
        quit_action = menu.addAction("關閉 Noir")

        selected = menu.exec(event.globalPos())

        if selected == look_action:
            self.sleeping = False
            self.look_direction = 1
            self.blink_frames = 0
        elif selected == sleep_action:
            self.sleeping = not self.sleeping
        elif selected == quit_action:
            QApplication.quit()

        self.update()

    # ---------- Temporary vector Noir ----------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Very subtle idle breathing. Sleep breathes more slowly.
        speed = 45 if not self.sleeping else 75
        breath = math.sin(self.frame / speed * math.tau)
        breath_y = breath * (1.4 if not self.sleeping else 1.0)

        # Ground shadow
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 35))
        painter.drawEllipse(42, 157, 108, 14)

        # Tail
        painter.setPen(QPen(QColor("#687382"), 1.2))
        painter.setBrush(QColor("#727d8c"))
        tail = QPainterPath()
        tail.moveTo(79, 127)
        tail.lineTo(62, 162)
        tail.lineTo(91, 146)
        tail.lineTo(108, 163)
        tail.lineTo(111, 126)
        tail.closeSubpath()
        painter.drawPath(tail)

        # Body
        painter.setPen(QPen(QColor("#9299a3"), 1.2))
        painter.setBrush(QColor("#f1f2ef"))
        painter.drawEllipse(
            50,
            int(67 + breath_y),
            87,
            int(88 - breath_y),
        )

        # Folded wings
        painter.setBrush(QColor("#aab2bd"))
        left_wing = QPainterPath()
        left_wing.moveTo(63, 91)
        left_wing.cubicTo(45, 109, 57, 140, 84, 148)
        left_wing.cubicTo(77, 128, 84, 105, 74, 92)
        left_wing.closeSubpath()
        painter.drawPath(left_wing)

        right_wing = QPainterPath()
        right_wing.moveTo(125, 91)
        right_wing.cubicTo(141, 111, 133, 139, 112, 147)
        right_wing.cubicTo(119, 126, 112, 105, 122, 92)
        right_wing.closeSubpath()
        painter.drawPath(right_wing)

        # Head
        head_y = int(31 + breath_y)
        painter.setBrush(QColor("#f8f8f5"))
        painter.drawEllipse(56, head_y, 83, 72)

        # Small crest
        painter.setPen(QPen(QColor("#858e99"), 2))
        crest_points = [(74, 40, 68, 21), (87, 36, 84, 17),
                        (101, 36, 104, 18), (114, 40, 121, 23)]
        for x1, y1, x2, y2 in crest_points:
            painter.drawLine(x1, int(y1 + breath_y),
                             x2, int(y2 + breath_y))

        # Beak
        painter.setPen(QPen(QColor("#252b32"), 1))
        painter.setBrush(QColor("#313943"))
        beak = QPainterPath()
        beak.moveTo(126, int(65 + breath_y))
        beak.lineTo(153, int(72 + breath_y))
        beak.lineTo(128, int(82 + breath_y))
        beak.closeSubpath()
        painter.drawPath(beak)

        # Eyes
        eye_y = int(61 + breath_y)
        painter.setPen(QPen(QColor("#66717e"), 1))

        if self.sleeping or self.blink_frames > 0:
            painter.setPen(QPen(QColor("#303943"), 3))
            painter.drawLine(79, eye_y + 8, 97, eye_y + 8)
            painter.drawLine(109, eye_y + 8, 127, eye_y + 8)
        else:
            painter.setBrush(QColor("#dfe9f1"))
            painter.drawEllipse(79, eye_y, 19, 17)
            painter.drawEllipse(109, eye_y, 19, 17)

            dx = self.look_direction * 2
            painter.setBrush(QColor("#3b5369"))
            painter.drawEllipse(85 + dx, eye_y + 4, 8, 9)
            painter.drawEllipse(115 + dx, eye_y + 4, 8, 9)

            painter.setBrush(QColor("#111820"))
            painter.drawEllipse(88 + dx, eye_y + 6, 3, 5)
            painter.drawEllipse(118 + dx, eye_y + 6, 3, 5)

        # Collar
        painter.setPen(QPen(QColor("#252a30"), 5))
        painter.drawArc(
            68,
            int(88 + breath_y),
            61,
            22,
            195 * 16,
            150 * 16,
        )

        # Small compass-like pendant
        painter.setPen(QPen(QColor("#5b5c60"), 1.5))
        painter.setBrush(QColor("#d4cfc3"))
        pendant_y = int(108 + breath_y)
        painter.drawEllipse(95, pendant_y, 12, 12)
        painter.drawLine(101, pendant_y + 2, 101, pendant_y + 10)
        painter.drawLine(97, pendant_y + 6, 105, pendant_y + 6)

        # Feet
        if not self.sleeping:
            painter.setPen(QPen(QColor("#574a42"), 2))
            painter.drawLine(80, 150, 78, 158)
            painter.drawLine(110, 150, 112, 158)
            painter.drawLine(72, 158, 84, 158)
            painter.drawLine(106, 158, 118, 158)

        # Sleep indicator
        if self.sleeping:
            painter.setPen(QPen(QColor("#56616d"), 2))
            painter.drawText(143, 49, "z")
            painter.drawText(154, 36, "z")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Noir")

    noir = NoirPet()
    noir.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
