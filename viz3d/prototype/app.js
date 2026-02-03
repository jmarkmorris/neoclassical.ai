import * as THREE from "./vendor/three/three.module.js";
import { CSS2DRenderer, CSS2DObject } from "./vendor/three/CSS2DRenderer.js";

const app = document.getElementById("app");
const canvas = document.getElementById("viz");
const navUpButton = document.getElementById("nav-up");
const sceneLabel = document.getElementById("scene-label");
const sceneSearch = document.getElementById("scene-search");
const sceneSearchToggle = document.getElementById("scene-search-toggle");
const sceneSearchPanel = document.getElementById("scene-search-panel");
const sceneSearchInput = document.getElementById("scene-search-input");
const sceneSearchResults = document.getElementById("scene-search-results");
const hoverTooltip = document.getElementById("hover-tooltip");
const detailPanel = document.getElementById("detail-panel");
const detailTitle = document.getElementById("detail-title");
const detailBody = document.getElementById("detail-body");
const detailClose = document.getElementById("detail-close");
const homeButton = document.getElementById("home-button");
const docButton = document.getElementById("doc-button");
const elementLegend = document.getElementById("element-legend");
const elementLegendItems = elementLegend
  ? Array.from(elementLegend.querySelectorAll("[data-scene]"))
  : [];
let elementInfoPinned = false;
const markdownPanel = document.getElementById("markdown-panel");
const markdownTitle = document.getElementById("markdown-title");
const markdownContent = document.getElementById("markdown-content");
const markdownBody = document.getElementById("markdown-body");
const markdownClose = document.getElementById("markdown-close");
const markdownLayoutToggle = document.getElementById("markdown-layout-toggle");
const markdownDocButton = document.getElementById("markdown-doc-button");
const mathJaxScript = document.getElementById("mathjax-script");
const periodicOverlay = document.getElementById("periodic-overlay");
const periodicGrid = document.getElementById("periodic-grid");
const periodicLegend = document.getElementById("periodic-legend");
const composerOverlay = document.getElementById("composer-overlay");
const composerDocsButton = document.getElementById("composer-docs-button");
const composerTabs = composerOverlay
  ? Array.from(composerOverlay.querySelectorAll(".composer-tab"))
  : [];
const composerPanels = composerOverlay
  ? Array.from(composerOverlay.querySelectorAll(".composer-panel"))
  : [];
const hud = document.getElementById("hud");
const infoDrawer = document.getElementById("info-drawer");
const infoBody = document.getElementById("info-body");
const rootLayoutMarginPx = { x: 160, y: 140 };

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight, false);
renderer.domElement.style.touchAction = "none";

