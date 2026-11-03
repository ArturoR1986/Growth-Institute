Elegí la consigna A: una vista para que el sponsor de una empresa pueda preparar conversaciones de seguimiento sin entrar a la plataforma del participante.

Prioricé tres preguntas: cuántas personas siguen inscritas, qué módulos publicados completaron y quiénes tienen asistencia registrada. El detalle individual muestra historial de módulos, minutos conectados y actividad semanal. Separé la cohorte actualmente activa de la elegibilidad histórica; no convertí participación en una puntuación de motivación ni en evidencia de aprendizaje.

El servidor consulta el mock API, valida los registros y entrega únicamente campos permitidos. Excluí notas del coach, correos y enlaces de sesiones. El sponsor tiene una cuenta independiente, contraseña con hash y una sesión temporal; el servidor comprueba su empresa y programa antes de devolver datos. Es una implementación local: no afirmo aislamiento multicliente ni autenticación lista para producción.

Elegí Python sin dependencias externas para facilitar la revisión. Dejé fuera notificaciones, administración, recuperación de contraseñas, administración multicliente. Incluí un modo offline explícito, errores sin sustitución silenciosa, pruebas de cálculos y acceso, y paginación del equipo. Probé el cálculo con 120 participantes; todavía envío el detalle completo en una respuesta.

La demo desplegada usa sesiones y límites de acceso en D1; las credenciales se entregan por separado. Con un día más, integraría identidad administrada e invitaciones de sponsor, paginación y detalle bajo demanda en el servidor, y pruebas automatizadas de navegador, accesibilidad y carga.

Transparencia: utilicé IA y hubo refinamientos posteriores al primer prototipo. No registré de forma fiable el tiempo activo, por lo que no presento este resultado como una ejecución cronometrada de cuatro horas.

