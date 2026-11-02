'use strict';
// This page is deliberately a local HTML viewer, not an R4 data adapter.
// The selected file is never sent to the server or stored in browser storage.
const choose = document.getElementById('original-file');
const status = document.getElementById('original-status');
const wrapper = document.getElementById('original-wrapper');
const empty = document.getElementById('original-empty');
const frame = document.getElementById('original-frame');
const close = document.getElementById('original-clear');
const MAX_BYTES = 64 * 1024 * 1024;
let currentSelection = 0;

function message(value, error = false) {
  status.textContent = value;
  status.classList.toggle('error', error);
}
function clearPreview() {
  currentSelection += 1;
  frame.removeAttribute('srcdoc');
  frame.src = 'about:blank';
  wrapper.hidden = true;
  empty.hidden = false;
}
close.addEventListener('click', () => {
  clearPreview();
  choose.value = '';
  message('Visualização encerrada. O arquivo original permanece inalterado.');
});
choose.addEventListener('change', async () => {
  clearPreview();
  const serial = currentSelection;
  const file = choose.files && choose.files[0];
  if (!file) return;
  if (!/\.html?$/i.test(file.name) || file.size === 0 || file.size > MAX_BYTES) {
    message('Escolha um HTML original com até 64 MiB.', true);
    return;
  }
  message('Lendo o HTML selecionado somente na memória deste navegador…');
  try {
    const content = await file.text();
    if (serial !== currentSelection) return;
    const documentCopy = new DOMParser().parseFromString(content, 'text/html');
    if (documentCopy.querySelector('meta[http-equiv="refresh"]')) {
      message('Este é o ponteiro ATLAS-ATUAL.html. Escolha o index.html dentro de .r4/atlas/builds/<id>/.', true);
      return;
    }
    const dataScript = documentCopy.querySelector('script#data[type="application/json"]');
    if (!dataScript || !documentCopy.querySelector('.tab-panel') ||
        !documentCopy.querySelector('meta[http-equiv="Content-Security-Policy" i]')) {
      message('O arquivo não tem o contrato esperado do Atlas original R4.', true);
      return;
    }
    const data = JSON.parse(dataScript.textContent);
    if (!data || typeof data !== 'object' || !Array.isArray(data.records)) {
      message('Dados de apresentação original ausentes ou incompatíveis.', true);
      return;
    }
    // Enforce the child document's OWN restrictive CSP, before any scripts.
    // Its original CSP (including its script SHA) remains intact; policies
    // intersect, so a user-selected document cannot enable network access.
    // Do NOT serialize the parsed DOM: that could invalidate the original
    // script SHA and corrupt source text.
    const noNetworkPolicy = "default-src 'none'; connect-src 'none'; " +
      "script-src 'unsafe-inline'; style-src 'unsafe-inline'; " +
      "img-src data: blob:; font-src 'none'; media-src 'none'; " +
      "worker-src 'none'; frame-src 'none'; object-src 'none'; " +
      "base-uri 'none'; form-action 'none'";
    const cspElement = '<meta http-equiv="Content-Security-Policy" content="' +
      noNetworkPolicy + '">';
    const headTag = /<head(?:\\s[^>]*)?>/i;
    if (!headTag.test(content)) {
      message('O HTML original está sem o cabeçalho obrigatório.', true);
      return;
    }
    const confined = content.replace(headTag, tag => tag + cspElement);
    // The iframe never receives allow-same-origin or allow-top-navigation.
    wrapper.hidden = false;
    empty.hidden = true;
    frame.srcdoc = confined;
    message('Atlas original aberto localmente (' + data.records.length +
            ' registros declarados). Navegação e arquivos privados continuam separados.');
  } catch (_) {
    message('O HTML não pôde ser lido ou seus dados declarados são inválidos.', true);
  }
});
