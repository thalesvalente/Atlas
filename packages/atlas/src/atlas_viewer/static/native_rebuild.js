'use strict';
// Verification GETs never accept changed source bytes implicitly. Only this
// explicit user action rebuilds the existing in-memory Catalog allowlist.
const rebuildButton = document.getElementById('native-rebuild');
rebuildButton.addEventListener('click', async () => {
  rebuildButton.disabled = true;
  const notice = document.getElementById('native-notice');
  notice.textContent = 'Reconstruindo o índice das fontes já selecionadas…';
  try {
    const response = await fetch('/api/reindex', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}'
    });
    if (!response.ok) throw new Error('Reconstrução recusada: HTTP ' + response.status);
    // Clear all source-scoped selections by reloading trusted application assets.
    window.location.reload();
  } catch (error) {
    notice.textContent = error.message;
    notice.classList.add('error');
    rebuildButton.disabled = false;
  }
});
