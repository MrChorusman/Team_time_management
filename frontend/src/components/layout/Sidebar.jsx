import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Calendar, 
  Users, 
  UsersRound, 
  FileText, 
  Bell, 
  Settings, 
  ChevronLeft,
  ChevronRight,
  User,
  Shield,
  LogOut
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { useNotifications } from '../../contexts/NotificationContext'
import { Button } from '../ui/button'
import { cn } from '../../lib/utils'

const Sidebar = ({ isOpen, onToggle }) => {
  const location = useLocation()
  const { user, employee, logout, isAdmin, isManager, canManageEmployees } = useAuth()
  const { unreadCount } = useNotifications()

  // Configuración de elementos del menú
  const menuItems = [
    {
      title: 'Dashboard',
      icon: LayoutDashboard,
      path: '/dashboard',
      show: true
    },
    {
      title: 'Calendario',
      icon: Calendar,
      path: '/calendar',
      show: employee?.approved
    },
    {
      title: 'Empleados',
      icon: Users,
      path: '/employees',
      show: canManageEmployees() || employee?.approved
    },
    {
      title: 'Equipos',
      icon: UsersRound,
      path: '/teams',
      show: canManageEmployees() || employee?.approved
    },
    {
      title: 'Reportes',
      icon: FileText,
      path: '/reports',
      show: employee?.approved
    },
    {
      title: 'Notificaciones',
      icon: Bell,
      path: '/notifications',
      show: true,
      badge: unreadCount > 0 ? unreadCount : null
    }
  ]

  const adminItems = [
    {
      title: 'Administración',
      icon: Shield,
      path: '/admin',
      show: isAdmin()
    }
  ]

  const profileItems = [
    {
      title: 'Mi Perfil',
      icon: User,
      path: '/profile',
      show: true
    }
  ]

  const isActive = (path) => {
    return location.pathname === path
  }

  const handleLogout = async () => {
    await logout()
  }

  return (
    <>
      {/* Overlay para móvil */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}
      
      {/* Sidebar */}
      <div className={cn(
        'fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        {/* Header del sidebar */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">TTM</span>
            </div>
            <span className="font-semibold text-gray-900 dark:text-white">
              Team Time Management
            </span>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="lg:hidden"
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
        </div>

        {/* Información del usuario */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {employee?.full_name || user?.email}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                {employee?.team?.name || 'Sin equipo asignado'}
              </p>
            </div>
          </div>
          
          {/* Estado del empleado */}
          {employee && (
            <div className="mt-2">
              <span className={cn(
                'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                employee.approved 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
              )}>
                {employee.approved ? 'Aprobado' : 'Pendiente de aprobación'}
              </span>
            </div>
          )}
        </div>

        {/* Navegación principal */}
        <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
          {/* Elementos principales */}
          <div className="space-y-1">
            {menuItems.filter(item => item.show).map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                    isActive(item.path)
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                  )}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  <span className="flex-1">{item.title}</span>
                  {item.badge && (
                    <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
                      {item.badge > 99 ? '99+' : item.badge}
                    </span>
                  )}
                </Link>
              )
            })}
          </div>

          {/* Separador */}
          {adminItems.some(item => item.show) && (
            <div className="border-t border-gray-200 dark:border-gray-700 my-4" />
          )}

          {/* Elementos de administración */}
          <div className="space-y-1">
            {adminItems.filter(item => item.show).map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                    isActive(item.path)
                      ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                  )}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  <span className="flex-1">{item.title}</span>
                </Link>
              )
            })}
          </div>
        </nav>

        {/* Footer del sidebar */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-1">
          {/* Perfil */}
          {profileItems.filter(item => item.show).map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                  isActive(item.path)
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                )}
              >
                <Icon className="w-5 h-5 mr-3" />
                <span className="flex-1">{item.title}</span>
              </Link>
            )
          })}
          
          {/* Cerrar sesión */}
          <button
            onClick={handleLogout}
            className="w-full flex items-center px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 rounded-lg transition-colors duration-200"
          >
            <LogOut className="w-5 h-5 mr-3" />
            <span className="flex-1 text-left">Cerrar Sesión</span>
          </button>
        </div>
      </div>
    </>
  )
}

export default Sidebar
