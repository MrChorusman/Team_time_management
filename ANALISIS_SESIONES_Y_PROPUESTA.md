# 📊 Análisis de Gestión de Sesiones y Roles - Propuesta de Mejora

**Fecha**: 1 de Noviembre de 2025  
**Rama**: `dev/dynamic-location-ux-improvements`

---

## 🔍 Problema Actual Identificado

### 1. **Desincronización entre Frontend y Backend**

**Situación Actual:**
- **Backend**: Usa HTTP-only cookies con Flask-Security-Too (✅ **CORRECTO** para seguridad)
- **Frontend**: Usa `localStorage` para persistir `user` y `employee` (⚠️ **PROBLEMÁTICO**)

**Problema:**
```
┌─────────────────────────────────────────────────────────────┐
│  Flujo Actual (PROBLEMÁTICO)                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Usuario hace login                                      │
│     ├─ Backend: Crea sesión (cookie HTTP-only, TTL: 30 min)│
│     └─ Frontend: Guarda user/employee en localStorage       │
│                                                              │
│  2. Usuario refresca la página (15 min después)             │
│     ├─ AuthContext.checkSession():                          │
│     │   ├─ Encuentra datos en localStorage ✓                │
│     │   └─ NO verifica con backend ✗                        │
│     └─ App continúa con sesión aparentemente válida         │
│                                                              │
│  3. Usuario refresca la página (35 min después)             │
│     ├─ AuthContext.checkSession():                          │
│     │   ├─ Encuentra datos en localStorage ✓                │
│     │   └─ NO verifica con backend ✗                        │
│     ├─ App muestra interfaz como si sesión fuera válida     │
│     └─ Primera API call → 401 UNAUTHORIZED ✗                │
│         └─ Usuario ve error inesperado                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Código Problemático:**
```javascript
// frontend/src/contexts/AuthContext.jsx (líneas 66-82)
const checkSession = async () => {
  try {
    setLoading(true)
    
    // ⚠️ PROBLEMA: Confía ciegamente en localStorage
    const storedUser = localStorage.getItem('user')
    const storedEmployee = localStorage.getItem('employee')
    
    if (storedUser) {
      const user = JSON.parse(storedUser)
      const employee = storedEmployee ? JSON.parse(storedEmployee) : null
      setUser(user)
      setEmployee(employee)
      setLoading(false)
      return  // ❌ RETORNA SIN VERIFICAR CON BACKEND
    }
    
    // Solo verifica con backend si NO hay localStorage
    const response = await authService.checkSession()
    // ...
  }
}
```

### 2. **Endpoints de Sesión Desalineados**

**Backend** (`backend/app/auth.py`):
- `/auth/me` (línea 170): ✅ Existe, requiere `@auth_required()`
- `/check-session` (línea 241): ✅ Existe, NO requiere autenticación

**Frontend** (`frontend/src/services/authService.js`):
- `checkSession()`: Llama a `/auth/me` (línea 27)

**Problema**: 
- `/auth/me` requiere autenticación → Si cookie expiró, devuelve 401
- Frontend NO maneja correctamente el 401 en `checkSession()`

---

## 📚 Mejores Prácticas 2024/2025 (Investigadas)

### ✅ **Estándar para Aplicaciones Web SPA**

1. **NO hacer logout automático en cada refresh**
   - Las sesiones DEBEN persistir entre refrescos
   - Hacer logout en cada refresh destruye la UX
   - **Lo correcto**: Validar sesión en cada carga y hacer logout SI está inválida

2. **Gestión Segura de Sesiones**:
   ```
   ✅ HTTP-only cookies → Tokens de sesión (inmune a XSS)
   ✅ SameSite=Strict → Protección CSRF
   ✅ Secure flag → Solo HTTPS en producción
   ❌ localStorage → NO para tokens/sesiones (vulnerable a XSS)
   ⚠️ localStorage → OK para datos NO sensibles (preferencias UI)
   ```

3. **Validación de Sesión**:
   - **Al cargar la app**: Verificar con backend si sesión es válida
   - **En cada API call**: Manejar 401 → Logout automático
   - **Periódicamente**: Refresh token antes de expiración (opcional)

4. **Validación de Roles**:
   - **Backend**: Verificar roles en CADA endpoint (nunca confiar en frontend)
   - **Frontend**: Verificar roles para UI/UX (ocultar botones, menús)
   - **Principio**: Backend es fuente de verdad, frontend es conveniencia

---

## 🎯 Propuesta de Solución

### **Fase 1: Refactorización de Gestión de Sesiones**

#### **A. Modificar AuthContext para SIEMPRE verificar con backend**

```javascript
// frontend/src/contexts/AuthContext.jsx

