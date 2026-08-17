/* Descifrado de las tandas con WebCrypto.

   Contraparte de 07_APP/tuberia/cifrar.py. La clave derivada se guarda en el
   teléfono tras la primera vez, así que la frase se escribe una sola vez. */

const CLAVE_GUARDADA = 'andes.clave';

let claveActual = null;

const b64aBytes = b64 =>
  Uint8Array.from(atob(b64), c => c.charCodeAt(0));

const bytesAb64 = bytes =>
  btoa(String.fromCharCode(...new Uint8Array(bytes)));

async function derivar(frase, cripto) {
  const material = await crypto.subtle.importKey(
    'raw', new TextEncoder().encode(frase), 'PBKDF2', false, ['deriveKey']
  );
  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: b64aBytes(cripto.sal),
      iterations: cripto.iteraciones,
      hash: 'SHA-256',
    },
    material,
    { name: 'AES-GCM', length: 256 },
    true,
    ['decrypt']
  );
}

export async function descifrar(clave, blob) {
  const bytes = new Uint8Array(blob);
  const texto = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: bytes.slice(0, 12) },
    clave,
    bytes.slice(12)
  );
  return new TextDecoder().decode(texto);
}

/** Comprueba la frase contra el canario antes de dar la clave por buena. */
export async function probarFrase(frase, cripto) {
  const clave = await derivar(frase, cripto);
  try {
    const texto = await descifrar(clave, b64aBytes(cripto.canario));
    if (texto !== 'andes-ok') return null;
  } catch {
    return null;
  }
  return clave;
}

export async function recordar(clave) {
  const crudo = await crypto.subtle.exportKey('raw', clave);
  try { localStorage.setItem(CLAVE_GUARDADA, bytesAb64(crudo)); } catch { /* cuota */ }
  claveActual = clave;
}

export async function recuperar(cripto) {
  if (claveActual) return claveActual;
  const guardada = localStorage.getItem(CLAVE_GUARDADA);
  if (!guardada) return null;
  try {
    const clave = await crypto.subtle.importKey(
      'raw', b64aBytes(guardada), { name: 'AES-GCM', length: 256 }, true, ['decrypt']
    );
    // Se revalida contra el canario: si se regeneró el contenido con otra frase,
    // la clave vieja ya no sirve y hay que volver a pedirla.
    const texto = await descifrar(clave, b64aBytes(cripto.canario));
    if (texto !== 'andes-ok') return null;
    claveActual = clave;
    return clave;
  } catch {
    return null;
  }
}

export function olvidar() {
  claveActual = null;
  try { localStorage.removeItem(CLAVE_GUARDADA); } catch { /* nada */ }
}

export function hayClave() { return claveActual !== null; }
