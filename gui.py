import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                             QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                             QPushButton, QSlider, QHeaderView, QMessageBox,
                             QSizePolicy, QComboBox, QGroupBox)
from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation,
                          QSequentialAnimationGroup, pyqtProperty)
from PyQt5.QtGui import QPainter, QColor, QFont
from race_manager import RaceManager

class GridWidget(QWidget):
    def __init__(self, race):
        super().__init__()
        self.race = race
        self.cell_size = 40
        self.setFixedSize(race.width * self.cell_size, race.height * self.cell_size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        emoji_font = QFont("Segoe UI Emoji", int(self.cell_size * 0.6))
        cell = self.cell_size
        grid = self.race.shared_grid
        for i in range(self.race.height):
            for j in range(self.race.width):
                x, y = j * cell, i * cell
                val = grid[i][j]
                if val == 0:
                    painter.fillRect(x, y, cell, cell, QColor(0x1A, 0x3A, 0x1A))
                elif val == 1:
                    painter.fillRect(x, y, cell, cell, QColor(0x8B, 0x45, 0x13))
                    painter.setFont(emoji_font)
                    painter.drawText(x, y, cell, cell, Qt.AlignCenter, "\U0001F9F1")
                elif val == 2:
                    painter.fillRect(x, y, cell, cell, QColor(0x8B, 0x00, 0x00))
                    painter.setFont(emoji_font)
                    painter.drawText(x, y, cell, cell, Qt.AlignCenter, "\U0001F525")
                elif val == 3:
                    painter.fillRect(x, y, cell, cell, QColor(0x44, 0x44, 0x44))
                    painter.setFont(emoji_font)
                    painter.drawText(x, y, cell, cell, Qt.AlignCenter, "\U0001F4A8")
                elif val == 4:
                    painter.fillRect(x, y, cell, cell, QColor(0xFF, 0xD7, 0x00))
                    painter.setFont(emoji_font)
                    painter.drawText(x, y, cell, cell, Qt.AlignCenter, "\U0001F198")
        team_colors = {0: QColor(0x00, 0x88, 0xFF), 1: QColor(0xFF, 0x44, 0x44)}
        for idx, team in enumerate(self.race.teams):
            x, y = team.get_position()
            cx = y * cell + cell // 2
            cy = x * cell + cell // 2
            painter.setBrush(team_colors[idx])
            painter.drawEllipse(cx - 12, cy - 12, 24, 24)
            status = team.worker.get_status()
            if status["wait_time"] > 0:
                painter.setPen(QColor(255, 255, 255))
                painter.setFont(QFont("Segoe UI Emoji", 16))
                painter.drawText(cx - 12, cy - 20, "\u23F8\uFE0F")

class BrainEmoji(QLabel):
    def __init__(self):
        super().__init__("\U0001F9E0")
        self._scale = 1.0
        self.setAlignment(Qt.AlignCenter)
        self.update_font()

    def set_scale(self, value):
        self._scale = value
        self.update_font()

    def get_scale(self):
        return self._scale

    scale = pyqtProperty(float, get_scale, set_scale)

    def update_font(self):
        size = int(32 * self._scale)
        self.setFont(QFont("Segoe UI Emoji", size))
        self.setStyleSheet("color: white;")

class RaceGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RACE Tournament")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #1A1A1A;")
        self.maps = ["apartment.json", "hospital.json", "metro.json"]
        self.current_map_index = 0
        self.team_names = ["AI Team 1", "AI Team 2"]
        self.tournament_tokens = {"AI Team 1": 0, "AI Team 2": 0}
        self.race = RaceManager(self.maps[0], self.team_names)
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_turn)
        self.running = False
        self.race_finished = False
        self.create_ui()
        self.update_display()

    def create_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        top_bar = QHBoxLayout()
        brand = QLabel("PyAiMind")
        brand.setStyleSheet("color: #6A0DAD; font-style: italic; font-weight: bold; font-size: 24px;")
        top_bar.addWidget(brand, alignment=Qt.AlignLeft)
        title = QLabel("Rescue Tournament")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 24px; font-family: Arial;")
        top_bar.addWidget(title, alignment=Qt.AlignCenter)
        token_box = QGroupBox("Token Standings")
        token_box.setStyleSheet("color: white; background-color: #2A2A2A; border: 1px solid #6A0DAD;")
        token_layout = QVBoxLayout()
        self.token_labels = {}
        for name in self.team_names:
            lbl = QLabel(f"{name}: {self.tournament_tokens[name]}")
            lbl.setStyleSheet("color: white;")
            token_layout.addWidget(lbl)
            self.token_labels[name] = lbl
        token_box.setLayout(token_layout)
        top_bar.addWidget(token_box, alignment=Qt.AlignRight)
        main_layout.addLayout(top_bar)

        content = QHBoxLayout()

        left_section = QVBoxLayout()

        brain_layout = QHBoxLayout()
        brain_layout.setSpacing(20)
        self.brain_emojis = []
        for i in range(2):
            brain_container = QVBoxLayout()
            brain_container.setAlignment(Qt.AlignCenter)
            emoji = BrainEmoji()
            label = QLabel(f"Brain {i+1}")
            label.setStyleSheet("color: white; font-size: 12px;")
            label.setAlignment(Qt.AlignCenter)
            brain_container.addWidget(emoji, alignment=Qt.AlignCenter)
            brain_container.addWidget(label, alignment=Qt.AlignCenter)
            brain_layout.addLayout(brain_container)
            self.brain_emojis.append(emoji)
        left_section.addLayout(brain_layout)

        self.grid_widget = GridWidget(self.race)
        left_section.addWidget(self.grid_widget, alignment=Qt.AlignCenter)
        content.addLayout(left_section, 6)

        right_panel = QVBoxLayout()

        map_layout = QHBoxLayout()
        self.map_selector = QComboBox()
        self.map_selector.addItems(self.maps)
        self.map_selector.setStyleSheet("color: white; background-color: #333;")
        self.map_selector.currentTextChanged.connect(self.load_selected_map)
        map_layout.addWidget(QLabel("Map:"))
        map_layout.addWidget(self.map_selector)
        right_panel.addLayout(map_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Team", "Rescued", "Steps", "Score"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QHeaderView::section { background-color: #6A0DAD; color: white; }"
                                 " QTableWidget { background-color: #1E1E1E; color: white; }")
        self.table.cellClicked.connect(self.team_info_update)
        right_panel.addWidget(self.table)

        info_box = QGroupBox("Team Members")
        info_box.setStyleSheet("color: white; background-color: #2A2A2A; border: 1px solid #6A0DAD;")
        info_layout = QVBoxLayout()
        self.member_labels = []
        roles = ["Coach (Brain)", "Assistant (Mediator)", "Rescuer (Worker)"]
        for role in roles:
            lbl = QLabel(role)
            lbl.setStyleSheet("color: white;")
            info_layout.addWidget(lbl)
            self.member_labels.append(lbl)
        info_box.setLayout(info_layout)
        right_panel.addWidget(info_box)

        btn_style = "QPushButton { background-color: #6A0DAD; color: white; } QPushButton:hover { background-color: #9B30FF; }"
        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet(btn_style)
        self.start_btn.clicked.connect(self.start_race)
        right_panel.addWidget(self.start_btn)
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setStyleSheet(btn_style)
        self.pause_btn.clicked.connect(self.pause_race)
        right_panel.addWidget(self.pause_btn)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setStyleSheet(btn_style)
        self.reset_btn.clicked.connect(self.reset_race)
        right_panel.addWidget(self.reset_btn)
        self.next_btn = QPushButton("Next Turn")
        self.next_btn.setStyleSheet(btn_style)
        self.next_btn.clicked.connect(self.next_turn)
        right_panel.addWidget(self.next_btn)
        self.next_map_btn = QPushButton("Next Map")
        self.next_map_btn.setStyleSheet(btn_style)
        self.next_map_btn.clicked.connect(self.next_map)
        right_panel.addWidget(self.next_map_btn)

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("-"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(200, 1000)
        self.speed_slider.setValue(500)
        self.speed_slider.valueChanged.connect(lambda val: self.timer.setInterval(val))
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(QLabel("+"))
        right_panel.addLayout(speed_layout)
        right_panel.addWidget(QLabel("Speed"))

        content.addLayout(right_panel, 4)
        main_layout.addLayout(content)

    def team_info_update(self, row):
        team_name = self.team_names[row]
        roles = ["Coach (Brain)", "Assistant (Mediator)", "Rescuer (Worker)"]
        for i, lbl in enumerate(self.member_labels):
            lbl.setText(f"{team_name} - {roles[i]}")

    def pulse_brain(self, index):
        emoji = self.brain_emojis[index]
        anim = QPropertyAnimation(emoji, b"scale")
        anim.setDuration(100)
        anim.setStartValue(1.0)
        anim.setEndValue(1.2)
        anim2 = QPropertyAnimation(emoji, b"scale")
        anim2.setDuration(100)
        anim2.setStartValue(1.2)
        anim2.setEndValue(1.0)
        group = QSequentialAnimationGroup()
        group.addAnimation(anim)
        group.addAnimation(anim2)
        group.start()

    def update_display(self):
        self.table.setRowCount(len(self.race.teams))
        scores = self.race.get_leaderboard()
        for i, team in enumerate(self.race.teams):
            self.table.setItem(i, 0, QTableWidgetItem(team.name))
            self.table.setItem(i, 1, QTableWidgetItem(str(team.get_rescued_count())))
            self.table.setItem(i, 2, QTableWidgetItem(str(team.get_steps_count())))
            self.table.setItem(i, 3, QTableWidgetItem(f"{scores[team.name]:.2f}"))
        for name, lbl in self.token_labels.items():
            lbl.setText(f"{name}: {self.tournament_tokens[name]}")
        self.grid_widget.update()

    def next_turn(self):
        if self.race_finished:
            return
        self.pulse_brain(self.race.current_turn)
        race_ended = self.race.step_turn()
        self.update_display()
        if race_ended:
            self.timer.stop()
            self.race_finished = True
            self.show_winner()

    def start_race(self):
        self.race_finished = False
        self.timer.start(self.speed_slider.value())
        self.running = True

    def pause_race(self):
        self.timer.stop()
        self.running = False

    def reset_race(self):
        self.timer.stop()
        self.running = False
        self.race_finished = False
        self.race = RaceManager(self.maps[self.current_map_index], self.team_names)
        self.grid_widget.race = self.race
        self.grid_widget.setFixedSize(self.race.width * 40, self.race.height * 40)
        self.update_display()

    def next_map(self):
        self.current_map_index = (self.current_map_index + 1) % len(self.maps)
        self.reset_with_map(self.maps[self.current_map_index])

    def load_selected_map(self):
        map_name = self.map_selector.currentText()
        self.current_map_index = self.maps.index(map_name)
        self.reset_with_map(map_name)

    def reset_with_map(self, map_name):
        self.timer.stop()
        self.race_finished = False
        self.race = RaceManager(map_name, self.team_names)
        self.grid_widget.race = self.race
        self.grid_widget.setFixedSize(self.race.width * 40, self.race.height * 40)
        self.update_display()

    def show_winner(self):
        winner = self.race.get_winner()
        self.tournament_tokens[winner] += 1
        self.update_display()
        QMessageBox.information(self, "Winner!", f"Winner: {winner}!")
        self.next_map()