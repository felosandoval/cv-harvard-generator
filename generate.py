"""
Generador de CV estilo Harvard
==============================
Lee data.json y genera un CV en LaTeX en español e inglés.

Uso:
    python generate.py            # genera versiones es y en
    python generate.py --lang es  # solo español
    python generate.py --lang en  # solo inglés
    python generate.py --compile  # también ejecuta pdflatex (requiere instalación de LaTeX)
"""

import json
import argparse
import subprocess
import os
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def t(obj, lang):
    """Devuelve la cadena localizada desde un diccionario bilingüe o el valor original."""
    if isinstance(obj, dict):
        return obj.get(lang, obj.get("es", ""))
    return obj


def tex_escape(s: str) -> str:
    """Escapa caracteres especiales de LaTeX (mantiene intactas secuencias ya escapadas)."""
    replacements = [
        ("&",  r"\&"),
        ("%",  r"\%"),
        ("$",  r"\$"),
        ("#",  r"\#"),
        ("_",  r"\_"),
        ("{",  r"\{"),
        ("}",  r"\}"),
        ("~",  r"\textasciitilde{}"),
        ("^",  r"\textasciicircum{}"),
    ]
    # Omite cadenas que ya contienen comandos LaTeX (incluyen barra invertida)
    if "\\" in s:
        return s
    for char, escaped in replacements:
        s = s.replace(char, escaped)
    return s


# ─────────────────────────────────────────────────────────────────────────────
# Constructores de secciones
# ─────────────────────────────────────────────────────────────────────────────

def build_header(data: dict, lang: str) -> str:
    p = data["personal"]
    links = p["links"]
    return (
        r"\begin{center}" + "\n"
        r"  {\LARGE\bfseries " + tex_escape(p["name"]) + r"} \\" + "\n"
        r"  \medskip" + "\n"
        r"  {\itshape " + tex_escape(t(p["title"], lang)) + r"} \\" + "\n"
        r"  " + tex_escape(t(p["location"], lang)) + r" \\" + "\n"
        r"  \href{mailto:" + p["email"] + r"}{" + tex_escape(p["email"]) + r"}"
        r" $|$ \href{tel:" + p["phone"].replace(" ", "") + r"}{" + tex_escape(p["phone"]) + r"} \\" + "\n"
        r"  \href{" + links["linkedin"] + r"}{\textcolor{linkblue}{LinkedIn}}"
        r" $|$ \href{" + links["github"] + r"}{\textcolor{linkblue}{GitHub}}"
        r" $|$ \href{" + links["credly"] + r"}{\textcolor{linkblue}{Credly}}"
        + "\n"
        r"\end{center}" + "\n"
    )


def build_section(title: str) -> str:
    return (
        "\n"
        r"\vspace{6pt}"
        r"\noindent{\bfseries\large " + tex_escape(title) + r"}"
        r"\vspace{2pt}\hrule\vspace{4pt}" + "\n"
    )


def build_subsection(title: str) -> str:
    return r"\noindent{\bfseries " + tex_escape(title) + r"}\vspace{2pt}" + "\n"


def build_entry(company: str, role: str, start: str, end: str, bullets: list) -> str:
    lines = [
        r"\noindent\begin{tabularx}{\linewidth}{@{}X r@{}}",
        r"  \textbf{" + tex_escape(company) + r"} & \\",
        r"  \textit{" + tex_escape(role) + r"} & \textit{" + tex_escape(start) + r" -- " + tex_escape(end) + r"} \\",
        r"\end{tabularx}",
    ]
    for b in bullets:
        lines.append(r"\hspace{1em}$\bullet$\enspace " + tex_escape(b) + r" \\")
    lines.append(r"\vspace{4pt}")
    return "\n".join(lines) + "\n"


def build_edu_entry(institution: str, degree: str, start: str, end: str) -> str:
    return (
        r"\noindent\begin{tabularx}{\linewidth}{@{}X r@{}}" + "\n"
        r"  \textbf{" + tex_escape(institution) + r"} & \textit{" + tex_escape(start) + r" -- " + tex_escape(end) + r"} \\" + "\n"
        r"\end{tabularx}" + "\n"
        r"\noindent " + tex_escape(degree) + "\n"
        r"\vspace{4pt}" + "\n"
    )


def build_cert_table(certs: list, lang: str) -> str:
    lines = [r"\begin{tabularx}{\linewidth}{@{}X r@{}}"]
    for c in certs:
        name = tex_escape(t(c["name"], lang))
        issuer = tex_escape(c["issuer"])
        year = c["year"]
        link = c["link"]
        lines.append(
            r"  \textbf{" + issuer + r"} --- " + name
            + r" & \href{" + link + r"}{\textcolor{linkblue}{link}} $|$ " + year + r" \\"
        )
    lines.append(r"\end{tabularx}")
    return "\n".join(lines) + "\n"


def build_skills(skills: dict, labels: dict, lang: str) -> str:
    lines = []
    lines.append(build_subsection(t(labels["technical"], lang)))
    lines.append(r"\begin{itemize}[leftmargin=1.5em, itemsep=1pt, topsep=2pt]")
    for sk in skills["technical"]:
        cat   = tex_escape(t(sk["category"], lang))
        items = tex_escape(t(sk["items"], lang))
        lines.append(r"  \item \textbf{" + cat + r":} " + items)
    lines.append(r"\end{itemize}")
    lines.append("")
    lines.append(build_subsection(t(labels["languages_sec"], lang)))
    lines.append(r"\begin{itemize}[leftmargin=1.5em, itemsep=1pt, topsep=2pt]")
    for lang_item in skills["languages"]:
        language = tex_escape(t(lang_item["language"], lang))
        level    = tex_escape(t(lang_item["level"], lang))
        lines.append(r"  \item " + language + r": " + level)
    lines.append(r"\end{itemize}")
    return "\n".join(lines) + "\n"


