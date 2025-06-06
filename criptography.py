from dotenv import load_dotenv
import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib
import json
from Crypto.Util.Padding import pad, unpad

# === Password e crittografia AES CBC ===
from dotenv import load_dotenv
import os

load_dotenv()
def_pwd = os.getenv("DATA_PASSWORD")

def cipher(html, filename, password = def_pwd):
    key = hashlib.sha256(password.encode()).digest()  # 32-byte key
    iv = get_random_bytes(16)  # IV random
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(html.encode(), AES.block_size))
    data = {
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

    # === Template HTML: include CryptoJS e script di decrittazione ===
    encrypted_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8" />
    <title>Ciphered page</title>
    <script src="https://cdn.jsdelivr.net/npm/crypto-js@4.1.1/crypto-js.min.js"></script>
    </head>
    <body>
    <p style="font-family:sans-serif;">🔐 Anauthorized access: content locked</p>
    <script>
        const ed = {{
            iv: "{data['iv']}",
            ciphertext: "{data['ciphertext']}"
        }};

        function decryptPage(password) {{
            try {{
                const key = CryptoJS.SHA256(password);
                const iv = CryptoJS.enc.Base64.parse(ed.iv);
                const decrypted = CryptoJS.AES.decrypt(ed.ciphertext, key, {{ iv: iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 }});
                const result = decrypted.toString(CryptoJS.enc.Utf8);
                if (!result) throw new Error("Wrong key or corrupted data");
                document.open(); document.write(result); document.close();
            }} catch (e) {{
                document.body.innerHTML = "<p style='color:red;font-family:sans-serif;'>❌ Deciphering failed: " + e.message + "</p>";
            }}
        }}

        // 1. Prova da query string
        const pms = new URLSearchParams(window.location.search);
        if (pms.has("key")) {{
            decryptPage(pms.get("key"));
        }} else {{
            // 2. Altrimenti ascolta postMessage
            window.addEventListener("message", (e) => {{
                if (e.data && typeof e.data === "string") {{
                    decryptPage(e.data);
                }}
            }}, false);
        }}
    </script>
    </body>
    </html>
    """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(encrypted_html)

    print(f"🔐 Ciphered html saved: {filename}!")
