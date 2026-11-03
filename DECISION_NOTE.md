Elegí la consigna A: una vista para que el sponsor de una empresa prepare conversaciones de seguimiento sin entrar a la plataforma del participante.

Prioricé tres preguntas: cuántas personas siguen inscritas, qué módulos publicados completaron y quiénes tienen asistencia registrada. El detalle individual muestra historial de módulos, minutos conectados y actividad semanal. Separé la cohorte actualmente activa de la elegibilidad histórica; no convertí participación en una puntuación de motivación ni en evidencia de aprendizaje.

El servidor consulta el mock API, valida los registros y entrega únicamente campos permitidos. Excluí notas del coach, correos y enlaces de sesiones. La demo pública tiene una cuenta de reviewer con contraseña protegida mediante hash, sesiones temporales y comprobación de empresa y programa en el servidor. Cloudflare D1 mantiene las sesiones y los límites de intentos de acceso; las credenciales se entregan por separado. No afirmo aislamiento multicliente ni una solución de identidad lista para producción.

El prototipo local usa Python sin dependencias externas. Para publicarlo, adapté el servidor a JavaScript sobre Cloudflare Workers, conservando la interfaz y verificando equivalencia de cálculos. Dejé fuera notificaciones, recuperación de contraseñas y administración multicliente. Incluí errores sin sustitución silenciosa, un modo offline local explícito, pruebas de cálculos y acceso, y paginación del equipo. Probé el cálculo con 120 participantes; todavía envío el detalle completo en una respuesta.

Con un día más, integraría identidad administrada e invitaciones de sponsor, paginación y detalle bajo demanda en el servidor, y pruebas automatizadas de navegador, accesibilidad y carga.

Transparencia: utilicé IA y hubo refinamientos posteriores al primer prototipo. No registré de forma fiable el tiempo activo, por lo que no presento este resultado como una ejecución cronometrada de cuatro horas.