def build_additional(add: dict, labels: dict, lang: str) -> str:
    lines = [
        r"\noindent " + tex_escape(t(labels["nationality"], lang)) + r": " + tex_escape(t(add["nationality"], lang)) + r"\\",
        r"\noindent " + tex_escape(t(labels["birthdate"], lang))   + r": " + tex_escape(t(add["birthdate"], lang))   + r"\\",
        r"\noindent " + tex_escape(t(labels["id_label"], lang))    + r": " + tex_escape(add["id"])                   + r"\\",
        r"\noindent " + tex_escape(t(labels["license"], lang))     + r": " + tex_escape(t(add["license"], lang)),
    ]
    return "\n".join(lines) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# Ensamblado del documento LaTeX
# ─────────────────────────────────────────────────────────────────────────────

PREAMBLE = r"""\documentclass[11pt, a4paper]{article}

% ── Codificación y fuente ────────────────────────────────────────────────────
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{mathptmx}          % Equivalente a Times New Roman

% ── Geometría de página ──────────────────────────────────────────────────────
\usepackage[
  a4paper,
  top=2cm, bottom=2cm,
  left=2cm, right=2cm
]{geometry}

% ── Microtipografía y espaciado ──────────────────────────────────────────────
\usepackage{microtype}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}

% ── Tablas ───────────────────────────────────────────────────────────────────
\usepackage{tabularx}
\usepackage{booktabs}

% ── Listas ───────────────────────────────────────────────────────────────────
\usepackage{enumitem}

% ── Hipervínculos y colores ──────────────────────────────────────────────────
\usepackage[hidelinks]{hyperref}
\usepackage{xcolor}
\definecolor{linkblue}{RGB}{0, 0, 180}
\hypersetup{colorlinks=true, urlcolor=linkblue, linkcolor=black}

% ── Alineado a la izquierda (evita exceso de guionado) ───────────────────────
\usepackage{ragged2e}

\pagestyle{empty}

"""


def generate_tex(data: dict, lang: str) -> str:
    labels = data["labels"]

    body_parts = []

    # Encabezado
    body_parts.append(build_header(data, lang))
    body_parts.append(r"\vspace{8pt}" + "\n")

    # Perfil
    body_parts.append(build_section(t(labels["profile"], lang)))
    body_parts.append(
        r"\justifying " + tex_escape(t(data["profile"], lang)) + "\n"
    )

    # Educación
    body_parts.append(build_section(t(labels["education"], lang)))
    for edu in data["education"]:
        body_parts.append(build_edu_entry(
            t(edu["institution"], lang),
            t(edu["degree"], lang),
            edu["start"],
            t(edu["end"], lang)
        ))

    # Experiencia
    body_parts.append(build_section(t(labels["experience"], lang)))
    for exp in data["experience"]:
        body_parts.append(build_entry(
            exp["company"],
            t(exp["role"], lang),
            t(exp["start"], lang),
            t(exp["end"], lang),
            [t(b, lang) for b in exp["bullets"]]
        ))

    # Voluntariado
    body_parts.append(build_section(t(labels["volunteering"], lang)))
    for vol in data["volunteering"]:
        body_parts.append(build_entry(
            t(vol["institution"], lang),
            t(vol["role"], lang),
            t(vol["start"], lang),
            t(vol["end"], lang),
            [t(b, lang) for b in vol["bullets"]]
        ))

    # Certificaciones
    body_parts.append(build_section(t(labels["certifications"], lang)))
    body_parts.append(build_cert_table(data["certifications"], lang))

    # Habilidades
    body_parts.append(build_section(t(labels["skills"], lang)))
    body_parts.append(build_skills(data["skills"], labels, lang))

    # Información adicional
    body_parts.append(build_section(t(labels["additional"], lang)))
    body_parts.append(build_additional(data["additional"], labels, lang))

    document = (
        PREAMBLE
        + r"\begin{document}" + "\n\n"
        + "\n".join(body_parts)
        + "\n\n"
        + r"\end{document}" + "\n"
    )
    return document


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Harvard-style CV generator (LaTeX)")
    parser.add_argument("--lang",    choices=["es", "en", "both"], default="both",
                        help="Language to generate (default: both)")
    parser.add_argument("--compile", action="store_true",
                        help="Run pdflatex after generating .tex files")
    parser.add_argument("--data",    default="data.json",
                        help="Path to the JSON data file (default: data.json)")
    parser.add_argument("--out",     default="output",
                        help="Output directory (default: latex)")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌  Data file not found: {data_path}")
        return

    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Convierte el nombre completo a PascalCase para el prefijo del archivo.
    name_pascal = "".join(part.capitalize() for part in data["personal"]["name"].replace("_", " ").split())
    base_filename = f"CV{name_pascal}"
    langs = ["es", "en"] if args.lang == "both" else [args.lang]

    for lang in langs:
        tex_content = generate_tex(data, lang)
        lang_suffix = "_en" if lang == "en" else ""
        filename    = f"{base_filename}{lang_suffix}.tex"
        filepath    = out_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(tex_content)

        print(f"✅  Generated: {filepath}")

        if args.compile:
            try:
                subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(out_dir), str(filepath)],
                    check=True,
                    capture_output=True
                )
                print(f"📄  PDF compiled: {out_dir / filename.replace('.tex', '.pdf')}")
            except FileNotFoundError:
                print("⚠️   pdflatex not found. Install a LaTeX distribution (e.g. TeX Live, MiKTeX).")
            except subprocess.CalledProcessError as e:
                print(f"❌  pdflatex error:\n{e.stdout.decode()}\n{e.stderr.decode()}")


if __name__ == "__main__":
    main()