const checkSession = async () => {
  try {
    setLoading(true)
    setError(null)
    
    // ✅ SIEMPRE verificar con backend (no confiar en localStorage)
    const response = await authService.checkSession()
    
    if (response.success && response.user) {
      setUser(response.user)
      setEmployee(response.employee || null)
      
      // localStorage solo como caché optimista (no como fuente de verdad)
      localStorage.setItem('user', JSON.stringify(response.user))
      if (response.employee) {
        localStorage.setItem('employee', JSON.stringify(response.employee))
      } else {
        localStorage.removeItem('employee')
      }
    } else {
      // Sesión inválida → Limpiar todo
      await handleInvalidSession()
    }
  } catch (error) {
    console.error('Error verificando sesión:', error)
    
    // Si error 401 → Sesión expirada
    if (error.response?.status === 401) {
      await handleInvalidSession()
    } else {
      // Otros errores (red, servidor) → Intentar usar caché local temporalmente
      // pero marcar como no verificado
      const cachedUser = localStorage.getItem('user')
      if (cachedUser) {
        setUser(JSON.parse(cachedUser))
        setEmployee(JSON.parse(localStorage.getItem('employee') || 'null'))
        // Mostrar advertencia de "sesión no verificada"
        setError('No se pudo verificar la sesión. Reconecta para continuar.')
      } else {
        await handleInvalidSession()
      }
    }
  } finally {
    setLoading(false)
  }
}

