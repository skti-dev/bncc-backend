import json
from pathlib import Path
import streamlit as st
from io import BytesIO

try:
    from services.auth_service import get_password_hash
except Exception:
    import bcrypt

    def get_password_hash(p):
        return bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


st.title('Gerador de senhas hashed a partir de CPFs')

uploaded_file = st.file_uploader('Escolha um arquivo JSON', type=['json'])
if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
    except Exception as e:
        st.error(f'Erro ao ler JSON: {e}')
        st.stop()

    out = []
    for item in data:
        email = item.get('email')
        cpf = item.get('cpf')
        if not email or not cpf:
            continue
        cpf_digits = ''.join(c for c in cpf if c.isdigit())
        senha = get_password_hash(cpf_digits)
        out.append({'email': email, 'senha': senha})

    result_bytes = json.dumps(out, ensure_ascii=False, indent=2).encode('utf-8')
    st.write('Resultado gerado:')
    st.json(out)

    st.download_button('Baixar JSON gerado', data=BytesIO(result_bytes), file_name='sample_output.json', mime='application/json')
