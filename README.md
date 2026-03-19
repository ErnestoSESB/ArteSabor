# ArteSabor
E-commerce criado para uma doceria local

## Como rodar este projeto localmente

1. **Pré-requisitos:**
   - Python 3.13.1 (ou compatível)
   - Git

2. **Clone o repositório:**
   ```sh
   git clone https://github.com/seu-usuario/seu-repo.git
   cd arte_sabor
   ```

3. **Crie e ative um ambiente virtual:**
   ```sh
   python -m venv venv
   # Ative o venv:
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

4. **Instale as dependências:**
   ```sh
   pip install -r requirements.txt
   ```
   - Se usar bibliotecas locais (ex: django-nexum-base), instale-as manualmente ou adicione ao requirements.txt.

5. **Configure variáveis de ambiente:**
   - Crie um arquivo `.env` (se necessário) ou ajuste o `settings.py` para sua máquina.

6. **Configure o banco de dados:**
   - Para SQLite, o arquivo `db.sqlite3` pode ser criado com as migrações.

7. **Rode as migrações:**
   ```sh
   python manage.py migrate
   ```

8. **(Opcional) Crie um superusuário:**
   ```sh
   python manage.py createsuperuser
   ```

9. **(Produção) Colete arquivos estáticos:**
   ```sh
   python manage.py collectstatic
   ```

10. **Rode o servidor de desenvolvimento:**
    ```sh
    python manage.py runserver
    ```

11. **Acesse:**
    - http://127.0.0.1:8000/
    - http://127.0.0.1:8000/admin/

12. **Arquivos de mídia:**
    - Certifique-se de que a pasta `media/` existe e está configurada em `MEDIA_ROOT`.

---

Se tiver dúvidas, consulte o settings.py ou abra uma issue.
