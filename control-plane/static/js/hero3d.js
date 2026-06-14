/* Landing hero 3D — a cluster of frosted-purple cubes (the brand mark) drifting
 * behind the headline. Progressive enhancement, but designed to actually be
 * SEEN: saturated material with clear contrast on white, prominent sizes.
 *
 *   - Three.js (~170 KB gzip) is dynamically imported after the page is idle,
 *     so it never blocks initial paint.
 *   - Renders everywhere WebGL is available, including mobile (lighter: fewer
 *     cubes, capped pixel ratio) and reduced-motion (a single static frame, no
 *     animation) — so the visual is always visible, never silently skipped.
 *   - Animation pauses when the hero scrolls away or the tab is hidden.
 */
(function () {
  "use strict";

  const canvas = document.getElementById("hero3d-canvas");
  if (!canvas) return;

  // WebGL capability probe on a throwaway canvas.
  try {
    const t = document.createElement("canvas");
    if (!(t.getContext("webgl2") || t.getContext("webgl"))) return;
  } catch (e) { return; }

  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const mobile = window.matchMedia && window.matchMedia("(max-width: 767.98px)").matches;

  const boot = () => import("/static/vendor/three/three.module.min.js").then((THREE) =>
    import("/static/vendor/three/RoundedBoxGeometry.js").then(({ RoundedBoxGeometry }) =>
      init(THREE, RoundedBoxGeometry)
    )
  ).catch(() => {});

  if ("requestIdleCallback" in window) requestIdleCallback(boot, { timeout: 2000 });
  else window.addEventListener("load", boot);

  function init(THREE, RoundedBoxGeometry) {
    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    } catch (e) { return; }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, mobile ? 1.5 : 2));

    const host = canvas.parentElement;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    camera.position.set(0, 0, mobile ? 13 : 9);

    scene.add(new THREE.AmbientLight(0xffffff, 0.6));
    const key = new THREE.DirectionalLight(0xffffff, 1.4);
    key.position.set(3, 5, 7);
    scene.add(key);
    const rim = new THREE.DirectionalLight(0x7b5cff, 0.9);
    rim.position.set(-5, -2, 3);
    scene.add(rim);

    const geo = new RoundedBoxGeometry(1, 1, 1, 6, 0.16);
    // Saturated purple so the cubes clearly stand out against the white hero.
    const mat = new THREE.MeshStandardMaterial({
      color: 0x7c5cf6, roughness: 0.32, metalness: 0.05,
      emissive: 0x4a2fd0, emissiveIntensity: 0.18,
    });

    // [x, y, z, scale]. Desktop spreads wide around the headline; mobile keeps
    // a few cubes in the top/bottom corners so they're visible in a narrow,
    // tall hero without sitting behind the text.
    let SEEDS = mobile ? [
      [-2.6, 4.6, -1, 1.2], [2.7, 5.0, -2, 1.0],
      [-2.8, -4.8, -1, 1.1], [2.6, -5.0, -2, 0.95],
    ] : [
      [-5.4, 1.7, -1, 1.5], [5.2, 2.0, -2, 1.25], [-4.2, -2.3, 0, 1.1],
      [4.6, -2.1, -1, 1.35], [-6.4, -0.4, -3, 0.95], [6.3, -0.2, -3, 1.0],
      [-2.8, 2.7, -4, 0.8], [2.6, -3.0, -4, 0.85],
    ];

    const group = new THREE.Group();
    const cubes = SEEDS.map(([x, y, z, s], i) => {
      const m = new THREE.Mesh(geo, mat);
      m.position.set(x, y, z);
      m.scale.setScalar(s);
      m.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
      m.userData = { sx: 0.0010 + i * 0.0004, sy: 0.0014 - i * 0.0002, phase: i, baseY: y };
      group.add(m);
      return m;
    });
    scene.add(group);

    function resize() {
      const w = host.clientWidth, h = host.clientHeight;
      if (!w || !h) return;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.render(scene, camera);
    }
    resize();
    window.addEventListener("resize", resize);

    // Reduced motion: show the static frame and stop.
    if (reduce) return;

    let targetX = 0, targetY = 0;
    if (!mobile) {
      window.addEventListener("pointermove", (e) => {
        targetX = (e.clientX / window.innerWidth - 0.5) * 0.4;
        targetY = (e.clientY / window.innerHeight - 0.5) * 0.3;
      });
    }

    let onScreen = true, running = false, raf = 0;
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((entries) => {
        onScreen = entries[0].isIntersecting;
        onScreen ? start() : stop();
      }, { threshold: 0.01 }).observe(host);
    }
    document.addEventListener("visibilitychange", () => {
      document.hidden ? stop() : (onScreen && start());
    });

    const clock = new THREE.Clock();
    function frame() {
      if (!running) return;
      const t = clock.getElapsedTime();
      cubes.forEach((m) => {
        m.rotation.x += m.userData.sx;
        m.rotation.y += m.userData.sy;
        m.position.y = m.userData.baseY + Math.sin(t * 0.6 + m.userData.phase) * 0.26;
      });
      group.rotation.y += (targetX - group.rotation.y) * 0.05;
      group.rotation.x += (targetY - group.rotation.x) * 0.05;
      renderer.render(scene, camera);
      raf = requestAnimationFrame(frame);
    }
    function start() { if (!running) { running = true; clock.start(); raf = requestAnimationFrame(frame); } }
    function stop() { running = false; cancelAnimationFrame(raf); }

    start();
  }
})();