const handleInvalidSession = async () => {
  setUser(null)
  setEmployee(null)
  localStorage.removeItem('user')
  localStorage.removeItem('employee')
  localStorage.removeItem('token') // si existe
  // NO navegar aquí, dejar que ProtectedRoute maneje la redirección
}
```

#### **B. Unificar Endpoint de Verificación de Sesión**

```python
# backend/app/auth.py

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Obtiene el usuario actual de la sesión.
    NO requiere @auth_required() para poder devolver 
    respuesta apropiada cuando no hay sesión.
    """
    try:
        if current_user.is_authenticated:
            employee_data = None
            if hasattr(current_user, 'employee') and current_user.employee:
                employee_data = current_user.employee.to_dict()
            
            user_dict = current_user.to_dict()
            
            return jsonify({
                'success': True,
                'user': user_dict,
                'employee': employee_data,
                'session_expires_at': session.get('_expires_at')  # Útil para frontend
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No hay sesión activa'
            }), 401
            
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {e}")
        return jsonify({
            'success': False,
            'message': 'Error verificando sesión'
        }), 500

# Deprecar /check-session (mantener por compatibilidad temporal)
@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """DEPRECATED: Usar /auth/me en su lugar"""
    return get_current_user()
```

#### **C. Interceptor Axios para Manejar 401 Globalmente**

```javascript
// frontend/src/services/apiClient.js

// ... código existente ...

// Interceptor de respuestas
apiClient.interceptors.response.use(
  (response) => {
    // ... logging existente ...
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Si error 401 y NO es del endpoint /auth/me (evitar loop)
    if (error.response?.status === 401 && !originalRequest.url.includes('/auth/me')) {
      console.error('❌ Sesión expirada o inválida')
      
      // Limpiar estado de autenticación
      localStorage.removeItem('user')
      localStorage.removeItem('employee')
      
      // Emitir evento personalizado para que AuthContext reaccione
      window.dispatchEvent(new CustomEvent('session-expired'))
      
      // Redirigir a login
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login?reason=session_expired'
      }
    }
    
    // ... resto del código de error ...
    return Promise.reject(error)
  }
)
```

```javascript
// frontend/src/contexts/AuthContext.jsx

useEffect(() => {
  // Escuchar evento de sesión expirada
  const handleSessionExpired = () => {
    setUser(null)
    setEmployee(null)
    setError('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.')
  }
  
  window.addEventListener('session-expired', handleSessionExpired)
  
  return () => {
    window.removeEventListener('session-expired', handleSessionExpired)
  }
}, [])
```

### **Fase 2: Validación de Roles Robusta**

#### **A. Backend: Decoradores de Roles**

```python
# backend/utils/decorators.py (NUEVO ARCHIVO)

from functools import wraps
from flask import jsonify
from flask_security import current_user, auth_required
import logging

logger = logging.getLogger(__name__)

def roles_required(*required_roles):
    """
    Decorador que verifica que el usuario tenga al menos uno de los roles especificados.
    Debe usarse DESPUÉS de @auth_required()
    
    Uso:
        @auth_bp.route('/admin/settings')
        @auth_required()
        @roles_required('admin')
        def admin_settings():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                logger.warning(f"Usuario no autenticado intentó acceder a {fn.__name__}")
                return jsonify({
                    'success': False,
                    'message': 'Autenticación requerida'
                }), 401
            
            user_roles = [role.name for role in current_user.roles]
            
            if not any(role in user_roles for role in required_roles):
                logger.warning(
                    f"Usuario {current_user.email} (roles: {user_roles}) "
                    f"intentó acceder a {fn.__name__} que requiere roles: {required_roles}"
                )
                return jsonify({
                    'success': False,
                    'message': f'Acceso denegado. Rol requerido: {", ".join(required_roles)}'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def admin_required():
    """Alias para roles_required('admin')"""
    return roles_required('admin')

def manager_or_admin_required():
    """Verifica que el usuario sea manager o admin"""
    return roles_required('admin', 'manager')
```

**Uso en endpoints:**
```python
# backend/app/admin.py

from backend.utils.decorators import admin_required

@admin_bp.route('/settings', methods=['GET'])
@auth_required()
@admin_required()
def get_settings():
    """Solo admins pueden ver configuración"""
    # ...

# backend/app/teams.py

from backend.utils.decorators import manager_or_admin_required

@teams_bp.route('/<int:team_id>/members', methods=['POST'])
@auth_required()
@manager_or_admin_required()
def add_team_member(team_id):
    """Solo managers o admins pueden añadir miembros"""
    # ...
```

#### **B. Frontend: Hook de Roles**

```javascript
// frontend/src/hooks/useRoles.js (NUEVO ARCHIVO)

import { useAuth } from '../contexts/AuthContext'

/**
 * Hook para verificar roles del usuario actual
 * 
 * @returns {Object} - Funciones de verificación de roles
 */
export const useRoles = () => {
  const { user } = useAuth()
  
  const hasRole = (roleName) => {
    if (!user || !user.roles) return false
    return user.roles.includes(roleName)
  }
  
  const hasAnyRole = (...roleNames) => {
    if (!user || !user.roles) return false
    return roleNames.some(role => user.roles.includes(role))
  }
  
  const hasAllRoles = (...roleNames) => {
    if (!user || !user.roles) return false
    return roleNames.every(role => user.roles.includes(role))
  }
  
  const isAdmin = () => hasRole('admin')
  const isManager = () => hasRole('manager')
  const isEmployee = () => hasRole('employee')
  const isViewer = () => hasRole('viewer')
  
  const canManageEmployees = () => hasAnyRole('admin', 'manager')
  const canManageTeams = () => isAdmin()
  const canViewReports = () => hasAnyRole('admin', 'manager', 'employee')
  const canManageSettings = () => isAdmin()
  
  return {
    // Verificaciones básicas
    hasRole,
    hasAnyRole,
    hasAllRoles,
    
    // Roles específicos
    isAdmin,
    isManager,
    isEmployee,
    isViewer,
    
    // Permisos compuestos
    canManageEmployees,
    canManageTeams,
    canViewReports,
    canManageSettings,
    
    // Datos raw
    roles: user?.roles || []
  }
}
```

**Uso en componentes:**
```javascript
// frontend/src/pages/employee/EmployeeRegisterPage.jsx

import { useRoles } from '../../hooks/useRoles'

const EmployeeRegisterPage = () => {
  const navigate = useNavigate()
  const { user, employee, updateEmployee, loading, logout } = useAuth()
  const { isAdmin, canManageEmployees } = useRoles()
  
  // ...
  
  const handleBackToDashboard = () => {
    // Los admin pueden acceder al dashboard sin perfil de empleado
    if (isAdmin()) {
      navigate('/dashboard')
      return
    }
    
    // Para no-admin, verificar si puede acceder al dashboard
    if (!employee || !employee.approved) {
      setShowDashboardWarning(true)
      setTimeout(() => setShowDashboardWarning(false), 5000)
    } else {
      navigate('/dashboard')
    }
  }
  
  // ...
}
```

---

## 📋 Plan de Implementación

### **Sprint 1: Sesiones Robustas** (Prioridad ALTA)

- [ ] 1.1. Modificar `AuthContext.checkSession()` para SIEMPRE verificar con backend
- [ ] 1.2. Unificar endpoint `/auth/me` en backend
- [ ] 1.3. Implementar interceptor Axios para 401 globales
- [ ] 1.4. Agregar manejo de evento `session-expired`
- [ ] 1.5. Pruebas exhaustivas:
  - [ ] Login → Refresh inmediato → Debe mantener sesión
  - [ ] Login → Esperar 35 min → Refresh → Debe logout automático
  - [ ] Login → Cerrar navegador → Abrir → Debe mantener sesión (si cookie no expiró)
  - [ ] Login → API call después de expiración → Debe logout con mensaje claro

### **Sprint 2: Validación de Roles** (Prioridad MEDIA)

- [ ] 2.1. Crear `backend/utils/decorators.py` con decoradores de roles
- [ ] 2.2. Crear hook `useRoles` en frontend
- [ ] 2.3. Aplicar decoradores en endpoints críticos:
  - [ ] Admin endpoints
  - [ ] Manager endpoints
  - [ ] Employee endpoints
- [ ] 2.4. Refactorizar componentes para usar `useRoles`:
  - [ ] `EmployeeRegisterPage.jsx`
  - [ ] `AdminPanel.jsx`
  - [ ] `TeamManagement.jsx`
  - [ ] Navigation components
- [ ] 2.5. Pruebas de roles:
  - [ ] Admin puede acceder a todo
  - [ ] Manager puede gestionar su equipo
  - [ ] Employee solo puede ver su info
  - [ ] Viewer solo puede ver reportes

### **Sprint 3: Seguridad Avanzada** (Prioridad BAJA - Futuro)

- [ ] 3.1. Implementar refresh tokens
- [ ] 3.2. Configurar CORS apropiadamente
- [ ] 3.3. Rate limiting en endpoints de autenticación
- [ ] 3.4. Logging de intentos de acceso no autorizado
- [ ] 3.5. 2FA opcional

---

## ⚠️ Aclaraciones Importantes

### **Sobre "Logout en cada refresh"**

**Requerimiento del usuario**: "Siempre que se refresque la página deberíamos hacer logout"

**Interpretación correcta**: 
- ❌ **NO**: Hacer logout literal en cada F5 (destruiría UX completamente)
- ✅ **SÍ**: Verificar sesión en cada carga y hacer logout **SI está inválida**

**Justificación**:
- Las aplicaciones web modernas (Gmail, Facebook, GitHub) mantienen sesión entre refrescos
- Hacer logout en cada refresh requeriría login constante → UX inaceptable
- Lo estándar es: sesión persiste mientras sea válida, logout cuando expire

### **Sobre localStorage vs Cookies**

**Estado actual**:
- Backend: ✅ HTTP-only cookies (SEGURO)
- Frontend: ⚠️ localStorage para user/employee (PROBLEMÁTICO)

**Solución propuesta**:
- Cookies: Autoridad única de sesión
- localStorage: Solo caché optimista para mejorar UX de carga inicial
- Siempre verificar con backend antes de confiar en localStorage

---

## 🎬 Próximos Pasos Inmediatos

1. **Validar esta propuesta con el usuario**
2. **Implementar Sprint 1 completo** (sesiones robustas)
3. **Probar exhaustivamente** con diferentes escenarios
4. **Commit a rama actual** y preparar para merge
5. **Continuar con Sprint 2** (validación de roles)

---

**Documento creado por**: AI Assistant  
**Para revisión de**: thelittle (Usuario)

