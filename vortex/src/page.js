"use strict";
/** The NGIO Grass Cache page: what will happen, what is missing, and how the run is going. */
const React = require("react");
const { MainPage } = require("vortex-api");
const { FOUR, NO_SEASONS } = require("./runner");

const h = React.createElement;
const MARK = { ok: "✔", warn: "⚠", error: "✖" };
const COLOR = { ok: "#3c9a3c", warn: "#c08a00", error: "#d9534f" };
const TIMING = [
  ["bootMinutes", "Wait for the first cell (minutes)", 15, 1, 120],
  ["stallMinutes", "Restart when no new cell for (minutes)", 10, 1, 120],
  ["restartDelaySeconds", "Pause before restarting (seconds)", 10, 0, 600],
  ["maxRestarts", "Restarts allowed per season", 20, 0, 500],
];
const SETTINGS_KEY = "ngio-grass-timing";

function loadTiming() {
  const base = Object.fromEntries(TIMING.map(([k, , d]) => [k, d]));
  try { return { ...base, ...JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}") }; } catch { return base; }
}

class GrassPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      mode: "four", seasons: { winter: true, spring: true, summer: true, autumn: true },
      lod: false, lodFrom: "winter", timing: loadTiming(), checks: [], checking: false, error: "",
    };
  }

  componentDidMount() {
    this.mounted = true;
    this.off = this.props.runner.onChange(() => this.forceUpdate());
    void this.refreshChecks();
  }

  componentWillUnmount() { this.mounted = false; if (this.off) this.off(); }

  safeSetState(update, cb) { if (this.mounted) this.setState(update, cb); }

  async refreshChecks() {
    const { runner } = this.props;
    if (runner.running) return;
    this.safeSetState({ checking: true });
    let checks = [];
    try {
      checks = await runner.preflight(this.state.mode === "four");
    } catch (e) {
      checks = [{ level: "error", text: `Checks failed: ${e.message}` }];
    }
    if (!this.picked().length) checks.push({ level: "error", text: "Pick at least one season." });
    this.unfinishedPlan = runner.running ? null : runner.unfinished();
    this.safeSetState({ checks, checking: false });
  }

  picked() {
    if (this.state.mode === "none") return [NO_SEASONS];
    return FOUR.filter((s) => this.state.seasons[s.key]);
  }

  config() {
    const t = this.state.timing;
    try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(t)); } catch { /* not important */ }
    return { bootSeconds: t.bootMinutes * 60, stallSeconds: t.stallMinutes * 60, restartDelaySeconds: t.restartDelaySeconds, maxRestarts: t.maxRestarts };
  }

  async start(resume) {
    const { runner } = this.props;
    this.setState({ error: "" });
    try {
      let plan;
      if (resume) {
        plan = runner.unfinished();
        if (!plan) throw new Error("there is no unfinished run to resume");
      } else {
        const picked = this.picked();
        const lodFrom = this.state.mode === "four" && this.state.lod
          ? (picked.find((s) => s.key === this.state.lodFrom) ?? picked[0] ?? null) : null;
        plan = { seasons: this.picked(), lodFrom };
      }
      plan.config = this.config();
      runner.log(`Run: ${plan.seasons.map((s) => s.name).join(", ")}.${resume ? " Resuming." : ""}`);
      await runner.start(plan, resume);
    } catch (e) {
      this.safeSetState({ error: `Could not start: ${e.message}` });
    }
  }

  async fix(check) {
    try { await check.fix(); } catch (e) { this.props.runner.log(`Could not apply the fix: ${e.message}`); }
    void this.refreshChecks();
  }

  renderOptions(disabled) {
    const s = this.state;
    const radio = (value, label) => h("label", { style: { display: "block", fontWeight: "normal" } },
      h("input", { type: "radio", name: "ngio-mode", checked: s.mode === value, disabled,
        onChange: () => this.setState({ mode: value }, () => void this.refreshChecks()) }), " ", label);
    return h("fieldset", { style: { marginBottom: 12 } },
      h("legend", null, "What to generate"),
      radio("four", "Four seasons (Seasons of Skyrim)"),
      h("div", { style: { marginLeft: 22 } }, FOUR.map((x) => h("label", { key: x.key, style: { marginRight: 14, fontWeight: "normal" } },
        h("input", { type: "checkbox", checked: s.seasons[x.key], disabled: disabled || s.mode !== "four",
          onChange: (e) => this.setState({ seasons: { ...s.seasons, [x.key]: e.target.checked } }, () => void this.refreshChecks()) }),
        " ", x.name))),
      radio("none", "No seasons: one cache"),
      h("label", { style: { fontWeight: "normal" } },
        h("input", { type: "checkbox", checked: s.lod, disabled: disabled || s.mode !== "four", onChange: (e) => this.setState({ lod: e.target.checked }) }),
        " Also copy one season without its suffix, for DynDOLOD grass LOD: "),
      h("select", { value: s.lodFrom, disabled: disabled || s.mode !== "four", onChange: (e) => this.setState({ lodFrom: e.target.value }) },
        FOUR.filter((x) => s.seasons[x.key]).map((x) => h("option", { key: x.key, value: x.key }, x.name))));
  }

  renderTiming(disabled) {
    const t = this.state.timing;
    return h("fieldset", { style: { marginBottom: 12 } },
      h("legend", null, "When to restart the game"),
      TIMING.map(([key, label, , min, max]) => h("div", { key, style: { marginBottom: 4 } },
        h("label", { style: { fontWeight: "normal", minWidth: 280, display: "inline-block" } }, label),
        h("input", { type: "number", min, max, value: t[key], disabled, style: { width: 80 },
          onChange: (e) => this.setState({ timing: { ...t, [key]: Math.max(min, Math.min(max, Number(e.target.value) || 0)) } }) }))));
  }

  renderChecks() {
    return h("fieldset", { style: { marginBottom: 12 } },
      h("legend", null, "Before you start"),
      this.state.checks.map((c, i) => h("div", { key: i, style: { display: "flex", gap: 8, marginBottom: 6, alignItems: "flex-start" } },
        h("span", { style: { color: COLOR[c.level], fontWeight: "bold", width: 16 } }, MARK[c.level]),
        h("span", { style: { flex: 1 } }, c.text),
        c.fix ? h("button", { className: "btn btn-default btn-sm", onClick: () => void this.fix(c) }, c.fixLabel) : null)),
      h("button", { className: "btn btn-default btn-sm", disabled: this.state.checking, onClick: () => void this.refreshChecks() },
        this.state.checking ? "Checking..." : "Check again"));
  }

  renderProgress() {
    const rows = this.props.runner.results;
    if (!rows.length) return null;
    return h("table", { className: "table table-condensed", style: { maxWidth: 640 } },
      h("thead", null, h("tr", null, ["Season", "State", "Cells done", "Restarts", "Cache files"].map((x) => h("th", { key: x }, x)))),
      h("tbody", null, rows.map((r) => h("tr", { key: r.season.key },
        h("td", null, r.season.name), h("td", null, r.state), h("td", null, r.cells), h("td", null, r.restarts), h("td", null, r.files || "")))));
  }

  render() {
    const { runner } = this.props;
    const running = runner.running;
    const blocked = this.state.checks.some((c) => c.level === "error");
    const unfinished = !running && this.unfinishedPlan;
    return h(MainPage, null, h(MainPage.Body, null, h("div", { style: { padding: 16, overflowY: "auto", height: "100%" } },
      h("h2", null, "NGIO Grass Cache"),
      h("p", { style: { maxWidth: 760 } },
        "Generates No Grass In Objects' grass cache for each season you pick, one after another. Skyrim starts through its "
        + "script extender, is restarted after a crash or a hang, and every season becomes its own mod. Your own mods are not "
        + "changed: the run's settings go into a temporary mod that is removed afterwards. You can leave it running overnight."),
      this.renderOptions(running),
      this.renderTiming(running),
      running ? null : this.renderChecks(),
      h("div", { style: { margin: "12px 0" } },
        h("button", { className: "btn btn-primary", disabled: running || blocked || this.state.checking, onClick: () => void this.start(false) }, "Start"), " ",
        unfinished ? h("button", { className: "btn btn-default", disabled: blocked, onClick: () => void this.start(true) }, "Resume unfinished run") : null, " ",
        h("button", { className: "btn btn-default", disabled: !running, onClick: () => void runner.stopRun(true).then(() => this.refreshChecks()) }, "Stop")),
      this.state.error ? h("div", { className: "alert alert-danger" }, this.state.error) : null,
      runner.finished ? h("div", { className: "alert alert-success" }, "The grass cache is ready. Its mods are enabled and deployed.") : null,
      this.renderProgress(),
      h("pre", { style: { maxHeight: 280, overflowY: "auto", whiteSpace: "pre-wrap", fontSize: 12 } }, runner.logLines.join("\n") || "The log appears here."),
      h("div", { style: { color: "gray", fontSize: 12 } }, `This log is also saved to ${runner.logFile()}`))));
  }
}

module.exports = { GrassPage };
