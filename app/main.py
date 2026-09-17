import sys, random
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMenu, QWidget, QVBoxLayout

def resource_path(relative):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base / relative

class NoirPet(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Noir")
        self.setFixedSize(190,190)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
        self.label=QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        layout=QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.addWidget(self.label)

        self.scale=0.80
        self.state="idle"
        self.frame=0
        self.drag_offset=None
        self.frames={}
        for state in ("idle","observe","walk","fly","sleep"):
            folder=resource_path(f"assets/noir/{state}")
            self.frames[state]=[QPixmap(str(p)) for p in sorted(folder.glob("*.png"))]

        screen=QApplication.primaryScreen().availableGeometry()
        self.move(screen.right()-self.width()-35, screen.bottom()-self.height()-25)

        self.timer=QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(180)
        self.behavior=QTimer(self); self.behavior.timeout.connect(self.choose_state); self.behavior.start(3500)
        self.render()

    def tick(self):
        seq=self.frames.get(self.state,[])
        if seq:
            self.frame=(self.frame+1)%len(seq)
        self.render()

    def choose_state(self):
        if self.state=="sleep" and random.random()<0.65:
            return
        self.state=random.choices(
            ["idle","observe","walk","fly","sleep"],
            weights=[45,25,14,6,10], k=1
        )[0]
        self.frame=0
        self.render()

    def render(self):
        seq=self.frames.get(self.state,[])
        if not seq: return
        pix=seq[self.frame % len(seq)]
        target=int(180*self.scale)
        self.label.setPixmap(pix.scaled(target,target,Qt.KeepAspectRatio,Qt.SmoothTransformation))

    def mousePressEvent(self,e):
        if e.button()==Qt.LeftButton:
            self.drag_offset=e.globalPosition().toPoint()-self.frameGeometry().topLeft()

    def mouseMoveEvent(self,e):
        if self.drag_offset is not None and e.buttons() & Qt.LeftButton:
            self.move(e.globalPosition().toPoint()-self.drag_offset)

    def mouseReleaseEvent(self,e):
        self.drag_offset=None

    def contextMenuEvent(self,e):
        m=QMenu(self)
        look=m.addAction("Noir，看這邊")
        sleep=m.addAction("叫醒 Noir" if self.state=="sleep" else "讓 Noir 睡一下")
        sm=m.addMenu("尺寸")
        small=sm.addAction("小（80%）"); medium=sm.addAction("中（100%）"); large=sm.addAction("大（125%）")
        m.addSeparator(); quit_=m.addAction("關閉 Noir")
        a=m.exec(e.globalPos())
        if a==look: self.state="observe"; self.frame=0
        elif a==sleep: self.state="idle" if self.state=="sleep" else "sleep"; self.frame=0
        elif a==small: self.scale=.80
        elif a==medium: self.scale=1.0
        elif a==large: self.scale=1.25
        elif a==quit_: QApplication.quit()
        self.render()

def main():
    app=QApplication(sys.argv)
    pet=NoirPet(); pet.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()
