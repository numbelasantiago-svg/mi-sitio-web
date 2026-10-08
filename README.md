# N-STUDIO · Prospección médica La Paz (oct 2026)

- `investigacion/informe-traumatologos-la-paz.md` — screening, scoring y análisis de 7 traumatólogos, mensajes y roadmap.
- `demos/` — demos estáticas (HTML/CSS/JS, sin dependencias) para los prospectos de prioridad A:
  - `dr-alvaro-guzman/` — web nueva (dominio actual caído).
  - `dr-juan-carlos-cruz/` — centralización La Paz + Santa Cruz.
  - `dr-marcelo-gumiel/` — rediseño de drgumiel.com orientado a conversión.
- `scripts/qa_nstudio.py` — QA pre-entrega: `python3 scripts/qa_nstudio.py demos/<slug> --modo demo`.

Las demos llevan `noindex` y el aviso «Propuesta de diseño (demo)». Abrir `index.html` en el navegador o publicar cada carpeta en Netlify como `nstudio-<slug>-demo`.
