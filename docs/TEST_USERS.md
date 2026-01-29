# Usuarios de Prueba - Team Time Management

**Fecha de creación**: 29 de Enero, 2026  
**Propósito**: Pruebas de regresión y validación de funcionalidades

---

## 👤 Usuario Administrador

**Email**: `admin.test@example.com`  
**Password**: `AdminTest123!`  
**Rol**: `admin`  
**Perfil de Empleado**: Sí (Admin Test User)  
**Equipo**: Equipo de Prueba  
**Ubicación**: Madrid, España

**Permisos**:
- Acceso completo a todas las funcionalidades
- Gestión de empleados y equipos
- Acceso a panel de administración
- Ver calendarios de todos los empleados
- Crear/editar/eliminar actividades de cualquier empleado

---

## 👤 Usuario Empleado

**Email**: `employee.test@example.com`  
**Password**: `EmployeeTest123!`  
**Rol**: `employee`  
**Perfil de Empleado**: Sí (Employee Test User)  
**Equipo**: Equipo de Prueba  
**Ubicación**: Barcelona, España

**Permisos**:
- Acceso a dashboard personal
- Ver su propio calendario
- Crear/editar/eliminar sus propias actividades
- Ver notificaciones personales
- Ver su perfil personal

---

## ⚠️ IMPORTANTE

- Estos usuarios son solo para pruebas y no deben usarse en producción real
- Las contraseñas son simples intencionalmente para facilitar pruebas
- Los usuarios pueden ser eliminados y recreados según necesidad
- No usar estos usuarios para datos reales de producción

---

## 🔄 Recrear Usuarios

Para recrear los usuarios de prueba, ejecutar:

```bash
cd backend
python3 scripts/create_test_users.py
```

El script es idempotente: si los usuarios ya existen, actualizará sus contraseñas.

---

**Última actualización**: 29 de Enero, 2026
