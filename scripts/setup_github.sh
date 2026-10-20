#!/usr/bin/env bash
# ==========================================================
# setup_github.sh - Configura el ecosistema de gestión en GitHub
#
# Crea en el repositorio actual:
#   1. Etiquetas (user-story, ms-carga, ms-reportes, infra, docs, power-bi)
#   2. Milestones de los 4 hitos del curso
#   3. Las historias de usuario de scripts/backlog/ como Issues
#   4. Un tablero de GitHub Projects con todas las historias
#
# Requisitos:
#   - GitHub CLI (gh) instalado y autenticado:  gh auth login
#   - Permiso de proyectos:                      gh auth refresh -s project
#   - Ejecutarlo desde la raíz del repositorio, después del primer push.
#
# Uso:
#   bash scripts/setup_github.sh            # crea todo
#   DRY_RUN=1 bash scripts/setup_github.sh  # solo muestra lo que haría
#
# Es seguro ejecutarlo más de una vez: omite lo que ya existe.
# ==========================================================
set -euo pipefail

DRY_RUN="${DRY_RUN:-0}"
BACKLOG_DIR="scripts/backlog"
PROJECT_TITLE="${PROJECT_TITLE:-CloudData - Backlog}"

run() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

if [ "$DRY_RUN" = "1" ]; then
  REPO="${REPO:-usuario/clouddata}"
else
  REPO="${REPO:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
fi
OWNER="${REPO%%/*}"
echo "Repositorio: $REPO"

# ---------- 1. Etiquetas ----------
echo "==> Etiquetas"
crear_etiqueta() {
  run gh label create "$1" --repo "$REPO" --color "$2" --description "$3" --force
}
crear_etiqueta "user-story"  "1D76DB" "Historia de usuario"
crear_etiqueta "ms-carga"    "7A3EC8" "Microservicio 1 - Carga y limpieza"
crear_etiqueta "ms-reportes" "A77CE6" "Microservicio 2 - Reportes"
crear_etiqueta "infra"       "0078D4" "Infraestructura Azure y CI/CD"
crear_etiqueta "docs"        "6E7781" "Documentación"
crear_etiqueta "power-bi"    "E8A317" "Visualización en Power BI"

# ---------- 2. Milestones ----------
echo "==> Milestones"
existentes=""
if [ "$DRY_RUN" != "1" ]; then
  existentes="$(gh api "repos/$REPO/milestones?state=all" --paginate -q '.[].title')"
fi
crear_milestone() {
  if printf '%s\n' "$existentes" | grep -Fxq "$1"; then
    echo "   ya existe: $1"
  else
    run gh api "repos/$REPO/milestones" -f title="$1" -f description="$2" --silent
  fi
}
crear_milestone "Hito 1 – Diseño y gestión"               "Arquitectura, justificación NIST, repositorio y backlog"
crear_milestone "Hito 2 – Persistencia e infraestructura" "Recursos Azure, Blob Storage y Azure SQL"
crear_milestone "Hito 3 – Microservicios en la nube"      "Implementación y despliegue en Azure Container Apps"
crear_milestone "Hito 4 – Visualización y cierre"         "Power BI, pruebas finales y presentación"

# ---------- 3. Historias de usuario ----------
echo "==> Historias de usuario"
URLS=()
while IFS='|' read -r id titulo milestone etiquetas; do
  [ -z "$id" ] && continue
  url=""
  if [ "$DRY_RUN" != "1" ]; then
    url="$(gh issue list --repo "$REPO" --state all --search "$id in:title" \
            --json url -q '.[0].url // empty')"
  fi
  if [ -n "$url" ]; then
    echo "   ya existe: $titulo"
  else
    if [ "$DRY_RUN" = "1" ]; then
      run gh issue create --repo "$REPO" --title "$titulo" \
        --body-file "$BACKLOG_DIR/$id.md" --label "$etiquetas" --milestone "$milestone"
      url="https://github.com/$REPO/issues/$id"
    else
      url="$(gh issue create --repo "$REPO" --title "$titulo" \
        --body-file "$BACKLOG_DIR/$id.md" --label "$etiquetas" --milestone "$milestone")"
      echo "   creada: $url"
    fi
  fi
  URLS+=("$url")
done < "$BACKLOG_DIR/backlog.txt"

# ---------- 4. Tablero de GitHub Projects ----------
echo "==> Tablero de GitHub Projects"
numero=""
if [ "$DRY_RUN" != "1" ]; then
  numero="$(gh project list --owner "$OWNER" --format json \
             -q ".projects[] | select(.title == \"$PROJECT_TITLE\") | .number" | head -n1)"
fi
if [ -z "$numero" ]; then
  if [ "$DRY_RUN" = "1" ]; then
    run gh project create --owner "$OWNER" --title "$PROJECT_TITLE" --format json
    numero="N"
  else
    numero="$(gh project create --owner "$OWNER" --title "$PROJECT_TITLE" --format json -q .number)"
    echo "   creado: proyecto #$numero"
  fi
else
  echo "   ya existe: proyecto #$numero"
fi
run gh project link "$numero" --owner "$OWNER" --repo "$REPO" || true

for url in "${URLS[@]}"; do
  run gh project item-add "$numero" --owner "$OWNER" --url "$url" || true
done

echo
echo "Listo. Pasos manuales que faltan (no se pueden hacer desde la CLI):"
echo "  1. En el tablero: cambiar la vista a 'Board' y en View -> Group by elegir 'Milestone'."
echo "  2. Settings -> Branches: proteger 'main' (PR obligatorio y checks en verde)."
