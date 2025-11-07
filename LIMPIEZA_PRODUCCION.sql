-- =====================================================
-- SCRIPT DE LIMPIEZA TOTAL DE PRODUCCIÓN
-- Opción A: Base de datos virgen para cliente nuevo
-- Fecha: 07/11/2025
-- =====================================================

-- ORDEN DE ELIMINACIÓN (respetando foreign keys):

-- 1. Notificaciones (dependen de users)
DELETE FROM notification;

-- 2. Actividades de calendario (dependen de employees)
-- Ya está vacía, pero por completitud:
DELETE FROM calendar_activity;

-- 3. Relaciones roles-usuarios (tabla intermedia)
DELETE FROM roles_users;

-- 4. Empleados (dependen de users y teams)
DELETE FROM employee;

-- 5. Usuarios
DELETE FROM "user";

-- 6. Equipos
DELETE FROM team;

-- 7. Resetear secuencias para que IDs empiecen en 1
ALTER SEQUENCE user_id_seq RESTART WITH 1;
ALTER SEQUENCE employee_id_seq RESTART WITH 1;
ALTER SEQUENCE team_id_seq RESTART WITH 1;
ALTER SEQUENCE notification_id_seq RESTART WITH 1;
ALTER SEQUENCE calendar_activity_id_seq RESTART WITH 1;

-- =====================================================
-- RESULTADO ESPERADO:
-- =====================================================
-- ✅ VACÍAS: user, employee, team, roles_users, notification, calendar_activity
-- ✅ MANTIENEN: role (5), holiday (644), countries (188), autonomous_communities (74), provinces (52), cities (201)
-- ✅ IDs reiniciados: Empiezan desde 1
-- =====================================================

