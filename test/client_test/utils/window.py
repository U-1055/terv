from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout


class Window(QMainWindow):

    def __init__(self, widget: QWidget):
        super().__init__()
        layout = QHBoxLayout()
        layout.addWidget(widget)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)


def setup_gui(widget: QWidget, app: QApplication = QApplication()):
    root = Window(widget)
    screen = root.screen()

    screen_width = screen.geometry().width()
    screen_height = screen.geometry().height()

    root_width = int(screen_width * 0.65)
    root_height = int(screen_height * 0.7)
    padx = (screen_width - root_width) // 2
    pady = (screen_height - root_height) // 2

    root.setGeometry(padx, pady, root_width, root_height)
    root.setMinimumSize(root_width, root_height)
    root.setWindowTitle('terv')
    root.show()

    app.exec()


if __name__ == '__main__':
    setup_gui(QWidget())
