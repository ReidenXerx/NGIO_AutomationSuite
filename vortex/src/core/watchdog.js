"use strict";
/**
 * Watch one season's precache run and decide when to relaunch, kill or stop. A port of the MO2
 * plugin's core/watchdog.py with the same rules and the same tests:
 * - PrecacheGrass.txt grows by a line per finished cell; NGIO deletes it when the cache is done.
 * - Before the first progress a long boot limit applies; after it, the shorter stall limit.
 * - A crash is confirmed on consecutive "not alive" checks; the trigger vanishing wins over that.
 */

const Action = Object.freeze({ WAIT: "wait", LAUNCH: "launch", KILL: "kill", FINISHED: "finished", FAILED: "failed" });
const State = Object.freeze({
  STARTING: "starting", RUNNING: "running", RESTARTING: "restarting",
  COMPLETING: "completing", FINISHED: "finished", FAILED: "failed",
});

const DEFAULTS = Object.freeze({
  bootSeconds: 15 * 60,
  stallSeconds: 10 * 60,
  restartDelaySeconds: 10,
  maxRestarts: 20,
  appearSeconds: 120,
  exitGraceSeconds: 120,
  deadChecks: 2,
});

class SeasonWatch {
  constructor(config = {}) {
    this.config = { ...DEFAULTS, ...config };
    this.state = State.STARTING;
    this.restarts = 0;
    this.launchedAt = 0;
    this.lastProgressAt = null;
    this.lastSize = -1;
    this.deadStreak = 0;
    this.restartAfter = 0;
    this.completingSince = 0;
    this.reason = "";
  }

  start(now) {
    this.state = State.STARTING;
    this.launchedAt = now;
    this.lastProgressAt = null;
    this.deadStreak = 0;
    return Action.LAUNCH;
  }

  restart(now, why, alive) {
    this.restarts += 1;
    if (this.restarts > this.config.maxRestarts) {
      this.state = State.FAILED;
      this.reason = `${why}; gave up after ${this.config.maxRestarts} restarts`;
      return alive ? Action.KILL : Action.FAILED;
    }
    this.state = State.RESTARTING;
    this.reason = why;
    this.restartAfter = now + this.config.restartDelaySeconds;
    return alive ? Action.KILL : Action.WAIT;
  }

  /** o: { now, triggerExists, triggerSize, gameAlive } — `now` in seconds. */
  tick(o) {
    let s = this.state;
    const c = this.config;
    if (s === State.FINISHED) return Action.FINISHED;
    if (s === State.FAILED) return o.gameAlive ? Action.KILL : Action.FAILED;

    if (!o.triggerExists && (s === State.STARTING || s === State.RUNNING)) {
      this.state = State.COMPLETING;
      this.completingSince = o.now;
      s = this.state;
    }
    if (s === State.COMPLETING) {
      if (!o.gameAlive) {
        this.state = State.FINISHED;
        return Action.FINISHED;
      }
      return o.now - this.completingSince > c.exitGraceSeconds ? Action.KILL : Action.WAIT;
    }

    if (s === State.RESTARTING) {
      if (o.gameAlive) return Action.KILL;
      if (o.now < this.restartAfter) return Action.WAIT;
      return this.start(o.now);
    }

    if (o.triggerSize !== this.lastSize) {
      if (this.lastSize !== -1) this.lastProgressAt = o.now;
      this.lastSize = o.triggerSize;
    }

    if (s === State.STARTING) {
      if (o.gameAlive) {
        this.state = State.RUNNING;
        this.deadStreak = 0;
        return Action.WAIT;
      }
      if (o.now - this.launchedAt > c.appearSeconds) return this.restart(o.now, "the game did not start", false);
      return Action.WAIT;
    }

    if (!o.gameAlive) {
      this.deadStreak += 1;
      if (this.deadStreak >= c.deadChecks) return this.restart(o.now, "the game closed before finishing (crash)", false);
      return Action.WAIT;
    }
    this.deadStreak = 0;
    if (this.lastProgressAt === null) {
      if (o.now - this.launchedAt > c.bootSeconds) return this.restart(o.now, "no progress since launch", true);
    } else if (o.now - this.lastProgressAt > c.stallSeconds) {
      return this.restart(o.now, "progress stopped (hang)", true);
    }
    return Action.WAIT;
  }
}

module.exports = { Action, State, SeasonWatch, DEFAULTS };
