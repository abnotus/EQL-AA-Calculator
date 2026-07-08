// Entry point: wires everything together and boots the app on DOMContentLoaded.

import { loadLocal, applyLoaded, DISCLAIMER_DISMISSED_KEY } from "./state.js";
import { cacheDom, el } from "./dom.js";
import { populateStaticControls, renderAll } from "./render.js";
import { wireEvents } from "./events.js";

function init() {
  cacheDom();
  populateStaticControls();
  applyLoaded(loadLocal());
  wireEvents();
  try {
    if (!localStorage.getItem(DISCLAIMER_DISMISSED_KEY)) el.disclaimerBanner.classList.remove("hidden");
  } catch (e) {
    el.disclaimerBanner.classList.remove("hidden");
  }
  renderAll();
}

document.addEventListener("DOMContentLoaded", init);
