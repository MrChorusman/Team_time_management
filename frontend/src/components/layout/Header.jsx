import { useState } from 'react'
import { 
  Menu, 
  Bell, 
  Sun, 
  Moon, 
  Search,
  ChevronDown,
  User,
  Settings,
  LogOut
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { useNotifications } from '../../contexts/NotificationContext'
import { useTheme } from '../../contexts/ThemeContext'
import { Button } from '../ui/button'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import { Badge } from '../ui/badge'
import { cn } from '@/lib/utils.js'

const Header = ({ onMenuClick }) => {
  const { user, employee, logout } = useAuth()
  const { unreadCount, summary, notifications } = useNotifications()
  const { theme, toggleTheme } = useTheme()
  const [searchQuery, setSearchQuery] = useState('')

  const handleLogout = async () => {
    await logout()
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Buenos días'
    if (hour < 18) return 'Buenas tardes'
    return 'Buenas noches'
  }

  const getUserDisplayName = () => {
    if (employee?.full_name) {
      return employee.full_name
    }
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`
    }
    return user?.email || 'Usuario'
  }

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Lado izquierdo */}
        <div className="flex items-center space-x-4">
          {/* Botón de menú móvil */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onMenuClick}
            className="lg:hidden"
          >
            <Menu className="w-5 h-5" />
          </Button>

          {/* Saludo y título */}
          <div className="hidden md:block">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              {getGreeting()}, {getUserDisplayName().split(' ')[0]}
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {new Date().toLocaleDateString('es-ES', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
        </div>

        {/* Barra de búsqueda central */}
        <div className="hidden lg:flex flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Buscar empleados, equipos..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Lado derecho */}
        <div className="flex items-center space-x-3">
          {/* Botón de búsqueda móvil */}
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
          >
            <Search className="w-5 h-5" />
          </Button>

          {/* Toggle de tema */}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleTheme}
            className="relative"
          >
            {theme === 'dark' ? (
              <Sun className="w-5 h-5" />
            ) : (
              <Moon className="w-5 h-5" />
            )}
          </Button>

          {/* Notificaciones */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <Badge 
                    variant="destructive" 
                    className="absolute -top-1 -right-1 px-1 min-w-[1.25rem] h-5 text-xs"
                  >
                    {unreadCount > 99 ? '99+' : unreadCount}
                  </Badge>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel className="flex items-center justify-between">
                <span>Notificaciones</span>
                {unreadCount > 0 && (
                  <Badge variant="secondary" className="text-xs">
                    {unreadCount} nuevas
                  </Badge>
                )}
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              
              {notifications.length > 0 ? (
                <>
                  {notifications.slice(0, 5).map((notification) => (
                    <DropdownMenuItem key={notification.id} className="flex-col items-start p-3">
                      <div className="flex items-start justify-between w-full">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {notification.title}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {notification.message}
                          </p>
                        </div>
                        {!notification.read && (
                          <div className="w-2 h-2 bg-blue-600 rounded-full ml-2 mt-1" />
                        )}
                      </div>
                      <p className="text-xs text-gray-400 mt-2">
                        {new Date(notification.created_at).toLocaleDateString('es-ES')}
                      </p>
                    </DropdownMenuItem>
                  ))}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="text-center text-blue-600 hover:text-blue-700">
                    Ver todas las notificaciones
                  </DropdownMenuItem>
                </>
              ) : (
                <DropdownMenuItem disabled className="text-center text-gray-500">
                  No hay notificaciones
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Menú de usuario */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center space-x-2 px-3">
                <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {getUserDisplayName()}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {employee?.team?.name || 'Sin equipo'}
                  </p>
                </div>
                <ChevronDown className="w-4 h-4 text-gray-500" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium">{getUserDisplayName()}</p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              
              <DropdownMenuItem className="flex items-center">
                <User className="w-4 h-4 mr-2" />
                Mi Perfil
              </DropdownMenuItem>
              
              <DropdownMenuItem className="flex items-center">
                <Settings className="w-4 h-4 mr-2" />
                Configuración
              </DropdownMenuItem>
              
              <DropdownMenuSeparator />
              
              <DropdownMenuItem 
                className="flex items-center text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                onClick={handleLogout}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Cerrar Sesión
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Información de estado del empleado */}
      {employee && !employee.approved && (
        <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                Tu registro de empleado está pendiente de aprobación por tu manager.
              </p>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}

export default Header
