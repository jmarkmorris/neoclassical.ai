import * as THREE from "./vendor/three/three.module.js";
import { CSS2DRenderer, CSS2DObject } from "./vendor/three/CSS2DRenderer.js";

const app = document.getElementById("app");
const canvas = document.getElementById("viz");

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

const levelConfigs = {
  root: {
    layout: "linear",
    spacing: 7.5,
    nodes: [
      { name: "Galaxy", scale: 21, radius: 2.8, color: "#243d8f" },
      {
        name: "Solar System",
        scale: 11,
        radius: 2.1,
        color: "#1f4f7a",
        children: "solarSystem",
      },
      { name: "Planet", scale: 6, radius: 1.6, color: "#1f5f4a" },
      { name: "Atom", scale: -10, radius: 1.2, color: "#6a4d1b" },
      { name: "Quark", scale: -19, radius: 0.9, color: "#5a1f2e" },
    ],
  },
  solarSystem: {
    layout: "orbit",
    nodes: [
      {
        name: "Star",
        scale: 9,
        radius: 2.2,
        color: "#b07a2a",
        childScene: "json/star.json",
      },
      {
        name: "Planet A",
        scale: 6,
        radius: 1,
        color: "#327a5e",
        orbit: {
          center: "Star",
          radius: 4.8,
          speed: 0.25,
          phase: 0,
          shape: "circular",
        },
      },
      {
        name: "Planet B",
        scale: 6,
        radius: 0.9,
        color: "#2c6c7e",
        orbit: {
          center: "Star",
          radius: 7.4,
          speed: 0.18,
          phase: 2.094,
          shape: "circular",
        },
      },
      {
        name: "Planet C",
        scale: 6,
        radius: 1.15,
        color: "#3f5f8a",
        orbit: {
          center: "Star",
          radius: 12,
          speed: 0.12,
          phase: 4.189,
          shape: "circular",
        },
      },
      {
        name: "Moon",
        scale: 5,
        radius: 0.5,
        color: "#9ea6bf",
        orbit: {
          center: "Planet C",
          radius: 2.4,
          speed: 0.6,
          phase: 0.6,
          shape: "circular",
        },
      },
    ],
  },
};

const sceneConfigCache = new Map();
const sceneLoadPromises = new Map();

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
  warpScale: 1,
  panStart: new THREE.Vector3(),
  panTarget: new THREE.Vector3(),
  targetPosition: new THREE.Vector3(),
  startTime: 0,
  duration: 900,
};

const autoWarpThresholds = {
  inPx: 80,
  outPx: 20,
  cooldownMs: 700,
  lastAt: 0,
};

