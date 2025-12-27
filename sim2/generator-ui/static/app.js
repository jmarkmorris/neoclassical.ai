const state = {
  base: null,
  baseName: null,
  generated: null,
  preview: [],
  meta: null,
  extent: 2,
};

const $ = (sel) => document.querySelector(sel);

const baseSelect = $("#baseSelect");
const seedInput = $("#seed");
const outputNameInput = $("#outputName");
const countPInput = $("#countP");
const countEInput = $("#countE");
const posType = $("#posType");
const posMaxRadius = $("#posMaxRadius");
const ringRadius = $("#ringRadius");
const ringThickness = $("#ringThickness");
const annulusInner = $("#annulusInner");
const annulusOuter = $("#annulusOuter");
const gaussianStd = $("#gaussianStd");
const clusterCount = $("#clusterCount");
const clusterSpread = $("#clusterSpread");
const clusterRadius = $("#clusterRadius");
const spiralTurns = $("#spiralTurns");
const spiralRadius = $("#spiralRadius");
const spiralJitter = $("#spiralJitter");
const velType = $("#velType");
const velMin = $("#velMin");
const velMax = $("#velMax");
const velMean = $("#velMean");
const velStd = $("#velStd");
const headingMode = $("#headingMode");
const minSep = $("#minSep");
const excludeRadius = $("#excludeRadius");
const moverType = $("#moverType");
const pathName = $("#pathName");
const generateBtn = $("#generateBtn");
const saveBtn = $("#saveBtn");
const downloadBtn = $("#downloadBtn");
const copySpecBtn = $("#copySpecBtn");
const copyJsonBtn = $("#copyJsonBtn");
const statusLine = $("#status");
const specOutput = $("#specOutput");
const jsonOutput = $("#jsonOutput");
const canvas = $("#previewCanvas");
const baseName = $("#baseName");
const worldSize = $("#worldSize");
const worldExtent = $("#worldExtent");

function setStatus(msg, isError = false) {
  statusLine.textContent = msg;
  statusLine.style.color = isError ? "#c33" : "#5c5c5c";
}

function toNumber(value, fallback = 0) {
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
}

function buildSpec() {
  const spec = {
    base: baseSelect.value,
    seed: toNumber(seedInput.value, 1),
    counts: {
      p: Math.max(0, parseInt(countPInput.value || "0", 10)),
      e: Math.max(0, parseInt(countEInput.value || "0", 10)),
    },
    position: {
      type: posType.value,
      max_radius: posMaxRadius.value ? toNumber(posMaxRadius.value) : null,
      ring_radius: toNumber(ringRadius.value),
      ring_thickness: toNumber(ringThickness.value),
      annulus_inner: toNumber(annulusInner.value),
      annulus_outer: toNumber(annulusOuter.value),
      gaussian_std: toNumber(gaussianStd.value),
      clusters: parseInt(clusterCount.value || "0", 10),
      cluster_spread: toNumber(clusterSpread.value),
      cluster_radius: toNumber(clusterRadius.value),
      spiral_turns: toNumber(spiralTurns.value),
      spiral_radius: toNumber(spiralRadius.value),
      spiral_jitter: toNumber(spiralJitter.value),
    },
    velocity: {
      type: velType.value,
      min: toNumber(velMin.value),
      max: toNumber(velMax.value),
      mean: toNumber(velMean.value),
      std: toNumber(velStd.value),
    },
    heading: {
      mode: headingMode.value,
    },
    constraints: {
      min_separation: toNumber(minSep.value),
      exclude_radius: toNumber(excludeRadius.value),
    },
    template: {
      mover: moverType.value,
    },
    output_name: outputNameInput.value,
  };

  if (moverType.value === "analytic" && pathName.value) {
    spec.template.path = pathName.value;
  }

  return spec;
}

function updateSpecOutput() {
  const spec = buildSpec();
  specOutput.value = JSON.stringify(spec, null, 2);
}

function updateOptionGroups() {
  document.querySelectorAll(".option-group[data-pos]").forEach((group) => {
    const types = group.dataset.pos.split(" ");
    group.style.display = types.includes(posType.value) ? "block" : "none";
  });
  document.querySelectorAll(".option-group[data-vel]").forEach((group) => {
    const types = group.dataset.vel.split(" ");
    group.style.display = types.includes(velType.value) ? "block" : "none";
  });
}

function fetchBases() {
  fetch("/api/bases")
    .then((res) => res.json())
    .then((data) => {
      baseSelect.innerHTML = "";
      data.bases.forEach((name) => {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        baseSelect.appendChild(opt);
      });
      if (data.default) {
        baseSelect.value = data.default;
      }
      loadBase();
    })
    .catch((err) => {
      setStatus(`Failed to load base list: ${err}`, true);
    });
}

