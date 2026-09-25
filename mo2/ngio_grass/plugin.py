"""MO2 tool plugin: Tools menu > NGIO Grass Cache."""
from __future__ import annotations

import mobase
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget

from . import VERSION
from .ui import RunDialog

SETTINGS = [
    ("boot_minutes", "Minutes to wait for the first cell after a launch (heavy load orders boot slowly)", 15),
    ("stall_minutes", "Minutes without a new cell before the game counts as hung and is restarted", 10),
    ("restart_delay_seconds", "Seconds to wait after the game closes before starting it again", 10),
    ("max_restarts", "Restarts allowed per season before the run stops", 20),
]


class NgioGrassTool(mobase.IPluginTool):
    def __init__(self):
        super().__init__()
        self._organizer: mobase.IOrganizer | None = None
        self._parent: QWidget | None = None
        self._dialog: RunDialog | None = None

    def init(self, organizer: mobase.IOrganizer) -> bool:
        self._organizer = organizer
        return True

    def name(self) -> str:
        return "NGIO Grass Cache"

    def author(self) -> str:
        return "DuduPhudu"

    def description(self) -> str:
        return ("Generates the No Grass In Objects grass cache for every season in one unattended run: "
                "starts Skyrim through MO2, restarts it after crashes, and turns each season into its own mod.")

    def version(self) -> mobase.VersionInfo:
        major, minor, patch, beta = VERSION
        return mobase.VersionInfo(major, minor, patch, mobase.ReleaseType.BETA if beta else mobase.ReleaseType.FINAL)

    def requirements(self) -> list:
        return [mobase.PluginRequirementFactory.gameDependency(["Skyrim Special Edition", "Skyrim VR"])]

    def settings(self) -> list[mobase.PluginSetting]:
        return [mobase.PluginSetting(key, text, default) for key, text, default in SETTINGS]

    def displayName(self) -> str:
        return "NGIO Grass Cache"

    def tooltip(self) -> str:
        return "Generate the grass cache for every season, unattended"

    def icon(self) -> QIcon:
        return QIcon()

    def setParentWidget(self, parent: QWidget) -> None:
        self._parent = parent

    def display(self) -> None:
        if self._organizer is None:
            return
        if self._dialog is None:
            self._dialog = RunDialog(self._parent, self._organizer, self.name())
        self._dialog.refresh_checks()
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()
