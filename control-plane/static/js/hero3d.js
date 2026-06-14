/* Landing hero 3D backdrop — a soft cluster of frosted-purple cubes drifting
 * behind the headline, matching the EVERJUST brand mark. Progressive
 * enhancement only:
 *   - Three.js (~170 KB gzip) is dynamically imported ONLY on capable desktops
 *     after the page is idle, so mobile / reduced-motion users never download
 *     it and initial paint is never blocked,
 *   - skipped on reduced-motion, small screens, and when WebGL is unavailable,
 *   - pauses when the tab is hidden or the hero scrolls out of view.
 */
(function () {
  "use strict";

  const canvas = document.getElementById("hero3d-canvas");
  if (!canvas) return;

  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const small = window.matchMedia && window.matchMedia("(max-width: 767.98px)").matches;
  if (reduce || small) return;                  // mobile / reduced-motion: static hero, no download

  // Cheap WebGL capability probe on a throwaway canvas (don't touch the real one).
  try {
    const t = document.createElement("canvas");
    if (!(t.getContext("webgl2") || t.getContext("webgl"))) return;
  } catch (e) { return; }

  const boot = () => import("/static/vendor/three/three.module.min.js").then((THREE) =>
    import("/static/vendor/three/RoundedBoxGeometry.js").then(({ RoundedBoxGeometry }) =>
      init(THREE, RoundedBoxGeometry)
    )
  ).catch(() => { /* enhancement only */ });

  // Defer the heavy import until the browser is idle / after load.
  if ("requestIdleCallback" in window) requestIdleCallback(boot, { timeout: 2500 });
  else window.addEventListener("load", boot);

  function init(THREE, RoundedBoxGeometry) {
    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    } catch (e) { return; }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    const host = canvas.parentElement;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    camera.position.set(0, 0, 9);

    scene.add(new THREE.AmbientLight(0xffffff, 0.85));
    const key = new THREE.DirectionalLight(0xffffff, 1.1);
    key.position.set(4, 6, 6);
    scene.add(key);
    const fill = new THREE.PointLight(0x8b6df6, 0.7, 60);
    fill.position.set(-6, -3, 4);
    scene.add(fill);

    const geo = new RoundedBoxGeometry(1, 1, 1, 6, 0.18);
    const mat = new THREE.MeshStandardMaterial({
      color: 0xbca9f7, roughness: 0.42, metalness: 0.0,
      emissive: 0x6e4ff0, emissiveIntensity: 0.12,
    });

    const SEEDS = [
      [-5.2, 1.9, -1, 1.15], [5.0, 2.1, -2, 0.95], [-4.4, -2.2, 0, 0.8],
      [4.6, -2.0, -1, 1.05], [-6.2, -0.2, -3, 0.7], [6.1, 0.1, -3, 0.75],
    ];
    const group = new THREE.Group();
    const cubes = SEEDS.map(([x, y, z, s], i) => {
      const m = new THREE.Mesh(geo, mat);
      m.position.set(x, y, z);
      m.scale.setScalar(s);
      m.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
      m.userData = { sx: 0.0009 + i * 0.0004, sy: 0.0012 - i * 0.0002, phase: i, baseY: y };
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
    }
    resize();
    window.addEventListener("resize", resize);

    let targetX = 0, targetY = 0;
    window.addEventListener("pointermove", (e) => {
      targetX = (e.clientX / window.innerWidth - 0.5) * 0.35;
      targetY = (e.clientY / window.innerHeight - 0.5) * 0.25;
    });

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
        m.position.y = m.userData.baseY + Math.sin(t * 0.6 + m.userData.phase) * 0.22;
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