const zoomLimits = { min: 0.35, max: 6 };
const raycaster = new THREE.Raycaster();
const pointerNdc = new THREE.Vector2();
let lastZoomGestureTime = 0;

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
      const idMap = new Map(
        data.objects.map((obj) => [obj.id, obj.label || obj.id])
      );
      const nodes = data.objects.map((obj) => {
        const node = {
          name: obj.label || obj.id,
          scale: obj.scaleExponent ?? 0,
          radius: obj.radius ?? 1,
          color: obj.color ?? "#3a5a8a",
          position: obj.position ?? [0, 0, 0],
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

      const config = {
        layout: "static",
        nodes,
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

function fitCameraToLevel(level) {
  worldGroup.updateMatrixWorld(true);
  const bounds = new THREE.Box3().setFromObject(level.group);
  const worldToLocal = new THREE.Matrix4()
    .copy(worldGroup.matrixWorld)
    .invert();
  bounds.applyMatrix4(worldToLocal);
  const size = new THREE.Vector3();
  bounds.getSize(size);
  if (!isFinite(size.x) || !isFinite(size.y) || size.lengthSq() === 0) {
    return;
  }

  const center = new THREE.Vector3();
  bounds.getCenter(center);

  const viewHeight = baseViewHeight;
  const viewWidth = baseViewHeight * (window.innerWidth / window.innerHeight);
  const marginFactor = 0.8;
  const zoomX = (viewWidth * marginFactor) / Math.max(size.x, 0.01);
  const zoomY = (viewHeight * marginFactor) / Math.max(size.y, 0.01);
  const nextZoom = clampZoom(Math.min(zoomX, zoomY));

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
  label.innerHTML = `<div class="label-title">${node.name}</div><div class="label-scale">10^${node.scale}</div>`;
  const maxWidth = Math.max(50, node.radius * 22);
  label.style.maxWidth = `${maxWidth}px`;
  return new CSS2DObject(label);
}

function createNode(nodeData) {
  const group = new THREE.Group();
  const geometry = new THREE.SphereGeometry(nodeData.radius, 32, 20);
  const material = new THREE.MeshBasicMaterial({
    color: nodeData.color,
    transparent: true,
    opacity: 0.86,
  });
  const mesh = new THREE.Mesh(geometry, material);
  group.add(mesh);

  const outlineGeometry = new THREE.EdgesGeometry(geometry);
  const outlineMaterial = new THREE.LineBasicMaterial({
    color: "#d5dcff",
    transparent: true,
    opacity: 0.3,
  });
  const outline = new THREE.LineSegments(outlineGeometry, outlineMaterial);
  group.add(outline);

  const labelObject = createLabel(nodeData);
  group.add(labelObject);

  return {
    group,
    mesh,
    outline,
    labelObject,
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

    if (nodeData.orbit) {
      orbiters.push(node);
    }
  });

  const level = {
    id: levelId,
    group,
    nodes,
    nodeByName,
    orbiters,
    layout: config.layout,
  };

  levels.set(levelId, level);
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

function setLevelOpacity(level, opacity) {
  level.nodes.forEach((node) => {
    node.mesh.material.opacity = node.baseOpacity.mesh * opacity;
    node.outline.material.opacity = node.baseOpacity.outline * opacity;
    node.labelObject.element.style.opacity = opacity;
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
  const desiredRadius = baseViewHeight * 0.42;
  const warpScale = Math.max(2.4, desiredRadius / targetNode.data.radius);

  transitionState.active = true;
  transitionState.fromLevel = currentLevel;
  transitionState.toLevel = toLevel;
  transitionState.direction = "in";
  transitionState.warpScale = warpScale;
  transitionState.panStart.copy(worldGroup.position);
  transitionState.panTarget.set(-targetPosition.x, -targetPosition.y, 0);
  transitionState.targetPosition.copy(targetPosition);
  transitionState.startTime = performance.now();

  toLevel.group.position.copy(targetPosition);
  toLevel.group.scale.setScalar(1 / warpScale);
  setLevelOpacity(toLevel, 0);
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

  const targetPosition = parentNode.group.position.clone();
  const desiredRadius = baseViewHeight * 0.42;
  const warpScale = Math.max(2.4, desiredRadius / parentNode.data.radius);

  transitionState.active = true;
  transitionState.fromLevel = currentLevel;
  transitionState.toLevel = parentLevel;
  transitionState.direction = "out";
  transitionState.warpScale = warpScale;
  transitionState.panStart.copy(worldGroup.position);
  transitionState.panTarget.set(0, 0, 0);
  transitionState.targetPosition.copy(targetPosition);
  transitionState.startTime = performance.now();

  parentLevel.group.position.copy(targetPosition).multiplyScalar(-1);
  parentLevel.group.scale.setScalar(warpScale);
  setLevelOpacity(parentLevel, 0);
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

    fromLevel.group.scale.setScalar(1);
    setLevelOpacity(fromLevel, 0);
    worldGroup.remove(fromLevel.group);

    toLevel.group.scale.setScalar(1);
    toLevel.group.position.set(0, 0, 0);
    setLevelOpacity(toLevel, 1);

    currentLevel = toLevel;
    fitCameraToLevel(currentLevel);
  } else {
    toLevel.group.position.set(0, 0, 0);
    toLevel.group.scale.setScalar(1);
    setLevelOpacity(toLevel, 1);

    fromLevel.group.scale.setScalar(1);
    setLevelOpacity(fromLevel, 0);
    worldGroup.remove(fromLevel.group);

    currentLevel = toLevel;
    navigationStack.pop();
    fitCameraToLevel(currentLevel);
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
  const fade = smoothstep(0.2, 0.85, t);

  const fromLevel = transitionState.fromLevel;
  const toLevel = transitionState.toLevel;

  if (transitionState.direction === "in") {
    fromLevel.group.scale.setScalar(
      1 + (transitionState.warpScale - 1) * eased
    );
    toLevel.group.scale.setScalar(
      1 / transitionState.warpScale +
        (1 - 1 / transitionState.warpScale) * eased
    );

    worldGroup.position.lerpVectors(
      transitionState.panStart,
      transitionState.panTarget,
      eased
    );

    setLevelOpacity(fromLevel, 1 - fade);
    setLevelOpacity(toLevel, fade);
  } else {
    const childScale =
      1 + (1 / transitionState.warpScale - 1) * eased;
    fromLevel.group.scale.setScalar(childScale);
    toLevel.group.scale.setScalar(
      transitionState.warpScale + (1 - transitionState.warpScale) * eased
    );

    const parentPosition = transitionState.targetPosition
      .clone()
      .multiplyScalar(-1)
      .lerp(new THREE.Vector3(0, 0, 0), eased);
    toLevel.group.position.copy(parentPosition);

    setLevelOpacity(fromLevel, 1 - fade);
    setLevelOpacity(toLevel, fade);
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
  if (now - lastZoomGestureTime > 200) {
    return;
  }
  if (now - autoWarpThresholds.lastAt < autoWarpThresholds.cooldownMs) {
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
      return;
    }
  }

  if (
    candidate.radiusPx <= autoWarpThresholds.outPx &&
    navigationStack.length > 0
  ) {
    autoWarpThresholds.lastAt = now;
    startLevelTransitionOut();
  }
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
      const now = performance.now();
      const dx = event.clientX - lastTapX;
      const dy = event.clientY - lastTapY;
      const distance = Math.hypot(dx, dy);
      if (now - lastTapTime < 320 && distance < 24) {
        if (!focusOnPointer(event.clientX, event.clientY)) {
          setTargetZoom(camera.zoom * 1.2, 360);
        }
        lastTapTime = 0;
      } else {
        lastTapTime = now;
        lastTapX = event.clientX;
        lastTapY = event.clientY;
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
  maybeAutoWarp(now);

  if (currentLevel && currentLevel.layout === "orbit") {
    updateLevelOrbits(currentLevel, now / 1000);
  }

  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
}

function onResize() {
  updateCamera();
  renderer.setSize(window.innerWidth, window.innerHeight, false);
  labelRenderer.setSize(window.innerWidth, window.innerHeight);
}

function init() {
  currentLevel = buildLevel("root");
  worldGroup.add(currentLevel.group);
  updateCamera();
  fitCameraToLevel(currentLevel);
  animate();
}

init();

window.addEventListener("resize", onResize);
canvas.addEventListener("pointerdown", onPointerDown);
canvas.addEventListener("pointermove", onPointerMove);
canvas.addEventListener("pointerup", onPointerUp);
canvas.addEventListener("pointercancel", onPointerUp);
canvas.addEventListener("wheel", onWheel, { passive: false });
