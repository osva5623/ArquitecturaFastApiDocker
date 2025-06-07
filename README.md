# 🚀 RCS Backend con FastAPI + Docker + ngrok

Este proyecto expone una API básica construida con **FastAPI**, la ejecuta en **Docker** y la publica en internet usando **ngrok** con autenticación.

---

## 📦 Requisitos

- Docker
- Docker Compose
- Cuenta gratuita en [ngrok.com](https://ngrok.com) para obtener un authtoken

---

## 📁 Estructura del proyecto

```
rcs-backend/
├── app/
│   └── rcs_handler.py       # API RCS
├── main.py                  # Conf FastApi
├── requirements.txt         # Dependencias de Python
├── Dockerfile               # Imagen con FastAPI + ngrok
├── docker-compose.yml       # Orquestación
└── .env                     # Authtoken de ngrok
```

---

## ⚙️ Configuración

1. **Crea el archivo `.env` con tu token de ngrok:**

   ```env
   NGROK_AUTHTOKEN=tu_token_ngrok
   ```

   Puedes obtenerlo desde: https://dashboard.ngrok.com/get-started/your-authtoken

---

## 🚀 Ejecución

Levanta el contenedor con:

```bash
docker-compose up --build
```

Verás algo como:

```
Forwarding                    https://abcd1234.ngrok.io -> http://localhost:8000
```

🔗 Abre en tu navegador:
- `https://abcd1234.ngrok.io/` → Te responde con: `{"mensaje": "Hola Mundo desde FastAPI"}`
- `https://abcd1234.ngrok.io/docs` → Swagger UI (documentación interactiva)
- `https://abcd1234.ngrok.io/redoc` → ReDoc

---

## 🧪 Probar localmente (opcional)

Si prefieres probar sin ngrok:

```bash
uvicorn app.main:app --reload
```

Y accede a:
- `http://localhost:5050`
- `http://localhost:5050/docs`

---

## 🛠️ Personalización

Puedes modificar el archivo `app/main.py` para agregar nuevas rutas, autenticación, o lógica personalizada.

---

## 📌 Notas

- Esta configuración usa `ngrok` dentro del contenedor, útil para pruebas rápidas o compartir con terceros.
- En entornos de producción se recomienda usar dominios fijos y servicios como Nginx + HTTPS.

---

## 🧑‍💻 Oswaldo Jimenez

> Proyecto de backend de prueba para RCS con FastAPI + Docker + ngrok
