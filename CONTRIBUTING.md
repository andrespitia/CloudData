# Guía de contribución

Este documento define cómo se trabaja en el repositorio: estrategia de ramas, convención de commits y flujo de Pull Requests.

## Estrategia de ramas

Se usa un flujo basado en `main` con ramas de funcionalidad (*feature branches*), también conocido como GitHub Flow.

| Rama | Propósito | Ejemplo |
| --- | --- | --- |
| `main` | Versión estable. Protegida: solo recibe cambios por Pull Request con las pruebas en verde. | `main` |
| `feature/<id>-<tema>` | Nueva funcionalidad asociada a una historia de usuario | `feature/hu-03-endpoint-upload` |
| `fix/<id>-<tema>` | Corrección de un error | `fix/hu-04-fechas-formato-latino` |
| `docs/<tema>` | Cambios solo de documentación | `docs/readme-nist` |

Flujo de trabajo:

```bash
git checkout main
git pull
git checkout -b feature/hu-03-endpoint-upload
# ... cambios ...
git add .
git commit -m "feat(carga): agrega endpoint POST /upload"
git push -u origin feature/hu-03-endpoint-upload
```

Luego se abre un Pull Request hacia `main` usando la plantilla, se enlaza la historia con `Closes #<número>` y, cuando las pruebas pasan, se fusiona con **Squash and merge**. La rama se elimina después de fusionar.

### Protección de `main`

En **Settings → Branches → Add branch ruleset** (o *Add rule*) sobre `main`:

- Require a pull request before merging
- Require status checks to pass (`ci-carga-limpieza`, `ci-reportes`, `compose`, `pr-title`)
- Block force pushes

## Commits semánticos

Todos los commits y títulos de Pull Request siguen la convención [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/):

```
<tipo>(<alcance opcional>): <descripción en minúscula y en imperativo>
```

| Tipo | Cuándo usarlo | Ejemplo |
| --- | --- | --- |
| `feat` | Nueva funcionalidad | `feat(reportes): agrega endpoint de top productos` |
| `fix` | Corrección de un error | `fix(carga): acepta fechas con formato dd/mm/aaaa` |
| `docs` | Solo documentación | `docs: agrega mapeo de actores NIST SP 500-292` |
| `refactor` | Cambio interno sin alterar el comportamiento | `refactor(carga): separa la limpieza en un módulo` |
| `test` | Agregar o corregir pruebas | `test(carga): cubre filas duplicadas` |
| `ci` | Cambios en GitHub Actions | `ci: agrega pipeline del microservicio de reportes` |
| `chore` | Mantenimiento o configuración | `chore: actualiza .gitignore` |

Alcances sugeridos: `carga`, `reportes`, `infra`, `powerbi`, `docs`.

El workflow `pr-title.yml` valida automáticamente que el título de cada Pull Request cumpla esta convención.

## Historias de usuario

Cada trabajo nace de una historia de usuario creada con la plantilla **Historia de usuario** (`.github/ISSUE_TEMPLATE/user_story.md`), con:

- Formato «Como [rol], quiero [acción], para [beneficio]».
- Criterios de aceptación verificables.
- Etiqueta `user-story` y un milestone.
- Checklist de tareas técnicas.
