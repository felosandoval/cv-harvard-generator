# 📄 Generador de CV Harvard

Un **generador bilingüe de CV en LaTeX** limpio, inspirado en el estilo de currículum de Harvard Business School.  
Edita un único archivo `data.json` y genera un CV profesional en PDF en **español y/o inglés** con un solo comando.

---

## 🗂 Estructura del proyecto

```
cv-harvard/
├── data.json        ← Tus datos del CV (el único archivo que necesitas editar)
├── generate.py      ← Script generador
└── README.md
```

Después de ejecutar el generador, los archivos de salida `.tex` (y opcionalmente `.pdf`) aparecerán en directorio "/output".

---

## ⚙️ Requisitos

| Requisito | Notas |
|---|---|
| **Python 3.8+** | No se necesitan librerías externas |
| **Distribución LaTeX** | Solo necesaria si quieres compilación automática (`--compile`) |

**Distribuciones LaTeX recomendadas:**
- **Windows:** [MiKTeX](https://miktex.org/) o [TeX Live](https://tug.org/texlive/)
- **macOS:** [MacTeX](https://www.tug.org/mactex/)
- **Linux:** `sudo apt install texlive-full` (o equivalente)

> Sin una instalación de LaTeX, el generador igualmente produce archivos `.tex` que puedes compilar en [Overleaf](https://www.overleaf.com/) (gratis, en línea).

---

## 🚀 Uso

```bash
# Generar versiones en español e inglés
python generate.py

# Generar solo español
python generate.py --lang es

# Generar solo inglés
python generate.py --lang en

# Generar y compilar automáticamente a PDF (requiere pdflatex instalado)
python generate.py --compile

# Archivo de datos y directorio de salida personalizados
python generate.py --data my_data.json --out ./output
```

---

## ✏️ Cómo personalizar

Abre `data.json` y completa tu información. Cada campo que tenga las claves `"es"` y `"en"` admite **contenido independiente por idioma**: no solo traducción, también adaptación profesional.

### Secciones principales

| Sección | Descripción |
|---|---|
| `personal` | Nombre, título, ubicación, contacto y enlaces sociales |
| `profile` | Párrafo de resumen profesional |
| `education` | Estudios (institución, nombre del grado, fechas) |
| `experience` | Experiencia laboral (empresa, rol, fechas, viñetas) |
| `volunteering` | Ayudantías y voluntariado |
| `certifications` | Certificaciones con enlaces y años |
| `skills` | Habilidades técnicas y nivel de idiomas |
| `additional` | Nacionalidad, fecha de nacimiento, ID, licencia de conducir |
| `labels` | Títulos de sección; personalízalos si renombras secciones |

### Agregar una nueva experiencia

```json
{
  "company": "NOMBRE DE LA EMPRESA",
  "role": {
    "es": "Rol en Español",
    "en": "Role in English"
  },
  "start": { "es": "Ene 2024", "en": "Jan 2024" },
  "end":   { "es": "Dic 2024", "en": "Dec 2024" },
  "bullets": [
    {
      "es": "Logro o responsabilidad en español.",
      "en": "Achievement or responsibility in English."
    }
  ]
}
```

### ⚠️ Caracteres especiales de LaTeX en JSON

Si tu texto contiene `&`, `%`, `$`, `#`, `_`, `{`, `}` y **no** es un comando LaTeX, el generador los escapará automáticamente.  
Si necesitas un comando LaTeX literal en el JSON (por ejemplo `\&` para categorías de habilidades), escríbelo directamente con la barra invertida; el generador lo detectará y omitirá el escape.

---

## 🌍 Filosofía de adaptación por idioma

Este proyecto **no** realiza traducciones literales palabra por palabra. El contenido se adapta para reflejar convenciones profesionales de cada idioma y cultura.

| ❌ Literal | ✅ Adaptado |
|---|---|
| Ingeniería en Informática | Computer Science |
| Practicante | Intern |
| Ayudante de Bases de Datos | Database Teaching Assistant |
| Encargado de Seguridad | Security Lead |

---

## 📐 Diseño

El formato sigue el estilo de currículum de **Harvard Business School**:
- Times New Roman (mediante `mathptmx`)
- A4, márgenes de 2 cm en todos los lados
- Líneas de sección de ancho completo
- Fechas alineadas a la derecha
- Párrafo de perfil justificado

---

## 📋 Compilar manualmente en Overleaf

1. Ejecuta `python generate.py` para generar los archivos `.tex`.
2. Ve a [overleaf.com](https://www.overleaf.com) → **New Project → Upload Project**.
3. Sube el archivo `.tex` generado.
4. Configura el compilador en **pdfLaTeX** y presiona **Recompile**.

---

## 📝 Licencia

MIT: úsalo libremente, adáptalo a tus necesidades y comparte mejoras.
