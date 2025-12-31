import * as THREE from "./vendor/three/three.module.js";
import { CSS2DRenderer, CSS2DObject } from "./vendor/three/CSS2DRenderer.js";

const app = document.getElementById("app");
const canvas = document.getElementById("viz");
const navUpButton = document.getElementById("nav-up");
const sceneLabel = document.getElementById("scene-label");
const sceneSearchToggle = document.getElementById("scene-search-toggle");
const sceneSearchPanel = document.getElementById("scene-search-panel");
const sceneSearchInput = document.getElementById("scene-search-input");
const sceneSearchResults = document.getElementById("scene-search-results");

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
const linkStyle = {
  minLength: 0.7,
  tipClearance: 0.12,
  headLengthMin: 0.14,
  headLengthMax: 0.24,
  headWidthFactor: 0.4,
  lineOpacity: 0.6,
  headOpacity: 0.85,
};

const sceneConfigCache = new Map();
const sceneLoadPromises = new Map();
let haloSeed = 0;
const rootScenePath = "json/physics_frontiers.json";
let sceneIndex = [];
let sceneIndexReady = false;
const searchBackStack = [];

const levels = new Map();
const navigationStack = [];
let currentLevel = null;

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
  fromLevel: null,
  toLevel: null,
  direction: "in",
  focusNodeName: null,
  targetZoom: null,
  toFitScale: 1,
  warpScale: 1,
  panStart: new THREE.Vector3(),
  panTarget: new THREE.Vector3(),
  targetPosition: new THREE.Vector3(),
  startTime: 0,
  duration: 2250,
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

