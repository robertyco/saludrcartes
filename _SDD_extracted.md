SDD – Sitio Web saludrcartes
1. Introducción y objetivos
Este documento es el Diseño de Software (SDD) del sitio saludrcartes, un sitio personal de registro clínico para Roberto Carlos Cartes Jiménez. Centraliza diagnósticos, medicamentos, alergias y resultados de especialidades médicas en un solo lugar, junto con los documentos de respaldo descargables, para consulta propia, de familiares y de personal de salud en situaciones de urgencia.
Objetivos del sitio
- Dar acceso rápido al historial médico completo desde cualquier dispositivo.
- Permitir que personal de salud, familiares o servicios de urgencia encuentren en segundos la información crítica: diagnósticos, alergias, medicamentos y contactos.
- Respaldar cada afección con los documentos clínicos que la sustentan, descargables en PDF.
- Entregar una experiencia visual cálida, cercana y accesible, alineada a la paleta de color definida, alejada de la estética fría típica de los portales clínicos tradicionales.
Alcance del documento
Este SDD define la arquitectura de información, el sistema de diseño visual, la especificación de cada página, el modelo de datos, la gestión de documentos descargables, los requisitos de seguridad y privacidad, la accesibilidad, el stack tecnológico recomendado y el plan de implementación por fases.
2. Arquitectura de la información
mapa del sitio · 3 grupos, 12 páginas
Desde Inicio se accede a tres grupos: Registro clínico (Diagnósticos, Medicamentos y Alergias, Laboratorio), Especialidades médicas (ocho páginas) y Emergencia (Contactos de emergencia). La página de Inicio muestra una tarjeta clicable por cada una de las doce páginas, con una descripción resumida de su contenido; al hacer clic se navega directamente al detalle de esa afección o categoría.
3. Sistema de diseño visual
La paleta del brief se implementa como variables CSS globales, para mantener consistencia entre las 13 páginas.

| Rol | Hex | Uso recomendado |
| Verde vitalidad | #0E9F6E | Color principal: logo, títulos destacados, enlaces, botón principal |
| Turquesa sereno | #38BDF8 | Fondos de sección, iconos, ilustraciones, etiquetas de datos |
| Coral alegre | #FF6B6B | Acentos emocionales, badges, alertas (siempre con texto oscuro encima) |
| Amarillo solar | #FFC94A | Logros, recordatorios positivos (siempre con texto oscuro encima) |
| Violeta esperanza | #8B5CF6 | Secciones de bienestar emocional, citas, apoyo |
| Crema luminoso | #FFF8F0 | Fondo principal del sitio |
| Tinta amable | #1F2937 | Texto principal y títulos |
| Blanco puro | #FFFFFF | Tarjetas, formularios, áreas de lectura |