function loadBase() {
  if (!baseSelect.value) {
    return;
  }
  fetch(`/api/base?name=${encodeURIComponent(baseSelect.value)}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        setStatus(data.error, true);
        return;
      }
      state.base = data.base;
      state.baseName = baseSelect.value;
      const directives = (data.base || {}).directives || {};
      const world = directives.world_size || (directives.domain_half_extent ? directives.domain_half_extent * 2 : null);
      const extent = directives.domain_half_extent || (directives.world_size ? directives.world_size / 2 : 2);
      state.extent = extent;
      baseName.textContent = baseSelect.value;
      worldSize.textContent = world ? world.toFixed(2) : "-";
      worldExtent.textContent = extent.toFixed(2);
      updateSpecOutput();
    })
    .catch((err) => setStatus(`Failed to load base: ${err}`, true));
}

function drawPreview() {
  const ctx = canvas.getContext("2d");
  const { width, height } = canvas.getBoundingClientRect();
  canvas.width = Math.floor(width * window.devicePixelRatio);
  canvas.height = Math.floor(height * window.devicePixelRatio);
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#f9f8f4";
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = "rgba(0,0,0,0.1)";
  ctx.lineWidth = 1;
  ctx.strokeRect(6, 6, width - 12, height - 12);

  ctx.strokeStyle = "rgba(0,0,0,0.08)";
  ctx.beginPath();
  ctx.moveTo(width / 2, 6);
  ctx.lineTo(width / 2, height - 6);
  ctx.moveTo(6, height / 2);
  ctx.lineTo(width - 6, height / 2);
  ctx.stroke();

  if (!state.preview || state.preview.length === 0) {
    return;
  }

  const extent = state.extent || 2;
  const maxSpeed = Math.max(
    ...state.preview.map((p) => p.speed || 0),
    toNumber(velMax.value, 0.2),
  );
  const arrowMax = Math.min(width, height) * 0.06;

  state.preview.forEach((p) => {
    const xNorm = (p.x + extent) / (2 * extent);
    const yNorm = (p.y + extent) / (2 * extent);
    const x = 6 + xNorm * (width - 12);
    const y = 6 + yNorm * (height - 12);

    const color = p.polarity === "p" ? "#e84b4b" : "#3b6eea";
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();

    const headingRad = (p.heading_deg * Math.PI) / 180;
    const dx = Math.cos(headingRad);
    const dy = -Math.sin(headingRad);
    const len = maxSpeed > 0 ? (p.speed / maxSpeed) * arrowMax : 0;
    const tipX = x + dx * len;
    const tipY = y + dy * len;

    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(tipX, tipY);
    ctx.stroke();

    const head = 6;
    const angle = Math.atan2(dy, dx);
    ctx.beginPath();
    ctx.moveTo(tipX, tipY);
    ctx.lineTo(tipX - head * Math.cos(angle - Math.PI / 6), tipY - head * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(tipX - head * Math.cos(angle + Math.PI / 6), tipY - head * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();
  });
}

function generatePreview() {
  const spec = buildSpec();
  updateSpecOutput();
  setStatus("Generating...");

  fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(spec),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        setStatus(data.error, true);
        return;
      }
      state.generated = data.payload;
      state.preview = data.preview || [];
      state.meta = data.meta || {};
      jsonOutput.value = JSON.stringify(state.generated, null, 2);
      drawPreview();
      setStatus("Preview updated.");
    })
    .catch((err) => setStatus(`Generate failed: ${err}`, true));
}

function saveJson() {
  if (!state.generated) {
    setStatus("Nothing to save yet.", true);
    return;
  }
  const name = outputNameInput.value || "generated.json";
  fetch("/api/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, payload: state.generated }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        setStatus(data.error, true);
        return;
      }
      setStatus(`Saved to json/${data.saved}`);
    })
    .catch((err) => setStatus(`Save failed: ${err}`, true));
}

function downloadJson() {
  if (!state.generated) {
    setStatus("Nothing to download yet.", true);
    return;
  }
  const data = JSON.stringify(state.generated, null, 2);
  const blob = new Blob([data], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = outputNameInput.value || "generated.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(a.href);
  setStatus("Downloaded JSON.");
}

function copyText(text) {
  if (!navigator.clipboard) {
    setStatus("Clipboard API not available.", true);
    return;
  }
  navigator.clipboard.writeText(text).then(
    () => setStatus("Copied to clipboard."),
    () => setStatus("Clipboard copy failed.", true),
  );
}

function copySpec() {
  copyText(specOutput.value || "");
}

function copyJson() {
  copyText(jsonOutput.value || "");
}

window.addEventListener("resize", () => {
  if (state.preview.length) {
    drawPreview();
  }
});

baseSelect.addEventListener("change", loadBase);
posType.addEventListener("change", updateOptionGroups);
velType.addEventListener("change", updateOptionGroups);
posType.addEventListener("change", updateSpecOutput);
velType.addEventListener("change", updateSpecOutput);

[seedInput, outputNameInput, countPInput, countEInput, posMaxRadius, ringRadius, ringThickness, annulusInner,
  annulusOuter, gaussianStd, clusterCount, clusterSpread, clusterRadius, spiralTurns, spiralRadius, spiralJitter,
  velMin, velMax, velMean, velStd, headingMode, minSep, excludeRadius, moverType, pathName]
  .forEach((el) => {
    el.addEventListener("input", updateSpecOutput);
  });

generateBtn.addEventListener("click", generatePreview);
saveBtn.addEventListener("click", saveJson);
downloadBtn.addEventListener("click", downloadJson);
copySpecBtn.addEventListener("click", copySpec);
copyJsonBtn.addEventListener("click", copyJson);

updateOptionGroups();
fetchBases();
updateSpecOutput();
