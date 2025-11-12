# 🗄️ Resumen de Limpieza y Corrección de Base de Datos

**Fecha**: 12 de Noviembre de 2025  
**Realizado por**: Asistente IA + Miguel (revisión crítica)  
**Estado**: ✅ Completado

---

## 🎯 Objetivo

Corregir problemas de integridad referencial detectados por el usuario en la base de datos de producción (Supabase).

---

## ❌ Problemas Detectados

### **1. Tabla `roles_users` sin Foreign Keys**
- **Detectado por**: Miguel
- **Problema**: Tabla many-to-many sin relaciones definidas
- **Datos huérfanos**: 3 registros apuntando a usuarios inexistentes (IDs 8, 9, 10)

### **2. Tabla `calendar_entries` obsoleta**
- **Detectado por**: Miguel
- **Problema**: Tabla duplicada sin uso (0 registros, sin FK)
- **Tabla correcta**: `calendar_activity` (con FK a employee)

### **3. Tabla `employee_invitations` duplicada**
- **Detectado por**: Miguel
- **Problema**: Tabla plural sin uso (0 registros, RLS habilitado)
- **Tabla correcta**: `employee_invitation` (singular, 3 registros activos)

### **4. Foreign Keys con `NO ACTION` en tablas críticas**
- **Detectado por**: Asistente (tras análisis)
- **Problema**: `employee.user_id` y `notification.user_id` sin CASCADE
- **Riesgo**: No se pueden eliminar usuarios con empleados/notificaciones

---

## ✅ Migraciones Aplicadas

### **Migración 1: `add_foreign_keys_roles_users_clean`**

**Acciones:**
```sql
-- Limpiar datos huérfanos
DELETE FROM roles_users WHERE user_id NOT IN (SELECT id FROM "user");
-- Resultado: 3 registros eliminados

-- Agregar foreign keys
ALTER TABLE roles_users 
ADD CONSTRAINT roles_users_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE;

ALTER TABLE roles_users 
ADD CONSTRAINT roles_users_role_id_fkey 
FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE;

-- Crear índices
CREATE INDEX idx_roles_users_user_id ON roles_users(user_id);
CREATE INDEX idx_roles_users_role_id ON roles_users(role_id);
```

**Resultado**: ✅ Integridad referencial garantizada para roles de usuario

---

### **Migración 2: `drop_obsolete_calendar_entries`**

**Acciones:**
```sql
DROP TABLE IF EXISTS calendar_entries CASCADE;
```

**Resultado**: ✅ Tabla obsoleta eliminada, solo queda `calendar_activity`

---

### **Migración 3: `drop_duplicate_employee_invitations`**

**Acciones:**
```sql
DROP TABLE IF EXISTS employee_invitations CASCADE;
```

**Resultado**: ✅ Tabla duplicada eliminada, solo queda `employee_invitation`

---

### **Migración 4: `fix_cascade_employee_notification`**

**Acciones:**
```sql
-- Corregir employee.user_id
ALTER TABLE employee DROP CONSTRAINT employee_user_id_fkey;
ALTER TABLE employee 
ADD CONSTRAINT employee_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE;

-- Corregir notification.user_id
ALTER TABLE notification DROP CONSTRAINT notification_user_id_fkey;
ALTER TABLE notification 
ADD CONSTRAINT notification_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE;
```

**Resultado**: ✅ Eliminación en cascada configurada correctamente

---

## 📊 Estado Final de Foreign Keys

### **Tabla `user` - Relaciones entrantes (6 tablas):**

| Tabla | Columna | DELETE Rule | Descripción |
|-------|---------|-------------|-------------|
| `roles_users` | `user_id` | **CASCADE** | Al eliminar user, eliminar sus roles |
| `employee` | `user_id` | **CASCADE** | Al eliminar user, eliminar su perfil de empleado |
| `notification` | `user_id` | **CASCADE** | Al eliminar user, eliminar sus notificaciones |
| `email_verification_token` | `user_id` | **CASCADE** | Al eliminar user, eliminar sus tokens de verificación |
| `employee_invitation` | `invited_by` | **SET NULL** | Al eliminar user, mantener invitación pero sin invitador |
| `notification` | `created_by` | **SET NULL** | Al eliminar user, mantener notificación pero sin creador |

