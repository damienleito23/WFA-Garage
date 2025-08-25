# WFA Garage — Website (Flask)

Acesta este un site complet pentru **WFA Garage** cu:
- Pagini publice: Acasă, Produse (filtrate pe *piese* și *detailing*), Contact.
- Panou **Admin** cu autentificare (adăugare / editare / ștergere produse).
- Încărcare imagini produse.
- Fundal setat cu sigla/brandul furnizat (`static/images/wfa-bg.png`).

## Cum rulezi local

1. Instalează Python 3.10+.
2. În terminal:

```bash
cd wfa_garage_site
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
set FLASK_SECRET_KEY=schimba-asta   # Windows CMD
export FLASK_SECRET_KEY=schimba-asta # macOS/Linux

# Creează baza de date + admin implicit
export WFA_DEFAULT_PASS=WFA#Garage2025
flask --app app.py init-db

# Pornește serverul
python app.py
```

3. Deschide http://localhost:5000
4. Intră la **Admin** cu:
   - Utilizator: `wfa_admin`
   - Parola: `WFA#Garage2025`

> Schimbă parola imediat după prima logare: poți adăuga un nou admin din DB, sau îmi spui și ți-o adaptez în cod.

## Deploy ușor (gratuit)
- **Railway** sau **Render**: conectezi repo-ul GitHub, adaugi variabila `FLASK_SECRET_KEY`, rulezi comanda de init în *deploy hook* (`flask --app app.py init-db`) și pornești web service pe portul 5000.
- **Fly.io**: opțional (necesită Dockerfile).

Dacă vrei panel grafic de Content (NetlifyCMS/Strapi), pot migra datele — spune-mi ce preferi.
