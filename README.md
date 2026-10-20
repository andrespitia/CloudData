#####################
# CloudData
#####################

Plataforma que permite a una empresa centralizar información procedente de distintas fuentes, procesarla automáticamente, almacenarla y consultar indicadores de negocio desde Power BI.

CloudData integra datos de varias fuentes en Microsoft Azure, los procesa con dos micro servicios, los guarda en una capa de persistencia y los publica en Power BI. Este repositorio contiene la primera fase del proyecto: diseño de la arquitectura, justificación teórica según el NIST y entorno de gestión en GitHub.

--------------------------------------------------------------------
 Autor  Andres Leonardo Espitia Ramírez 
 Asignatura  Cloud Computing 
 Fase actual  Hito 1 – Diseño y gestión 
 Nube  Microsoft Azure (cuenta Azure for Students) 
--------------------------------------------------------------------
## Contenido

1. Bases del proyecto(#1-bases-del-proyecto)
2. Descripción del dominio(#2-descripción-del-dominio)
3. Justificación NIST SP 800-145(#3-justificación-nist-sp-800-145)
4. Mapeo de actores NIST SP 500-292(#4-mapeo-de-actores-nist-sp-500-292)
5. Diagrama de arquitectura(#5-diagrama-de-arquitectura)
6. Especificación de la API REST(#6-especificación-de-la-api-rest)
7. Entorno de ingeniería de software en GitHub(#7-entorno-de-ingeniería-de-software-en-github)
8. Estructura del repositorio(#8-estructura-del-repositorio)
9. Ejecución local(#9-ejecución-local)
10.Conclusiones(#10-conclusiones)
11.Referencias(#11-referencias)
   
--------------------------------------------------------------------
## 1. Bases del proyecto
--------------------------------------------------------------------
Nombre: CloudData – Plataforma de integración y análisis de datos en Azure.

Objetivo general: diseñar una plataforma en la nube de Microsoft Azure que integre datos de varias fuentes, los procese mediante dos microservicios desacoplados y los presente en Power BI para apoyar decisiones de ventas e inventario.

Objetivos específicos:

1. Definir una problemática de negocio real que justifique la adopción de la nube.
2. Diseñar una arquitectura desacoplada con dos microservicios y una capa de persistencia.
3. Configurar el entorno de gestión de ingeniería de software en GitHub.
4. Fundamentar el sistema según la definición de computación en la nube del NIST SP 800-145 y la arquitectura de referencia del NIST SP 500-292.

Alcance: el proyecto soluciona una problemática de carga y consolidación de datos mediante servicios en la nube y dos microservicios que procesan los datos para que luego los resultados se consulten como indicadores de negocio. Se prioriza una solución funcional, económica y fácil de mantener.

Tecnologías:

 Capa  Tecnología 

 Fuentes  Archivos CSV, Excel o XML; base Azure SQL de ventas 
 Ingesta  Endpoint `POST /upload` del Microservicio 1 
 Microservicio 1  Carga y limpieza – Python + pandas + FastAPI 
 Microservicio 2  Reportes (KPI) – Python + FastAPI 
 Almacenamiento de archivos  Azure Blob Storage (`raw/`, `processed/`) 
 Datos consolidados  Azure SQL Database 
 Ejecución  Azure Container Apps 
 Visualización  Power BI 
 Gestión del proyecto  GitHub (repositorio, Issues, Projects y Actions) 

--------------------------------------------------------------------
## 2. Descripción del dominio
--------------------------------------------------------------------
### 2.1 Problemática de negocio

La empresa es una cadena de tiendas de tecnología que tarda entre 2 y 3 días en obtener un reporte consolidado de ventas e inventario, lo que retrasa la reposición de productos.

Situación actual:

- Las ventas se registran en un ERP sobre Oracle y el inventario en SQL Server on-premises.
- Los proveedores envían catálogos y despachos en CSV y Excel por correo.
- La tienda online entrega los pedidos mediante una API REST.
- Los reportes se consolidan a mano en Excel cada semana, con registros duplicados y errores de digitación.
- El servidor local se satura en los cierres de mes.

Consecuencias: decisiones tomadas con datos desactualizados, quiebres de stock en productos de alta rotación y horas de trabajo manual en tareas repetitivas.

### 2.2 Solución: una aplicación nativa de la nube

CloudData reemplaza el proceso manual por un flujo automático:

1. Cada tienda o área sube su archivo de ventas al Microservicio 1.
2. El Microservicio 1 – Carga y limpieza valida, normaliza y elimina duplicados, y guarda los datos en la capa de persistencia.
3. El Microservicio 2 – Reportes calcula indicadores de ventas e inventario.
4. Power BI muestra los indicadores a la gerencia desde la web o el celular.

En este proyecto, las fuentes de la empresa (Oracle, SQL Server, archivos de proveedores y la API de la tienda online) se simulan con archivos CSV, Excel o XML y una base Azure SQL de ventas.

Indicadores de éxito esperados: reporte disponible pocas horas después de cada carga, 0 registros duplicados en la capa consolidada y un tablero único de ventas e inventario.

### 2.3 Por qué no es un sistema CRUD

Un sistema CRUD solo crea, lee, actualiza y borra registros tal como llegan. CloudData transforma los datos con reglas de negocio y genera indicadores a partir de ellos.

### 2.4 Casos de uso principales

 ID  Caso de uso  Actor  Microservicio 
 
 CU-01  Subir el archivo de ventas  Encargado de tienda  Carga y limpieza 
 CU-02  Consultar el informe de calidad de una carga  Encargado de tienda  Carga y limpieza 
 CU-03  Consultar el resumen de ventas de la cadena  Gerente comercial  Reportes 
 CU-04  Comparar las ventas entre tiendas  Gerente comercial  Reportes 
 CU-05  Identificar los productos más vendidos  Jefe de compras  Reportes 
 CU-06  Detectar productos con inventario bajo  Jefe de compras  Reportes 
 CU-07  Visualizar los indicadores en un tablero  Gerencia  Power BI (consume Reportes) 

### 2.5 Justificación del uso de la nube

 Necesidad del negocio  
  
 Unificar archivos y bases de datos heterogéneos  El Microservicio 1 recibe CSV, Excel o XML y los lleva a un formato común en Azure SQL 
 Datos confiables  
 El Microservicio 1 valida, normaliza y elimina duplicados antes de consolidar. Información disponible para la gerencia  
 El Microservicio 2 calcula indicadores y Power BI los muestra en tableros web 
 Crecer sin rehacer el sistema  La arquitectura por microservicios permite sumar fuentes y servicios 
 
--------------------------------------------------------------------
## 3. Justificación NIST SP 800-145
--------------------------------------------------------------------

El NIST SP 800-145 define la computación en la nube como un modelo que permite acceso ubicuo, conveniente y bajo demanda, a través de la red, a un conjunto compartido de recursos configurables que se aprovisionan y liberan rápidamente con un mínimo esfuerzo de gestión. La definición se compone de 5 características esenciales, 3 modelos de servicio y 4 modelos de despliegue.

CloudData cumple las cinco características esenciales, usa los modelos PaaS y SaaS y se despliega en nube pública.

### 3.1 Las 5 características esenciales

 Característica	Aplicación en CloudeData
**Autoservicio bajo demanda** -->	El equipo crea Blob Storage, Azure SQL y Container Apps desde el portal o Azure CLI, sin intervención del proveedor.
**Amplio acceso a la red** -->	Las APIs de los microservicios y los tableros de Power BI se consumen por HTTPS desde navegador.
**Agrupación de recursos** -->	Azure atiende a muchos clientes sobre la misma infraestructura (multi-tenant); ambos microservicios comparten un mismo entorno de Container Apps.
**Elasticidad rápida** -->	Cada microservicio escala de 0 a 3 réplicas según la carga; Azure SQL serverless ajusta su capacidad y se pausa sin uso.
**Servicio medido** -->	El consumo se mide y factura por uso; Azure Monitor y Cost Management muestran métricas y costos, como tambien con la implementacion de alertas de consumo mediante el panel de alertas.


### 3.2 Modelos de servicio

 IaaS  No se usa 
 PaaS  Azure Blob Storage, Azure SQL Database, Azure Container Apps 
 SaaS  Power BI, GitHub 

### 3.3 Modelo de despliegue

Nube pública: todos los servicios corren en Microsoft Azure; las demás fuentes se simulan con archivos. Si en el futuro se conectaran directamente las bases Oracle y SQL Server de la empresa, el modelo podria pasar a ser nube híbrida.

### 3.4 Responsabilidad compartida

En PaaS, Microsoft administra el hardware, la red, el sistema operativo y los parches. El equipo de desarrollo es responsable del código de los microservicios, los datos, la configuración de accesos y la protección de credenciales y tokens.


## 4. Mapeo de actores NIST SP 500-292

La arquitectura de referencia NIST SP 500-292 define cinco actores que participan en todo sistema en la nube. En AzureData se identifican así:

| Actor NIST | Quién cumple el rol | Responsabilidades en el proyecto | Impacto económico |

| **Consumidor** (*Cloud Consumer*) | La cadena de tiendas de tecnología: encargados de tienda, gerencia y jefe de compras | Usa la aplicación, carga los datos y consume los reportes | Paga solo por uso (gasto operativo, OpEx). Elimina la compra de servidores (gasto de capital, CapEx) y reduce horas de trabajo manual. |
| **Proveedor** (*Cloud Provider*) | Microsoft Azure | Opera los centros de datos, Container Apps, Azure SQL y Blob Storage; garantiza disponibilidad y seguridad física | Recupera su inversión por economías de escala al compartir infraestructura entre millones de clientes; ofrece cuotas gratuitas que reducen el costo de entrada. |
| **Intermediario** (*Cloud Broker*) | El equipo de desarrollo de AzureData | Agrega e integra varios servicios de Azure y Power BI en una sola solución para el consumidor | Le ahorra a la empresa el costo de integrar los servicios por su cuenta. |
| **Auditor** (*Cloud Auditor*) | Auditores independientes que certifican a Azure (ISO/IEC 27001, SOC 1/2/3), con informes publicados en el Microsoft Service Trust Portal | Evalúan de forma independiente la seguridad, privacidad y rendimiento del proveedor | La empresa no paga auditorías propias de infraestructura: hereda las certificaciones del proveedor. |
| **Operador** (*Cloud Carrier*) | Los proveedores de internet de las tiendas y la red global de Microsoft | Transportan los datos entre tiendas, Azure y los usuarios de Power BI | Costo de conectividad que la empresa ya paga. La entrada de datos a Azure es gratuita y los primeros 100 GB mensuales de salida no se cobran. |

### 4.1 Análisis del impacto económico

| Concepto | Servidor propio | AzureData en la nube |

| Inversión inicial | Compra de servidor, licencias y espacio físico (CapEx) | Ninguna; la infraestructura se crea bajo demanda |
| Costo mensual | Fijo, aunque el servidor esté ocioso | Variable y proporcional al uso; cómputo en cero sin peticiones |
| Picos de fin de mes | Se compra capacidad para el peor caso y se desperdicia el resto del mes | La elasticidad agrega réplicas solo durante el pico |
| Mantenimiento | Personal propio para parches, respaldos y hardware | Incluido en el servicio PaaS |
| Riesgo financiero | Alto: el hardware se deprecia aunque el proyecto cambie | Bajo: al eliminar el grupo de recursos, el gasto se detiene |

| Servicio | Base del cobro | Costo mensual estimado |
| --- | --- | --- |
| Azure Container Apps | Concesión gratuita mensual: 180.000 vCPU-segundos, 360.000 GiB-segundos y 2 millones de peticiones | 0 USD dentro de la concesión |
| Azure SQL Database | Oferta gratuita: 100.000 vCore-segundos y 32 GB por base de datos al mes, o serverless con autopausa | 0 USD con la oferta gratuita; pocos USD en serverless |
| Azure Blob Storage | Por GB almacenado y operación | Menos de 1 USD para pocos GB |
| Power BI Desktop y GitHub | Gratuitos para este uso | 0 USD |

El proyecto se ejecutara dentro del crédito de Azure for Students (100 USD), con un presupuesto de 20 USD y alerta al 80 % en Cost Management.

## 5. Diagrama de arquitectura

El sistema tiene dos microservicios en Python con responsabilidades separadas. No se llaman entre sí: se comunican a través de la capa de persistencia (Blob Storage y Azure SQL).

### 5.1 Componentes y protocolos

```mermaid
flowchart LR
    subgraph FUENTES["Fuentes de datos"]
        ARCH["Archivos de tiendas<br/>CSV · XLSX · XML"]
        ORIG[("Azure SQL<br/>ventas")]
    end

    subgraph AZURE["Microsoft Azure · rg-CloudData-dev"]
        subgraph CAPPS["Azure Container Apps"]
            MS1["Microservicio 1<br/>Carga y limpieza<br/>Python + pandas + FastAPI"]
            MS2["Microservicio 2<br/>Reportes KPI<br/>Python + FastAPI"]
        end
        subgraph PERS["Capa de persistencia"]
            BLOB[("Azure Blob Storage<br/>raw/ · processed/")]
            SQL[("Azure SQL Database<br/>datos consolidados")]
        end
    end

    PBI["Power BI<br/>tablero gerencial"]

    ARCH -->"HTTPS POST /upload · multipart/form-data" MS1
    ORIG -->"TDS/SQL · puerto 1433" MS1
    MS1 -->"HTTPS · Blob REST API" BLOB
    MS1 -->"TDS/SQL · puerto 1433 · escritura" SQL
    SQL -->"TDS/SQL · puerto 1433 · lectura" MS2
    MS2 -->"HTTPS · REST · JSON" PBI
    SQL -.->"DirectQuery · TDS/SQL" PBI
```

### 5.2 Vista general



### 5.3 Flujo de datos

1. El usuario sube un archivo CSV, Excel o XML al endpoint `POST /upload` del Microservicio 1; la base Azure SQL de ventas se lee directamente.
2. El Microservicio 1 guarda el archivo original en `raw/` de Blob Storage.
3. Lo valida, normaliza y elimina duplicados con pandas; guarda el resultado en `processed/` y lo carga en Azure SQL.
4. El Microservicio 2 consulta Azure SQL y expone indicadores por API REST.
5. Power BI lee Azure SQL (DirectQuery) y, opcionalmente, los indicadores de la API.

### 5.4 Los dos microservicios

  Microservicio 1: Carga y limpieza  Microservicio 2: Reportes (KPI) 
 ---  ---  --- 
 Responsabilidad  Recibir archivos, validar, normalizar y eliminar duplicados  Calcular indicadores de ventas e inventario 
 Tecnología  Python + FastAPI + pandas  Python + FastAPI 
 Entrada  Archivos CSV, Excel o XML; base Azure SQL de ventas  Tablas consolidadas en Azure SQL 
 Salida  `raw/` y `processed/` en Blob Storage; tablas en Azure SQL  API REST para reportes 
 Endpoints  `POST /upload`, `GET /health`  `GET /kpi/ventas`, `GET /kpi/top-productos`, `GET /health` 
 Despliegue  Container App propia, de 0 a 3 réplicas  Container App propia, de 0 a 3 réplicas 

### 5.5 Capa de persistencia

 Componente  Qué guarda  Para qué 
 ---  ---  --- 
 Azure Blob Storage  `raw/`: archivo original tal como llegó. `processed/`: archivo depurado  Trazabilidad: cualquier dato del reporte se puede rastrear hasta su archivo de origen 
 Azure SQL Database  Ventas e inventario consolidados  Consultas rápidas y consistentes del Microservicio 2 y de Power BI 

### 5.6 Protocolos de comunicación

 Origen → Destino  Protocolo  Formato 
 ---  ---  --- 
 Usuario → Microservicio 1  HTTPS (TLS)  `multipart/form-data` → respuesta JSON 
 Microservicio 1 → Blob Storage  HTTPS, API REST de Blob mediante el SDK de Azure  Archivo 
 Microservicio 1 → Azure SQL  TDS (protocolo de SQL Server), cifrado, puerto 1433  Filas SQL 
 Microservicio 2 → Azure SQL  TDS cifrado, puerto 1433, solo lectura  Consultas SQL 
 Power BI → Microservicio 2  HTTPS (TLS)  JSON 
 Power BI → Azure SQL  TDS (DirectQuery), solo lectura  Consultas SQL 

### 5.7 Por qué la arquitectura es desacoplada

- Sin llamadas directas entre microservicios: el Microservicio 1 escribe en la capa de persistencia y el Microservicio 2 solo lee de ella.
- Despliegue independiente: cada uno tiene su propio código, imagen Docker, workflow de GitHub Actions y Container App.
- Escalado independiente: el de carga crece en los cierres de mes y el de reportes cuando la gerencia consulta.
- Tolerancia a fallos: si el Microservicio 1 falla, los reportes siguen disponibles con los datos ya consolidados.

---

## 6. Especificación de la API REST

### 6.1 Convenciones

- URL base: cada microservicio tiene su propia dirección en Azure Container Apps, por ejemplo `https://carga-limpieza.<entorno>.azurecontainerapps.io` y `https://reportes.<entorno>.azurecontainerapps.io`.
- Formato: JSON en UTF-8. Fechas en ISO 8601 (`AAAA-MM-DD`). Montos en pesos, sin separadores de miles.
- Errores: código HTTP adecuado y cuerpo `{"detail": "mensaje"}`.
- Documentación interactiva: cada servicio publica su especificación OpenAPI en `/docs`.

### 6.2 Resumen de endpoints

 Servicio  Verbo  Ruta  Descripción  Respuesta 
 ---  ---  ---  ---  --- 
 Carga y limpieza  `POST`  `/upload`  Sube y procesa un archivo de ventas  `201 Created` 
 Carga y limpieza  `GET`  `/cargas/{id_carga}`  Informe de calidad de una carga (planificado, hito 2)  `200 OK` 
 Carga y limpieza  `GET`  `/health`  Estado del servicio  `200 OK` 
 Reportes  `GET`  `/kpi/ventas`  Ventas totales, número de ventas y ticket promedio  `200 OK` 
 Reportes  `GET`  `/kpi/ventas-por-tienda`  Total vendido por tienda, de mayor a menor  `200 OK` 
 Reportes  `GET`  `/kpi/top-productos?limite=5`  Productos más vendidos por unidades  `200 OK` 
 Reportes  `GET`  `/kpi/ventas-por-dia?desde=&hasta=`  Tendencia diaria de ventas  `200 OK` 
 Reportes  `GET`  `/kpi/inventario-bajo-stock?minimo=10`  Productos con inventario bajo (planificado, hito 3)  `200 OK` 
 Reportes  `GET`  `/health`  Estado del servicio  `200 OK` 

### 6.3 Microservicio 1 – Carga y limpieza

#### `POST /upload`

Sube un archivo de ventas (CSV, XLSX o XML) y aplica las reglas de calidad. Columnas obligatorias: `id_venta`, `fecha`, `tienda`, `producto`, `cantidad`, `precio`.

Petición (`multipart/form-data`):

```bash
curl -X POST "https://carga-limpieza.<entorno>.azurecontainerapps.io/upload" \
     -F "archivo=@ventas.csv"
```

Respuesta `201 Created`:

```json
{
  "archivo": "ventas.csv",
  "estado": "procesado",
  "recibidas": 7,
  "cargadas": 4,
  "descartadas": {
    "sin_id": 1,
    "cantidad_invalida": 1,
    "fecha_invalida": 0,
    "duplicadas": 1
  }
}
```

Errores:

 Código  Causa  Cuerpo 
 ---  ---  --- 
 `415`  Formato no soportado  `{"detail": "Formato no soportado. Use CSV, XLSX o XML."}` 
 `422`  Faltan columnas obligatorias  `{"detail": "Faltan columnas obligatorias: ['precio']"}` 

### 6.4 Microservicio 2 – Reportes

#### `GET /kpi/ventas`

```json
{ "ventas_totales": 548000.0, "numero_ventas": 4, "ticket_promedio": 137000.0 }
```

#### `GET /kpi/ventas-por-tienda`

```json
[
  { "tienda": "Norte", "total": 368000.0 },
  { "tienda": "Centro", "total": 180000.0 }
]
```

#### `GET /kpi/top-productos?limite=2`

 Parámetro  Tipo  Obligatorio  Descripción 
 ---  ---  ---  --- 
 `limite`  entero de 1 a 50  No (por defecto 5)  Número de productos a devolver 

```json
[
  { "producto": "Mouse inalámbrico", "unidades": 4, "total": 180000.0 },
  { "producto": "Cable HDMI", "unidades": 4, "total": 128000.0 }
]
```

#### `GET /kpi/ventas-por-dia?desde=2026-10-02&hasta=2026-10-03`

```json
[
  { "fecha": "2026-10-02", "total": 45000.0 },
  { "fecha": "2026-10-03", "total": 128000.0 }
]
```

#### `GET /health` (ambos servicios)

```json
{ "estado": "ok", "servicio": "reportes" }
```

---

## 7. Entorno de ingeniería de software en GitHub

### 7.1 Repositorio y `.gitignore`

Repositorio individual con un [`.gitignore`](.gitignore) adaptado al stack: Python (entornos virtuales, caché, pruebas), secretos (`.env`, claves), Azure, Docker, Power BI y archivos del sistema operativo.

### 7.2 Estrategia de ramas

- `main`: versión estable, protegida. Solo recibe cambios por Pull Request con las pruebas en verde.
- `feature/<id>-<tema>`, `fix/<id>-<tema>`, `docs/<tema>`: una rama por historia de usuario, integrada a `main` mediante Pull Request.

### 7.3 Commits semánticos

 Tipo  Uso  Ejemplo 
 ---  ---  --- 
 `feat:`  Nueva funcionalidad  `feat(carga): agrega endpoint POST /upload` 
 `fix:`  Corrección de un error  `fix(carga): acepta fechas dd/mm/aaaa` 
 `docs:`  Documentación  `docs: agrega mapeo de actores NIST SP 500-292` 
 `refactor:`  Mejora interna sin cambiar el comportamiento  `refactor(reportes): separa el cálculo de KPI` 

El workflow `pr-title.yml` valida que el título de cada Pull Request siga esta convención. El detalle está en [CONTRIBUTING.md](CONTRIBUTING.md).

### 7.4 Tablero y backlog

- GitHub Projects: tablero agrupado por Milestone con el backlog inicial.
- Milestones: Hito 1 – Diseño y gestión · Hito 2 – Persistencia e infraestructura · Hito 3 – Microservicios en la nube · Hito 4 – Visualización y cierre.
- Historias de usuario: 13 Issues con la etiqueta `user-story`, formato «Como [rol], quiero [acción], para [beneficio]», criterios de aceptación y checklist de tareas técnicas. Su contenido está en [`scripts/backlog/`](scripts/backlog) y se publica con [`scripts/setup_github.sh`](scripts/setup_github.sh).

### 7.5 Plantillas

 Archivo  Uso 
 ---  --- 
 [`.github/ISSUE_TEMPLATE/user_story.md`](.github/ISSUE_TEMPLATE/user_story.md)  Crear historias de usuario estandarizadas 
 [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md)  Formalizar entregas y revisiones de código 

### 7.6 Integración continua

Cada microservicio tiene su propio workflow (`ci-carga-limpieza.yml` y `ci-reportes.yml`) que ejecuta las pruebas y construye la imagen Docker solo cuando cambia su carpeta.

---

## 8. Estructura del repositorio

```
CloudData/
├── README.md
├── CONTRIBUTING.md                 # ramas y commits semánticos
├── .gitignore
├── .github/
│   ├── ISSUE_TEMPLATE/user_story.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/                  # ci-carga-limpieza, ci-reportes, pr-title
├── docs/arquitectura.png
├── data-samples/ventas.csv         # archivo de prueba con errores típicos
├── services/
│   ├── carga-limpieza/             # Microservicio 1: Python + pandas + FastAPI
│   │   ├── app/  (main.py, limpieza.py)
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── reportes/                   # Microservicio 2: Python + FastAPI
│       ├── app/  (main.py, kpi.py)
│       ├── tests/
│       ├── requirements.txt
│       └── Dockerfile
├── powerbi/                        # reporte .pbix
└── scripts/
    ├── setup_github.sh             # crea etiquetas, milestones, issues y tablero
    └── backlog/                    # historias de usuario
```

---

## 9. Ejecución local

Requisito: Python 3.12.

```bash
cd services/carga-limpieza
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt pytest
pytest
uvicorn app.main:app --reload --port 8000
```

Luego se abre `http://localhost:8000/docs` y se prueba `POST /upload` con `data-samples/ventas.csv`. El Microservicio 2 se ejecuta igual desde `services/reportes`, en el puerto 8001.

---

## 10. Conclusiones

- La problemática justifica una solución en la nube con pago por uso y escalado automático.
- La arquitectura con dos microservicios en Python separa la carga y limpieza de datos de la generación de reportes; cada uno se desarrolla, despliega y escala de forma independiente.
- El diseño cumple las cinco características esenciales del NIST SP 800-145, lo que lo valida formalmente como un sistema de computación en la nube.
- El mapeo de actores del NIST SP 500-292 muestra que la empresa traslada la inversión y el mantenimiento de infraestructura al proveedor y paga solo por lo que usa.
- GitHub organiza el trabajo con ramas protegidas, commits semánticos, historias de usuario y un tablero por hitos durante todo el curso.