const labelRenderer = new CSS2DRenderer();
labelRenderer.setSize(window.innerWidth, window.innerHeight);
labelRenderer.domElement.style.position = "absolute";
labelRenderer.domElement.style.top = "0";
labelRenderer.domElement.style.left = "0";
labelRenderer.domElement.style.pointerEvents = "none";
labelRenderer.domElement.style.zIndex = "2";
app.appendChild(labelRenderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color("#0b0e1a");

const camera = new THREE.OrthographicCamera();
camera.position.set(0, 0, 30);
camera.zoom = 1;

const baseViewHeight = 26;
const worldGroup = new THREE.Group();
scene.add(worldGroup);

const levelConfigs = {};
const linkColors = {
  reactant: "#9fb0e1",
  product: "#d5dcff",
  emission: "#f0d39a",
  default: "#c5cee8",
};
const colorTokens = {
  RED: "#ff0000",
  BLUE: "#0000ff",
  PURPLE: "#4b0082",
};
const defaultAutoMarkdownPalette = [
  "#243d8f",
  "#2f6b6f",
  "#5a1f2e",
  "#4b0082",
  "#3a5f9f",
  "#2f4f7a",
  "#7a4a1f",
  "#1c2a4f",
  "#3c6a7a",
  "#3f6a5a",
  "#6a3c3c",
];
const linkStyle = {
  minLength: 0.7,
  tipClearance: 0.12,
  headLengthMin: 0.14,
  headLengthMax: 0.24,
  headWidthFactor: 0.4,
  lineOpacity: 0.6,
  headOpacity: 0.85,
};
const binaryStyle = {
  shellOpacity: 0.5,
  shellOutlineOpacity: 0.28,
  ringOpacity: 0.35,
  ringTubeFactor: 0.04,
  particleRadiusFactor: 0.08,
  positrinoColor: "#ff0000",
  electrinoColor: "#0000ff",
  baseOrbitSpeed: 0.18,
};
const generationTransitions = {
  electron: { nextScene: "json/standard-model-particles/muon.json", nextLabel: "Muon" },
  muon: { nextScene: "json/standard-model-particles/tau.json", nextLabel: "Tau" },
  neutrino: {
    nextScene: "json/standard-model-particles/muon_neutrino.json",
    nextLabel: "Muon Neutrino",
  },
  muon_neutrino: {
    nextScene: "json/standard-model-particles/tau_neutrino.json",
    nextLabel: "Tau Neutrino",
  },
  up_quark: { nextScene: "json/standard-model-particles/charm.json", nextLabel: "Charm" },
  charm: { nextScene: "json/standard-model-particles/top.json", nextLabel: "Top" },
  down_quark: { nextScene: "json/standard-model-particles/strange.json", nextLabel: "Strange" },
  strange: { nextScene: "json/standard-model-particles/bottom.json", nextLabel: "Bottom" },
};

const motionHandlers = {
  orbit: (node, level, timeSeconds) => {
    const orbit = node.data.orbit;
    if (!orbit) {
      return;
    }
    const centerNode =
      level.nodeByName.get(orbit.center) ?? level.nodeById.get(orbit.center);
    const centerPos = centerNode
      ? centerNode.group.position
      : Array.isArray(orbit.center)
        ? new THREE.Vector3(
            orbit.center[0] ?? 0,
            orbit.center[1] ?? 0,
            orbit.center[2] ?? 0
          )
        : new THREE.Vector3(0, 0, 0);
    const yScale =
      orbit.shape === "ellipsoid" ? orbit.yScale ?? 0.85 : 1;
    const angle = timeSeconds * orbit.speed + (orbit.phase ?? 0);
    const x = centerPos.x + Math.cos(angle) * orbit.radius;
    const y = centerPos.y + Math.sin(angle) * orbit.radius * yScale;
    node.group.position.set(x, y, 0);
  },
  binaryOrbit: (node, level, timeSeconds) => {
    if (!node.binaryBandData || !node.binaryBandData.length) {
      return;
    }
    node.binaryBandData.forEach((band) => {
      const angle = timeSeconds * band.speed + band.phase;
      const x = Math.cos(angle) * band.radius;
      const y = Math.sin(angle) * band.radius;
      band.positrino.position.set(x, y, 0);
      band.electrino.position.set(-x, -y, 0);
    });
  },
};

const sceneConfigCache = new Map();
const sceneLoadPromises = new Map();
const markdownCache = new Map();
const markdownSectionCache = new Map();
const markdownRenderer =
  typeof window !== "undefined" && window.markdownit
    ? window.markdownit({ html: false, linkify: true, breaks: false })
    : null;
if (markdownRenderer) {
  markdownRenderer.disable("escape");
}
const markdownDirectoryCache = new Map();
const markdownSubdirCache = new Map();
let mathJaxReady = typeof window !== "undefined" && !!window.MathJax?.typesetPromise;
let pendingMathTypeset = false;
let activeMarkdownPath = null;
let markdownTwoColumns = true;
let composerActivePanel = "tree";
let haloSeed = 0;
let infoDrawerOpen = false;
const infoMarkdownPath = "info.md";
const rootScenePath = "json/architrino_assembly_architecture.json";
const metaScenePath = "json/meta/meta.json";
const composerSceneId = "composer";
const composerDocsPath =
  "markdown/architrino-assembly-architecture/ideas-designs/arch-api.md";
const cacheBustToken = Date.now().toString();
let sceneIndex = [];
let sceneIndexReady = false;
const markdownReaderScenes = new Map();
const searchBackStack = [];
const metaBackStack = [];
const composerPanelMap = new Map([
  ["composer_tree", "tree"],
  ["composer_path", "path"],
  ["composer_orbit", "orbit"],
  ["composer_interactions", "interactions"],
  ["composer_preview", "preview"],
  ["composer_export", "export"],
]);
const periodicTableCache = { data: null, ready: false };
let periodicGridBuilt = false;

const levels = new Map();
const navigationStack = [];
let currentLevel = null;

const ringLayoutDefaults = {
  haloScale: 1.18,
  guardBandMin: 0.15,
  guardBandRatio: 0.08,
  startAngle: Math.PI / 2,
};
const standardRingMaxCount = 14;

function maxRingNodeRadius(ringRadius, count) {
  if (!Number.isFinite(ringRadius) || count <= 1) {
    return Infinity;
  }
  const chord = 2 * ringRadius * Math.sin(Math.PI / count);
  const guardBand = Math.max(
    ringLayoutDefaults.guardBandMin,
    chord * ringLayoutDefaults.guardBandRatio
  );
  return (chord - guardBand) / (2 * ringLayoutDefaults.haloScale);
}

function computeRingLayout(nodes) {
  const count = nodes.length;
  if (!count || count > standardRingMaxCount) {
    return null;
  }
  let baseRadius = Math.max(...nodes.map((node) => node.radius ?? 0));
  if (!Number.isFinite(baseRadius) || baseRadius <= 0) {
    baseRadius = 1.6;
  }
  const ringRadius = Math.max(
    6,
    Math.min(count, standardRingMaxCount) * baseRadius * 1.4
  );
  const maxRadius = maxRingNodeRadius(ringRadius, count);
  if (Number.isFinite(maxRadius) && maxRadius > 0) {
    baseRadius = maxRadius;
  }
  const positions = [];
  for (let i = 0; i < count; i += 1) {
    const angle = (i / count) * Math.PI * 2 + ringLayoutDefaults.startAngle;
    positions.push([
      Number((Math.cos(angle) * ringRadius).toFixed(2)),
      Number((Math.sin(angle) * ringRadius).toFixed(2)),
    ]);
  }
  return { ringRadius, nodeRadius: baseRadius, positions };
}

const zoomState = {
  active: false,
  startZoom: 1,
  targetZoom: 1,
  startTime: 0,
  duration: 420,
};

const panTween = {
  active: false,
  start: new THREE.Vector3(),
  target: new THREE.Vector3(),
  startTime: 0,
  duration: 420,
};

const transitionState = {
  active: false,
  mode: null,
  fromLevel: null,
  toLevel: null,
  startTime: 0,
  duration: 2250,
  payload: null,
};

const autoWarpThresholds = {
  inPx: 80,
  cooldownMs: 700,
  lastAt: 0,
};

const labelFadeState = {
  active: false,
  level: null,
  startTime: 0,
  duration: 700,
};

const zoomLimits = { min: 0.35, max: 6 };
const raycaster = new THREE.Raycaster();
const pointerNdc = new THREE.Vector2();
let lastZoomGestureTime = 0;
const detailFieldOrder = [
  { key: "temperature", label: "Typical temperature/energy" },
  { key: "numberDensity", label: "Number density (km^-3)" },
  { key: "classification", label: "Classification" },
];
let activeDetailNodeId = null;
let hoveredDetailNodeId = null;
let hoverTooltipVisible = false;
const periodicCategoryColors = {
  "alkali metal": "#d24d57",
  "alkaline earth metal": "#e67e22",
  "transition metal": "#f39c12",
  "post-transition metal": "#9b59b6",
  metalloid: "#8e44ad",
  "diatomic nonmetal": "#3498db",
  "polyatomic nonmetal": "#2980b9",
  "noble gas": "#1abc9c",
  "lanthanide": "#95a5a6",
  "actinide": "#7f8c8d",
  "unknown": "#556277",
};

if (mathJaxScript) {
  mathJaxScript.addEventListener("load", () => {
    mathJaxReady = true;
    if (pendingMathTypeset) {
      typesetMarkdown();
    }
  });
}

function formatSuperscripts(text) {
  return String(text).replace(/\^(-?\d+)/g, "<sup>$1</sup>");
}

async function listMarkdownFilesInDir(directory) {
  if (!directory) {
    return [];
  }
  const normalized = directory.replace(/\/+$/, "").replace(/^\.?\//, "");
  if (markdownDirectoryCache.has(normalized)) {
    return markdownDirectoryCache.get(normalized);
  }
  try {
    const response = await fetch(appendCacheBust(`${normalized}/`));
    if (!response.ok) {
      markdownDirectoryCache.set(normalized, []);
      return [];
    }
    const html = await response.text();
    const matches = [];
    const hrefRegex = /href="([^"]+\.md)"/gi;
    let match = null;
    while ((match = hrefRegex.exec(html))) {
      matches.push(match[1]);
    }
    const files = Array.from(
      new Set(
        matches
          .map((href) => decodeURIComponent(href))
          .map((href) => href.split("?")[0])
          .map((href) => href.split("#")[0])
          .map((href) => href.replace(/^\.?\//, ""))
          .filter((href) => href.endsWith(".md"))
          .filter((href) => !href.includes("/"))
          .map((href) => `${normalized}/${href}`)
      )
    );
    markdownDirectoryCache.set(normalized, files);
    return files;
  } catch (error) {
    console.warn("Failed to read markdown directory", directory, error);
    markdownDirectoryCache.set(normalized, []);
    return [];
  }
}

async function listMarkdownDirectoriesInDir(directory) {
  if (!directory) {
    return [];
  }
  const normalized = directory.replace(/\/+$/, "").replace(/^\.?\//, "");
  if (markdownSubdirCache.has(normalized)) {
    return markdownSubdirCache.get(normalized);
  }
  try {
    const response = await fetch(appendCacheBust(`${normalized}/`));
    if (!response.ok) {
      markdownSubdirCache.set(normalized, []);
      return [];
    }
    const html = await response.text();
    const matches = [];
    const hrefRegex = /href="([^"]+\/)"/gi;
    let match = null;
    while ((match = hrefRegex.exec(html))) {
      matches.push(match[1]);
    }
    const directories = Array.from(
      new Set(
        matches
          .map((href) => decodeURIComponent(href))
          .map((href) => href.split("?")[0])
          .map((href) => href.split("#")[0])
          .map((href) => href.replace(/^\.?\//, ""))
          .filter((href) => href && href !== "../" && href !== "./")
          .filter((href) => href.endsWith("/"))
          .map((href) => href.replace(/\/$/, ""))
          .filter((href) => !href.includes("/"))
          .map((href) => `${normalized}/${href}`)
      )
    );
    markdownSubdirCache.set(normalized, directories);
    return directories;
  } catch (error) {
    console.warn("Failed to read markdown directories", directory, error);
    markdownSubdirCache.set(normalized, []);
    return [];
  }
}

function titleFromSlug(slug) {
  return slug
    .split(/[-_]+/g)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

async function buildAutoMarkdownNodes(scene, existingNodes) {
  if (!scene?.autoSphereRing || (!scene?.autoMarkdownDirectory && !scene?.autoMarkdownPath)) {
    return [];
  }
  const includeExisting = scene.autoMarkdownIncludeExistingInLayout === true;
  const sectionKey = scene.autoMarkdownSection ?? null;
  let entries = [];
  let useDirectories = false;
  let usedHeadingLevel =
    typeof scene.autoMarkdownHeadingLevel === "number"
      ? scene.autoMarkdownHeadingLevel
      : 3;
  let sectionSubheadings = null;

  if (scene.autoMarkdownPath) {
    const preferredLevels = [usedHeadingLevel];
    if (usedHeadingLevel === 2) {
      preferredLevels.push(3);
    } else if (usedHeadingLevel !== 2) {
      preferredLevels.push(2);
    }
    try {
      const response = await fetch(appendCacheBust(scene.autoMarkdownPath));
      if (response.ok) {
        const text = await response.text();
        let content = text;
        if (sectionKey) {
          const section = extractMarkdownSection(text, sectionKey);
          content = section?.body ?? "";
        }
        const lines = content.split(/\r?\n/);
        for (const level of preferredLevels) {
          const levelEntries = [];
          lines.forEach((line) => {
            const heading = parseMarkdownHeading(line);
            if (heading && heading.level === level) {
              levelEntries.push({ title: heading.title });
            }
          });
          if (levelEntries.length) {
            entries = levelEntries;
            usedHeadingLevel = level;
            break;
          }
        }
        if (!sectionKey && usedHeadingLevel === 2) {
          sectionSubheadings = new Map();
          let currentSection = null;
          text.split(/\r?\n/).forEach((line) => {
            const heading = parseMarkdownHeading(line);
            if (!heading) {
              return;
            }
            if (heading.level === 2) {
              currentSection = heading.title;
              if (!sectionSubheadings.has(currentSection)) {
                sectionSubheadings.set(currentSection, false);
              }
            } else if (heading.level === 3 && currentSection) {
              sectionSubheadings.set(currentSection, true);
            } else if (heading.level <= 2) {
              currentSection = heading.title;
            }
          });
        }
      }
    } catch (error) {
      console.warn("Failed to read markdown file", scene.autoMarkdownPath, error);
    }
  } else {
    useDirectories = scene.autoMarkdownSubdirectories === true;
    entries = useDirectories
      ? (await listMarkdownDirectoriesInDir(scene.autoMarkdownDirectory)).sort()
      : (await listMarkdownFilesInDir(scene.autoMarkdownDirectory)).sort();
  }

  if (Array.isArray(scene.autoMarkdownExcludePaths) && scene.autoMarkdownExcludePaths.length) {
    const exclude = new Set(
      scene.autoMarkdownExcludePaths.map((path) => normalizeMarkdownPath(path))
    );
    entries = entries.filter((entry) => !exclude.has(normalizeMarkdownPath(entry)));
  }

  const defaultIndex = scene.autoMarkdownDefaultIndex === true;
  const indexPaths = Array.isArray(scene.autoMarkdownIndexPaths)
    ? new Set(scene.autoMarkdownIndexPaths.map((path) => normalizeMarkdownPath(path)))
    : null;
  const plainPaths = Array.isArray(scene.autoMarkdownPlainPaths)
    ? new Set(scene.autoMarkdownPlainPaths.map((path) => normalizeMarkdownPath(path)))
    : null;
  const plainSectionPaths = Array.isArray(scene.autoMarkdownPlainSectionPaths)
    ? new Set(scene.autoMarkdownPlainSectionPaths.map((path) => normalizeMarkdownPath(path)))
    : null;
  const defaultSectionDepth =
    typeof scene.autoMarkdownSectionDepth === "number"
      ? scene.autoMarkdownSectionDepth
      : 2;
  const pathOverrides =
    scene.autoMarkdownOverrides && typeof scene.autoMarkdownOverrides === "object"
      ? scene.autoMarkdownOverrides
      : null;

  if (!entries.length && !includeExisting) {
    return [];
  }
  const fileInfos = scene.autoMarkdownPath
    ? entries.map((entry) => ({ title: entry.title }))
    : useDirectories
      ? entries.map((path) => ({ path, isNonEmpty: false }))
      : await Promise.all(
          entries.map(async (path) => {
            try {
              const response = await fetch(appendCacheBust(path));
              if (!response.ok) {
                return { path, isNonEmpty: false };
              }
              const text = await response.text();
              return { path, isNonEmpty: text.trim().length > 0 };
            } catch (error) {
              console.warn("Failed to read markdown file", path, error);
              return { path, isNonEmpty: false };
            }
          })
        );
  const usedIds = new Set(existingNodes.map((node) => node.id));
  let baseRadius =
    typeof scene.autoMarkdownNodeRadius === "number"
      ? scene.autoMarkdownNodeRadius
      : 1.6;
  const existingMaxRadius = includeExisting
    ? existingNodes.reduce(
        (maxRadius, node) => Math.max(maxRadius, node.radius ?? 0),
        0
      )
    : 0;
  const layoutRadius = Math.max(baseRadius, existingMaxRadius);
  const palette =
    Array.isArray(scene.autoMarkdownPalette) && scene.autoMarkdownPalette.length
      ? scene.autoMarkdownPalette
      : defaultAutoMarkdownPalette;
  const baseColor = scene.autoMarkdownColor ?? null;
  const maxRingCount =
    typeof scene.autoMarkdownMaxRingCount === "number"
      ? scene.autoMarkdownMaxRingCount
      : 14;
  const autoEntries = [];
  fileInfos.forEach((info) => {
    const entryName = info.title ?? info.path?.split("/").pop() ?? "";
    const slug = useDirectories
      ? entryName
      : entryName.replace(/\.md$/i, "");
    const id = slug
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "");
    if (!id || usedIds.has(id)) {
      return;
    }
    autoEntries.push({ info, slug, id });
  });
  const layoutCount = includeExisting
    ? existingNodes.length + autoEntries.length
    : autoEntries.length;
  const ringRadius =
    typeof scene.autoMarkdownRingRadius === "number"
      ? scene.autoMarkdownRingRadius
      : Math.max(6, Math.min(layoutCount, maxRingCount) * layoutRadius * 1.4);
  const gridSpacing =
    typeof scene.autoMarkdownGridSpacing === "number"
      ? scene.autoMarkdownGridSpacing
      : layoutRadius * 2.6;
  const useRing = layoutCount <= maxRingCount;
  const columns = useRing ? 1 : Math.ceil(Math.sqrt(layoutCount));
  const rows = useRing ? layoutCount : Math.ceil(layoutCount / columns);
  const startX = useRing ? 0 : -((columns - 1) * gridSpacing) / 2;
  const startY = useRing ? 0 : ((rows - 1) * gridSpacing) / 2;

  if (useRing && layoutCount > 1) {
    const maxRadius = maxRingNodeRadius(ringRadius, layoutCount);
    if (Number.isFinite(maxRadius) && maxRadius > 0 && maxRadius < baseRadius) {
      baseRadius = maxRadius;
    }
  }

  if (includeExisting) {
    existingNodes.forEach((node) => {
      node.radius = baseRadius;
    });
  }

  const positionForIndex = (index) => {
    if (useRing) {
      const orderIndex = layoutCount - 1 - index;
      const angle =
        ringLayoutDefaults.startAngle + (orderIndex / layoutCount) * Math.PI * 2;
      return [Math.cos(angle) * ringRadius, Math.sin(angle) * ringRadius];
    }
    const row = Math.floor(index / columns);
    const col = index % columns;
    return [startX + col * gridSpacing, startY - row * gridSpacing];
  };

  if (includeExisting) {
    existingNodes.forEach((node, index) => {
      const [x, y] = positionForIndex(index);
      node.position = [Number(x.toFixed(2)), Number(y.toFixed(2)), 0];
    });
  }

  const isSectionIndex = !!sectionKey;
  const isTwoLevelRoot = !isSectionIndex && scene.autoMarkdownPath && usedHeadingLevel === 2;

  return autoEntries
    .map((entry, index) => {
      const { info, slug, id } = entry;
      const layoutIndex = includeExisting ? existingNodes.length + index : index;
      const [x, y] = positionForIndex(layoutIndex);
      let color = baseColor ?? palette[index % palette.length] ?? "#3a5a8a";
      if (typeof color === "string" && colorTokens[color]) {
        color = colorTokens[color];
      }
      const nodeName = scene.autoMarkdownPath
        ? info.title ?? titleFromSlug(slug)
        : titleFromSlug(slug);
      const node = {
        id,
        name: nodeName,
        radius: baseRadius,
        position: [Number(x.toFixed(2)), Number(y.toFixed(2)), 0],
        color,
        wrapLabel: scene.wrapLabels ?? true,
      };
      if (scene.autoMarkdownPath) {
        const override = pathOverrides
          ? pathOverrides[normalizeMarkdownPath(scene.autoMarkdownPath)]
          : null;
        const sectionDepth =
          typeof override?.sectionDepth === "number" ? override.sectionDepth : defaultSectionDepth;
        const allowSectionIndex =
          sectionDepth >= 2 &&
          !(plainSectionPaths && plainSectionPaths.has(normalizeMarkdownPath(scene.autoMarkdownPath)));
        const hasSubheadings =
          isTwoLevelRoot && info.title
            ? sectionSubheadings?.get(info.title) === true
            : false;
        if (isTwoLevelRoot && info.title && hasSubheadings && allowSectionIndex) {
          const childScene = ensureMarkdownSectionIndexScene(
            scene.autoMarkdownPath,
            info.title,
            scene
          );
          if (childScene) {
            node.childScene = childScene;
          }
        } else {
          node.markdownPath = scene.autoMarkdownPath;
          node.markdownSection = info.title ?? null;
        }
      } else if (useDirectories) {
        const childScene = ensureMarkdownDirectoryScene(
          info.path,
          scene,
          node.name
        );
        if (childScene) {
          node.childScene = childScene;
        }
      } else if (info.isNonEmpty) {
        const normalizedPath = normalizeMarkdownPath(info.path);
        const override = pathOverrides ? pathOverrides[normalizedPath] : null;
        node.markdownPath = info.path;
        let autoIndex = defaultIndex;
        if (indexPaths && indexPaths.has(normalizedPath)) {
          autoIndex = true;
        }
        if (plainPaths && plainPaths.has(normalizedPath)) {
          autoIndex = false;
        }
        if (override?.mode === "index") {
          autoIndex = true;
        } else if (override?.mode === "doc") {
          autoIndex = false;
        }
        node.markdownAutoIndex = autoIndex;
        if (typeof override?.headingLevel === "number") {
          node.markdownHeadingLevel = override.headingLevel;
        }
        if (override?.columns === 1 || override?.columns === 2) {
          node.markdownColumns = override.columns;
        }
        const sectionDepth =
          typeof override?.sectionDepth === "number" ? override.sectionDepth : defaultSectionDepth;
        const plainSectionList = [];
        if (plainSectionPaths && plainSectionPaths.has(normalizedPath)) {
          plainSectionList.push(info.path);
        }
        if (sectionDepth < 2) {
          plainSectionList.push(info.path);
        }
        if (plainSectionList.length) {
          node.markdownPlainSectionPaths = plainSectionList;
        }
        if (scene.autoMarkdownColumns === 1 || scene.autoMarkdownColumns === 2) {
          node.markdownColumns = scene.autoMarkdownColumns;
        }
      }
      return node;
    })
    .filter(Boolean);
}

function closeDetailPanel() {
  if (!detailPanel) {
    return;
  }
  detailPanel.classList.remove("is-open");
  detailPanel.setAttribute("aria-hidden", "true");
  detailPanel.inert = true;
  activeDetailNodeId = null;
  hoveredDetailNodeId = null;
  if (detailTitle) {
    detailTitle.textContent = "";
  }
  if (detailBody) {
    detailBody.innerHTML = "";
  }
}

function showHoverTooltip(text, x, y) {
  if (!hoverTooltip) {
    return;
  }
  hoverTooltip.textContent = text;
  hoverTooltip.classList.add("is-visible");
  hoverTooltip.setAttribute("aria-hidden", "false");

  const padding = 12;
  const rect = hoverTooltip.getBoundingClientRect();
  let left = x + padding;
  let top = y + padding;
  if (left + rect.width > window.innerWidth - padding) {
    left = x - rect.width - padding;
  }
  if (top + rect.height > window.innerHeight - padding) {
    top = y - rect.height - padding;
  }
  hoverTooltip.style.left = `${left}px`;
  hoverTooltip.style.top = `${top}px`;
  hoverTooltipVisible = true;
}

function hideHoverTooltip() {
  if (!hoverTooltip || !hoverTooltipVisible) {
    return;
  }
  hoverTooltip.classList.remove("is-visible");
  hoverTooltip.setAttribute("aria-hidden", "true");
  hoverTooltipVisible = false;
}

function hideMarkdownPanel() {
  if (!markdownPanel) {
    return;
  }
  markdownPanel.classList.remove("is-open");
  markdownPanel.setAttribute("aria-hidden", "true");
  markdownPanel.inert = true;
  if (markdownTitle) {
    markdownTitle.textContent = "";
  }
  if (markdownBody) {
    markdownBody.innerHTML = "";
  }
  activeMarkdownPath = null;
}

function applyMarkdownLayout() {
  if (!markdownPanel || !markdownLayoutToggle) {
    return;
  }
  markdownPanel.classList.toggle("two-columns", markdownTwoColumns);
  markdownLayoutToggle.setAttribute(
    "aria-label",
    markdownTwoColumns ? "Switch to single column" : "Switch to two columns"
  );
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function normalizeMarkdownKey(text) {
  return String(text)
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function normalizeMarkdownPath(path) {
  return String(path)
    .replace(/\\/g, "/")
    .replace(/^\.?\//, "")
    .toLowerCase();
}

function deriveMarkdownConfig(markdownPolicy) {
  if (!markdownPolicy) {
    return null;
  }
  const derived = {};
  const source = markdownPolicy.source ?? {};
  const sourcePath = typeof source.path === "string" ? source.path : null;
  const sourceType =
    source.type ??
    (sourcePath && sourcePath.toLowerCase().endsWith(".md") ? "file" : "directory");
  if (sourceType === "file" && sourcePath) {
    derived.autoMarkdownPath = sourcePath;
  } else if (sourceType === "directory" && sourcePath) {
    derived.autoMarkdownDirectory = sourcePath;
    derived.autoMarkdownSubdirectories = source.subdirectories === true;
  }

  const layout = markdownPolicy.layout ?? {};
  if (layout.includeExisting !== undefined) {
    derived.autoMarkdownIncludeExistingInLayout = layout.includeExisting === true;
  }
  if (typeof layout.nodeRadius === "number") {
    derived.autoMarkdownNodeRadius = layout.nodeRadius;
  }
  if (typeof layout.ringRadius === "number") {
    derived.autoMarkdownRingRadius = layout.ringRadius;
  }
  if (typeof layout.maxRingCount === "number") {
    derived.autoMarkdownMaxRingCount = layout.maxRingCount;
  }
  if (typeof layout.gridSpacing === "number") {
    derived.autoMarkdownGridSpacing = layout.gridSpacing;
  }
  if (Array.isArray(layout.palette)) {
    derived.autoMarkdownPalette = layout.palette;
  }
  if (typeof layout.color === "string") {
    derived.autoMarkdownColor = layout.color;
  }

  const render = markdownPolicy.render ?? {};
  if (render.defaultMode === "index") {
    derived.autoMarkdownDefaultIndex = true;
  } else if (render.defaultMode === "doc") {
    derived.autoMarkdownDefaultIndex = false;
  }
  if (typeof render.headingLevel === "number") {
    derived.autoMarkdownHeadingLevel = render.headingLevel;
  }
  if (typeof render.sectionDepth === "number") {
    derived.autoMarkdownSectionDepth = render.sectionDepth;
  }
  if (render.columns === 1 || render.columns === 2) {
    derived.autoMarkdownColumns = render.columns;
  }

  if (Array.isArray(markdownPolicy.exclude)) {
    derived.autoMarkdownExcludePaths = markdownPolicy.exclude;
  }

  const overrides = Array.isArray(markdownPolicy.overrides) ? markdownPolicy.overrides : [];
  const indexPaths = [];
  const plainPaths = [];
  const plainSectionPaths = [];
  const perPath = {};
  overrides.forEach((override) => {
    if (!override || typeof override.path !== "string") {
      return;
    }
    const normalized = normalizeMarkdownPath(override.path);
    const record = perPath[normalized] ?? {};
    if (override.mode === "index") {
      indexPaths.push(override.path);
      record.mode = "index";
    } else if (override.mode === "doc") {
      plainPaths.push(override.path);
      record.mode = "doc";
    }
    if (typeof override.headingLevel === "number") {
      record.headingLevel = override.headingLevel;
    }
    if (typeof override.sectionDepth === "number") {
      record.sectionDepth = override.sectionDepth;
      if (override.sectionDepth < 2) {
        plainSectionPaths.push(override.path);
      }
    }
    if (override.columns === 1 || override.columns === 2) {
      record.columns = override.columns;
    }
    perPath[normalized] = record;
  });
  if (indexPaths.length) {
    derived.autoMarkdownIndexPaths = indexPaths;
  }
  if (plainPaths.length) {
    derived.autoMarkdownPlainPaths = plainPaths;
  }
  if (plainSectionPaths.length) {
    derived.autoMarkdownPlainSectionPaths = plainSectionPaths;
  }
  if (Object.keys(perPath).length) {
    derived.autoMarkdownOverrides = perPath;
  }

  return derived;
}

function parseMarkdownHeading(line) {
  const match = line.match(/^(#{2,3})\s+(.*)$/);
  if (!match) {
    const numbered = line.match(/^\*\*(\d+)\.\s+(.+?)\*\*/);
    if (!numbered) {
      return null;
    }
    return { level: 3, title: numbered[2].trim() };
  }
  const level = match[1].length;
  let title = match[2].trim();
  const boldMatch = title.match(/^\*\*(.+?)\*\*/);
  if (boldMatch) {
    title = boldMatch[1].trim();
  }
  return { level, title };
}

function extractMarkdownSection(markdown, sectionKey) {
  const target = normalizeMarkdownKey(sectionKey);
  if (!target) {
    return null;
  }
  const lines = markdown.split(/\r?\n/);
  let sectionTitle = null;
  let start = -1;
  let end = lines.length;
  let startLevel = null;
  for (let i = 0; i < lines.length; i += 1) {
    const heading = parseMarkdownHeading(lines[i]);
    if (!heading) {
      continue;
    }
    const headingKey = normalizeMarkdownKey(heading.title);
    if (start === -1) {
      if (headingKey === target) {
        sectionTitle = heading.title;
        start = i + 1;
        startLevel = heading.level;
      }
      continue;
    }
    if (heading.level <= (startLevel ?? heading.level)) {
      end = i;
      break;
    }
  }
  if (start === -1) {
    return null;
  }
  const body = lines.slice(start, end).join("\n").trim();
  return { title: sectionTitle, body };
}

function typesetMarkdown() {
  if (!markdownBody) {
    return;
  }
  const mathJax = window.MathJax;
  if (!mathJax?.typesetPromise) {
    pendingMathTypeset = true;
    return;
  }
  mathJaxReady = true;
  pendingMathTypeset = false;
  if (mathJax.typesetClear) {
    mathJax.typesetClear([markdownBody]);
  }
  mathJax.typesetPromise([markdownBody]).catch((error) => {
    console.error(error);
  });
}

async function showMarkdownPanel(level) {
  if (!markdownPanel || !level?.markdownPath) {
    hideMarkdownPanel();
    return;
  }
  const markdownPath = level.markdownPath;
  const sectionKey = level.markdownSection ?? null;
  const cacheKey = sectionKey ? `${markdownPath}::${sectionKey}` : markdownPath;
  if (activeMarkdownPath === cacheKey && markdownPanel.classList.contains("is-open")) {
    return;
  }
  if (sectionKey) {
    markdownTwoColumns = false;
  } else if (level.markdownColumns === 1) {
    markdownTwoColumns = false;
  } else if (level.markdownColumns === 2) {
    markdownTwoColumns = true;
  } else {
    markdownTwoColumns = true;
  }
  const sectionCache = sectionKey ? markdownSectionCache : markdownCache;
  let html = sectionCache.get(cacheKey);
  if (!html) {
    try {
      const response = await fetch(markdownPath);
      if (!response.ok) {
        throw new Error(`Failed to load markdown: ${markdownPath}`);
      }
      const text = await response.text();
      let markdownSource = text;
      if (sectionKey) {
        const section = extractMarkdownSection(text, sectionKey);
        if (section) {
          const heading = section.title ?? level.name ?? "Notes";
          markdownSource = `## ${heading}\n\n${section.body}`;
        }
      }
      if (markdownRenderer) {
        html = markdownRenderer.render(markdownSource);
      } else {
        html = `<pre>${escapeHtml(markdownSource)}</pre>`;
      }
      sectionCache.set(cacheKey, html);
    } catch (error) {
      console.error(error);
      html = `<p>Unable to load markdown.</p>`;
    }
  }
  if (markdownTitle) {
    markdownTitle.textContent = level.name ?? "Notes";
  }
  if (markdownBody) {
    markdownBody.innerHTML = html;
  }
  markdownPanel.classList.add("is-open");
  markdownPanel.setAttribute("aria-hidden", "false");
  markdownPanel.inert = false;
  activeMarkdownPath = cacheKey;
  applyMarkdownLayout();
  typesetMarkdown();
}

async function renderInfoDrawer() {
  if (!infoBody) {
    return;
  }
  let html = markdownCache.get(infoMarkdownPath);
  if (!html) {
    try {
      const response = await fetch(infoMarkdownPath);
      if (!response.ok) {
        throw new Error(`Failed to load info markdown: ${infoMarkdownPath}`);
      }
      const text = await response.text();
      html = markdownRenderer ? markdownRenderer.render(text) : `<pre>${escapeHtml(text)}</pre>`;
      markdownCache.set(infoMarkdownPath, html);
    } catch (error) {
      console.error(error);
      html = `<p>Unable to load info.</p>`;
    }
  }
  infoBody.innerHTML = html;
}

async function toggleInfoDrawer() {
  if (!hud || !infoDrawer) {
    return;
  }
  await setInfoDrawer(!infoDrawerOpen);
}

async function setInfoDrawer(open) {
  if (!hud || !infoDrawer) {
    return;
  }
  if (infoDrawerOpen === open) {
    return;
  }
  infoDrawerOpen = open;
  hud.classList.toggle("is-open", infoDrawerOpen);
  hud.setAttribute("aria-expanded", infoDrawerOpen ? "true" : "false");
  infoDrawer.classList.toggle("is-open", infoDrawerOpen);
  infoDrawer.setAttribute("aria-hidden", infoDrawerOpen ? "false" : "true");
  if (infoDrawerOpen) {
    await renderInfoDrawer();
  }
}

function updateSceneMarkdown() {
  if (!currentLevel || !currentLevel.markdownPath) {
    hideMarkdownPanel();
    return;
  }
  if (currentLevel.markdownAutoOpen === false) {
    hideMarkdownPanel();
    return;
  }
  showMarkdownPanel(currentLevel);
}

function getNodeGeneration(node) {
  const count = node?.data?.binaryBands?.length ?? 0;
  if (count >= 3) {
    return "I";
  }
  if (count === 2) {
    return "II";
  }
  if (count === 1) {
    return "III";
  }
  return null;
}

function getPulsingBandName(node) {
  const count = node?.data?.binaryBands?.length ?? 0;
  if (count >= 3) {
    return "outer";
  }
  if (count === 2) {
    return "middle";
  }
  return null;
}

function getNextGenerationInfo(level) {
  if (!level || !level.sceneId) {
    return null;
  }
  const currentGen = getNodeGeneration(level.primaryBinaryNode);
  if (!currentGen || currentGen === "III") {
    return null;
  }
  const mapping = generationTransitions[level.sceneId];
  if (!mapping) {
    return null;
  }
  const nextGen = currentGen === "I" ? "II" : "III";
  return { ...mapping, nextGen };
}

function setDetailPanel(node) {
  if (!detailPanel || !detailTitle || !detailBody) {
    return;
  }
  const details = node?.data?.details;
  if (!details) {
    closeDetailPanel();
    return;
  }
  detailPanel.classList.add("is-open");
  detailPanel.setAttribute("aria-hidden", "false");
  detailPanel.inert = false;
  activeDetailNodeId = node.data.id ?? node.data.name ?? null;
  hoveredDetailNodeId = activeDetailNodeId;
  detailTitle.textContent = node.data.name ?? node.data.id ?? "Details";
  detailBody.innerHTML = "";

  const appendDetailRow = (label, value) => {
    const row = document.createElement("div");
    row.className = "detail-row";
    const keyCell = document.createElement("div");
    keyCell.className = "detail-key";
    keyCell.innerHTML = formatSuperscripts(label);
    const valueCell = document.createElement("div");
    valueCell.className = "detail-value";
    valueCell.innerHTML = formatSuperscripts(value);
    row.appendChild(keyCell);
    row.appendChild(valueCell);
    detailBody.appendChild(row);
  };

  if (currentLevel?.sceneId === "standard_model" && node.data.category) {
    appendDetailRow("Class", node.data.category);
  }

  const usedKeys = new Set();
  detailFieldOrder.forEach((field) => {
    if (details[field.key] === undefined || details[field.key] === null) {
      return;
    }
    usedKeys.add(field.key);
    appendDetailRow(field.label, details[field.key]);
  });

  Object.keys(details)
    .filter((key) => !usedKeys.has(key))
    .forEach((key) => {
      appendDetailRow(key, details[key]);
    });
}

function purgeWorldState() {
  transitionState.active = false;
  transitionState.mode = null;
  transitionState.fromLevel = null;
  transitionState.toLevel = null;
  transitionState.payload = null;
  closeDetailPanel();
  hideHoverTooltip();
  hideMarkdownPanel();
  zoomState.active = false;
  panTween.active = false;
  labelFadeState.active = false;
  worldGroup.clear();
  worldGroup.position.set(0, 0, 0);
  levels.clear();
  if (labelRenderer?.domElement) {
    labelRenderer.domElement.innerHTML = "";
  }
}

function appendCacheBust(path) {
  const separator = path.includes("?") ? "&" : "?";
  return `${path}${separator}v=${cacheBustToken}`;
}

async function loadSceneConfig(scenePath) {
  if (sceneConfigCache.has(scenePath)) {
    return sceneConfigCache.get(scenePath);
  }
  if (sceneLoadPromises.has(scenePath)) {
    return sceneLoadPromises.get(scenePath);
  }

  const promise = fetch(appendCacheBust(scenePath))
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Failed to load scene ${scenePath}`);
      }
      return response.json();
    })
    .then(async (data) => {
      const hideScaleLabels = Boolean(data.scene?.hideScaleLabels);
      const wrapLabels = data.scene?.wrapLabels ?? true;
      const markdownDerived = deriveMarkdownConfig(data.scene?.markdown);
      const idMap = new Map(
        data.objects.map((obj) => [obj.id, obj.label || obj.id])
      );
      let nodes = data.objects.map((obj) => {
        const hasScale =
          obj.scaleExponent !== undefined && obj.scaleExponent !== null;
        const binaryBands = Array.isArray(obj.binaryBands)
          ? obj.binaryBands
          : null;
        let color = obj.color ?? "#3a5a8a";
        if (typeof color === "string" && colorTokens[color]) {
          color = colorTokens[color];
        }
        const stripeColors = Array.isArray(obj.stripeColors)
          ? obj.stripeColors.map((stripeColor) =>
              typeof stripeColor === "string" && colorTokens[stripeColor]
                ? colorTokens[stripeColor]
                : stripeColor
            )
          : null;
        const node = {
          id: obj.id,
          name: obj.label || obj.id,
          scale: hasScale ? obj.scaleExponent : null,
          hasScale,
          radius: obj.radius ?? 1,
          color,
          position: obj.position ?? [0, 0, 0],
          category: obj.category,
          reaction: obj.reaction,
          details: obj.details ?? null,
          renderStyle: obj.renderStyle ?? null,
          markdownPath: obj.markdownPath ?? null,
          markdownSection: obj.markdownSection ?? null,
          markdownColumns: obj.markdownColumns ?? null,
          markdownHeadingLevel: obj.markdownHeadingLevel ?? null,
          binaryBands,
          glowRing: obj.glowRing ?? false,
          glowRingColor: obj.glowRingColor ?? null,
          glowRingOpacity: obj.glowRingOpacity ?? null,
          glowRingThickness: obj.glowRingThickness ?? null,
          glowRingScale: obj.glowRingScale ?? null,
          stripeColors,
          stripeCount: obj.stripeCount ?? null,
          stripeThickness: obj.stripeThickness ?? null,
          stripeOpacity: obj.stripeOpacity ?? null,
          baseOpacity: obj.baseOpacity ?? null,
          hideScaleLabel: obj.hideScaleLabel ?? hideScaleLabels,
          wrapLabel: obj.wrapLabel ?? wrapLabels,
        };
        if (Array.isArray(obj.subScenes) && obj.subScenes.length > 0) {
          node.childScene = obj.subScenes[0];
        }
        if (obj.motion && obj.motion.type === "orbit") {
          const orbit = obj.motion.orbit || obj.motion;
          const centerLabel = idMap.get(orbit.center) ?? orbit.center;
          node.orbit = {
            center: centerLabel,
            radius: orbit.radius ?? 1,
            speed: orbit.speed ?? 0,
            phase: orbit.phase ?? 0,
            shape: orbit.shape ?? "circular",
            yScale: orbit.yScale,
          };
          node.motionType = "orbit";
        }
        if (binaryBands && binaryBands.length > 0) {
          node.motionType = "binaryOrbit";
        }
        return node;
      });
      const autoMarkdownScene = markdownDerived ? { ...data.scene, ...markdownDerived } : data.scene;
      const autoNodes = await buildAutoMarkdownNodes(autoMarkdownScene, nodes);
      if (autoNodes.length) {
        nodes = nodes.concat(autoNodes);
      }

      const sceneName =
        data.scene?.name ?? data.scene?.id ?? data.scene?.title ?? scenePath;
      const sceneId = data.scene?.id ?? null;
      const config = {
        layout: nodes.some((node) => node.orbit) ? "orbit" : "static",
        nodes,
        links: Array.isArray(data.links) ? data.links : [],
        sceneName,
        sceneId,
        markdownPath: data.scene?.markdownPath ?? null,
        markdownSection: data.scene?.markdownSection ?? null,
        markdownColumns: data.scene?.markdownColumns ?? null,
        markdownAutoOpen: data.scene?.markdownAutoOpen ?? true,
        centerOn: data.scene?.centerOn ?? null,
        autoSphereRing: data.scene?.autoSphereRing ?? false,
        autoMarkdownDirectory: markdownDerived?.autoMarkdownDirectory ?? null,
        autoMarkdownPath: markdownDerived?.autoMarkdownPath ?? null,
        autoMarkdownSection: markdownDerived?.autoMarkdownSection ?? null,
        autoMarkdownHeadingLevel: markdownDerived?.autoMarkdownHeadingLevel ?? null,
        autoMarkdownIncludeExistingInLayout:
          markdownDerived?.autoMarkdownIncludeExistingInLayout ?? false,
        autoMarkdownNodeRadius:
          markdownDerived?.autoMarkdownNodeRadius ?? null,
        autoMarkdownRingRadius:
          markdownDerived?.autoMarkdownRingRadius ?? null,
        autoMarkdownMaxRingCount:
          markdownDerived?.autoMarkdownMaxRingCount ?? null,
        autoMarkdownGridSpacing:
          markdownDerived?.autoMarkdownGridSpacing ?? null,
        autoMarkdownColumns:
          markdownDerived?.autoMarkdownColumns ?? null,
        autoMarkdownPalette:
          markdownDerived?.autoMarkdownPalette ?? null,
        autoMarkdownColor:
          markdownDerived?.autoMarkdownColor ?? null,
        autoMarkdownExcludePaths: Array.isArray(markdownDerived?.autoMarkdownExcludePaths)
          ? markdownDerived.autoMarkdownExcludePaths
          : [],
        autoMarkdownPlainPaths: Array.isArray(markdownDerived?.autoMarkdownPlainPaths)
          ? markdownDerived.autoMarkdownPlainPaths
          : [],
        autoMarkdownDefaultIndex: markdownDerived?.autoMarkdownDefaultIndex ?? null,
        autoMarkdownIndexPaths: Array.isArray(markdownDerived?.autoMarkdownIndexPaths)
          ? markdownDerived.autoMarkdownIndexPaths
          : [],
        autoMarkdownPlainSectionPaths: Array.isArray(markdownDerived?.autoMarkdownPlainSectionPaths)
          ? markdownDerived.autoMarkdownPlainSectionPaths
          : [],
        autoMarkdownSectionDepth: markdownDerived?.autoMarkdownSectionDepth ?? null,
        autoMarkdownOverrides: markdownDerived?.autoMarkdownOverrides ?? null,
        autoMarkdownSubdirectories: markdownDerived?.autoMarkdownSubdirectories ?? false,
      };
      levelConfigs[scenePath] = config;
      sceneConfigCache.set(scenePath, config);
      return config;
    })
    .catch((error) => {
      console.error(error);
      sceneLoadPromises.delete(scenePath);
      return null;
    });

  sceneLoadPromises.set(scenePath, promise);
  return promise;
}

async function resetToRootScene() {
  if (transitionState.active) {
    return;
  }
  const config = await loadSceneConfig(rootScenePath);
  if (!config) {
    return;
  }
  purgeWorldState();
  const rootLevel = buildLevel(rootScenePath);
  worldGroup.add(rootLevel.group);
  rootLevel.group.position.set(0, 0, 0);
  rootLevel.group.scale.setScalar(1);
  layoutRootLevel(rootLevel);
  setLevelOpacity(rootLevel, 1);
  setLevelLabelOpacity(rootLevel, 0);
  setLevelLinkOpacity(rootLevel, 1);
  currentLevel = rootLevel;
  navigationStack.length = 0;
  searchBackStack.length = 0;
  labelFadeState.active = true;
  labelFadeState.level = currentLevel;
  labelFadeState.startTime = performance.now();
  updateCamera();
  fitCameraToLevel(currentLevel);
  updateSceneLabel();
  updateSceneMarkdown();
}

async function jumpToScene(scenePath, options = {}) {
  if (transitionState.active) {
    return;
  }
  const config = levelConfigs[scenePath] ?? (await loadSceneConfig(scenePath));
  if (!config) {
    return;
  }
  await ensureDynamicSceneConfig(scenePath);
  if (options.mode === "instant") {
    purgeWorldState();
    const level = buildLevel(scenePath);
    worldGroup.add(level.group);
    level.group.position.set(0, 0, 0);
    level.group.scale.setScalar(1);
    setLevelOpacity(level, 1);
    setLevelLabelOpacity(level, 0);
    setLevelLinkOpacity(level, 1);
    currentLevel = level;
    navigationStack.length = 0;
    if (Array.isArray(options.restoreNavStack)) {
      options.restoreNavStack.forEach((item) => {
        if (item && item.levelId && item.focusNodeId) {
          navigationStack.push({
            levelId: item.levelId,
            focusNodeId: item.focusNodeId,
          });
        }
      });
    }
    labelFadeState.active = true;
    labelFadeState.level = currentLevel;
    labelFadeState.startTime = performance.now();
    updateCamera();
    fitCameraToLevel(currentLevel);
    updateSceneLabel();
    updateSceneMarkdown();
    return;
  }

  const nextLevel = buildLevel(scenePath);
  hideMarkdownPanel();
  purgeWorldState();
  if (currentLevel && !worldGroup.children.includes(currentLevel.group)) {
    worldGroup.add(currentLevel.group);
  }
  worldGroup.add(nextLevel.group);
  nextLevel.group.position.set(0, 0, 0);
  nextLevel.group.scale.setScalar(options.startScale ?? 1);
  setLevelOpacity(nextLevel, 0);
  setLevelLabelOpacity(nextLevel, 0);
  setLevelLinkOpacity(nextLevel, 0);

  const zoomTarget = computeFitZoomForLevel(nextLevel);
  transitionState.active = true;
  transitionState.mode = "jump";
  transitionState.fromLevel = currentLevel;
  transitionState.toLevel = nextLevel;
  transitionState.payload = {
    zoomStart: camera.zoom,
    zoomTarget,
    startScale: options.startScale ?? 1,
  };
  transitionState.startTime = performance.now();
  transitionState.duration = options.duration ?? 700;

  navigationStack.length = 0;
  if (Array.isArray(options.restoreNavStack)) {
    options.restoreNavStack.forEach((item) => {
      if (item && item.levelId && item.focusNodeId) {
        navigationStack.push({
          levelId: item.levelId,
          focusNodeId: item.focusNodeId,
        });
      }
    });
  }
}

function clampZoom(value) {
  return Math.min(zoomLimits.max, Math.max(zoomLimits.min, value));
}

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function smoothstep(edge0, edge1, x) {
  const t = Math.min(1, Math.max(0, (x - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function setTargetZoom(nextZoom, duration = 420) {
  zoomState.active = true;
  zoomState.startZoom = camera.zoom;
  zoomState.targetZoom = clampZoom(nextZoom);
  zoomState.startTime = performance.now();
  zoomState.duration = duration;
}

function setTargetPan(nextPosition, duration = 420) {
  panTween.active = true;
  panTween.start.copy(worldGroup.position);
  panTween.target.copy(nextPosition);
  panTween.startTime = performance.now();
  panTween.duration = duration;
}

function applyZoom(value) {
  camera.zoom = clampZoom(value);
  camera.updateProjectionMatrix();
}

function computeFocusZoom(radius, fraction = 0.32) {
  const targetFraction = clamp(fraction, 0.15, 0.6);
  const safeRadius = Math.max(radius, 0.01);
  const targetZoom = (targetFraction * baseViewHeight) / (2 * safeRadius);
  return clampZoom(targetZoom);
}

function getMarkdownReaderSceneId(markdownPath, markdownSection) {
  if (!markdownSection) {
    return `__markdown_reader__:${markdownPath}`;
  }
  const normalized = normalizeMarkdownKey(markdownSection);
  return `__markdown_reader__:${markdownPath}::${normalized}`;
}

function getMarkdownIndexSceneId(markdownPath, headingLevel) {
  const levelToken = typeof headingLevel === "number" ? `::h${headingLevel}` : "";
  return `__markdown_index__:${markdownPath}${levelToken}`;
}

function getMarkdownDocSceneId(markdownPath) {
  return `__markdown_doc__:${markdownPath}`;
}

function getMarkdownSectionIndexSceneId(markdownPath, markdownSection) {
  const normalized = normalizeMarkdownKey(markdownSection);
  return `__markdown_section_index__:${markdownPath}::${normalized}`;
}

function getMarkdownDirectorySceneId(directory) {
  return `__markdown_directory__:${directory}`;
}

function ensureMarkdownReaderScene(nodeData) {
  const markdownPath = nodeData.markdownPath;
  if (!markdownPath) {
    return null;
  }
  const sceneName = nodeData.name ?? "Notes";
  const markdownSection = nodeData.markdownSection ?? null;
  const headingLevel =
    typeof nodeData.markdownHeadingLevel === "number"
      ? nodeData.markdownHeadingLevel
      : 2;

  if (!markdownSection) {
    if (nodeData.markdownAutoIndex === false) {
      const sceneId = getMarkdownDocSceneId(markdownPath);
      if (levelConfigs[sceneId]) {
        return sceneId;
      }
      levelConfigs[sceneId] = {
        layout: "static",
        nodes: [],
        links: [],
        sceneName,
        sceneId,
        markdownPath,
        markdownSection: null,
        markdownColumns: nodeData.markdownColumns ?? null,
        markdownAutoOpen: true,
        centerOn: null,
      };
      markdownReaderScenes.set(sceneId, true);
      return sceneId;
    }
    const sceneId = getMarkdownIndexSceneId(markdownPath, headingLevel);
    if (levelConfigs[sceneId]) {
      return sceneId;
    }
      levelConfigs[sceneId] = {
        layout: "static",
        nodes: [],
        links: [],
        sceneName,
        sceneId,
        markdownPath,
        markdownSection: null,
        markdownColumns: nodeData.markdownColumns ?? null,
        markdownAutoOpen: false,
        centerOn: null,
        autoSphereRing: true,
        autoMarkdownPath: markdownPath,
        autoMarkdownHeadingLevel: headingLevel,
        autoMarkdownIncludeExistingInLayout: false,
        autoMarkdownPlainSectionPaths: Array.isArray(nodeData.markdownPlainSectionPaths)
          ? nodeData.markdownPlainSectionPaths
          : [],
      };
    markdownReaderScenes.set(sceneId, true);
    return sceneId;
  }

  const sceneId = getMarkdownReaderSceneId(markdownPath, markdownSection);
  if (levelConfigs[sceneId]) {
    return sceneId;
  }
  levelConfigs[sceneId] = {
    layout: "static",
    nodes: [],
    links: [],
    sceneName,
    sceneId,
    markdownPath,
    markdownSection,
    markdownColumns: nodeData.markdownColumns ?? null,
    markdownAutoOpen: true,
    centerOn: null,
  };
  markdownReaderScenes.set(sceneId, true);
  return sceneId;
}

function ensureMarkdownSectionIndexScene(markdownPath, markdownSection, parentScene) {
  if (!markdownPath || !markdownSection) {
    return null;
  }
  const sceneId = getMarkdownSectionIndexSceneId(markdownPath, markdownSection);
  if (levelConfigs[sceneId]) {
    return sceneId;
  }
  levelConfigs[sceneId] = {
    layout: "static",
    nodes: [],
    links: [],
    sceneName: markdownSection,
    sceneId,
    markdownPath,
    markdownSection,
    markdownColumns: parentScene?.autoMarkdownColumns ?? null,
    markdownAutoOpen: false,
    centerOn: null,
    autoSphereRing: true,
    autoMarkdownPath: markdownPath,
    autoMarkdownSection: markdownSection,
    autoMarkdownHeadingLevel: 3,
    autoMarkdownIncludeExistingInLayout: false,
    autoMarkdownNodeRadius: parentScene?.autoMarkdownNodeRadius,
    autoMarkdownRingRadius: parentScene?.autoMarkdownRingRadius,
    autoMarkdownMaxRingCount: parentScene?.autoMarkdownMaxRingCount,
    autoMarkdownGridSpacing: parentScene?.autoMarkdownGridSpacing,
    autoMarkdownColumns: parentScene?.autoMarkdownColumns,
    autoMarkdownPalette: parentScene?.autoMarkdownPalette,
    autoMarkdownColor: parentScene?.autoMarkdownColor,
  };
  return sceneId;
}

function ensureMarkdownDirectoryScene(directory, parentScene, nodeName) {
  if (!directory) {
    return null;
  }
  const sceneId = getMarkdownDirectorySceneId(directory);
  if (levelConfigs[sceneId]) {
    return sceneId;
  }
  levelConfigs[sceneId] = {
    layout: "static",
    nodes: [],
    links: [],
    sceneName: nodeName ?? titleFromSlug(directory.split("/").pop() ?? "Notes"),
    sceneId,
    markdownPath: null,
    markdownSection: null,
    markdownColumns: null,
    markdownAutoOpen: false,
    centerOn: null,
    autoSphereRing: true,
    autoMarkdownDirectory: directory,
    autoMarkdownIncludeExistingInLayout: false,
    autoMarkdownNodeRadius: parentScene?.autoMarkdownNodeRadius,
    autoMarkdownRingRadius: parentScene?.autoMarkdownRingRadius,
    autoMarkdownMaxRingCount: parentScene?.autoMarkdownMaxRingCount,
    autoMarkdownGridSpacing: parentScene?.autoMarkdownGridSpacing,
    autoMarkdownColumns: parentScene?.autoMarkdownColumns,
    autoMarkdownPalette: parentScene?.autoMarkdownPalette,
    autoMarkdownColor: parentScene?.autoMarkdownColor,
  };
  return sceneId;
}

async function ensureDynamicSceneConfig(sceneId) {
  const config = levelConfigs[sceneId];
  if (!config || !config.autoSphereRing) {
    return;
  }
  if (!Array.isArray(config.nodes)) {
    config.nodes = [];
  }
  if (config.nodes.length) {
    return;
  }
  const autoNodes = await buildAutoMarkdownNodes(config, config.nodes);
  if (autoNodes.length) {
    config.nodes = config.nodes.concat(autoNodes);
  }
}

function computeWarpScale(objectRadius) {
  const aspect = window.innerWidth / window.innerHeight;
  const viewHeight = baseViewHeight / camera.zoom;
  const viewWidth = (baseViewHeight * aspect) / camera.zoom;
  const halfDiagonal = 0.5 * Math.hypot(viewWidth, viewHeight);
  const targetRadius = halfDiagonal * 1.05;
  return Math.max(1.2, targetRadius / Math.max(objectRadius, 0.01));
}

function computeWarpScaleForLevel(level, overshoot = 1.25) {
  const { size } = getLevelBoundsFromNodes(level);
  const radius = Math.max(size.x, size.y) * 0.5;
  const base = computeWarpScale(Math.max(radius, 0.01));
  return Math.max(1.4, base * overshoot);
}

function getSafeViewportWorld() {
  const aspect = window.innerWidth / window.innerHeight;
  const viewWidth = baseViewHeight * aspect;
  const worldPerPixel = viewWidth / Math.max(window.innerWidth, 1);
  const safeWidth = Math.max(
    2,
    viewWidth - 2 * (rootLayoutMarginPx.x * worldPerPixel)
  );
  const safeHeight = Math.max(
    2,
    baseViewHeight - 2 * (rootLayoutMarginPx.y * worldPerPixel)
  );
  return { safeWidth, safeHeight };
}

function cloneNodeData(nodeData) {
  if (typeof structuredClone === "function") {
    return structuredClone(nodeData);
  }
  return JSON.parse(JSON.stringify(nodeData));
}

function resetNodeScale(node) {
  if (!node?.group) {
    return;
  }
  const baseScale =
    typeof node.baseScale === "number"
      ? node.baseScale
      : typeof node.data?.baseScale === "number"
        ? node.data.baseScale
        : 1;
  node.group.scale.setScalar(baseScale);
}

function layoutRootLevel(level) {
  if (!level || level.id !== rootScenePath) {
    return;
  }
  const nodes = level.nodes;
  if (!nodes?.length) {
    return;
  }
  nodes.forEach((node) => {
    if (node.data && typeof node.data.baseRadius !== "number") {
      node.data.baseRadius = node.data.radius ?? 0;
    }
  });
  const baseRadius = Math.max(
    ...nodes.map((node) => node.data?.baseRadius ?? node.data?.radius ?? 0)
  );
  const { safeWidth, safeHeight } = getSafeViewportWorld();
  const safeRadius = Math.max(2, Math.min(safeWidth, safeHeight) / 2);
  let targetRadius = baseRadius;
  if (nodes.length > 1) {
    let r = baseRadius;
    for (let i = 0; i < 6; i += 1) {
      const candidateRing = Math.max(2, safeRadius - r);
      const maxRadius = maxRingNodeRadius(candidateRing, nodes.length);
      if (!Number.isFinite(maxRadius) || maxRadius <= 0) {
        break;
      }
      r = Math.min(maxRadius, safeRadius - 2);
    }
    targetRadius = r;
  }
  const ringRadius = Math.max(2, safeRadius - targetRadius);
  const scaleFactor = baseRadius > 0 ? targetRadius / baseRadius : 1;
  if (Number.isFinite(scaleFactor)) {
    nodes.forEach((node) => {
      node.group.scale.setScalar(scaleFactor);
      node.baseScale = scaleFactor;
      if (node.data) {
        node.data.baseScale = scaleFactor;
      }
      if (node.data?.baseRadius) {
        node.data.radius = node.data.baseRadius * scaleFactor;
      }
    });
  }

  const angleStep = (-Math.PI * 2) / nodes.length;
  const startAngle = ringLayoutDefaults.startAngle;
  nodes.forEach((node, index) => {
    const angle = startAngle + angleStep * index;
    const x = Math.cos(angle) * ringRadius;
    const y = Math.sin(angle) * ringRadius;
    node.group.position.set(x, y, node.group.position.z);
  });
}

function getTransitionFocusNode(level) {
  if (!level) {
    return null;
  }
  const focusNodeId = transitionState.payload?.focusNodeId;
  if (!focusNodeId) {
    return null;
  }
  return (
    level.nodeById.get(focusNodeId) ?? level.nodeByName.get(focusNodeId)
  );
}

function getLevelBoundsLocal(level) {
  return getLevelBoundsFromNodes(level);
}

function computeFitZoomForLevel(level) {
  const { size } = getLevelBoundsFromNodes(level);
  if (!isFinite(size.x) || !isFinite(size.y) || size.lengthSq() === 0) {
    return camera.zoom;
  }

  const aspect = window.innerWidth / window.innerHeight;
  const viewHeight = baseViewHeight;
  const viewWidth = baseViewHeight * aspect;
  const marginFactor = 0.8;
  const zoomX = (viewWidth * marginFactor) / Math.max(size.x, 0.01);
  const zoomY = (viewHeight * marginFactor) / Math.max(size.y, 0.01);
  return clampZoom(Math.min(zoomX, zoomY));
}

function fitCameraToLevel(level) {
  const { size } = getLevelBoundsFromNodes(level);
  if (!isFinite(size.x) || !isFinite(size.y) || size.lengthSq() === 0) {
    return;
  }

  const center = getLevelCenter(level);
  const nextZoom = computeFitZoomForLevel(level);

  zoomState.active = false;
  panTween.active = false;
  worldGroup.position.set(-center.x, -center.y, 0);
  applyZoom(nextZoom);
}

function updateCamera() {
  const aspect = window.innerWidth / window.innerHeight;
  const viewHeight = baseViewHeight;
  const viewWidth = viewHeight * aspect;
  camera.left = -viewWidth / 2;
  camera.right = viewWidth / 2;
  camera.top = viewHeight / 2;
  camera.bottom = -viewHeight / 2;
  camera.updateProjectionMatrix();
}

function createLabel(node) {
  const label = document.createElement("div");
  label.className = "label";
  if (node.wrapLabel) {
    label.classList.add("label-wrap");
    label.style.maxWidth = "120px";
  }
  const scaleHtml = node.hideScaleLabel || !node.hasScale
    ? ""
    : `<div class="label-scale">10^${node.scale}</div>`;
  const tagHtml =
    node.category === "Reaction" ? `<div class="label-tag">RXN</div>` : "";
  label.innerHTML = `<div class="label-title">${node.name}</div>${scaleHtml}${tagHtml}`;
  return new CSS2DObject(label);
}

function getBinaryBandRadii(shellRadius, bands) {
  if (!Array.isArray(bands) || bands.length === 0) {
    return [];
  }
  const radiiByBand = {
    outer: 0.75,
    middle: 0.52,
    inner: 0.32,
  };
  return bands.map((band) => {
    const factor = radiiByBand[band] ?? 0.5;
    return shellRadius * factor;
  });
}

function createStripedSphereNode(nodeData) {
  const group = new THREE.Group();
  const sphereGeometry = new THREE.SphereGeometry(nodeData.radius, 32, 20);
  const baseOpacity = nodeData.baseOpacity ?? 0.72;
  const sphereMaterial = new THREE.MeshBasicMaterial({
    color: nodeData.color,
    transparent: true,
    opacity: baseOpacity,
  });
  sphereMaterial.depthWrite = false;
  const mesh = new THREE.Mesh(sphereGeometry, sphereMaterial);
  group.add(mesh);

  const outlineGeometry = new THREE.EdgesGeometry(sphereGeometry);
  const outlineMaterial = new THREE.LineBasicMaterial({
    color: "#7a7a7a",
    transparent: true,
    opacity: 0.3,
  });
  outlineMaterial.depthWrite = false;
  const outline = new THREE.LineSegments(outlineGeometry, outlineMaterial);
  group.add(outline);

  const extraMeshes = [];
  const stripeCount = nodeData.stripeCount ?? 7;
  const stripeThickness =
    nodeData.stripeThickness ?? Math.max(0.03, nodeData.radius * 0.06);
  const stripeOpacity = nodeData.stripeOpacity ?? 0.85;
  const stripeColors =
    nodeData.stripeColors ?? ["#ff0000", "#4b0082"];

  for (let i = 0; i < stripeCount; i += 1) {
    const t = (i + 1) / (stripeCount + 1);
    const phi = t * Math.PI;
    const ringRadius = Math.sin(phi) * nodeData.radius;
    const y = Math.cos(phi) * nodeData.radius;
    if (ringRadius <= 0.0001) {
      continue;
    }
    const ringGeometry = new THREE.TorusGeometry(
      ringRadius,
      stripeThickness,
      12,
      48
    );
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: stripeColors[i % stripeColors.length],
      transparent: true,
      opacity: stripeOpacity,
    });
    ringMaterial.depthWrite = false;
    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
    ring.rotation.x = Math.PI / 2;
    ring.position.y = y;
    group.add(ring);
    extraMeshes.push({ mesh: ring, baseOpacity: stripeOpacity });
  }

  const labelObject = createLabel(nodeData);
  group.add(labelObject);

  return {
    group,
    mesh,
    outline,
    labelObject,
    labelMaxWidth: null,
    halo: null,
    haloBaseOpacity: 0,
    haloIntensity: 1,
    haloPhase: haloSeed++ * 0.6,
    baseScale: 1,
    data: nodeData,
    baseOpacity: {
      mesh: baseOpacity,
      outline: outlineMaterial.opacity,
      label: 1,
    },
    extraMeshes,
    binaryBandData: [],
  };
}

function createBinaryCoreNode(nodeData, useCutaway) {
  const group = new THREE.Group();
  const shellRadius = nodeData.radius;
  const shellGeometry = useCutaway
    ? new THREE.SphereGeometry(
        shellRadius,
        36,
        22,
        Math.PI * 0.15,
        Math.PI * 1.7,
        0,
        Math.PI
      )
    : new THREE.SphereGeometry(shellRadius, 36, 22);
  const shellMaterial = new THREE.MeshBasicMaterial({
    color: nodeData.color,
    transparent: true,
    opacity: binaryStyle.shellOpacity,
    side: THREE.DoubleSide,
  });
  shellMaterial.depthWrite = false;
  const mesh = new THREE.Mesh(shellGeometry, shellMaterial);
  group.add(mesh);

  const outlineGeometry = new THREE.EdgesGeometry(shellGeometry);
  const outlineMaterial = new THREE.LineBasicMaterial({
    color: "#7a7a7a",
    transparent: true,
    opacity: binaryStyle.shellOutlineOpacity,
  });
  outlineMaterial.depthWrite = false;
  const outline = new THREE.LineSegments(outlineGeometry, outlineMaterial);
  group.add(outline);

  const extraMeshes = [];
  const binaryBandData = [];
  const bandRadii = getBinaryBandRadii(
    shellRadius,
    nodeData.binaryBands
  );
  const particleRadius = shellRadius * binaryStyle.particleRadiusFactor;

  const bandSpeedFactor = {
    outer: 1,
    middle: 2,
    inner: 4,
  };
  bandRadii.forEach((bandRadius, index) => {
    const ringGeometry = new THREE.TorusGeometry(
      bandRadius,
      shellRadius * binaryStyle.ringTubeFactor,
      16,
      64
    );
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: nodeData.color,
      transparent: true,
      opacity: binaryStyle.ringOpacity,
      side: THREE.DoubleSide,
    });
    ringMaterial.depthWrite = false;
    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
    group.add(ring);
    extraMeshes.push({ mesh: ring, baseOpacity: binaryStyle.ringOpacity });

    const positrinoMaterial = new THREE.MeshBasicMaterial({
      color: binaryStyle.positrinoColor,
      transparent: true,
      opacity: 0.9,
    });
    positrinoMaterial.depthWrite = false;
    const electrinoMaterial = new THREE.MeshBasicMaterial({
      color: binaryStyle.electrinoColor,
      transparent: true,
      opacity: 0.9,
    });
    electrinoMaterial.depthWrite = false;

    const positrino = new THREE.Mesh(
      new THREE.SphereGeometry(particleRadius, 16, 12),
      positrinoMaterial
    );
    const electrino = new THREE.Mesh(
      new THREE.SphereGeometry(particleRadius, 16, 12),
      electrinoMaterial
    );
    group.add(positrino);
    group.add(electrino);
    extraMeshes.push({ mesh: positrino, baseOpacity: 0.9 });
    extraMeshes.push({ mesh: electrino, baseOpacity: 0.9 });

    const bandName = nodeData.binaryBands?.[index];
    ring.userData.bandName = bandName;
    binaryBandData.push({
      radius: bandRadius,
      speed: binaryStyle.baseOrbitSpeed * (bandSpeedFactor[bandName] ?? 1),
      phase: index * 0.7,
      bandName,
      ring,
      ringBaseOpacity: binaryStyle.ringOpacity,
      positrino,
      electrino,
    });
  });

  const labelObject = createLabel(nodeData);
  group.add(labelObject);

  return {
    group,
    mesh,
    outline,
    labelObject,
    labelMaxWidth: null,
    halo: null,
    haloBaseOpacity: 0,
    haloIntensity: 1,
    haloPhase: haloSeed++ * 0.6,
    baseScale: 1,
    data: nodeData,
    baseOpacity: {
      mesh: shellMaterial.opacity,
      outline: outlineMaterial.opacity,
      label: 1,
    },
    extraMeshes,
    binaryBandData,
  };
}

function createNode(nodeData) {
  if (nodeData.renderStyle === "binaryShell") {
    return createBinaryCoreNode(nodeData, true);
  }
  if (nodeData.renderStyle === "binarySphere") {
    return createBinaryCoreNode(nodeData, false);
  }
  if (nodeData.renderStyle === "stripedSphere") {
    return createStripedSphereNode(nodeData);
  }
  const group = new THREE.Group();
  const geometry = new THREE.SphereGeometry(nodeData.radius, 32, 20);
  const isReaction = nodeData.category === "Reaction";
  const material = new THREE.MeshBasicMaterial({
    color: nodeData.color,
    transparent: true,
    opacity: isReaction ? 0.92 : 0.86,
  });
  material.depthWrite = false;
  const mesh = new THREE.Mesh(geometry, material);
  group.add(mesh);

  const outlineGeometry = new THREE.EdgesGeometry(geometry);
  const outlineMaterial = new THREE.LineBasicMaterial({
    color: isReaction ? "#f6dd9c" : "#7a7a7a",
    transparent: true,
    opacity: isReaction ? 0.55 : 0.3,
  });
  outlineMaterial.depthWrite = false;
  const outline = new THREE.LineSegments(outlineGeometry, outlineMaterial);
  group.add(outline);

  const labelObject = createLabel(nodeData);
  group.add(labelObject);

  const extraMeshes = [];
  if (nodeData.glowRing) {
    const ringRadius = nodeData.radius * (nodeData.glowRingScale ?? 1.06);
    const ringThickness =
      nodeData.glowRingThickness ?? Math.max(0.02, nodeData.radius * 0.045);
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: nodeData.glowRingColor ?? nodeData.color,
      transparent: true,
      opacity: nodeData.glowRingOpacity ?? 0.35,
      side: THREE.DoubleSide,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const ringGeometry = new THREE.TorusGeometry(
      ringRadius,
      ringThickness,
      12,
      64
    );
    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
    ring.rotation.x = Math.PI / 2;
    ring.renderOrder = -1;
    ring.userData.isGlowRing = true;
    group.add(ring);
    extraMeshes.push({ mesh: ring, baseOpacity: ringMaterial.opacity });
  }

  let halo = null;
  if (nodeData.childScene || nodeData.markdownPath) {
    const haloGeometry = new THREE.SphereGeometry(nodeData.radius * 1.18, 24, 16);
    const haloMaterial = new THREE.MeshBasicMaterial({
      color: "#d5dcff",
      transparent: true,
      opacity: 0.2,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    halo = new THREE.Mesh(haloGeometry, haloMaterial);
    halo.renderOrder = -1;
    group.add(halo);
  }

  return {
    group,
    mesh,
    outline,
    labelObject,
    labelMaxWidth: null,
    halo,
    haloBaseOpacity: halo ? halo.material.opacity : 0,
    haloIntensity: 1,
    haloPhase: haloSeed++ * 0.6,
    baseScale: 1,
    data: nodeData,
    baseOpacity: {
      mesh: material.opacity,
      outline: outlineMaterial.opacity,
      label: 1,
    },
    extraMeshes,
  };
}

function buildLevel(levelId) {
  if (levels.has(levelId)) {
    return levels.get(levelId);
  }

  const config = levelConfigs[levelId];
  const group = new THREE.Group();
  let nodes = [];
  const nodeByName = new Map();
  const nodeById = new Map();
  const motionNodes = [];
  const ringTargets = [];
  const ringTargetByMesh = new Map();
  let primaryBinaryNode = null;

  const useAutoSphereRing =
    !!config.autoSphereRing &&
    !config.autoMarkdownDirectory &&
    config.layout === "static";
  const ringNodes = useAutoSphereRing
    ? config.nodes.filter((node) => node?.category !== "legend")
    : [];
  const ringLayout = useAutoSphereRing ? computeRingLayout(ringNodes) : null;
  const useClockwiseOrder =
    !!ringLayout &&
    !!config.autoSphereRing &&
    (config.autoMarkdownPath || config.autoMarkdownDirectory || config.autoMarkdownSection);
  let ringIndex = 0;

  const spacing = config.spacing ?? 7;
  const centerOffset = (config.nodes.length - 1) / 2;
  const isElementScene = typeof levelId === "string" && levelId.startsWith("json/elements/");

  config.nodes.forEach((nodeDataRaw, index) => {
    const nodeData = cloneNodeData(nodeDataRaw);
    if (nodeData.category === "legend") {
      return;
    }
    if (ringLayout) {
      const positionIndex =
        useClockwiseOrder && ringIndex > 0
          ? ringLayout.positions.length - ringIndex
          : ringIndex;
      const pos = ringLayout.positions[positionIndex];
      if (pos) {
        nodeData.position = [pos[0], pos[1], 0];
      }
      nodeData.radius = ringLayout.nodeRadius;
      ringIndex += 1;
    }
    const node = createNode(nodeData);
    const hasPosition =
      Array.isArray(nodeData.position) && nodeData.position.length >= 2;
    if (hasPosition) {
      node.group.position.set(
        nodeData.position[0] ?? 0,
        nodeData.position[1] ?? 0,
        nodeData.position[2] ?? 0
      );
    } else if (config.layout === "linear") {
      node.group.position.x = (index - centerOffset) * spacing;
    }
    group.add(node.group);
    nodes.push(node);
    nodeByName.set(nodeData.name, node);
    if (nodeData.id) {
      nodeById.set(nodeData.id, node);
    }

    if (nodeData.motionType) {
      motionNodes.push(node);
    }
    if (node.binaryBandData && node.binaryBandData.length) {
      node.binaryBandData.forEach((band) => {
        if (!band.ring) {
          return;
        }
        ringTargets.push({ mesh: band.ring, node, bandName: band.bandName });
        ringTargetByMesh.set(band.ring, { node, bandName: band.bandName });
      });
      if (!primaryBinaryNode) {
        primaryBinaryNode = node;
      }
    }
  });

  // Re-pack nucleus for element scenes: alternate P/N inside a faint circle.
  if (isElementScene) {
    let nucleusRadius = 0;
    const nucleons = nodes.filter(
      (n) => n.data.category === "proton" || n.data.category === "neutron"
    );
    const electrons = nodes.filter((n) => n.data.category === "electron");
    if (nucleons.length) {
      const avgRadius =
        nucleons.reduce((s, n) => s + (n.data.radius ?? 0.3), 0) /
        nucleons.length;
      // Make electrons match nucleon size for visual consistency.
      electrons.forEach((e) => {
        e.data.radius = avgRadius;
        e.mesh.geometry.dispose();
        e.mesh.geometry = new THREE.SphereGeometry(avgRadius, 32, 20);
        e.outline.geometry.dispose();
        e.outline.geometry = new THREE.EdgesGeometry(e.mesh.geometry);
      });
      const golden = Math.PI * (3 - Math.sqrt(5));
      let packRadius = Math.max(
        avgRadius * 2.2,
        Math.sqrt(nucleons.length) * avgRadius * 1.25
      );
      const positions = [];
      for (let i = 0; i < nucleons.length; i++) {
        const r = packRadius * Math.sqrt((i + 0.35) / nucleons.length);
        const theta = i * golden;
        positions.push(
          new THREE.Vector3(Math.cos(theta) * r, Math.sin(theta) * r, 0)
        );
      }
      const protons = nucleons.filter((n) => n.data.category === "proton");
      const neutrons = nucleons.filter((n) => n.data.category === "neutron");
      const ordered = [];
      while (protons.length || neutrons.length) {
        if (protons.length) ordered.push(protons.shift());
        if (neutrons.length) ordered.push(neutrons.shift());
      }
      ordered.forEach((node, idx) => {
        if (positions[idx]) {
          node.group.position.copy(positions[idx]);
        }
      });

      nucleusRadius = packRadius + avgRadius * 0.5;
      // Nucleus boundary retained via radius for layout, but no visible ring drawn.
    }

    // Orbit guides (thin rings) for each populated shell.
    const uniqueRadii = Array.from(
      new Set(
        electrons
          .map((e) => e.data.orbit?.radius)
          .filter((r) => typeof r === "number")
      )
    ).sort((a, b) => a - b);

    if (uniqueRadii.length) {
      const minShellRadius = nucleusRadius + 0.6;
      const shellGap = 0.9;
      const radiusMap = new Map();
      uniqueRadii.forEach((r, idx) => {
        radiusMap.set(r, minShellRadius + idx * shellGap);
      });

      electrons.forEach((e) => {
        const currentRadius = e.data.orbit?.radius;
        if (typeof currentRadius !== "number") {
          return;
        }
        const newRadius = radiusMap.get(currentRadius) ?? currentRadius;
        const pos = e.group.position;
        const angle = Math.atan2(pos.y, pos.x) || 0;
        if (!e.data.orbit) {
          e.data.orbit = { center: "origin", radius: newRadius, speed: 0, phase: angle };
        } else {
          e.data.orbit.radius = newRadius;
          e.data.orbit.phase = angle;
        }
        e.group.position.set(
          Math.cos(angle) * newRadius,
          Math.sin(angle) * newRadius,
          0
        );
      });

      const remappedRadii = uniqueRadii.map((r) => radiusMap.get(r) ?? r);
      remappedRadii.forEach((r) => {
        const guideGeo = new THREE.RingGeometry(
          Math.max(0.01, r - 0.06),
          r + 0.06,
          96
        );
        const guideMat = new THREE.MeshBasicMaterial({
          color: "#8fa7ff",
          transparent: true,
          opacity: 0.28,
          side: THREE.DoubleSide,
          depthWrite: false,
        });
        const guide = new THREE.Mesh(guideGeo, guideMat);
        guide.userData.excludeFromBounds = true;
        group.add(guide);
      });
    }
  } else {
    // Non-element scenes: still render orbit guides if present.
    const electrons = nodes.filter((n) => n.data.category === "electron");
    const shellRadii = Array.from(
      new Set(
        electrons
          .map((e) => e.data.orbit?.radius)
          .filter((r) => typeof r === "number")
      )
    ).sort((a, b) => a - b);
    shellRadii.forEach((r) => {
      const guideGeo = new THREE.RingGeometry(
        Math.max(0.01, r - 0.08),
        r + 0.08,
        96
      );
      const guideMat = new THREE.MeshBasicMaterial({
        color: "#8fa7ff",
        transparent: true,
        opacity: 0.28,
        side: THREE.DoubleSide,
        depthWrite: false,
      });
      const guide = new THREE.Mesh(guideGeo, guideMat);
      guide.userData.excludeFromBounds = true;
      group.add(guide);
    });
  }

  const level = {
    id: levelId,
    name: config.sceneName ?? levelId,
    sceneId: config.sceneId ?? null,
    markdownPath: config.markdownPath ?? null,
    markdownSection: config.markdownSection ?? null,
    markdownColumns: config.markdownColumns ?? null,
    markdownAutoOpen: config.markdownAutoOpen ?? true,
    centerOn: config.centerOn,
    group,
    nodes,
    nodeByName,
    nodeById,
    motionNodes,
    ringTargets,
    ringTargetByMesh,
    primaryBinaryNode,
    layout: config.layout,
    links: [],
  };

  if (level.id === rootScenePath) {
    layoutRootLevel(level);
  }

  levels.set(levelId, level);
  buildLevelLinks(level, config);
  updateLevelMotions(level, 0);
  return level;
}

function updateLevelMotions(level, timeSeconds) {
  level.motionNodes.forEach((node) => {
    const handler = motionHandlers[node.data.motionType];
    if (handler) {
      handler(node, level, timeSeconds);
    }
  });
}

function getLevelBoundsFromNodes(level) {
  const min = new THREE.Vector3(Infinity, Infinity, Infinity);
  const max = new THREE.Vector3(-Infinity, -Infinity, -Infinity);
  let hasNode = false;

  level.nodes.forEach((node) => {
    if (node.data?.excludeFromBounds) {
      return;
    }
    const radius = node.data.radius ?? 0;
    if (node.data.orbit) {
      const orbit = node.data.orbit;
      const centerNode =
        level.nodeByName.get(orbit.center) ?? level.nodeById.get(orbit.center);
      const centerPos = centerNode
        ? centerNode.group.position
        : Array.isArray(orbit.center)
          ? new THREE.Vector3(
              orbit.center[0] ?? 0,
              orbit.center[1] ?? 0,
              orbit.center[2] ?? 0
            )
          : node.group.position;
      const orbitRadius = orbit.radius ?? 0;
      const yScale = orbit.shape === "ellipsoid" ? orbit.yScale ?? 0.85 : 1;
      min.x = Math.min(min.x, centerPos.x - orbitRadius - radius);
      max.x = Math.max(max.x, centerPos.x + orbitRadius + radius);
      min.y = Math.min(min.y, centerPos.y - orbitRadius * yScale - radius);
      max.y = Math.max(max.y, centerPos.y + orbitRadius * yScale + radius);
      min.z = Math.min(min.z, centerPos.z - radius);
      max.z = Math.max(max.z, centerPos.z + radius);
    } else {
      const pos = node.group.position;
      min.x = Math.min(min.x, pos.x - radius);
      min.y = Math.min(min.y, pos.y - radius);
      min.z = Math.min(min.z, pos.z - radius);
      max.x = Math.max(max.x, pos.x + radius);
      max.y = Math.max(max.y, pos.y + radius);
      max.z = Math.max(max.z, pos.z + radius);
    }
    hasNode = true;
  });

  if (!hasNode) {
    return { size: new THREE.Vector3(), center: new THREE.Vector3() };
  }

  const size = new THREE.Vector3(
    max.x - min.x,
    max.y - min.y,
    max.z - min.z
  );
  const center = new THREE.Vector3(
    (min.x + max.x) / 2,
    (min.y + max.y) / 2,
    (min.z + max.z) / 2
  );
  return { size, center };
}

function getLevelCenter(level) {
  if (!level) {
    return new THREE.Vector3();
  }
  if (level.centerOn === "origin") {
    return new THREE.Vector3();
  }
  if (level.centerOn) {
    const node =
      level.nodeById.get(level.centerOn) ??
      level.nodeByName.get(level.centerOn);
    if (node) {
      return node.group.position.clone();
    }
  }
  return getLevelBoundsFromNodes(level).center;
}

function buildLevelLinks(level, config) {
  if (!config.links.length) {
    return;
  }
  config.links.forEach((link) => {
    const linkColor = link.color ?? linkColors[link.kind] ?? linkColors.default;
    const arrow = new THREE.ArrowHelper(
      new THREE.Vector3(1, 0, 0),
      new THREE.Vector3(),
      1,
      linkColor,
      linkStyle.headLengthMax,
      linkStyle.headLengthMax * linkStyle.headWidthFactor
    );
    arrow.line.material.transparent = true;
    arrow.line.material.opacity = linkStyle.lineOpacity;
    arrow.line.material.depthWrite = false;
    arrow.cone.material.transparent = true;
    arrow.cone.material.opacity = linkStyle.headOpacity;
    arrow.cone.material.depthWrite = false;
    level.group.add(arrow);
    level.links.push({
      arrow,
      from: link.from,
      to: link.to,
      direction: link.direction,
      length: link.length,
      kind: link.kind,
      opacity: 1,
      baseOpacity: {
        line: linkStyle.lineOpacity,
        cone: linkStyle.headOpacity,
      },
    });
  });
}

function getNodeForLink(level, linkId) {
  if (!linkId) {
    return null;
  }
  return level.nodeById.get(linkId) || level.nodeByName.get(linkId) || null;
}

function updateLevelLinks(level) {
  if (!level || !level.links.length) {
    return;
  }
  level.links.forEach((link) => {
    const fromNode = getNodeForLink(level, link.from);
    if (!fromNode) {
      return;
    }
    const fromPos = fromNode.group.position.clone();
    const fromRadius = fromNode.data.radius ?? 0;

    if (link.to) {
      const toNode = getNodeForLink(level, link.to);
      if (!toNode) {
        return;
      }
      const toPos = toNode.group.position.clone();
      const toRadius = toNode.data.radius ?? 0;
      const dir = toPos.clone().sub(fromPos);
      const distance = dir.length();
      if (distance <= 0.0001) {
        return;
      }
      dir.normalize();
      const length = Math.max(
        linkStyle.minLength,
        distance - fromRadius - toRadius - linkStyle.tipClearance
      );
      const origin = fromPos
        .clone()
        .add(dir.clone().multiplyScalar(fromRadius + linkStyle.tipClearance));
      const headLength = clamp(
        length * 0.3,
        linkStyle.headLengthMin,
        linkStyle.headLengthMax
      );
      const headWidth = headLength * linkStyle.headWidthFactor;
      link.arrow.position.copy(origin);
      link.arrow.setDirection(dir);
      link.arrow.setLength(length, headLength, headWidth);
    } else if (Array.isArray(link.direction)) {
      const dir = new THREE.Vector3(
        link.direction[0] ?? 0,
        link.direction[1] ?? 0,
        link.direction[2] ?? 0
      );
      if (dir.lengthSq() < 0.0001) {
        return;
      }
      dir.normalize();
      const length = Math.max(linkStyle.minLength, link.length ?? 2);
      const origin = fromPos
        .clone()
        .add(dir.clone().multiplyScalar(fromRadius + linkStyle.tipClearance));
      const headLength = clamp(
        length * 0.3,
        linkStyle.headLengthMin,
        linkStyle.headLengthMax
      );
      const headWidth = headLength * linkStyle.headWidthFactor;
      link.arrow.position.copy(origin);
      link.arrow.setDirection(dir);
      link.arrow.setLength(length, headLength, headWidth);
    }
  });
}

function setLevelLinkOpacity(level, opacity) {
  if (!level || !level.links.length) {
    return;
  }
  level.links.forEach((link) => {
    link.opacity = opacity;
    link.arrow.line.material.opacity = link.baseOpacity.line * opacity;
    link.arrow.cone.material.opacity = link.baseOpacity.cone * opacity;
  });
}

function updateLevelLabelWrap(level) {
  if (!level) {
    return;
  }
  level.nodes.forEach((node) => {
    if (!node.data.wrapLabel) {
      return;
    }
    const metrics = getNodeScreenMetrics(node);
    const diameter = metrics.radiusPx * 2;
    const targetWidth = Math.round(diameter * 0.8);
    const minWidth = 36;
    const maxAllowed = Math.round(diameter * 0.95);
    const maxWidth = Math.max(minWidth, Math.min(targetWidth, maxAllowed));
    if (node.labelMaxWidth !== maxWidth) {
      node.labelMaxWidth = maxWidth;
      node.labelObject.element.style.maxWidth = `${maxWidth}px`;
      node.labelObject.element.style.width = `${maxWidth}px`;
    }
  });
}

function updateGlowRingOrientation(level) {
  if (!level?.nodes?.length) {
    return;
  }
  level.nodes.forEach((node) => {
    if (!node.extraMeshes || !node.extraMeshes.length) {
      return;
    }
    node.extraMeshes.forEach((entry) => {
      const mesh = entry.mesh;
      if (!mesh?.userData?.isGlowRing) {
        return;
      }
      mesh.quaternion.copy(camera.quaternion);
    });
  });
}

function setNodeExtraOpacity(node, opacity) {
  if (!node.extraMeshes || !node.extraMeshes.length) {
    return;
  }
  node.extraMeshes.forEach((entry) => {
    entry.mesh.material.opacity = entry.baseOpacity * opacity;
  });
}

function setLevelOpacity(level, opacity) {
  level.nodes.forEach((node) => {
    node.mesh.material.opacity = node.baseOpacity.mesh * opacity;
    node.outline.material.opacity = node.baseOpacity.outline * opacity;
    node.labelObject.element.style.opacity = opacity;
    node.haloIntensity = opacity;
    setNodeExtraOpacity(node, opacity);
  });
}

function setLevelOpacityWithLabel(level, meshOpacity, labelOpacity) {
  level.nodes.forEach((node) => {
    node.mesh.material.opacity = node.baseOpacity.mesh * meshOpacity;
    node.outline.material.opacity = node.baseOpacity.outline * meshOpacity;
    node.labelObject.element.style.opacity = labelOpacity;
    node.haloIntensity = meshOpacity;
    setNodeExtraOpacity(node, meshOpacity);
  });
}

function setLevelLabelOpacity(level, labelOpacity) {
  level.nodes.forEach((node) => {
    node.labelObject.element.style.opacity = labelOpacity;
  });
}

function setLevelOpacityWithFocus(level, focusId, focusOpacity, otherOpacity) {
  level.nodes.forEach((node) => {
    const opacity =
      node.data.id === focusId || node.data.name === focusId
        ? focusOpacity
        : otherOpacity;
    node.mesh.material.opacity = node.baseOpacity.mesh * opacity;
    node.outline.material.opacity = node.baseOpacity.outline * opacity;
    node.labelObject.element.style.opacity = opacity;
    node.haloIntensity = opacity;
    setNodeExtraOpacity(node, opacity);
  });
}

function setLevelOpacityWithFocusAndLabel(
  level,
  focusId,
  focusOpacity,
  otherOpacity,
  labelOpacity
) {
  level.nodes.forEach((node) => {
    const opacity =
      node.data.id === focusId || node.data.name === focusId
        ? focusOpacity
        : otherOpacity;
    node.mesh.material.opacity = node.baseOpacity.mesh * opacity;
    node.outline.material.opacity = node.baseOpacity.outline * opacity;
    node.labelObject.element.style.opacity = opacity * labelOpacity;
    node.haloIntensity = opacity;
    setNodeExtraOpacity(node, opacity);
  });
}

function updateLevelHalo(level, timeSeconds) {
  if (!level) {
    return;
  }
  level.nodes.forEach((node) => {
    if (!node.halo) {
      return;
    }
    const pulse = 0.5 + 0.5 * Math.sin(timeSeconds * 1.5 + node.haloPhase);
    const scale = 1.02 + 0.06 * pulse;
    node.halo.scale.setScalar(scale);
    node.halo.material.opacity =
      node.haloBaseOpacity * node.haloIntensity * (0.35 + 0.65 * pulse);
  });
}

function updateBinaryRingPulse(level, timeSeconds) {
  if (!level) {
    return;
  }
  level.nodes.forEach((node) => {
    if (!node.binaryBandData || !node.binaryBandData.length) {
      return;
    }
    const pulsingBand = getPulsingBandName(node);
    node.binaryBandData.forEach((band) => {
      if (!band.ring) {
        return;
      }
      const base = band.ringBaseOpacity ?? binaryStyle.ringOpacity;
      const pulse =
        pulsingBand && band.bandName === pulsingBand
          ? 0.65 + 0.35 * Math.sin(timeSeconds * 2.2 + node.haloPhase)
          : 1;
      band.ring.material.opacity = base * (node.haloIntensity ?? 1) * pulse;
    });
  });
}

function beginLevelTransition(targetNode, childLevelId) {
  if (transitionState.active) {
    return;
  }
  if (!childLevelId) {
    return;
  }

  closeDetailPanel();
  hideHoverTooltip();
  hideMarkdownPanel();
  const toLevel = buildLevel(childLevelId);
  if (!worldGroup.children.includes(toLevel.group)) {
    worldGroup.add(toLevel.group);
  }

  const targetWorld = new THREE.Vector3();
  targetNode.group.getWorldPosition(targetWorld);
  const targetPosition = targetWorld.sub(worldGroup.position);
  const toLevelCenter = getLevelCenter(toLevel);
  const warpScale = computeWarpScale(targetNode.data.radius);
  const toStartScale = 0.5;
  const focusNodeId = targetNode.data.id ?? targetNode.data.name;
  const zoomTarget = computeFitZoomForLevel(toLevel);
  const panStart = worldGroup.position.clone();
  const panTarget = new THREE.Vector3(-targetPosition.x, -targetPosition.y, 0);

  zoomState.active = false;
  panTween.active = false;

  transitionState.active = true;
  transitionState.fromLevel = currentLevel;
  transitionState.toLevel = toLevel;
  transitionState.mode = "warpIn";
  transitionState.payload = {
    focusNodeId,
    zoomStart: camera.zoom,
    zoomTarget,
    warpScale,
    toStartScale,
    panStart,
    panTarget,
  };
  transitionState.startTime = performance.now();
  transitionState.duration = 2250;

  toLevel.group.position.copy(targetPosition).sub(toLevelCenter);
  toLevel.group.scale.setScalar(toStartScale);
  setLevelOpacity(toLevel, 0);
  setLevelLabelOpacity(toLevel, 0);
  setLevelOpacityWithFocus(currentLevel, focusNodeId, 1, 0);
  setLevelLinkOpacity(currentLevel, 0);

  navigationStack.push({
    levelId: currentLevel.id,
    focusNodeId: targetNode.data.id ?? targetNode.data.name,
  });
}

async function startLevelTransitionFromNode(targetNode) {
  const childLevelId = targetNode.data.children || targetNode.data.childScene;
  if (!childLevelId) {
    return;
  }

  if (!levelConfigs[childLevelId]) {
    const config = await loadSceneConfig(childLevelId);
    if (!config) {
      return;
    }
  }
  await ensureDynamicSceneConfig(childLevelId);

  beginLevelTransition(targetNode, childLevelId);
}

function startLevelTransitionOut() {
  if (transitionState.active || navigationStack.length === 0) {
    return;
  }

  closeDetailPanel();
  hideHoverTooltip();
  hideMarkdownPanel();
  const parentInfo = navigationStack[navigationStack.length - 1];
  const parentLevel = buildLevel(parentInfo.levelId);
  const parentNode =
    parentLevel.nodeById.get(parentInfo.focusNodeId) ??
    parentLevel.nodeByName.get(parentInfo.focusNodeId);
  if (!parentNode) {
    return;
  }

  if (!worldGroup.children.includes(parentLevel.group)) {
    worldGroup.add(parentLevel.group);
  }

  const parentCenter = getLevelCenter(parentLevel);
  zoomState.active = false;
  panTween.active = false;

  transitionState.active = true;
  transitionState.fromLevel = currentLevel;
  transitionState.toLevel = parentLevel;
  transitionState.mode = "warpOut";
  transitionState.payload = {
    focusNodeId: parentInfo.focusNodeId,
    zoomStart: camera.zoom,
    zoomTarget: computeFitZoomForLevel(parentLevel),
    toStartScale: computeWarpScaleForLevel(parentLevel),
    panStart: worldGroup.position.clone(),
    fromPivot: null,
  };
  transitionState.startTime = performance.now();
  transitionState.duration = 2250;

  parentLevel.group.position
    .copy(parentCenter)
    .multiplyScalar(-1)
    .sub(worldGroup.position);
  parentLevel.group.scale.setScalar(transitionState.payload.toStartScale);
  setLevelOpacity(parentLevel, 0);
  setLevelLabelOpacity(parentLevel, 0);
  setLevelOpacity(currentLevel, 1);

  const pivotOrigin = new THREE.Vector3(
    -worldGroup.position.x,
    -worldGroup.position.y,
    0
  );
  if (pivotOrigin.lengthSq() > 0.0001) {
    const pivot = new THREE.Group();
    pivot.position.copy(pivotOrigin);
    worldGroup.add(pivot);
    const oldPos = currentLevel.group.position.clone();
    worldGroup.remove(currentLevel.group);
    pivot.add(currentLevel.group);
    currentLevel.group.position.copy(oldPos).sub(pivotOrigin);
    transitionState.payload.fromPivot = pivot;
  }
}

function finalizeTransition() {
  if (!transitionState.active) {
    return;
  }
  const handler = transitionHandlers[transitionState.mode];
  if (!handler) {
    transitionState.active = false;
    transitionState.payload = null;
    return;
  }
  handler.finalize();
  transitionState.active = false;
  transitionState.payload = null;
}

function updateTransition(now) {
  if (!transitionState.active) {
    return;
  }
  const handler = transitionHandlers[transitionState.mode];
  if (!handler) {
    finalizeTransition();
    return;
  }
  const done = handler.update(now);
  if (done) {
    finalizeTransition();
  }
}

const transitionHandlers = {
  warpIn: {
    update: (now) => {
      const { fromLevel, toLevel, payload } = transitionState;
      if (!fromLevel || !toLevel || !payload) {
        return true;
      }
      const elapsed = now - transitionState.startTime;
      const t = Math.min(1, elapsed / transitionState.duration);
      const panProgress = smoothstep(0, 0.35, t);
      const scaleProgress = smoothstep(0.35, 1, t);
      const zoomProgress = scaleProgress;

      const nextZoom =
        payload.zoomStart +
        (payload.zoomTarget - payload.zoomStart) * zoomProgress;
      applyZoom(nextZoom);

      const focusNode = getTransitionFocusNode(fromLevel);
      if (focusNode) {
        const baseScale = focusNode.baseScale ?? focusNode.data?.baseScale ?? 1;
        focusNode.group.scale.setScalar(
          baseScale * (1 + (payload.warpScale - 1) * scaleProgress)
        );
      }
      const toScale =
        payload.toStartScale +
        (1 - payload.toStartScale) * scaleProgress;
      toLevel.group.scale.setScalar(toScale);
      worldGroup.position.lerpVectors(
        payload.panStart,
        payload.panTarget,
        panProgress
      );

      const focusFade = 1 - smoothstep(0.55, 1, scaleProgress);
      const toFade = Math.pow(smoothstep(0.2, 1, scaleProgress), 1.6);
      setLevelOpacityWithFocus(
        fromLevel,
        payload.focusNodeId,
        focusFade,
        0
      );
      setLevelLinkOpacity(fromLevel, 0);
      setLevelOpacityWithLabel(toLevel, toFade, 0);
      setLevelLinkOpacity(toLevel, toFade);
      return t >= 1;
    },
    finalize: () => {
      const { fromLevel, toLevel, payload } = transitionState;
      if (!fromLevel || !toLevel || !payload) {
        return;
      }
      const fromFocus = getTransitionFocusNode(fromLevel);
      if (fromFocus) {
        resetNodeScale(fromFocus);
      }
      fromLevel.group.scale.setScalar(1);
      setLevelOpacity(fromLevel, 0);
      setLevelLinkOpacity(fromLevel, 0);
      worldGroup.remove(fromLevel.group);

      toLevel.group.scale.setScalar(1);
      setLevelOpacity(toLevel, 1);
      setLevelLabelOpacity(toLevel, 0);
      setLevelLinkOpacity(toLevel, 1);

      currentLevel = toLevel;
      zoomState.active = false;
      panTween.active = false;
      applyZoom(payload.zoomTarget ?? camera.zoom);
      labelFadeState.active = true;
      labelFadeState.level = currentLevel;
      labelFadeState.startTime = performance.now();
      updateSceneLabel();
      updateSceneMarkdown();
    },
  },
  warpOut: {
    update: (now) => {
      const { fromLevel, toLevel, payload } = transitionState;
      if (!fromLevel || !toLevel || !payload) {
        return true;
      }
      const elapsed = now - transitionState.startTime;
      const t = Math.min(1, elapsed / transitionState.duration);
      const scaleProgress = smoothstep(0.35, 1, t);
      const zoomProgress = scaleProgress;

      const nextZoom =
        payload.zoomStart +
        (payload.zoomTarget - payload.zoomStart) * zoomProgress;
      applyZoom(nextZoom);

      const toScale =
        payload.toStartScale + (1 - payload.toStartScale) * scaleProgress;
      toLevel.group.scale.setScalar(toScale);
      worldGroup.position.copy(payload.panStart);

      const fromScale = Math.max(0.05, 1 - 0.95 * scaleProgress);
      if (payload.fromPivot) {
        payload.fromPivot.scale.setScalar(fromScale);
      } else {
        fromLevel.group.scale.setScalar(fromScale);
      }

      const fromFade = 1 - smoothstep(0.35, 0.95, t);
      const toFade = smoothstep(0.3, 1, t);
      setLevelOpacity(fromLevel, fromFade);
      setLevelLinkOpacity(fromLevel, fromFade);
      setLevelOpacityWithLabel(toLevel, toFade, 0);
      setLevelLinkOpacity(toLevel, toFade);
      return t >= 1;
    },
    finalize: () => {
      const { fromLevel, toLevel, payload } = transitionState;
      if (!fromLevel || !toLevel || !payload) {
        return;
      }
      toLevel.group.scale.setScalar(1);
      setLevelOpacity(toLevel, 1);
      setLevelLabelOpacity(toLevel, 0);
      setLevelLinkOpacity(toLevel, 1);

      const toFocus = getTransitionFocusNode(toLevel);
      if (toFocus) {
        resetNodeScale(toFocus);
      }
      if (payload.fromPivot) {
        payload.fromPivot.scale.setScalar(1);
        payload.fromPivot.remove(fromLevel.group);
        worldGroup.remove(payload.fromPivot);
        payload.fromPivot = null;
      } else {
        fromLevel.group.scale.setScalar(1);
        worldGroup.remove(fromLevel.group);
      }
      setLevelOpacity(fromLevel, 0);
      setLevelLinkOpacity(fromLevel, 0);

      currentLevel = toLevel;
      navigationStack.pop();
      zoomState.active = false;
      panTween.active = false;
      applyZoom(payload.zoomTarget ?? camera.zoom);
      labelFadeState.active = true;
      labelFadeState.level = currentLevel;
      labelFadeState.startTime = performance.now();
      updateSceneLabel();
      updateSceneMarkdown();
    },
  },
  jump: {
    update: (now) => {
      const { fromLevel, toLevel, payload } = transitionState;
      if (!toLevel || !payload) {
        return true;
      }
      const elapsed = now - transitionState.startTime;
      const t = Math.min(1, elapsed / transitionState.duration);
      const fade = smoothstep(0, 1, t);
      if (fromLevel) {
        setLevelOpacity(fromLevel, 1 - fade);
        setLevelLinkOpacity(fromLevel, 1 - fade);
      }
      setLevelOpacity(toLevel, fade);
      setLevelLinkOpacity(toLevel, fade);
      const startScale = payload.startScale ?? 1;
      const scale = startScale + (1 - startScale) * fade;
      toLevel.group.scale.setScalar(scale);
      const nextZoom =
        payload.zoomStart + (payload.zoomTarget - payload.zoomStart) * fade;
      applyZoom(nextZoom);
      return t >= 1;
    },
    finalize: () => {
      const { fromLevel, toLevel, payload } = transitionState;
      if (!toLevel || !payload) {
        return;
      }
      if (fromLevel) {
        setLevelOpacity(fromLevel, 0);
        setLevelLinkOpacity(fromLevel, 0);
        worldGroup.remove(fromLevel.group);
      }
      toLevel.group.scale.setScalar(1);
      setLevelOpacity(toLevel, 1);
      setLevelLabelOpacity(toLevel, 0);
      setLevelLinkOpacity(toLevel, 1);
      currentLevel = toLevel;
      applyZoom(payload.zoomTarget ?? camera.zoom);
      labelFadeState.active = true;
      labelFadeState.level = currentLevel;
      labelFadeState.startTime = performance.now();
      updateSceneLabel();
      updateSceneMarkdown();
    },
  },
};

function getNodeScreenMetrics(node) {
  const worldPos = new THREE.Vector3();
  node.group.getWorldPosition(worldPos);
  const worldEdge = worldPos.clone().add(new THREE.Vector3(node.data.radius, 0, 0));

  const ndcPos = worldPos.clone().project(camera);
  const ndcEdge = worldEdge.clone().project(camera);

  const centerPx = {
    x: (ndcPos.x * 0.5 + 0.5) * canvas.clientWidth,
    y: (-ndcPos.y * 0.5 + 0.5) * canvas.clientHeight,
  };
  const edgePx = {
    x: (ndcEdge.x * 0.5 + 0.5) * canvas.clientWidth,
    y: (-ndcEdge.y * 0.5 + 0.5) * canvas.clientHeight,
  };
  const radiusPx = Math.hypot(edgePx.x - centerPx.x, edgePx.y - centerPx.y);
  return { centerPx, radiusPx };
}

function findClosestNodeToCenter() {
  if (!currentLevel) {
    return null;
  }
  const center = {
    x: canvas.clientWidth / 2,
    y: canvas.clientHeight / 2,
  };
  let best = null;
  currentLevel.nodes.forEach((node) => {
    const metrics = getNodeScreenMetrics(node);
    const dist = Math.hypot(
      metrics.centerPx.x - center.x,
      metrics.centerPx.y - center.y
    );
    if (!best || dist < best.dist) {
      best = { node, dist, ...metrics };
    }
  });
  if (!best) {
    return null;
  }
  best.isInside = best.dist <= best.radiusPx * 0.9;
  return best;
}

function maybeAutoWarp(now) {
  if (transitionState.active) {
    return;
  }
  if (now - autoWarpThresholds.lastAt < autoWarpThresholds.cooldownMs) {
    return;
  }
  if (now - lastZoomGestureTime > 320) {
    return;
  }

  const candidate = findClosestNodeToCenter();
  if (!candidate) {
    return;
  }

  if (candidate.radiusPx >= autoWarpThresholds.inPx && candidate.isInside) {
    const childLevelId =
      candidate.node.data.children || candidate.node.data.childScene;
    if (childLevelId) {
      autoWarpThresholds.lastAt = now;
      startLevelTransitionFromNode(candidate.node);
    }
  }
}

function updateNavButton() {
  if (!navUpButton) {
    return;
  }
  if (transitionState.active) {
    navUpButton.disabled = true;
    updateDocButton();
    return;
  }
  navUpButton.disabled =
    navigationStack.length === 0 && searchBackStack.length === 0;
  updateDocButton();
}

async function ensurePeriodicTable() {
  if (periodicTableCache.ready) {
    return periodicTableCache.data;
  }
  try {
    const resp = await fetch("json/chemistry/periodic_table.json");
    if (!resp.ok) {
      throw new Error("Failed to load periodic table");
    }
    const data = await resp.json();
    periodicTableCache.data = data;
    periodicTableCache.ready = true;
    return data;
  } catch (err) {
    console.error(err);
    periodicTableCache.data = null;
    periodicTableCache.ready = false;
    return null;
  }
}

function getPeriodicColor(category) {
  if (!category) {
    return periodicCategoryColors.unknown;
  }
  const key = category.toLowerCase();
  return periodicCategoryColors[key] || periodicCategoryColors.unknown;
}

function showPeriodicElementDetail(el) {
  if (!detailPanel || !detailTitle || !detailBody) {
    return;
  }
  detailPanel.classList.add("is-open");
  detailPanel.setAttribute("aria-hidden", "false");
  detailPanel.inert = false;
  detailTitle.textContent = `${el.symbol} — ${el.name}`;
  const fields = [
    ["Atomic #", el.number],
    ["Category", el.category],
    ["Phase", el.phase],
    ["Atomic mass", el.atomic_mass ? `${el.atomic_mass}` : null],
    ["Electron config", el.electron_configuration_semantic],
    ["Electronegativity", el.electronegativity_pauling],
    ["Electron affinity", el.electron_affinity],
    ["Melting point", el.melt],
    ["Boiling point", el.boil],
    ["Density", el.density],
    ["Block", el.block],
    ["Shells", Array.isArray(el.shells) ? el.shells.join(", ") : el.shells],
    ["Summary", el.summary],
  ];
  detailBody.innerHTML = "";
  fields.forEach(([label, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    const isSummary = label === "Summary";
    const row = document.createElement("div");
    row.className = "detail-row" + (isSummary ? " summary-row" : "");
    const key = document.createElement("div");
    key.className = "detail-key";
    key.textContent = label;
    const val = document.createElement("div");
    val.className = "detail-value";
    val.textContent = String(value);
    row.appendChild(key);
    row.appendChild(val);
    detailBody.appendChild(row);
  });
}

function buildPeriodicGrid(data) {
  if (!periodicGrid || !periodicLegend || !data?.elements) {
    return;
  }
  periodicGrid.innerHTML = "";
  periodicLegend.innerHTML = "";
  const frag = document.createDocumentFragment();
  const legendSet = new Map();
  data.elements.forEach((el) => {
    const btn = document.createElement("button");
    btn.className = "ptable-cell";
    btn.style.gridColumn = el.xpos;
    btn.style.gridRow = el.ypos;
    const color = getPeriodicColor(el.category);
    btn.style.background = `${color}22`;
    btn.style.borderColor = color;
    btn.dataset.symbol = el.symbol;
    btn.dataset.number = el.number;
    btn.innerHTML = `
      <div class="ptable-number">${el.number}</div>
      <div class="ptable-symbol">${el.symbol}</div>
      <div class="ptable-name">${el.name}</div>
    `;
    btn.addEventListener("click", () => {
      showPeriodicElementDetail(el);
      if (currentLevel) {
        searchBackStack.push({
          levelId: currentLevel.id,
          navigationStack: navigationStack.map((entry) => ({
            levelId: entry.levelId,
            focusNodeId: entry.focusNodeId,
          })),
        });
        updateNavButton();
      }
      const sceneId = el.symbol.toLowerCase();
      const path = `json/elements/${sceneId}.json`;
      if (periodicOverlay) {
        periodicOverlay.classList.add("is-fading");
      }
      jumpToScene(path, { mode: "jump", startScale: 0.35, duration: 2000 });
    });
    btn.addEventListener("mouseenter", () => showPeriodicElementDetail(el));
    frag.appendChild(btn);
    const legendKey = el.category || "Unknown";
    if (!legendSet.has(legendKey)) {
      legendSet.set(legendKey, color);
    }
  });
  periodicGrid.appendChild(frag);
  const legendFrag = document.createDocumentFragment();
  Array.from(legendSet.entries())
    .sort((a, b) => a[0].localeCompare(b[0]))
    .forEach(([label, color]) => {
      const item = document.createElement("div");
      item.className = "ptable-legend-item";
      item.innerHTML = `<span class="ptable-legend-swatch" style="background:${color}"></span>${label}`;
      legendFrag.appendChild(item);
    });
  periodicLegend.appendChild(legendFrag);
  periodicGridBuilt = true;
}

async function updatePeriodicOverlay() {
  if (!periodicOverlay) {
    return;
  }
  const isPeriodic = currentLevel?.sceneId === "periodic_table";
  periodicOverlay.classList.toggle("is-open", !!isPeriodic);
  periodicOverlay.setAttribute("aria-hidden", isPeriodic ? "false" : "true");
  periodicOverlay.inert = !isPeriodic;
  if (!isPeriodic) {
    if (periodicOverlay.contains(document.activeElement)) {
      (navUpButton ?? homeButton ?? sceneSearchToggle ?? document.body).focus();
    }
    periodicOverlay.classList.remove("is-fading");
    return;
  }
  const data = await ensurePeriodicTable();
  if (data && !periodicGridBuilt) {
    buildPeriodicGrid(data);
  }
}

function updateElementLegend() {
  if (!elementLegend) {
    return;
  }
  const isElement =
    currentLevel && typeof currentLevel.id === "string"
      ? currentLevel.id.startsWith("json/elements/")
      : false;
  elementLegend.classList.toggle("is-open", isElement);
  elementLegend.setAttribute("aria-hidden", isElement ? "false" : "true");
  elementLegend.inert = !isElement;
}

function getElementBySymbol(symbol) {
  if (!symbol) {
    return null;
  }
  const upper = symbol.toUpperCase();
  if (!periodicTableCache.data?.elements) {
    return null;
  }
  return periodicTableCache.data.elements.find(
    (el) => el.symbol.toUpperCase() === upper
  );
}

async function updateElementInfoPanel() {
  if (!detailPanel || !detailTitle || !detailBody) {
    return;
  }
  const scenePath = currentLevel?.id ?? "";
  const sceneId = currentLevel?.sceneId ?? "";
  const symbolFromPath = scenePath.includes("/elements/")
    ? scenePath.split("/").pop()?.replace(".json", "")
    : null;
  const symbol = (sceneId || symbolFromPath || "").trim();
  const isElement =
    scenePath.includes("/elements/") || /^[a-z]{1,3}$/i.test(symbol);

  if (!isElement) {
    if (elementInfoPinned) {
      detailPanel.classList.remove("is-open");
      detailPanel.setAttribute("aria-hidden", "true");
      detailPanel.inert = true;
      elementInfoPinned = false;
    }
    return;
  }

  const data = await ensurePeriodicTable();
  if (!data?.elements) {
    return;
  }
  const el = getElementBySymbol(symbol);
  if (!el) {
    return;
  }

  detailPanel.classList.add("is-open");
  detailPanel.setAttribute("aria-hidden", "false");
  detailPanel.inert = false;
  elementInfoPinned = true;

  detailTitle.textContent = `${el.name} (${el.symbol})`;
  const protons = el.number ?? 0;
  const neutrons = Math.max(0, Math.round(el.atomic_mass ?? 0) - protons);
  const electrons = protons;
  const orbitals =
    typeof el.electron_configuration_semantic === "string"
      ? el.electron_configuration_semantic.split(/\s+/).filter(Boolean)
      : [];

  const fields = [
    ["Atomic #", el.number],
    ["Category", el.category],
    ["Phase", el.phase],
    ["Atomic mass", el.atomic_mass ? `${el.atomic_mass}` : null],
    ["Electron config", el.electron_configuration_semantic],
    ["Melting point", el.melt],
    ["Boiling point", el.boil],
    ["Density", el.density],
    ["Shells", Array.isArray(el.shells) ? el.shells.join(", ") : el.shells],
    ["Protons", protons],
    ["Neutrons", neutrons],
    ["Electrons", electrons],
  ];

  detailBody.innerHTML = "";
  fields.forEach(([label, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    const row = document.createElement("div");
    row.className = "detail-row";
    const key = document.createElement("div");
    key.className = "detail-key";
    key.textContent = label;
    const val = document.createElement("div");
    val.className = "detail-value";
    val.textContent = String(value);
    row.appendChild(key);
    row.appendChild(val);
    detailBody.appendChild(row);
  });

  if (orbitals.length) {
    const row = document.createElement("div");
    row.className = "detail-row detail-row-full";
    const key = document.createElement("div");
    key.className = "detail-key";
    key.textContent = "Orbitals (inner \u2192 outer)";
    const val = document.createElement("div");
    val.className = "detail-value";
    val.style.width = "100%";
    const list = document.createElement("div");
    list.style.display = "flex";
    list.style.flexWrap = "wrap";
    list.style.gap = "6px";
    list.style.marginTop = "8px";
    list.style.justifyContent = "flex-start";
    orbitals.forEach((orb) => {
      const chip = document.createElement("span");
      chip.textContent = orb;
      chip.style.padding = "2px 6px";
      chip.style.borderRadius = "8px";
      chip.style.background = "rgba(255,255,255,0.08)";
      chip.style.border = "1px solid rgba(160, 170, 220, 0.25)";
      list.appendChild(chip);
    });
    val.appendChild(list);
    row.appendChild(key);
    row.appendChild(val);
    detailBody.appendChild(row);
  }
}
function wireElementLegend() {
  if (!elementLegendItems.length) {
    return;
  }
  elementLegendItems.forEach((btn) => {
    const scenePath = btn.getAttribute("data-scene");
    if (!scenePath) {
      return;
    }
    btn.addEventListener("click", () => {
      if (transitionState.active) {
        return;
      }
      if (currentLevel) {
        searchBackStack.push({
          levelId: currentLevel.id,
          navigationStack: navigationStack.map((entry) => ({
            levelId: entry.levelId,
            focusNodeId: entry.focusNodeId,
          })),
        });
        updateNavButton();
      }
      jumpToScene(scenePath, { mode: "jump" });
    });
  });
}


function updateDocButton() {
  if (!docButton) {
    return;
  }
  const hasDoc = !!currentLevel?.markdownPath;
  docButton.classList.toggle("is-hidden", !hasDoc);
  docButton.disabled = transitionState.active || !hasDoc;
}

function updateMetaButton() {
  const button = document.getElementById("meta-button");
  if (!button) {
    return;
  }
  const isMeta = currentLevel?.id === metaScenePath;
  button.classList.toggle("is-active", isMeta);
  button.setAttribute("aria-pressed", String(isMeta));
}

function setComposerPanel(panelId) {
  if (!composerOverlay) {
    return;
  }
  const targetId = panelId || "tree";
  const hasPanel = composerPanels.some(
    (panel) => panel.dataset.panel === targetId
  );
  const nextPanel = hasPanel ? targetId : "tree";
  composerActivePanel = nextPanel;
  composerTabs.forEach((tab) => {
    const isActive = tab.dataset.panel === nextPanel;
    tab.classList.toggle("is-active", isActive);
    tab.setAttribute("aria-selected", String(isActive));
    tab.tabIndex = isActive ? 0 : -1;
  });
  composerPanels.forEach((panel) => {
    const isActive = panel.dataset.panel === nextPanel;
    panel.classList.toggle("is-active", isActive);
    panel.setAttribute("aria-hidden", String(!isActive));
  });
}

function updateComposerOverlay() {
  if (!composerOverlay) {
    return;
  }
  const isComposer = currentLevel?.sceneId === composerSceneId;
  composerOverlay.classList.toggle("is-open", !!isComposer);
  composerOverlay.setAttribute("aria-hidden", isComposer ? "false" : "true");
  composerOverlay.inert = !isComposer;
  if (isComposer) {
    setComposerPanel(composerActivePanel);
  }
}

function openComposerDocs() {
  if (transitionState.active) {
    return;
  }
  showMarkdownPanel({
    name: "Arch API",
    markdownPath: composerDocsPath,
    markdownColumns: 2,
  });
}

function updateMarkdownDocButton() {
  if (!markdownDocButton) {
    return;
  }
  const hasDoc = !!currentLevel?.markdownPath;
  markdownDocButton.classList.toggle("is-hidden", !hasDoc);
  markdownDocButton.disabled = !hasDoc;
}

function updateSceneLabel() {
  if (!sceneLabel) {
    return;
  }
  sceneLabel.textContent = currentLevel?.name ?? "";
  updateDocButton();
  updateMetaButton();
  updateMarkdownDocButton();
  updateComposerOverlay();
  updatePeriodicOverlay();
  updateElementLegend();
  updateElementInfoPanel();
}

function openMetaRing() {
  if (transitionState.active) {
    return;
  }
  if (currentLevel?.id === metaScenePath) {
    const backState = metaBackStack.pop();
    if (backState?.levelId) {
      jumpToScene(backState.levelId, {
        restoreNavStack: backState.navigationStack,
      });
    } else {
      resetToRootScene();
    }
    return;
  }
  if (currentLevel) {
    metaBackStack.push({
      levelId: currentLevel.id,
      navigationStack: navigationStack.map((entry) => ({
        levelId: entry.levelId,
        focusNodeId: entry.focusNodeId,
      })),
    });
  }
  jumpToScene(metaScenePath, { mode: "jump", startScale: 0.7, duration: 760 });
}


async function ensureSceneIndex() {
  if (sceneIndexReady) {
    return;
  }
  try {
    const response = await fetch("json/scenes_index.json");
    if (!response.ok) {
      throw new Error("Failed to load scene index");
    }
    const data = await response.json();
    sceneIndex = Array.isArray(data.scenes) ? data.scenes : [];
    sceneIndexReady = true;
  } catch (error) {
    console.error(error);
    sceneIndex = [];
  }
}

function setSearchOpen(isOpen) {
  if (!sceneSearchPanel) {
    return;
  }
  if (!isOpen && sceneSearchPanel.contains(document.activeElement)) {
    sceneSearchToggle?.focus();
  }
  sceneSearch?.classList.toggle("is-open", isOpen);
  sceneSearchPanel.classList.toggle("is-open", isOpen);
  sceneSearchPanel.setAttribute("aria-hidden", String(!isOpen));
  sceneSearchPanel.inert = !isOpen;
  if (isOpen && sceneSearchInput) {
    sceneSearchInput.value = "";
    updateSearchResults("");
    sceneSearchInput.focus();
  }
}

function isSearchOpen() {
  return sceneSearchPanel?.classList.contains("is-open");
}

function isSearchEventTarget(target) {
  return (
    sceneSearchPanel?.contains(target) || sceneSearchToggle?.contains(target)
  );
}

function normalizeSearch(text) {
  return text.trim().toLowerCase();
}

function updateSearchResults(query) {
  if (!sceneSearchResults) {
    return;
  }
  const normalized = normalizeSearch(query);
  const matches = sceneIndex.filter((scene) => {
    if (!normalized) {
      return true;
    }
    const name = (scene.name || "").toLowerCase();
    const id = (scene.id || "").toLowerCase();
    return name.includes(normalized) || id.includes(normalized);
  });

  sceneSearchResults.innerHTML = "";
  matches.slice(0, 10).forEach((scene) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "scene-search-item";
    item.textContent = scene.name ?? scene.id ?? scene.path;
    item.addEventListener("click", () => {
      if (currentLevel) {
        searchBackStack.push({
          levelId: currentLevel.id,
          navigationStack: navigationStack.map((entry) => ({
            levelId: entry.levelId,
            focusNodeId: entry.focusNodeId,
          })),
        });
      }
      setSearchOpen(false);
      jumpToScene(scene.path, { mode: "jump" });
    });
    sceneSearchResults.appendChild(item);
  });
}

function focusOnPointer(clientX, clientY) {
  if (!currentLevel || transitionState.active) {
    return false;
  }
  const nextGenInfo = getNextGenerationInfo(currentLevel);
  if (nextGenInfo && currentLevel.ringTargets?.length) {
    const rect = canvas.getBoundingClientRect();
    pointerNdc.x = ((clientX - rect.left) / rect.width) * 2 - 1;
    pointerNdc.y = -((clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointerNdc, camera);
    const pulsingTargets = currentLevel.ringTargets.filter(
      (target) => target.bandName === getPulsingBandName(target.node)
    );
    if (pulsingTargets.length) {
      const intersections = raycaster.intersectObjects(
        pulsingTargets.map((target) => target.mesh),
        false
      );
      if (intersections.length) {
        closeDetailPanel();
        hideHoverTooltip();
        jumpToScene(nextGenInfo.nextScene, { mode: "jump" });
        return true;
      }
    }
  }
  const rect = canvas.getBoundingClientRect();
  pointerNdc.x = ((clientX - rect.left) / rect.width) * 2 - 1;
  pointerNdc.y = -((clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointerNdc, camera);
  const intersections = raycaster.intersectObjects(
    currentLevel.nodes.map((node) => node.mesh),
    false
  );
  if (!intersections.length) {
    return false;
  }
  const hit = intersections[0].object;
  const targetNode = currentLevel.nodes.find((node) => node.mesh === hit);
  if (!targetNode) {
    return false;
  }

  if (currentLevel?.sceneId === composerSceneId) {
    const panelId = composerPanelMap.get(targetNode.data.id ?? "");
    if (panelId) {
      closeDetailPanel();
      hideHoverTooltip();
      setComposerPanel(panelId);
      return true;
    }
  }

  if (targetNode.data.children || targetNode.data.childScene) {
    closeDetailPanel();
    hideHoverTooltip();
    startLevelTransitionFromNode(targetNode);
  } else if (targetNode.data.markdownPath) {
    closeDetailPanel();
    hideHoverTooltip();
    const readerSceneId = ensureMarkdownReaderScene(targetNode.data);
    if (readerSceneId) {
      targetNode.data.childScene = readerSceneId;
      startLevelTransitionFromNode(targetNode);
    }
  } else {
    return true;
  }
  return true;
}

function updateDetailHover(clientX, clientY) {
  if (!currentLevel || transitionState.active) {
    return;
  }
  if (!detailPanel) {
    return;
  }
  const rect = canvas.getBoundingClientRect();
  pointerNdc.x = ((clientX - rect.left) / rect.width) * 2 - 1;
  pointerNdc.y = -((clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointerNdc, camera);
  const intersections = raycaster.intersectObjects(
    currentLevel.nodes.map((node) => node.mesh),
    false
  );
  if (!intersections.length) {
    return;
  }
  const hit = intersections[0].object;
  const targetNode = currentLevel.nodes.find((node) => node.mesh === hit);
  if (!targetNode || !targetNode.data.details) {
    return;
  }
  const nextId = targetNode.data.id ?? targetNode.data.name;
  if (nextId && nextId === hoveredDetailNodeId) {
    return;
  }
  setDetailPanel(targetNode);
}

function updateDecayHover(clientX, clientY) {
  if (!currentLevel || transitionState.active) {
    return;
  }
  const nextGenInfo = getNextGenerationInfo(currentLevel);
  if (!nextGenInfo) {
    hideHoverTooltip();
    return;
  }
  const pulsingBandName = getPulsingBandName(currentLevel.primaryBinaryNode);
  if (!pulsingBandName || !currentLevel.ringTargets?.length) {
    hideHoverTooltip();
    return;
  }
  const rect = canvas.getBoundingClientRect();
  pointerNdc.x = ((clientX - rect.left) / rect.width) * 2 - 1;
  pointerNdc.y = -((clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointerNdc, camera);
  const pulsingTargets = currentLevel.ringTargets.filter(
    (target) => target.bandName === pulsingBandName
  );
  if (!pulsingTargets.length) {
    hideHoverTooltip();
    return;
  }
  const intersections = raycaster.intersectObjects(
    pulsingTargets.map((target) => target.mesh),
    false
  );
  if (!intersections.length) {
    hideHoverTooltip();
    return;
  }
  const label = `Decay to Gen ${nextGenInfo.nextGen} ${nextGenInfo.nextLabel}`;
  showHoverTooltip(label, clientX, clientY);
}

const activePointers = new Map();
const panState = {
  active: false,
  moved: false,
  startX: 0,
  startY: 0,
  startWorldX: 0,
  startWorldY: 0,
};

let pinchStartDistance = 0;
let pinchStartZoom = 1;

let lastTapTime = 0;
let lastTapX = 0;
let lastTapY = 0;

function getWorldPerPixel() {
  const worldHeight = (camera.top - camera.bottom) / camera.zoom;
  return worldHeight / canvas.clientHeight;
}

function getPinchDistance() {
  const pointers = Array.from(activePointers.values());
  if (pointers.length < 2) {
    return 0;
  }
  const dx = pointers[0].x - pointers[1].x;
  const dy = pointers[0].y - pointers[1].y;
  return Math.hypot(dx, dy);
}

function onPointerDown(event) {
  if (transitionState.active) {
    return;
  }
  canvas.setPointerCapture(event.pointerId);
  activePointers.set(event.pointerId, { x: event.clientX, y: event.clientY });

  if (activePointers.size === 1) {
    panState.active = true;
    panState.moved = false;
    panState.startX = event.clientX;
    panState.startY = event.clientY;
    panState.startWorldX = worldGroup.position.x;
    panState.startWorldY = worldGroup.position.y;
  }

  if (activePointers.size === 2) {
    panState.active = false;
    zoomState.active = false;
    pinchStartDistance = getPinchDistance();
    pinchStartZoom = camera.zoom;
  }
}

function onPointerMove(event) {
  if (transitionState.active) {
    return;
  }

  if (activePointers.has(event.pointerId)) {
    activePointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
  }

  if (activePointers.size === 1 && panState.active) {
    const dx = event.clientX - panState.startX;
    const dy = event.clientY - panState.startY;
    const worldPerPixel = getWorldPerPixel();
    worldGroup.position.x = panState.startWorldX + dx * worldPerPixel;
    worldGroup.position.y = panState.startWorldY - dy * worldPerPixel;
    if (Math.hypot(dx, dy) > 6) {
      panState.moved = true;
    }
  }

  if (activePointers.size === 2) {
    const distance = getPinchDistance();
    if (pinchStartDistance > 0) {
      const zoom = pinchStartZoom * (distance / pinchStartDistance);
      applyZoom(zoom);
      lastZoomGestureTime = performance.now();
    }
  }

  if (event.buttons === 0 && activePointers.size === 0 && !panState.active) {
    updateDetailHover(event.clientX, event.clientY);
    updateDecayHover(event.clientX, event.clientY);
  }
}

function onPointerUp(event) {
  if (activePointers.has(event.pointerId)) {
    activePointers.delete(event.pointerId);
  }

  if (activePointers.size < 2) {
    pinchStartDistance = 0;
  }

  if (activePointers.size === 0) {
    panState.active = false;
    if (!panState.moved && !transitionState.active) {
      if (!focusOnPointer(event.clientX, event.clientY)) {
        const now = performance.now();
        const dx = event.clientX - lastTapX;
        const dy = event.clientY - lastTapY;
        const distance = Math.hypot(dx, dy);
        if (now - lastTapTime < 320 && distance < 24) {
          if (currentLevel && currentLevel.id !== rootScenePath) {
            resetToRootScene();
          }
          lastTapTime = 0;
        } else {
          lastTapTime = now;
          lastTapX = event.clientX;
          lastTapY = event.clientY;
        }
      } else {
        lastTapTime = 0;
      }
    }
  }
}

function onWheel(event) {
  if (!event.ctrlKey || transitionState.active) {
    return;
  }
  event.preventDefault();
  zoomState.active = false;

  const zoomFactor = Math.exp(-event.deltaY * 0.0025);
  applyZoom(camera.zoom * zoomFactor);
  lastZoomGestureTime = performance.now();
}

function animate(now = 0) {
  requestAnimationFrame(animate);

  if (zoomState.active && !transitionState.active) {
    const elapsed = performance.now() - zoomState.startTime;
    const t = Math.min(1, elapsed / zoomState.duration);
    const eased = easeInOutCubic(t);
    const nextZoom =
      zoomState.startZoom +
      (zoomState.targetZoom - zoomState.startZoom) * eased;
    applyZoom(nextZoom);
    if (t >= 1) {
      zoomState.active = false;
    }
  }

  if (panTween.active && !transitionState.active) {
    const elapsed = performance.now() - panTween.startTime;
    const t = Math.min(1, elapsed / panTween.duration);
    const eased = easeInOutCubic(t);
    worldGroup.position.lerpVectors(panTween.start, panTween.target, eased);
    if (t >= 1) {
      panTween.active = false;
    }
  }

  updateTransition(now);

  if (labelFadeState.active && labelFadeState.level) {
    const elapsed = now - labelFadeState.startTime;
    const t = Math.min(1, elapsed / labelFadeState.duration);
    const fade = smoothstep(0, 1, t);
    setLevelLabelOpacity(labelFadeState.level, fade);
    if (t >= 1) {
      labelFadeState.active = false;
    }
  }
  maybeAutoWarp(now);
  updateNavButton();

  const timeSeconds = now / 1000;
  if (transitionState.active) {
    updateLevelHalo(transitionState.fromLevel, timeSeconds);
    updateLevelHalo(transitionState.toLevel, timeSeconds);
    updateBinaryRingPulse(transitionState.fromLevel, timeSeconds);
    updateBinaryRingPulse(transitionState.toLevel, timeSeconds);
  } else {
    updateLevelHalo(currentLevel, timeSeconds);
    updateBinaryRingPulse(currentLevel, timeSeconds);
  }

  if (currentLevel) {
    updateLevelMotions(currentLevel, now / 1000);
  }
  if (transitionState.active) {
    updateLevelLinks(transitionState.fromLevel);
    updateLevelLinks(transitionState.toLevel);
    updateLevelLabelWrap(transitionState.fromLevel);
    updateLevelLabelWrap(transitionState.toLevel);
    updateGlowRingOrientation(transitionState.fromLevel);
    updateGlowRingOrientation(transitionState.toLevel);
  } else {
    updateLevelLinks(currentLevel);
    updateLevelLabelWrap(currentLevel);
    updateGlowRingOrientation(currentLevel);
  }

  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
}

function onResize() {
  updateCamera();
  renderer.setSize(window.innerWidth, window.innerHeight, false);
  labelRenderer.setSize(window.innerWidth, window.innerHeight);
  if (currentLevel?.id === rootScenePath) {
    layoutRootLevel(currentLevel);
    fitCameraToLevel(currentLevel);
  }
}

async function init() {
  closeDetailPanel();
  const universeConfig = await loadSceneConfig(rootScenePath);
  if (!universeConfig) {
    return;
  }
  currentLevel = buildLevel(rootScenePath);
  worldGroup.add(currentLevel.group);
  layoutRootLevel(currentLevel);
  updateCamera();
  fitCameraToLevel(currentLevel);
  updateSceneLabel();
  updateSceneMarkdown();
  animate();
}

if (typeof window !== "undefined") {
  window.openMetaRing = openMetaRing;
}

init();

window.addEventListener("resize", onResize);
canvas.addEventListener("pointerdown", onPointerDown);
canvas.addEventListener("pointermove", onPointerMove);
canvas.addEventListener("pointerup", onPointerUp);
canvas.addEventListener("pointercancel", onPointerUp);
canvas.addEventListener("pointerleave", () => {
  hideHoverTooltip();
});
canvas.addEventListener("wheel", onWheel, { passive: false });

if (navUpButton) {
  navUpButton.addEventListener("click", () => {
    if (transitionState.active) {
      return;
    }
    if (navigationStack.length > 0) {
      startLevelTransitionOut();
      return;
    }
    if (searchBackStack.length > 0) {
      const backState = searchBackStack.pop();
      if (backState?.levelId) {
        jumpToScene(backState.levelId, {
          restoreNavStack: backState.navigationStack,
        });
      }
      return;
    }
    if (metaBackStack.length > 0) {
      const backState = metaBackStack.pop();
      if (backState?.levelId) {
        jumpToScene(backState.levelId, {
          restoreNavStack: backState.navigationStack,
        });
      }
    }
  });
}

if (homeButton) {
  homeButton.addEventListener("click", () => {
    if (transitionState.active) {
      return;
    }
    resetToRootScene();
  });
}

wireElementLegend();
updateElementInfoPanel();

if (docButton) {
  docButton.addEventListener("click", () => {
    if (transitionState.active) {
      return;
    }
    if (currentLevel?.markdownPath) {
      const docLevel = currentLevel.markdownSection
        ? { ...currentLevel, markdownSection: null }
        : currentLevel;
      showMarkdownPanel(docLevel);
    }
  });
}

if (hud) {
  hud.addEventListener("click", () => {
    toggleInfoDrawer();
  });
  hud.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      toggleInfoDrawer();
    } else if (event.key === "Escape" && infoDrawerOpen) {
      setInfoDrawer(false);
    }
  });
}

if (detailClose) {
  detailClose.addEventListener("click", () => {
    closeDetailPanel();
  });
}

if (markdownClose) {
  markdownClose.addEventListener("click", () => {
    hideMarkdownPanel();
  });
}

if (markdownDocButton) {
  markdownDocButton.addEventListener("click", () => {
    if (transitionState.active) {
      return;
    }
    if (currentLevel?.markdownPath) {
      const docLevel = currentLevel.markdownSection
        ? { ...currentLevel, markdownSection: null }
        : currentLevel;
      showMarkdownPanel(docLevel);
    }
  });
}

if (markdownLayoutToggle) {
  markdownLayoutToggle.addEventListener("click", () => {
    markdownTwoColumns = !markdownTwoColumns;
    applyMarkdownLayout();
  });
}

if (composerTabs.length) {
  composerTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      setComposerPanel(tab.dataset.panel);
    });
  });
}

if (composerDocsButton) {
  composerDocsButton.addEventListener("click", () => {
    openComposerDocs();
  });
}

if (sceneSearchToggle) {
  sceneSearchToggle.addEventListener("click", async () => {
    if (!isSearchOpen()) {
      await ensureSceneIndex();
    }
    setSearchOpen(!isSearchOpen());
  });
}

if (sceneSearchInput) {
  sceneSearchInput.addEventListener("input", (event) => {
    updateSearchResults(event.target.value);
  });
  sceneSearchInput.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setSearchOpen(false);
      return;
    }
    if (event.key === "Enter") {
      const firstItem = sceneSearchResults?.querySelector(
        ".scene-search-item"
      );
      if (firstItem) {
        firstItem.click();
      }
    }
  });
}

document.addEventListener("pointerdown", (event) => {
  if (!isSearchOpen()) {
    return;
  }
  if (isSearchEventTarget(event.target)) {
    return;
  }
  setSearchOpen(false);
});

document.addEventListener("focusin", (event) => {
  if (!isSearchOpen()) {
    return;
  }
  if (isSearchEventTarget(event.target)) {
    return;
  }
  setSearchOpen(false);
});

window.addEventListener("keydown", async (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    if (!isSearchOpen()) {
      await ensureSceneIndex();
      setSearchOpen(true);
    } else {
      setSearchOpen(false);
    }
  } else if (event.key === "Escape" && isSearchOpen()) {
    setSearchOpen(false);
  }
});
