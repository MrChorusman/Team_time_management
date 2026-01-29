# Nota: Usuarios de Prueba en Producción

**Fecha**: 29 de Enero, 2026

## Problema Identificado

Los usuarios de prueba creados con el script `create_test_users.py` se están creando en la base de datos local, no en producción. Esto causa que las pruebas de regresión automatizadas fallen con error 401 (Credenciales inválidas).

## Solución

Para ejecutar las pruebas de regresión en producción, los usuarios de prueba deben ser creados directamente en la base de datos de producción.

### Opción 1: Ejecutar script directamente contra producción

Asegúrate de que las variables de entorno de producción estén configuradas correctamente antes de ejecutar:

```bash
cd backend
# Verificar que .env.production tiene las credenciales correctas de Supabase
python3 scripts/create_test_users.py
```

### Opción 2: Crear usuarios manualmente en Supabase Dashboard

1. Acceder a Supabase Dashboard
2. Ir a Table Editor → `user`
3. Crear usuario admin:
   - Email: `admin.test@example.com`
   - Password: Hash de `AdminTest123!` usando bcrypt
   - active: `true`
   - confirmed_at: Fecha actual
4. Asignar rol `admin` en tabla `user_roles`
5. Crear perfil de empleado asociado en tabla `employee`

### Opción 3: Usar SQL directo

Ejecutar SQL directamente en Supabase SQL Editor para crear los usuarios.

## Verificación

Una vez creados los usuarios en producción, verificar que el login funciona:

```bash
curl -X POST https://team-time-management.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin.test@example.com","password":"AdminTest123!"}'
```

Debería retornar `{"success": true, ...}`

---

**Nota**: Las pruebas de regresión automatizadas (`regression_tests.py`) requieren que estos usuarios existan en producción para funcionar correctamente.