Reglas de contraste (WCAG)
- Texto normal: mínimo 4.5:1. Texto grande, iconos y componentes interactivos: mínimo 3:1.
- Nunca texto blanco sobre coral (#FF6B6B) o amarillo (#FFC94A); usarlos como fondos decorativos con texto #1F2937 encima.
- Los estados (Atención, Estable, Mejorando) se comunican con icono + etiqueta de texto, nunca solo con color.
Componentes base
- Fondo del sitio: #FFF8F0.
- Tarjeta de salud: fondo #FFFFFF, borde 2px #0E9F6E, radio 20px, sombra muy tenue.
- Botón principal: fondo #0E9F6E, texto blanco, radio 999px (píldora), peso 700.
- Botón secundario: fondo blanco, borde #0E9F6E, texto #0E9F6E.
- Esquinas redondeadas e ilustraciones orgánicas en toda la interfaz, en vez de la estética clínica tradicional.
Tipografía sugerida: una tipografía redondeada y amigable para títulos (por ejemplo Quicksand o Nunito, peso 700) combinada con una tipografía de alta legibilidad para texto largo (por ejemplo Inter o Source Sans), tamaño base 16px y jerarquía clara entre H1/H2/H3.
:root {
  --verde-vitalidad: #0E9F6E;
  --turquesa-sereno: #38BDF8;
  --coral-alegre: #FF6B6B;
  --amarillo-solar: #FFC94A;
  --violeta-esperanza: #8B5CF6;
  --crema-luminoso: #FFF8F0;
  --tinta-amable: #1F2937;
  --blanco: #FFFFFF;
}
4. Especificación de la página de Inicio
La portada muestra una grilla de 12 tarjetas clicables (componente tarjeta-salud), una por cada página del sitio, ordenadas por grupo (Registro clínico, Especialidades médicas, Emergencia).
Cada tarjeta contiene
- Icono o ilustración orgánica representativa de la categoría.
- Título de la página (por ejemplo "Cardiología").
- Descripción resumida de 1–2 líneas (por ejemplo "Diagnóstico, ECG y ecocardiogramas, tratamiento actual").
- Indicador opcional de estado ("Estable", "En seguimiento") con icono + etiqueta, nunca solo color.
- Toda la tarjeta es un enlace: un clic en cualquier punto navega al detalle de esa página.
Encabezado de Inicio: nombre del sitio, un saludo breve y, de forma destacada y siempre visible (sticky), un botón hacia la página de Contactos de emergencia, con fondo coral y texto oscuro, para que sea ubicable al instante en una urgencia.
Orden visual sugerido: Diagnósticos y Medicamentos y Alergias primero (lo más consultado), luego Laboratorio, luego las ocho especialidades, y Contactos de emergencia siempre visible aparte de la grilla.
5. Páginas de contenido clínico
Las once páginas de detalle (todas salvo Inicio y Contactos de emergencia) comparten una misma plantilla:
- Encabezado: nombre de la página con el color de acento de su grupo, breadcrumb de vuelta a Inicio.
- Resumen de la afección: estado actual, fecha de diagnóstico, médico o centro tratante.
- Detalle clínico: texto y/o tabla con la evolución (fecha, hallazgo, acción tomada).
- Documentos descargables: lista de archivos PDF/imagen que respaldan la afección, cada uno con nombre, fecha y botón de descarga.
- Notas y tratamiento actual: indicaciones vigentes.
Contenido específico por página:

| Página | Contenido específico | Tipo de documento típico |
| Diagnósticos | Diagnósticos activos e históricos, código CIE-10, fecha, médico tratante | Informes médicos, epicrisis (PDF) |
| Medicamentos y Alergias | Medicamentos vigentes (dosis, horario, vía), alergias con nivel de severidad | Recetas médicas (PDF) |
| Laboratorio | Resultados de exámenes con fecha y rango de referencia | Informes de laboratorio (PDF) |
| Neurología | Diagnóstico neurológico, EEG, resonancia cerebral, evolución | Informes e imágenes (PDF) |
| Cardiología | ECG, ecocardiograma, diagnóstico y control cardiológico | Informes (PDF) |
| Fisiatría | Evaluación funcional, plan de rehabilitación física | Informes y planes (PDF) |
| Rehabilitación | Registro de sesiones, progreso, objetivos terapéuticos | Informes de evolución (PDF) |
| Fonoaudiología | Evaluación de habla y deglución, plan de terapia | Informes (PDF) |
| Psiquiatría | Diagnóstico, tratamiento farmacológico, evolución | Informes (PDF) |
| Traumatología superior | Lesiones de extremidad superior, cirugías, radiografías | Informes e imágenes (PDF) |
| Traumatología inferior | Lesiones de extremidad inferior, cirugías, radiografías | Informes e imágenes (PDF) |

6. Página de Contactos de emergencia
Es la página de mayor prioridad de uso: debe cargar rápido, leerse fácil sin lentes puestos y, si se habilita el modo emergencia (sección 9), poder compartirse con un desconocido sin exponer el resto del sitio.
Bloque "Información crítica" (arriba de todo, fondo coral con texto oscuro): grupo sanguíneo, alergias graves, condiciones que deben conocerse de inmediato.
Lista de contactos, cada uno con: nombre, relación (familiar, médico tratante, seguro de salud), teléfono (con enlace tel: para llamar con un toque), y tipo de contacto.
Acciones rápidas: botón para llamar al contacto principal, botón para descargar una ficha resumen en PDF (diagnósticos + alergias + medicamentos + contactos) pensada para imprimir o mostrar en una atención de urgencia.
7. Modelo de datos
Esquema relacional sobre Supabase (PostgreSQL), con una tabla de categorías que mapea a las 12 páginas del sitio.

| Entidad | Campos principales | Relación |
| categoria (página) | id, slug, nombre, grupo, color_acento, orden | 1:N con afeccion |
| afeccion | id, categoria_id, título, descripción, estado, fecha_diagnóstico, médico_tratante | N:1 con categoria; 1:N con documento |
| documento | id, afeccion_id, nombre, tipo_archivo, url_storage, fecha_subida, es_descargable | N:1 con afeccion |
| medicamento | id, nombre, dosis, frecuencia, vía, fecha_inicio, fecha_fin, activo | N:1 con afeccion (opcional, para medicamentos ligados a un diagnóstico) |
| alergia | id, sustancia, severidad, reacción, fecha_registro | Independiente, mostrada en Medicamentos y Alergias |
| contacto_emergencia | id, nombre, relación, teléfono, tipo_contacto, orden | Independiente |

Cada fila de categoria corresponde a una de las 12 tarjetas de Inicio y define el color de acento y el orden de aparición, de modo que agregar una página nueva en el futuro no requiere tocar código, solo una fila.
8. Gestión de documentos descargables
- Almacenamiento: Supabase Storage, en un bucket privado (no público) con un objeto por documento; la tabla documento guarda solo la referencia (url_storage), nunca el archivo.
- Formatos aceptados: PDF como formato principal; JPG/PNG para radiografías o imágenes sueltas que luego se puede optar por convertir a PDF.
- Nombres de archivo: convención categoria-AAAA-MM-DD-descripcion.pdf para que sean identificables incluso fuera del sitio.
- Descarga: cada documento listado en la página de su categoría muestra nombre, fecha y un botón "Descargar"; el acceso al archivo se resuelve con una URL firmada de corta duración generada por una Netlify Function, nunca con una URL pública permanente.
- Vista previa: para PDF, un visor embebido simple antes de descargar; para imágenes, una miniatura clicable.
9. Seguridad y privacidad
Este sitio aloja datos de salud personales, la categoría de dato más sensible según la Ley 19.628 sobre Protección de la Vida Privada. El diseño debe tratarlo como confidencial por defecto.
- Autenticación obligatoria: todo el sitio detrás de login (Supabase Auth), incluida la página de Inicio; sin cuentas de invitado.
- No indexación: robots.txt con Disallow: / y meta noindex, nofollow en todas las páginas, para que no aparezca en buscadores.
- Row Level Security (RLS) en todas las tablas de Supabase, de modo que solo el usuario dueño de los datos pueda leer o escribir sus propias filas.
- Documentos privados: bucket de Storage privado, acceso solo mediante URLs firmadas de corta duración (sección 8), nunca enlaces públicos permanentes.
- Cifrado en tránsito y en reposo: TLS en todas las conexiones (por defecto en Netlify y Supabase) y cifrado en reposo en la base de datos y el storage.
- "Modo emergencia" opcional: si se desea que un tercero (paramédico, familiar) acceda sin login en una urgencia, implementarlo como un enlace separado y de un solo propósito que muestre únicamente la página de Contactos de emergencia más alergias y medicamentos críticos, con expiración o revocación manual, nunca exponiendo el resto del historial.
- Respaldos: backups automáticos de la base de datos (Supabase los ofrece por defecto en sus planes pagos) y, al menos trimestralmente, una exportación manual descargada aparte.
- Registro de accesos: log de inicios de sesión y de descargas de documentos, para poder revisar quién accedió y cuándo.
10. Accesibilidad y usabilidad
- Cumplir WCAG 2.1 nivel AA: contraste mínimo 4.5:1 en texto normal y 3:1 en texto grande e iconos interactivos (tabla de combinaciones en la sección 3).
- Todo estado o alerta se comunica con icono + texto, nunca solo con color, para personas con daltonismo.
- Texto alternativo (alt) descriptivo en toda imagen clínica (radiografías, gráficos), e indicación del contenido en los enlaces de descarga ("Descargar informe de ecocardiograma, PDF, 2 MB").
- Navegación completa por teclado, con foco visible en tarjetas, botones y enlaces de descarga.
- Tamaño de texto ajustable por el usuario sin romper el diseño (unidades relativas, no píxeles fijos).
- Objetivos táctiles de al menos 44x44 px en botones y tarjetas, pensando en uso con una sola mano en una urgencia.
11. Stack tecnológico recomendado

| Capa | Tecnología | Nota |
| Frontend | HTML / CSS / JavaScript | Páginas estáticas, tarjetas y componentes como en el diseño del sistema visual |
| Backend / API | Netlify Functions (Node.js) | Genera las URLs firmadas de descarga y centraliza las consultas a Supabase |
| Base de datos | Supabase (PostgreSQL) | Tablas del modelo de datos de la sección 7, con RLS activado |
| Almacenamiento de archivos | Supabase Storage | Bucket privado para los documentos descargables |
| Autenticación | Supabase Auth | Login obligatorio en todo el sitio |
| Hosting / CDN | Netlify | Despliegue continuo desde el repositorio |

Este es el mismo stack (HTML/CSS/JS, Netlify Functions y Supabase) que ya usas en tu otro proyecto, lo que permite reutilizar configuración, patrones de código y aprendizaje y acelerar el desarrollo de saludrcartes.
12. Diseño responsive
- Enfoque mobile-first: la grilla de tarjetas de Inicio pasa de 3 columnas (escritorio) a 2 (tablet, ~768px) a 1 columna (móvil, <480px).
- Las tablas de contenido clínico (evolución, documentos) se transforman en tarjetas apiladas en móvil, evitando el scroll horizontal.
- El botón de Contactos de emergencia permanece siempre visible (sticky) en la parte superior, en cualquier tamaño de pantalla.
- Los botones de descarga y los enlaces tel: mantienen un área táctil de al menos 44x44 px en todos los breakpoints.
13. Roadmap de implementación
- Fase 1 — Fundamentos: repositorio, proyecto Supabase con autenticación y RLS, sistema de diseño (tokens CSS, componentes de tarjeta y botón), página de Inicio con tarjetas (aún sin datos reales).
- Fase 2 — Núcleo clínico: tablas categoria, afeccion, documento; páginas Diagnósticos, Medicamentos y Alergias y Laboratorio funcionando con datos y descarga de documentos.
- Fase 3 — Especialidades: las ocho páginas de especialidad (Neurología, Cardiología, Fisiatría, Rehabilitación, Fonoaudiología, Psiquiatría, Traumatología superior e inferior) sobre la misma plantilla de la sección 5.
- Fase 4 — Emergencia y seguridad: página de Contactos de emergencia, ficha PDF descargable, URLs firmadas de descarga, revisión completa de RLS y robots.txt; evaluar el "modo emergencia" opcional.
- Fase 5 — Pulido: revisión de accesibilidad (contraste, teclado, lectores de pantalla), diseño responsive en los tres breakpoints, pruebas con usuarios (tú mismo y, si corresponde, un familiar) y respaldo inicial de todos los documentos.
14. PDFs con información y url de cuaderno de Gemini con info medica
https://notebook.google.com/notebook/057ddfa9-d1ff-4088-b271-529a129f5c36
https://notebook.google.com/notebook/98fe4218-9c9d-406a-8e03-125fdaa11dd7
C:\Users\rober\OneDrive\Escritorio\Escritorio\HEC