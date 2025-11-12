# 🔗 Correcciones de Integridad Referencial - Base de Datos

**Fecha**: 12 de Noviembre de 2025  
**Estado**: ✅ Completado

---

## 🎯 Problemas Detectados

### **1. Tabla `roles_users` sin Foreign Keys**
- **Detectado por**: Usuario Miguel
- **Problema**: Tabla many-to-many sin relaciones definidas
- **Riesgo**: Datos huérfanos, inconsistencias, violaciones de integridad

### **2. Tabla `calendar_entries` obsoleta**
- **Detectado por**: Usuario Miguel  
- **Problema**: Tabla duplicada sin uso, sin foreign keys
- **Situación**: 
  - `calendar_entries`: 0 registros, sin FK, **no usada en código** ❌
  - `calendar_activity`: Tabla actual con FK, **usada en producción** ✅

---

## ✅ Soluciones Implementadas

### **Migración 1: `add_foreign_keys_roles_users_clean`**

#### Paso 1: Limpieza de datos huérfanos
```sql
-- Eliminar registros que apuntan a usuarios inexistentes
DELETE FROM roles_users
WHERE user_id NOT IN (SELECT id FROM "user");
```

**Resultado**: 3 registros huérfanos eliminados (users 8, 9, 10)

#### Paso 2: Agregar foreign keys
```sql
ALTER TABLE roles_users 
ADD CONSTRAINT roles_users_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE;

ALTER TABLE roles_users 
ADD CONSTRAINT roles_users_role_id_fkey 
FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE;
```

#### Paso 3: Crear índices
```sql
CREATE INDEX idx_roles_users_user_id ON roles_users(user_id);
CREATE INDEX idx_roles_users_role_id ON roles_users(role_id);
```

**Beneficios:**
- ✅ Integridad referencial garantizada
- ✅ Eliminación en cascada (si se borra un user, sus roles se borran automáticamente)
- ✅ Mejor rendimiento en consultas de roles

---

### **Migración 2: `drop_obsolete_calendar_entries`**

```sql
DROP TABLE IF EXISTS calendar_entries CASCADE;
```

**Razones:**
1. Tabla con 0 registros
2. No usada en ningún archivo de backend
3. Sin foreign keys definidas
4. Duplica funcionalidad de `calendar_activity`

**Tabla activa**: `calendar_activity`
- Columnas: `id`, `employee_id`, `date`, `activity_type`, `hours`, `description`, `start_time`, `end_time`, `created_at`, `updated_at`
- FK: `calendar_activity_employee_id_fkey` → `employee.id`
- Estado: **Productiva y usada**

---

## 📊 Estado Final de Relaciones

### **Tabla: `roles_users`** (many-to-many)
| Columna | Tipo | FK a | Acción al eliminar |
|---------|------|------|-------------------|
| `user_id` | INTEGER | `user.id` | CASCADE |
| `role_id` | INTEGER | `role.id` | CASCADE |

**Índices:**
- `idx_roles_users_user_id`
- `idx_roles_users_role_id`

---

### **Tabla: `role`**
| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | SERIAL | PK |
| `name` | VARCHAR(80) | UNIQUE |
| `description` | VARCHAR(255) | Nullable |
| `created_at` | TIMESTAMP | Default NOW() |
| `updated_at` | TIMESTAMP | Default NOW() |

**Relaciones entrantes:**
- `roles_users.role_id` → CASCADE

---

### **Tabla: `user`**
| Columna principal | FK relacionadas |
|------------------|-----------------|
| `id` (PK) | 8 tablas apuntan aquí |

**Relaciones entrantes (8 tablas):**
1. `roles_users.user_id` → CASCADE
2. `employee.user_id` → ?
3. `notification.user_id` → ?
4. `notification.created_by` → ?
5. `employee_invitation.invited_by` → SET NULL
6. `employee_invitations.invited_by_id` → ?
7. `email_verification_token.user_id` → CASCADE

---

### **Tabla: `calendar_activity`** (ACTIVA)
| Columna | FK a | Acción |
|---------|------|--------|
| `employee_id` | `employee.id` | ? |

**Nota**: Revisar si falta ON DELETE CASCADE en otras tablas.

---

## ⚠️ Recomendaciones Adicionales

### **1. Verificar acciones ON DELETE en otras FKs**
Algunas foreign keys podrían beneficiarse de definir explícitamente la acción:
- `employee.user_id` → ¿CASCADE o RESTRICT?
- `employee.team_id` → ¿CASCADE o SET NULL?
- `calendar_activity.employee_id` → ¿CASCADE o RESTRICT?

### **2. Agregar índices adicionales**
```sql
-- Ya existen en código, verificar en BD:
CREATE INDEX IF NOT EXISTS idx_employee_user_id ON employee(user_id);
CREATE INDEX IF NOT EXISTS idx_employee_team_id ON employee(team_id);
CREATE INDEX IF NOT EXISTS idx_calendar_activity_employee_id ON calendar_activity(employee_id);
CREATE INDEX IF NOT EXISTS idx_calendar_activity_date ON calendar_activity(date);
```

---

## 🧪 Verificación Post-Migración

### **Test 1: Verificar FKs de roles_users**
```sql
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_name = 'roles_users';
```

**Resultado esperado**: 2 filas (user_id y role_id)

### **Test 2: Verificar que calendar_entries no existe**
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name = 'calendar_entries';
```

**Resultado esperado**: 0 filas

### **Test 3: Integridad referencial roles_users**
```sql
-- Esto debería funcionar sin errores:
SELECT u.id, u.email, r.name as role_name
FROM "user" u
JOIN roles_users ru ON u.id = ru.user_id
JOIN role r ON ru.role_id = r.id;
```

**Resultado esperado**: Todos los usuarios con sus roles (solo admin@teamtime.com actualmente)

---

## ✅ Conclusión

**Base de datos corregida:**
- ✅ `roles_users` ahora tiene foreign keys correctas
- ✅ Tabla obsoleta `calendar_entries` eliminada
- ✅ Datos huérfanos limpiados
- ✅ Integridad referencial garantizada

**Próximos pasos:**
- Continuar con prueba del sistema de verificación de email
- Opcional: Revisar otras FKs para agregar ON DELETE CASCADE donde aplique

