"use strict";
/**
 * NGIO Grass Cache for Vortex: a page (Skyrim SE / VR only) that generates the No Grass In Objects
 * grass cache for every season in one unattended run. Same rules as the MO2 plugin in ../mo2.
 */
const { selectors } = require("vortex-api");
const { Runner } = require("./src/runner");
const { GrassPage } = require("./src/page");

const GAMES = ["skyrimse", "skyrimvr"];

function main(context) {
  let runner;
  const getRunner = () => (runner = runner || new Runner(context.api));

  context.registerMainPage("settings", "NGIO Grass Cache", GrassPage, {
    id: "ngio-grass-cache",
    group: "per-game",
    visible: () => GAMES.includes(selectors.activeGameId(context.api.getState())),
    props: () => ({ runner: getRunner() }),
  });

  context.once(() => {
    // Closing Vortex mid-run: stop the game and move PrecacheGrass.txt out of the game folder, so
    // NGIO does not start precaching on the next normal launch. Synchronous: the window is going.
    window.addEventListener("beforeunload", () => {
      if (runner && runner.running) runner.emergencyStop();
    });
  });
  return true;
}

module.exports = { default: main };
