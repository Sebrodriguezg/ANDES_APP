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
