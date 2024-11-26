import os
import shutil
import sys
import subprocess
import platform
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QTreeView, QSplitter, QMessageBox, QInputDialog, QToolBar
)
from PyQt6.QtGui import QFileSystemModel, QAction, QIcon
from PyQt6.QtCore import Qt


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Explorer")
        self.setGeometry(100, 100, 1200, 600)

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.left_panel = self.create_file_explorer()
        splitter.addWidget(self.left_panel)

        self.right_panel = self.create_file_explorer()
        splitter.addWidget(self.right_panel)

        layout.addWidget(splitter)

        self.create_toolbar()

    # Создание файлового менеджера
    def create_file_explorer(self):
        tree_view = QTreeView()

        file_model = QFileSystemModel()
        file_model.setRootPath(os.path.expanduser("~"))

        tree_view.setModel(file_model)
        tree_view.setRootIndex(file_model.index(os.path.expanduser("~")))
        tree_view.setSortingEnabled(True)

        tree_view.doubleClicked.connect(lambda index: self.open_file(file_model, index))

        return tree_view

    # Создание панели инструментов
    def create_toolbar(self):
        toolbar = QToolBar("Основные действия", self)
        self.addToolBar(toolbar)

        toolbar.addAction(self.create_toolbar_action("Копировать", self.copy_file))
        toolbar.addAction(self.create_toolbar_action("Переместить", self.move_file))
        toolbar.addAction(self.create_toolbar_action("Удалить", self.delete_file))
        toolbar.addAction(self.create_toolbar_action("Переименовать", self.rename_file))
        toolbar.addAction(self.create_toolbar_action("Создать файл", self.create_file))
        toolbar.addAction(self.create_toolbar_action("Поиск файла", self.search_file))

    def create_toolbar_action(self, text, callback):
        action = QAction(text, self)
        action.triggered.connect(callback)
        return action

    # Получени выбранного пути
    def get_selected_path(self, panel):
        index = panel.currentIndex()
        model = panel.model()
        return model.filePath(index)

    # Функция открытия файла
    def open_file(self, model, index):
        path = model.filePath(index)
        if os.path.isfile(path):
            try:
                if platform.system() == "Windows":
                    os.startfile(path)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", path])
                else:
                    subprocess.run(["xdg-open", path])
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{e}")
        elif os.path.isdir(path):
            QMessageBox.information(self, "Каталог", f"Выбрана папка: {path}")

    # Функция копирования файла
    def copy_file(self):
        source = self.get_selected_path(self.left_panel)
        destination = self.get_selected_path(self.right_panel)

        if not source or not destination or not os.path.isdir(destination):
            QMessageBox.warning(self, "Предупреждение", "Выберите файл/папку для копирования и папку назначения.")
            return

        try:
            if os.path.isdir(source):
                shutil.copytree(source, os.path.join(destination, os.path.basename(source)))
            else:
                shutil.copy(source, destination)
            QMessageBox.information(self, "Успех", "Файл(ы) успешно скопированы.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при копировании: {e}")

    # Функция перемещения файла
    def move_file(self):
        source = self.get_selected_path(self.left_panel)
        destination = self.get_selected_path(self.right_panel)

        if not source or not destination or not os.path.isdir(destination):
            QMessageBox.warning(self, "Предупреждение", "Выберите файл/папку для перемещения и папку назначения.")
            return

        try:
            shutil.move(source, destination)
            QMessageBox.information(self, "Успех", "Файл(ы) успешно перемещены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при перемещении: {e}")

    # Функция удаления файла
    def delete_file(self):
        source = self.get_selected_path(self.left_panel)

        if not source:
            QMessageBox.warning(self, "Предупреждение", "Выберите файл или папку для удаления.")
            return

        confirm = QMessageBox.question(
            self, "Подтверждение", f"Вы уверены, что хотите удалить '{source}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(source):
                    shutil.rmtree(source)
                else:
                    os.remove(source)
                QMessageBox.information(self, "Успех", "Файл(ы) успешно удалены.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {e}")

    # Переименование файла
    def rename_file(self):
        source = self.get_selected_path(self.left_panel)

        if not source:
            QMessageBox.warning(self, "Предупреждение", "Выберите файл или папку для переименования.")
            return

        new_name, ok = QInputDialog.getText(self, "Переименование", "Введите новое имя:")
        if ok and new_name:
            try:
                new_path = os.path.join(os.path.dirname(source), new_name)
                os.rename(source, new_path)
                QMessageBox.information(self, "Успех", "Файл(ы) успешно переименованы.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при переименовании: {e}")

    # Создание файла
    def create_file(self):
        destination = self.get_selected_path(self.left_panel)

        if not destination or not os.path.isdir(destination):
            QMessageBox.warning(self, "Предупреждение", "Выберите папку для создания файла.")
            return

        file_name, ok = QInputDialog.getText(self, "Создание файла", "Введите имя файла:")
        if ok and file_name:
            try:
                new_file_path = os.path.join(destination, file_name)
                with open(new_file_path, 'w') as file:
                    file.write("")
                QMessageBox.information(self, "Успех", "Файл успешно создан.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при создании файла: {e}")

    # Функция поиска вхождения строки в массиве
    def search_in_list(self, list_files, search_path, dirpath):
        results = []
        search_path = search_path.lower()
        for file in list_files:
            path = file.lower()
            if path.find(search_path) != -1:
                results.append(os.path.join(dirpath, file))
        return results

    # Функция поиска файла
    def search_file(self):
        search_name, ok = QInputDialog.getText(self, "Поиск", "Введите имя файла или папки для поиска:")
        if ok and search_name:
            root = os.path.expanduser("~")
            result = []
            for dirpath, dirnames, filenames in os.walk(root):
                result.extend(self.search_in_list(dirnames, search_name, dirpath))
                result.extend(self.search_in_list(filenames, search_name, dirpath))

            if result:
                QMessageBox.information(self, "Результаты поиска", "\n".join(result))
            else:
                QMessageBox.information(self, "Результаты поиска", "Файл или папка не найдены.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileManager()
    window.show()
    sys.exit(app.exec())
