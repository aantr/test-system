from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, \
    QWidget, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import QSize, Qt


# Наследуемся от QMainWindow
class MainWindow(QMainWindow):
    # Переопределяем конструктор класса
    def __init__(self):
        # Обязательно нужно вызвать метод супер класса
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(480, 80))  # Устанавливаем размеры
        self.setWindowTitle("Работа с QTableWidget")  # Устанавливаем заголовок окна
        central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет

        grid_layout = QGridLayout()  # Создаём QGridLayout
        central_widget.setLayout(grid_layout)  # Устанавливаем данное размещение в центральный виджет

        table = QTableWidget(self)  # Создаём таблицу
        table.setColumnCount(3)  # Устанавливаем три колонки
        table.setRowCount(3)  # и одну строку в таблице

        # Устанавливаем заголовки таблицы
        table.setHorizontalHeaderLabels(["Header 1", "Header 2", "Header 3"])

        # заполняем первую строку
        table.setItem(0, 0, QTableWidgetItem("Text in column 1"))
        table.setItem(0, 1, QTableWidgetItem("Text in column 2"))
        table.setItem(0, 2, QTableWidgetItem("Text in column 3"))

        table.setItem(1, 0, QTableWidgetItem("wwqq Text in column 1"))
        table.setItem(1, 1, QTableWidgetItem("wwqq Text in column 2"))
        table.setItem(1, 2, QTableWidgetItem("wwqq Text in column 3"))

        table.setItem(2, 0, QTableWidgetItem("zxzxzzx Text in column 1"))
        table.setItem(2, 1, QTableWidgetItem("zxzxzzx Text in column 2"))
        table.setItem(2, 2, QTableWidgetItem("zxzxzzx Text in column 3"))

        # делаем ресайз колонок по содержимому
        table.resizeColumnsToContents()

        self.table = table
        grid_layout.addWidget(table, 0, 0)  # Добавляем таблицу в сетку

        button = QPushButton("Click me")
        button.clicked.connect(self.func)

        grid_layout.addWidget(button, 1, 0)

    def func(self):
        t = self.table.item(self.table.currentRow(), 0).text()
        print(t)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
