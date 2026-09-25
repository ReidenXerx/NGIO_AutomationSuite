"""Watch one season's precache run and decide when to relaunch, kill or stop.

Pure logic: the caller observes the world every few seconds (does PrecacheGrass.txt exist, has
it grown, is the game process alive) and carries out the action this returns. Nothing here
touches a file or a process, so every timing rule is testable with a fake clock.

What NGIO does, and what this relies on:
- The run starts when PrecacheGrass.txt exists in the game folder. NGIO appends every finished
  cell to it, so its size is the progress signal, and deletes it when the whole cache is done.
  NGIO resumes from that file on its own, so a relaunch continues rather than starts over.
- A heavy load order can take several minutes before the first cell. The stall timer only
  starts at the first sign of progress; until then a separate, longer boot limit applies.
  (1.6.0 users reported both: a 4-minute boot tripping the timer, and slow crash detection.)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Action(Enum):
    WAIT = "wait"
    LAUNCH = "launch"
    KILL = "kill"
    FINISHED = "finished"
    FAILED = "failed"


class State(Enum):
    STARTING = "starting"          # launch requested, game not seen yet
    RUNNING = "running"
    RESTARTING = "restarting"      # waiting for the old process to go, then the delay
    COMPLETING = "completing"      # NGIO deleted the trigger; waiting for the game to close
    FINISHED = "finished"
    FAILED = "failed"


@dataclass
class WatchConfig:
    boot_seconds: float = 15 * 60       # launch to first progress
    stall_seconds: float = 10 * 60      # no progress once it has started
    restart_delay_seconds: float = 10
    max_restarts: int = 20
    appear_seconds: float = 120         # launch to the game process existing at all
    exit_grace_seconds: float = 120     # NGIO closes the game itself when it finishes
    dead_checks: int = 2                # consecutive "not alive" ticks before calling it a crash


@dataclass
class Observation:
    now: float
    trigger_exists: bool
    trigger_size: int
    game_alive: bool


@dataclass
class SeasonWatch:
    config: WatchConfig = field(default_factory=WatchConfig)
    state: State = State.STARTING
    restarts: int = 0
    launched_at: float = 0.0
    last_progress_at: float | None = None
    last_size: int = -1
    dead_streak: int = 0
    restart_after: float = 0.0
    completing_since: float = 0.0
    reason: str = ""

    def start(self, now: float) -> Action:
        self.state = State.STARTING
        self.launched_at = now
        self.last_progress_at = None
        self.dead_streak = 0
        return Action.LAUNCH

    def _restart(self, now: float, why: str, alive: bool) -> Action:
        self.restarts += 1
        if self.restarts > self.config.max_restarts:
            self.state = State.FAILED
            self.reason = f"{why}; gave up after {self.config.max_restarts} restarts"
            return Action.KILL if alive else Action.FAILED
        self.state = State.RESTARTING
        self.reason = why
        self.restart_after = now + self.config.restart_delay_seconds
        return Action.KILL if alive else Action.WAIT

    def tick(self, o: Observation) -> Action:
        s = self.state
        if s is State.FINISHED:
            return Action.FINISHED
        if s is State.FAILED:
            return Action.KILL if o.game_alive else Action.FAILED

        # NGIO deletes the trigger when the cache is complete. Checked first, so a game that
        # finishes and closes in the same tick is not mistaken for a crash.
        if not o.trigger_exists and s in (State.STARTING, State.RUNNING):
            self.state = State.COMPLETING
            self.completing_since = o.now
            s = self.state
        if s is State.COMPLETING:
            if not o.game_alive:
                self.state = State.FINISHED
                return Action.FINISHED
            if o.now - self.completing_since > self.config.exit_grace_seconds:
                return Action.KILL
            return Action.WAIT

        if s is State.RESTARTING:
            if o.game_alive:
                return Action.KILL
            if o.now < self.restart_after:
                return Action.WAIT
            return self.start(o.now)

        # STARTING or RUNNING, trigger present.
        if o.trigger_size != self.last_size:
            if self.last_size != -1:
                self.last_progress_at = o.now
            self.last_size = o.trigger_size

        if s is State.STARTING:
            if o.game_alive:
                self.state = State.RUNNING
                self.dead_streak = 0
                return Action.WAIT
            if o.now - self.launched_at > self.config.appear_seconds:
                return self._restart(o.now, "the game did not start", False)
            return Action.WAIT

        # RUNNING
        if not o.game_alive:
            self.dead_streak += 1
            if self.dead_streak >= self.config.dead_checks:
                return self._restart(o.now, "the game closed before finishing (crash)", False)
            return Action.WAIT
        self.dead_streak = 0
        if self.last_progress_at is None:
            if o.now - self.launched_at > self.config.boot_seconds:
                return self._restart(o.now, "no progress since launch", True)
        elif o.now - self.last_progress_at > self.config.stall_seconds:
            return self._restart(o.now, "progress stopped (hang)", True)
        return Action.WAIT
