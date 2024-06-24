import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class CommandRunner(QThread):
    command_output = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()

            if stdout:
                self.command_output.emit(stdout.strip())
            if stderr:
                self.command_output.emit(stderr.strip())

        except Exception as e:
            print(f"Error executing command: {str(e)}")

        self.finished.emit(process.returncode == 0)


class StatusIndicator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(20, 20)
        self.setAutoFillBackground(True)
        self.setGreen()

    def setGreen(self):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(0, 255, 0))  # Green color
        self.setPalette(palette)

    def setRed(self):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(255, 0, 0))  # Red color
        self.setPalette(palette)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.indicator = StatusIndicator()
        self.layout().addWidget(self.indicator)

        self.runner = None
        self.buttons = [
            self.basic_status_button,
            self.detailed_status_button,
            self.update_check_button,
            self.update_preview_button,
            self.kernel_arguments_button,
            self.clear_button,
        ]

    def initUI(self):
        # Set up the layout
        layout = QVBoxLayout()

        # Create a button to clear the console
        self.clear_button = QPushButton('Clear Console')
        self.clear_button.clicked.connect(self.on_clear_button_click)

        # Create a button to show rpm-ostree basic status
        self.basic_status_button = QPushButton('Basic Status')
        self.basic_status_button.clicked.connect(self.on_basic_status_button_click)

        # Create a button to show rpm-ostree detailed status
        self.detailed_status_button = QPushButton('Detailed Status')
        self.detailed_status_button.clicked.connect(self.on_detailed_status_button_click)

        # Create a button to perform rpm-ostree update --check
        self.update_check_button = QPushButton('Update Check')
        self.update_check_button.clicked.connect(self.on_update_check_button_click)

        # Create a button to perform rpm-ostree update --preview
        self.update_preview_button = QPushButton('Update Preview Check')
        self.update_preview_button.clicked.connect(self.on_update_preview_button_click)

        # Create a button to perform rpm-ostree kargs
        self.kernel_arguments_button = QPushButton('Kernel Arguments Check')
        self.kernel_arguments_button.clicked.connect(self.on_kernel_arguments_button_click)

        # Add buttons to the layout
        layout.addWidget(self.clear_button)
        layout.addWidget(self.basic_status_button)
        layout.addWidget(self.detailed_status_button)
        layout.addWidget(self.update_check_button)
        layout.addWidget(self.update_preview_button)
        layout.addWidget(self.kernel_arguments_button)

        # Create a text edit widget for the console output
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)

        # Set the layout for the main window
        self.setLayout(layout)

        # Set main window properties
        self.setWindowTitle('Qt6 Application with rpm-ostree Commands')
        self.setGeometry(300, 300, 600, 400)

    def update_indicator(self, is_running):
        if is_running:
            self.indicator.setRed()
        else:
            self.indicator.setGreen()

        # Enable or disable buttons based on is_running
        for button in self.buttons:
            button.setEnabled(not is_running)

    def run_command(self, command):
        if self.runner and self.runner.isRunning():
            self.runner.requestInterruption()
            self.runner.wait()

        self.runner = CommandRunner(command)
        self.runner.command_output.connect(self.append_output)
        self.runner.finished.connect(self.command_finished)
        self.runner.start()

    def append_output(self, output):
        self.console.append(output)

    def command_finished(self, success):
        self.update_indicator(False)

    def on_clear_button_click(self):
        # Clear the console text
        self.console.clear()

    def on_basic_status_button_click(self):
        # Execute rpm-ostree basic status command
        self.update_indicator(True)
        self.run_command(['rpm-ostree', 'status'])

    def on_detailed_status_button_click(self):
        # Execute rpm-ostree detailed status command
        self.update_indicator(True)
        self.run_command(['rpm-ostree', 'status', '-v'])

    def on_update_check_button_click(self):
        # Execute rpm-ostree update --check command
        self.update_indicator(True)
        self.run_command(['rpm-ostree', 'update', '--check'])

    def on_update_preview_button_click(self):
        # Execute rpm-ostree update --preview command
        self.update_indicator(True)
        self.run_command(['rpm-ostree', 'update', '--preview'])

    def on_kernel_arguments_button_click(self):
        # Execute rpm-ostree kargs command
        self.update_indicator(True)
        self.run_command(['rpm-ostree', 'kargs'])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