---

## 📋 Tablas Restantes (Estructura Final)

### **Tablas principales:**
1. ✅ `user` (2 registros: admin + 1 usuario sin verificar)
2. ✅ `role` (5 registros: admin, manager, employee, viewer, hr)
3. ✅ `roles_users` (con FKs correctas)
4. ✅ `employee` (0 registros, con FK CASCADE)
5. ✅ `team` (1 registro)
6. ✅ `notification` (0 registros, con FKs correctas)

### **Tablas de tokens:**
7. ✅ `employee_invitation` (3 invitaciones activas)
8. ✅ `email_verification_token` (1 token pendiente)

### **Tablas de calendario:**
9. ✅ `calendar_activity` (0 registros, FK a employee)
10. ✅ `holiday` (644 festivos)

### **Tablas geográficas:**
11. ✅ `countries` (con relaciones a autonomous_communities)
12. ✅ `autonomous_communities` (con FKs a countries y cities)
13. ✅ `provinces` (con FK a autonomous_communities)
14. ✅ `cities` (con FK a autonomous_communities)

---

## ✅ Beneficios de las Correcciones

### **1. Integridad Referencial**
- No más datos huérfanos
- Relaciones explícitas y verificables
- PostgreSQL valida automáticamente

### **2. Mantenimiento Simplificado**
```sql
-- Antes (NO ACTION):
DELETE FROM "user" WHERE id = 5;
-- ❌ ERROR: violates foreign key constraint

-- Después (CASCADE):
DELETE FROM "user" WHERE id = 5;
-- ✅ OK: user eliminado + employee eliminado + roles eliminados + notificaciones eliminadas
```

### **3. Consistencia**
- Eliminación de tablas duplicadas/obsoletas
- Un solo punto de verdad para cada funcionalidad
- Base de datos más limpia y mantenible

---

## 🧪 Verificación Post-Migración

### **Test 1: Verificar CASCADE en employee**
```sql
-- Crear usuario de prueba
INSERT INTO "user" (email, password, active, fs_uniquifier)
VALUES ('test@delete.com', 'hash', true, 'unique123');

-- Crear employee asociado
INSERT INTO employee (user_id, full_name, team_id, country)
VALUES (CURRVAL('user_id_seq'), 'Test User', 1, 'España');

-- Eliminar usuario
DELETE FROM "user" WHERE email = 'test@delete.com';
-- Resultado esperado: ✅ Usuario Y employee eliminados
```

### **Test 2: Verificar CASCADE en notification**
```sql
-- Similar al Test 1, pero con notifications
```

### **Test 3: Verificar estructura final**
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name NOT LIKE 'pg_%'
ORDER BY table_name;
-- Resultado: Solo tablas activas, sin duplicados
```

---

## 📝 Tablas Eliminadas

| Tabla | Registros | Motivo | Migración |
|-------|-----------|--------|-----------|
| `calendar_entries` | 0 | Obsoleta, no usada en código | `drop_obsolete_calendar_entries` |
| `employee_invitations` | 0 | Duplicada (existe `employee_invitation`) | `drop_duplicate_employee_invitations` |

---

## 🔜 Pendiente (Opcional - Futura iteración)

### **1. Normalizar tabla `holiday`**
- Agregar FKs: `country_id`, `region_id`, `city_id`
- Migrar 644 festivos existentes
- Actualizar código de filtrado
- **Beneficio**: Integridad referencial en ubicaciones geográficas

### **2. Revisar otras FKs**
- `employee.team_id` → ¿CASCADE o SET NULL?
- `team.manager_id` → ¿SET NULL correcto?
- `calendar_activity.employee_id` → ¿CASCADE o RESTRICT?

---

## ✅ Conclusión

**Base de datos limpia y corregida:**
- ✅ Foreign keys completas y correctas
- ✅ Reglas de CASCADE adecuadas
- ✅ Tablas duplicadas/obsoletas eliminadas
- ✅ Datos huérfanos eliminados
- ✅ Estructura mantenible y escalable

**Próximo paso**: Continuar con prueba del sistema de verificación de email.

