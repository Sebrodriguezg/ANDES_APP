"""
Cifrado de las tandas de contenido.

El repositorio es público y gratuito, pero el banco de HRW es material con
copyright: no puede quedar legible ni indexable. Las tandas se publican cifradas
y la app las descifra en el teléfono con una clave que metes una sola vez.

Esquema, elegido para que WebCrypto lo pueda deshacer sin librerías:

    clave  = PBKDF2-HMAC-SHA256(frase, sal, 210 000 iteraciones) -> 256 bits
    tanda  = IV(12 bytes) || AES-256-GCM(contenido)

La sal y el número de iteraciones van en el manifiesto, que se queda en claro
porque solo contiene nombres de archivo y conteos.

No es una caja fuerte: protege contra el rastreo automático y la indexación, que
es exactamente el problema. Quien tenga la clave tiene el contenido.
"""

import base64
import json
import os
import secrets
import string
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITERACIONES = 210_000
TAM_SAL = 16
TAM_IV = 12

# Frase de prueba: se cifra con la misma clave y se guarda en el manifiesto para
# que la app pueda decir "clave incorrecta" al instante, en vez de reventar al
# intentar descifrar una tanda.
CANARIO = "andes-ok"

ARCHIVO_CLAVE = Path(__file__).resolve().parents[1] / ".clave"


def derivar(frase, sal):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=sal, iterations=ITERACIONES
    )
    return kdf.derive(frase.encode("utf-8"))


def cifrar(clave, datos_bytes):
    iv = os.urandom(TAM_IV)
    return iv + AESGCM(clave).encrypt(iv, datos_bytes, None)


def descifrar(clave, blob):
    return AESGCM(clave).decrypt(blob[:TAM_IV], blob[TAM_IV:], None)


def generar_frase():
    """Corta y tecleable en un celular, que es donde vas a escribirla."""
    alfabeto = string.ascii_lowercase + string.digits
    trozos = ["".join(secrets.choice(alfabeto) for _ in range(4)) for _ in range(3)]
    return "andes-" + "-".join(trozos)


def obtener_frase(explicita=None):
    """Toma la clave del argumento, del archivo local, o crea una nueva.

    El archivo .clave está en .gitignore: nunca sale del computador.
    """
    if explicita:
        return explicita, False
    if ARCHIVO_CLAVE.exists():
        frase = ARCHIVO_CLAVE.read_text(encoding="utf-8").strip()
        if frase:
            return frase, False
    frase = generar_frase()
    ARCHIVO_CLAVE.write_text(frase + "\n", encoding="utf-8")
    ARCHIVO_CLAVE.chmod(0o600)
    return frase, True


def preparar(frase):
    """Devuelve (clave, bloque para el manifiesto)."""
    sal = os.urandom(TAM_SAL)
    clave = derivar(frase, sal)
    canario = cifrar(clave, CANARIO.encode("utf-8"))
    bloque = {
        "algoritmo": "AES-GCM-256",
        "kdf": "PBKDF2-SHA256",
        "iteraciones": ITERACIONES,
        "sal": base64.b64encode(sal).decode(),
        "canario": base64.b64encode(canario).decode(),
    }
    return clave, bloque


def escribir_tanda(ruta, clave, tarjetas):
    crudo = json.dumps(tarjetas, ensure_ascii=False, separators=(",", ":"))
    ruta.write_bytes(cifrar(clave, crudo.encode("utf-8")))