function purgeWorldState() {
  transitionState.active = false;
  transitionState.fromLevel = null;
  transitionState.toLevel = null;
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

async function loadSceneConfig(scenePath) {
  if (sceneConfigCache.has(scenePath)) {
    return sceneConfigCache.get(scenePath);
  }
  if (sceneLoadPromises.has(scenePath)) {
    return sceneLoadPromises.get(scenePath);
  }

  const promise = fetch(scenePath)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Failed to load scene ${scenePath}`);
      }
      return response.json();
    })
    .then((data) => {
      const hideScaleLabels = Boolean(data.scene?.hideScaleLabels);
      const wrapLabels = data.scene?.wrapLabels ?? true;
      const idMap = new Map(
        data.objects.map((obj) => [obj.id, obj.label || obj.id])
      );
      const nodes = data.objects.map((obj) => {
        const hasScale =
          obj.scaleExponent !== undefined && obj.scaleExponent !== null;
        const node = {
          id: obj.id,
          name: obj.label || obj.id,
          scale: hasScale ? obj.scaleExponent : null,
          hasScale,
          radius: obj.radius ?? 1,
          color: obj.color ?? "#3a5a8a",
          position: obj.position ?? [0, 0, 0],
          category: obj.category,
          reaction: obj.reaction,
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
        }
        return node;
      });

      const sceneName =
        data.scene?.name ?? data.scene?.id ?? data.scene?.title ?? scenePath;
      const config = {
        layout: nodes.some((node) => node.orbit) ? "orbit" : "static",
        nodes,
        links: Array.isArray(data.links) ? data.links : [],
        sceneName,
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
}

async function jumpToScene(scenePath, options = {}) {
  if (transitionState.active) {
    return;
  }
  const config = await loadSceneConfig(scenePath);
  if (!config) {
    return;
  }
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
      if (item && item.levelId && item.focusNodeName) {
        navigationStack.push({
          levelId: item.levelId,
          focusNodeName: item.focusNodeName,
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

function computeWarpScale(objectRadius) {
  const aspect = window.innerWidth / window.innerHeight;
  const viewHeight = baseViewHeight / camera.zoom;
  const viewWidth = (baseViewHeight * aspect) / camera.zoom;
  const halfDiagonal = 0.5 * Math.hypot(viewWidth, viewHeight);
  const targetRadius = halfDiagonal * 1.05;
  return Math.max(1.2, targetRadius / Math.max(objectRadius, 0.01));
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
  const { size, center } = getLevelBoundsFromNodes(level);
  if (!isFinite(size.x) || !isFinite(size.y) || size.lengthSq() === 0) {
    return;
  }

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

function createNode(nodeData) {
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
    color: isReaction ? "#f6dd9c" : "#d5dcff",
    transparent: true,
    opacity: isReaction ? 0.55 : 0.3,
  });
  outlineMaterial.depthWrite = false;
  const outline = new THREE.LineSegments(outlineGeometry, outlineMaterial);
  group.add(outline);

  const labelObject = createLabel(nodeData);
  group.add(labelObject);

  let halo = null;
  if (nodeData.childScene) {
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
    data: nodeData,
    baseOpacity: {
      mesh: material.opacity,
      outline: outlineMaterial.opacity,
      label: 1,
    },
  };
}

function buildLevel(levelId) {
  if (levels.has(levelId)) {
    return levels.get(levelId);
  }

  const config = levelConfigs[levelId];
  const group = new THREE.Group();
  const nodes = [];
  const nodeByName = new Map();
  const nodeById = new Map();
  const orbiters = [];

  const spacing = config.spacing ?? 7;
  const centerOffset = (config.nodes.length - 1) / 2;

  config.nodes.forEach((nodeData, index) => {
    const node = createNode(nodeData);
    if (config.layout === "linear") {
      node.group.position.x = (index - centerOffset) * spacing;
    } else if (config.layout === "static" && nodeData.position) {
      node.group.position.set(
        nodeData.position[0] ?? 0,
        nodeData.position[1] ?? 0,
        nodeData.position[2] ?? 0
      );
    }
    group.add(node.group);
    nodes.push(node);
    nodeByName.set(nodeData.name, node);
    if (nodeData.id) {
      nodeById.set(nodeData.id, node);
    }

    if (nodeData.orbit) {
      orbiters.push(node);
    }
  });

  const level = {
    id: levelId,
    name: config.sceneName ?? levelId,
    group,
    nodes,
    nodeByName,
    nodeById,
    orbiters,
    layout: config.layout,
    links: [],
  };

  levels.set(levelId, level);
  buildLevelLinks(level, config);
  updateLevelOrbits(level, 0);
  return level;
}

function updateLevelOrbits(level, timeSeconds) {
  level.orbiters.forEach((node) => {
    const orbit = node.data.orbit;
    const centerNode = level.nodeByName.get(orbit.center);
    if (!centerNode) {
      return;
    }
    const yScale =
      orbit.shape === "ellipsoid" ? orbit.yScale ?? 0.85 : 1;
    const angle = timeSeconds * orbit.speed + (orbit.phase ?? 0);
    const x = centerNode.group.position.x + Math.cos(angle) * orbit.radius;
    const y =
      centerNode.group.position.y + Math.sin(angle) * orbit.radius * yScale;
    node.group.position.set(x, y, 0);
  });
}

function getLevelBoundsFromNodes(level) {
  const min = new THREE.Vector3(Infinity, Infinity, Infinity);
  const max = new THREE.Vector3(-Infinity, -Infinity, -Infinity);
  let hasNode = false;

  level.nodes.forEach((node) => {
    const radius = node.data.radius ?? 0;
    const pos = node.group.position;
    min.x = Math.min(min.x, pos.x - radius);
    min.y = Math.min(min.y, pos.y - radius);
    min.z = Math.min(min.z, pos.z - radius);
    max.x = Math.max(max.x, pos.x + radius);
    max.y = Math.max(max.y, pos.y + radius);
    max.z = Math.max(max.z, pos.z + radius);
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

function setLevelOpacity(level, opacity) {
  level.nodes.forEach((node) => {
    node.mesh.material.opacity = node.baseOpacity.mesh * opacity;
    node.outline.material.opacity = node.baseOpacity.outline * opacity;
    node.labelObject.element.style.opacity = opacity;
    node.haloIntensity = opacity;
  });
}

function setLevelOpacityWithLabel(level, meshOpacity, labelOpacity) {
  level.nodes.forEach((node) => {
    node.mesh.material.opacity = node.baseOpacity.mesh * meshOpacity;
    node.outline.material.opacity = node.baseOpacity.outline * meshOpacity;
    node.labelObject.element.style.opacity = labelOpacity;
    node.haloIntensity = meshOpacity;
  });
}

function setLevelLabelOpacity(level, labelOpacity) {
  level.nodes.forEach((node) => {
    node.labelObject.element.style.opacity = labelOpacity;
  });
}

function setLevelOpacityWithFocus(level, focusName, focusOpacity, otherOpacity) {
  level.nodes.forEach((node) => {
    const opacity = node.data.name === focusName ? focusOpacity : otherOpacity;
    node.mesh.material.opacity = node.baseOpacity.mesh * opacity;
    node.outline.material.opacity = node.baseOpacity.outline * opacity;
    node.labelObject.element.style.opacity = opacity;
    node.haloIntensity = opacity;
  });
}

function setLevelOpacityWithFocusAndLabel(
  level,
  focusName,
  focusOpacity,
  otherOpacity,
  labelOpacity
) {
  level.nodes.forEach((node) => {
    const opacity = node.data.name === focusName ? focusOpacity : otherOpacity;
    node.mesh.material.opacity = node.baseOpacity.mesh * opacity;
    node.outline.material.opacity = node.baseOpacity.outline * opacity;
    node.labelObject.element.style.opacity = opacity * labelOpacity;
    node.haloIntensity = opacity;
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

function beginLevelTransition(targetNode, childLevelId) {
  if (transitionState.active) {
    return;
  }
  if (!childLevelId) {
    return;
  }

  const toLevel = buildLevel(childLevelId);
  if (!worldGroup.children.includes(toLevel.group)) {
    worldGroup.add(toLevel.group);
  }

  const targetPosition = targetNode.group.position.clone();
  const { center: toLevelCenter } = getLevelBoundsFromNodes(toLevel);
  const warpScale = computeWarpScale(targetNode.data.radius);

  transitionState.active = true;
  transitionState.fromLevel = currentLevel;
  transitionState.toLevel = toLevel;
  transitionState.direction = "in";
  transitionState.focusNodeName = targetNode.data.name;
  transitionState.targetZoom = computeFitZoomForLevel(toLevel);
  transitionState.toFitScale = transitionState.targetZoom / camera.zoom;
  transitionState.warpScale = warpScale;
  transitionState.panStart.copy(worldGroup.position);
  transitionState.panTarget.set(-targetPosition.x, -targetPosition.y, 0);
  transitionState.targetPosition.copy(targetPosition);
  transitionState.startTime = performance.now();

  toLevel.group.position.copy(targetPosition).sub(toLevelCenter);
  toLevel.group.scale.setScalar(1);
  setLevelOpacity(toLevel, 0);
  setLevelLabelOpacity(toLevel, 0);
  setLevelOpacity(currentLevel, 1);

  navigationStack.push({
    levelId: currentLevel.id,
    focusNodeName: targetNode.data.name,
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

  beginLevelTransition(targetNode, childLevelId);
}

function startLevelTransitionOut() {
  if (transitionState.active || navigationStack.length === 0) {
    return;
  }

  const parentInfo = navigationStack[navigationStack.length - 1];
  const parentLevel = buildLevel(parentInfo.levelId);
  const parentNode = parentLevel.nodeByName.get(parentInfo.focusNodeName);
  if (!parentNode) {
    return;
  }

  if (!worldGroup.children.includes(parentLevel.group)) {
    worldGroup.add(parentLevel.group);
  }

  const { center: parentCenter } = getLevelBoundsFromNodes(parentLevel);
  const warpScale = computeWarpScale(parentNode.data.radius);

  transitionState.active = true;
  transitionState.fromLevel = currentLevel;
  transitionState.toLevel = parentLevel;
  transitionState.direction = "out";
  transitionState.focusNodeName = parentInfo.focusNodeName;
  transitionState.targetZoom = computeFitZoomForLevel(parentLevel);
  transitionState.toFitScale = transitionState.targetZoom / camera.zoom;
  transitionState.warpScale = warpScale;
  transitionState.panStart.copy(worldGroup.position);
  transitionState.panTarget.copy(worldGroup.position);
  transitionState.targetPosition.set(0, 0, 0);
  transitionState.startTime = performance.now();

  parentLevel.group.position
    .copy(parentCenter)
    .multiplyScalar(-1)
    .sub(worldGroup.position);
  parentLevel.group.scale.setScalar(1);
  setLevelOpacity(parentLevel, 0);
  setLevelLabelOpacity(parentLevel, 0);
  setLevelOpacity(currentLevel, 1);
}

function finalizeTransition() {
  const { fromLevel, toLevel } = transitionState;
  if (!fromLevel || !toLevel) {
    transitionState.active = false;
    return;
  }

  if (transitionState.direction === "in") {
    const rebaseOffset = worldGroup.position.clone();
    toLevel.group.position.add(rebaseOffset);
    worldGroup.position.set(0, 0, 0);

    const fromFocus = fromLevel.nodeByName.get(transitionState.focusNodeName);
    if (fromFocus) {
      fromFocus.group.scale.setScalar(1);
    }
    fromLevel.group.scale.setScalar(1);
    setLevelOpacity(fromLevel, 0);
    worldGroup.remove(fromLevel.group);

    toLevel.group.scale.setScalar(1);
    toLevel.group.position.set(0, 0, 0);
    setLevelOpacity(toLevel, 1);
    setLevelLabelOpacity(toLevel, 0);

    currentLevel = toLevel;
    fitCameraToLevel(currentLevel);
    labelFadeState.active = true;
    labelFadeState.level = currentLevel;
    labelFadeState.startTime = performance.now();
    updateSceneLabel();
  } else {
    const rebaseOffset = worldGroup.position.clone();
    toLevel.group.position.add(rebaseOffset);
    worldGroup.position.set(0, 0, 0);
    toLevel.group.scale.setScalar(1);
    setLevelOpacity(toLevel, 1);
    setLevelLabelOpacity(toLevel, 0);
    setLevelLinkOpacity(toLevel, 1);

    const toFocus = toLevel.nodeByName.get(transitionState.focusNodeName);
    if (toFocus) {
      toFocus.group.scale.setScalar(1);
    }
    fromLevel.group.scale.setScalar(1);
    setLevelOpacity(fromLevel, 0);
    setLevelLinkOpacity(fromLevel, 0);
    worldGroup.remove(fromLevel.group);

    currentLevel = toLevel;
    navigationStack.pop();
    zoomState.active = false;
    panTween.active = false;
    applyZoom(transitionState.targetZoom ?? camera.zoom);
    labelFadeState.active = true;
    labelFadeState.level = currentLevel;
    labelFadeState.startTime = performance.now();
    updateSceneLabel();
  }

  transitionState.active = false;
}

function updateTransition(now) {
  if (!transitionState.active) {
    return;
  }

  const elapsed = now - transitionState.startTime;
  const t = Math.min(1, elapsed / transitionState.duration);
  const eased = easeInOutCubic(t);
  const panProgress = smoothstep(0, 0.35, t);
  const scaleProgress = smoothstep(0.35, 1, t);

  const fromLevel = transitionState.fromLevel;
  const toLevel = transitionState.toLevel;

  if (transitionState.direction === "in") {
    const focusNode = fromLevel.nodeByName.get(transitionState.focusNodeName);
    if (focusNode) {
      focusNode.group.scale.setScalar(
        1 + (transitionState.warpScale - 1) * scaleProgress
      );
    }
    toLevel.group.scale.setScalar(transitionState.toFitScale);
    worldGroup.position.lerpVectors(
      transitionState.panStart,
      transitionState.panTarget,
      panProgress
    );

    const focusFade = 1 - smoothstep(0.55, 1, scaleProgress);
    const toFade = Math.pow(smoothstep(0.2, 1, scaleProgress), 1.6);
    setLevelOpacityWithFocus(
      fromLevel,
      transitionState.focusNodeName,
      focusFade,
      0
    );
    setLevelLinkOpacity(fromLevel, focusFade);
    setLevelOpacityWithLabel(toLevel, toFade, 0);
    setLevelLinkOpacity(toLevel, toFade);
  } else {
    toLevel.group.scale.setScalar(transitionState.toFitScale);
    worldGroup.position.copy(transitionState.panStart);

    const fromScale = 1 - 0.08 * scaleProgress;
    fromLevel.group.scale.setScalar(fromScale);

    const fromFade = 1 - smoothstep(0, 0.7, t);
    const toFade = smoothstep(0.4, 1, t);
    setLevelOpacity(fromLevel, fromFade);
    setLevelLinkOpacity(fromLevel, fromFade);
    setLevelOpacityWithLabel(toLevel, toFade, 0);
    setLevelLinkOpacity(toLevel, toFade);
  }

  if (t >= 1) {
    finalizeTransition();
  }
}

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
    return;
  }
  navUpButton.disabled =
    navigationStack.length === 0 && searchBackStack.length === 0;
}

function updateSceneLabel() {
  if (!sceneLabel) {
    return;
  }
  sceneLabel.textContent = currentLevel?.name ?? "";
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
            focusNodeName: entry.focusNodeName,
          })),
        });
      }
      setSearchOpen(false);
      jumpToScene(scene.path);
    });
    sceneSearchResults.appendChild(item);
  });
}

function focusOnPointer(clientX, clientY) {
  if (!currentLevel || transitionState.active) {
    return false;
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

  if (targetNode.data.children || targetNode.data.childScene) {
    startLevelTransitionFromNode(targetNode);
  } else {
    const panTarget = new THREE.Vector3(
      -targetNode.group.position.x,
      -targetNode.group.position.y,
      worldGroup.position.z
    );
    setTargetPan(panTarget, 420);
    setTargetZoom(camera.zoom * 1.35, 420);
  }
  return true;
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
  if (!activePointers.has(event.pointerId) || transitionState.active) {
    return;
  }

  activePointers.set(event.pointerId, { x: event.clientX, y: event.clientY });

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
  } else {
    updateLevelHalo(currentLevel, timeSeconds);
  }

  if (currentLevel && currentLevel.layout === "orbit") {
    updateLevelOrbits(currentLevel, now / 1000);
  }
  if (transitionState.active) {
    updateLevelLinks(transitionState.fromLevel);
    updateLevelLinks(transitionState.toLevel);
    updateLevelLabelWrap(transitionState.fromLevel);
    updateLevelLabelWrap(transitionState.toLevel);
  } else {
    updateLevelLinks(currentLevel);
    updateLevelLabelWrap(currentLevel);
  }

  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
}

function onResize() {
  updateCamera();
  renderer.setSize(window.innerWidth, window.innerHeight, false);
  labelRenderer.setSize(window.innerWidth, window.innerHeight);
}

async function init() {
  const universeConfig = await loadSceneConfig(rootScenePath);
  if (!universeConfig) {
    return;
  }
  currentLevel = buildLevel(rootScenePath);
  worldGroup.add(currentLevel.group);
  updateCamera();
  fitCameraToLevel(currentLevel);
  updateSceneLabel();
  animate();
}

init();

window.addEventListener("resize", onResize);
canvas.addEventListener("pointerdown", onPointerDown);
canvas.addEventListener("pointermove", onPointerMove);
canvas.addEventListener("pointerup", onPointerUp);
canvas.addEventListener("pointercancel", onPointerUp);
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
    }
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
