"""The NGIO Grass Cache window: what will happen, what is missing, and how the run is going."""
from __future__ import annotations

import datetime
import os
import traceback

import mobase
from PyQt6.QtCore import QCoreApplication, Qt, QTimer
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
                             QMessageBox, QPlainTextEdit, QPushButton, QRadioButton, QSpinBox, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from .controller import RunController, RunPlan
from .core.seasons import FOUR, NO_SEASONS
from .core.watchdog import WatchConfig

MARK = {"ok": "✔", "warn": "⚠", "error": "✖"}
COLOR = {"ok": "#3c9a3c", "warn": "#c08a00", "error": "#c0392b"}


class RunDialog(QDialog):
    def __init__(self, parent: QWidget | None, organizer: mobase.IOrganizer, plugin_name: str):
        super().__init__(parent)
        self.o = organizer
        self.plugin = plugin_name
        self.setWindowTitle("NGIO Grass Cache")
        self.resize(760, 720)
        self.ctl = RunController(organizer, self._log)
        self.log_path = os.path.join(organizer.pluginDataPath(), "ngio_grass", "run.log")

        root = QVBoxLayout(self)
        intro = QLabel(
            "Generates No Grass In Objects' grass cache for each season you pick, one after another. "
            "Skyrim starts through MO2, is restarted after a crash or a hang, and every season becomes "
            "its own mod. Nothing in your mods is changed. You can leave it running overnight.")
        intro.setWordWrap(True)
        root.addWidget(intro)

        # What to generate
        what = QGroupBox("What to generate")
        wl = QVBoxLayout(what)
        self.four = QRadioButton("Four seasons (Seasons of Skyrim)")
        self.none = QRadioButton("No seasons: one cache")
        self.four.setChecked(True)
        wl.addWidget(self.four)
        row = QHBoxLayout()
        row.addSpacing(22)
        self.season_boxes = {}
        for s in FOUR:
            box = QCheckBox(s.name)
            box.setChecked(True)
            self.season_boxes[s.key] = box
            row.addWidget(box)
        row.addStretch(1)
        wl.addLayout(row)
        wl.addWidget(self.none)
        lod = QHBoxLayout()
        self.lod = QCheckBox("Also copy one season without its suffix, for DynDOLOD grass LOD:")
        self.lod_from = QComboBox()
        for s in FOUR:
            self.lod_from.addItem(s.name, s.key)
        lod.addWidget(self.lod)
        lod.addWidget(self.lod_from)
        lod.addStretch(1)
        wl.addLayout(lod)
        root.addWidget(what)
        for w in (self.four, self.none, *self.season_boxes.values()):
            w.toggled.connect(self._mode_changed)

        # Timing
        timing = QGroupBox("When to restart the game")
        tl = QFormLayout(timing)
        self.spins = {}
        for key, label, lo, hi in (("boot_minutes", "Wait for the first cell (minutes)", 1, 120),
                                   ("stall_minutes", "Restart when no new cell for (minutes)", 1, 120),
                                   ("restart_delay_seconds", "Pause before restarting (seconds)", 0, 600),
                                   ("max_restarts", "Restarts allowed per season", 0, 500)):
            spin = QSpinBox()
            spin.setRange(lo, hi)
            value = self.o.pluginSetting(self.plugin, key)
            spin.setValue(value if isinstance(value, int) else int(str(value or 0)) or lo)
            self.spins[key] = spin
            tl.addRow(label, spin)
        root.addWidget(timing)

        # Checks
        self.checks_box = QGroupBox("Before you start")
        self.checks_layout = QVBoxLayout(self.checks_box)
        root.addWidget(self.checks_box)

        # Progress
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Season", "State", "Cells done", "Restarts", "Cache files"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setMaximumHeight(150)
        root.addWidget(self.table)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        root.addWidget(self.log_view, 1)
        where = QLabel(f"This log is also saved to {self.log_path}")
        where.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        where.setStyleSheet("color: gray;")
        root.addWidget(where)

        buttons = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.resume_btn = QPushButton("Resume unfinished run")
        self.stop_btn = QPushButton("Stop")
        close_btn = QPushButton("Close")
        self.start_btn.clicked.connect(lambda: self._start(resume=False))
        self.resume_btn.clicked.connect(lambda: self._start(resume=True))
        self.stop_btn.clicked.connect(self._stop)
        close_btn.clicked.connect(self.hide)
        for b in (self.start_btn, self.resume_btn, self.stop_btn):
            buttons.addWidget(b)
        buttons.addStretch(1)
        buttons.addWidget(close_btn)
        root.addLayout(buttons)

        # Closing MO2 mid-run: stop the game and move the trigger out, same as Stop.
        app = QCoreApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self._stop)

        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self._tick)
        self._update_buttons()

    # ---- helpers ------------------------------------------------------------------------
    def _log(self, text: str) -> None:
        stamp = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"{stamp}  {text}"
        self.log_view.appendPlainText(line)
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"{datetime.date.today()} {line}\n")
        except OSError:
            pass

    def _seasons(self):
        if self.none.isChecked():
            return [NO_SEASONS]
        return [s for s in FOUR if self.season_boxes[s.key].isChecked()]

    def _mode_changed(self, *_):
        four = self.four.isChecked()
        for box in self.season_boxes.values():
            box.setEnabled(four)
        self.lod.setEnabled(four)
        self.lod_from.setEnabled(four)
        self.refresh_checks()

    def _clear_checks(self):
        while self.checks_layout.count():
            item = self.checks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def refresh_checks(self) -> None:
        if self.ctl.running:
            return
        self._clear_checks()
        try:
            checks = self.ctl.preflight(seasonal=not self.none.isChecked())
        except Exception as e:  # a broken check must not hide the window
            checks = []
            self._log(f"Checks failed: {e}")
        if not self._seasons():
            from .controller import Check
            checks.append(Check("error", "Pick at least one season."))
        self._blocked = any(c.level == "error" for c in checks)
        for c in checks:
            row = QWidget()
            h = QHBoxLayout(row)
            h.setContentsMargins(0, 0, 0, 0)
            mark = QLabel(MARK[c.level])
            mark.setStyleSheet(f"color: {COLOR[c.level]}; font-weight: bold;")
            mark.setFixedWidth(18)
            text = QLabel(c.text)
            text.setWordWrap(True)
            h.addWidget(mark, 0, Qt.AlignmentFlag.AlignTop)
            h.addWidget(text, 1)
            if c.fix:
                btn = QPushButton(c.fix_label)
                btn.clicked.connect(lambda _=False, fix=c.fix: self._apply_fix(fix))
                h.addWidget(btn, 0, Qt.AlignmentFlag.AlignTop)
            self.checks_layout.addWidget(row)
        again = QPushButton("Check again")
        again.clicked.connect(self.refresh_checks)
        self.checks_layout.addWidget(again, 0, Qt.AlignmentFlag.AlignLeft)
        self._update_buttons()

    def _apply_fix(self, fix):
        try:
            fix()
            self.o.refresh(True)
        except Exception as e:
            self._log(f"Could not apply the fix: {e}")
        QTimer.singleShot(1500, self.refresh_checks)

    def _update_buttons(self):
        running = self.ctl.running
        blocked = getattr(self, "_blocked", False)
        self.start_btn.setEnabled(not running and not blocked)
        self.resume_btn.setVisible(not running and self.ctl.unfinished() is not None)
        self.resume_btn.setEnabled(not blocked)
        self.stop_btn.setEnabled(running)
        for w in (self.four, self.none, self.lod, self.lod_from, *self.season_boxes.values(), *self.spins.values()):
            w.setEnabled(not running)
        if not running:
            self._mode_changed_enable_only()

    def _mode_changed_enable_only(self):
        four = self.four.isChecked()
        for box in self.season_boxes.values():
            box.setEnabled(four)
        self.lod.setEnabled(four)
        self.lod_from.setEnabled(four)

    def _config(self) -> WatchConfig:
        v = {k: s.value() for k, s in self.spins.items()}
        for k, val in v.items():
            self.o.setPluginSetting(self.plugin, k, val)
        return WatchConfig(boot_seconds=v["boot_minutes"] * 60, stall_seconds=v["stall_minutes"] * 60,
                           restart_delay_seconds=v["restart_delay_seconds"], max_restarts=v["max_restarts"])

    # ---- run ---------------------------------------------------------------------------
    def _start(self, resume: bool):
        try:
            if resume:
                found = self.ctl.unfinished()
                if found is None:
                    raise RuntimeError("there is no unfinished run to resume")
                plan = found
                plan.config = self._config()
            else:
                lod = None
                if self.four.isChecked() and self.lod.isChecked():
                    lod = next(s for s in FOUR if s.key == self.lod_from.currentData())
                plan = RunPlan(seasons=self._seasons(), lod_from=lod, config=self._config())
            names = ", ".join(s.name for s in plan.seasons)
            self._log(f"Run: {names}." + (" Resuming." if resume else ""))
            self.ctl.start(plan, resume=resume)
            self._fill_table()
            self.timer.start()
        except Exception as e:
            self._log(f"Could not start: {e}")
            self._log(traceback.format_exc())
            self.ctl.running = False
            QMessageBox.warning(self, "NGIO Grass Cache", f"Could not start:\n{e}")
        self._update_buttons()

    def _stop(self):
        if not self.ctl.running:
            return
        self.timer.stop()
        try:
            self.ctl.stop()
        except Exception as e:
            self._log(f"Stop failed: {e}")
        self._update_buttons()
        self.refresh_checks()

    def _tick(self):
        try:
            self.ctl.tick()
        except Exception as e:
            self._log(f"Error during the run: {e}")
            self._log(traceback.format_exc())
        self._fill_table()
        if not self.ctl.running:
            self.timer.stop()
            self._update_buttons()
            if self.ctl.finished:
                QMessageBox.information(self, "NGIO Grass Cache", "The grass cache is ready. Its mods are enabled.")
            self.refresh_checks()

    def _fill_table(self):
        rows = self.ctl.results
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, value in enumerate((r.season.name, r.state, r.cells, r.restarts, r.files or "")):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

    def closeEvent(self, event):
        # Closing the window keeps a run going; reopen it from the Tools menu.
        event.ignore()
        self.hide()
