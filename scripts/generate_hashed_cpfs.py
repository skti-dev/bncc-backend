"""Script para gerar senhas hashed a partir de CPFs.

Uso:
  python scripts/generate_hashed_cpfs.py input.json output.json

input.json deve ser um array de objetos: [{ "email": "...", "cpf": "..." }, ...]
output.json será: [{ "email": "...", "senha": "<bcrypt-hash>" }, ...]

O script reutiliza a função `get_password_hash` do `services.auth_service` para garantir compatibilidade.
"""
import json
import re
import sys
from pathlib import Path

try:
    from services.auth_service import get_password_hash
except Exception:
    # fallback: local implementation using bcrypt
    import bcrypt

    def get_password_hash(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def clean_cpf(cpf: str) -> str:
    return re.sub(r"\D", "", cpf or "")


def process(input_path: Path, output_path: Path):
    data = json.loads(input_path.read_text(encoding='utf-8'))
    out = []
    for item in data:
        email = item.get('email')
        cpf = clean_cpf(item.get('cpf', ''))
        if not email or not cpf:
            continue
        senha = get_password_hash(cpf)
        out.append({"email": email, "senha": senha})

    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {len(out)} entries to {output_path}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/generate_hashed_cpfs.py input.json output.json")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    process(input_path, output_path)


if __name__ == '__main__':
    main()
