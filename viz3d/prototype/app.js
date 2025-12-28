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

const scaleItems = [
  { name: "Galaxy", scale: 21, radius: 2.8, color: "#243d8f" },
  { name: "Solar System", scale: 11, radius: 2.1, color: "#1f4f7a" },
  { name: "Planet", scale: 6, radius: 1.6, color: "#1f5f4a" },
  { name: "Atom", scale: -10, radius: 1.2, color: "#6a4d1b" },
  { name: "Quark", scale: -19, radius: 0.9, color: "#5a1f2e" },
];

const focusTargets = [];
const raycaster = new THREE.Raycaster();
const pointerNdc = new THREE.Vector2();

function buildScaleObjects() {
  const spacing = 7.5;
  const centerOffset = (scaleItems.length - 1) / 2;

  scaleItems.forEach((item, index) => {
    const group = new THREE.Group();
    const geometry = new THREE.SphereGeometry(item.radius, 32, 20);
    const material = new THREE.MeshBasicMaterial({
      color: item.color,
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

    const label = document.createElement("div");
    label.className = "label";
    label.innerHTML = `<div class="label-title">${item.name}</div><div class="label-scale">10^${item.scale}</div>`;
    const labelObject = new CSS2DObject(label);
    labelObject.position.set(0, 0, 0);
    group.add(labelObject);

    group.position.x = (index - centerOffset) * spacing;
    worldGroup.add(group);
    focusTargets.push({ mesh, group });
  });
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

const zoomLimits = { min: 0.35, max: 6 };

function clampZoom(value) {
  return Math.min(zoomLimits.max, Math.max(zoomLimits.min, value));
}

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
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

function focusOnPointer(clientX, clientY) {
  const rect = canvas.getBoundingClientRect();
  pointerNdc.x = ((clientX - rect.left) / rect.width) * 2 - 1;
  pointerNdc.y = -((clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointerNdc, camera);
  const intersections = raycaster.intersectObjects(
    focusTargets.map((target) => target.mesh),
    false
  );
  if (!intersections.length) {
    return false;
  }
  const hit = intersections[0].object;
  const target = focusTargets.find((entry) => entry.mesh === hit);
  if (!target) {
    return false;
  }
  const nextPosition = new THREE.Vector3(
    -target.group.position.x,
    -target.group.position.y,
    worldGroup.position.z
  );
  setTargetPan(nextPosition, 420);
  setTargetZoom(camera.zoom * 1.35, 420);
  return true;
}

function onPointerDown(event) {
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
  if (!activePointers.has(event.pointerId)) {
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
    if (!panState.moved) {
      const now = performance.now();
      const dx = event.clientX - lastTapX;
      const dy = event.clientY - lastTapY;
      const distance = Math.hypot(dx, dy);
      if (now - lastTapTime < 320 && distance < 24) {
        if (!focusOnPointer(event.clientX, event.clientY)) {
          setTargetZoom(camera.zoom * 1.35, 360);
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
  if (!event.ctrlKey) {
    return;
  }
  event.preventDefault();
  zoomState.active = false;

  const zoomFactor = Math.exp(-event.deltaY * 0.0025);
  applyZoom(camera.zoom * zoomFactor);
}

function animate() {
  requestAnimationFrame(animate);

  if (zoomState.active) {
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

  if (panTween.active) {
    const elapsed = performance.now() - panTween.startTime;
    const t = Math.min(1, elapsed / panTween.duration);
    const eased = easeInOutCubic(t);
    worldGroup.position.lerpVectors(panTween.start, panTween.target, eased);
    if (t >= 1) {
      panTween.active = false;
    }
  }

  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
}

function onResize() {
  updateCamera();
  renderer.setSize(window.innerWidth, window.innerHeight, false);
  labelRenderer.setSize(window.innerWidth, window.innerHeight);
}

buildScaleObjects();
updateCamera();
animate();

window.addEventListener("resize", onResize);
canvas.addEventListener("pointerdown", onPointerDown);
canvas.addEventListener("pointermove", onPointerMove);
canvas.addEventListener("pointerup", onPointerUp);
canvas.addEventListener("pointercancel", onPointerUp);
canvas.addEventListener("wheel", onWheel, { passive: false });
