// Dentro del visor de la app (un iframe sobre el feed), «volver» cierra el visor
// en vez de navegar: así el feed sigue exactamente donde estaba.
(() => {
  if (window.parent === window) return;
  const a = document.querySelector('.andes-barra a');
  if (!a) return;
  a.remove();   // el visor ya tiene su propio «✕ Volver»; queda el de pantalla completa
})();

// Pantalla completa en horizontal: así se leen los lienzos anchos en el teléfono.
(() => {
  const b = document.getElementById('andes-completa');
  if (!b) return;
  const pintar = () => { b.textContent = document.fullscreenElement ? '✕ Salir' : '⤢ Pantalla completa'; };
  b.addEventListener('click', async () => {
    try {
      if (document.fullscreenElement) { await document.exitFullscreen(); return; }
      await document.documentElement.requestFullscreen();
      await screen.orientation?.lock?.('landscape');
    } catch { /* iOS o navegador sin soporte: se queda como está */ }
  });
  document.addEventListener('fullscreenchange', pintar);
})();
