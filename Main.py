import sys
from PyQt5.QtWidgets import QApplication
from gui import RaceGUI

def main():
    app = QApplication(sys.argv)
    window = RaceGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()