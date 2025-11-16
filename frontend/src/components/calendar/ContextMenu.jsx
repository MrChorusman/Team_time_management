import React, { useEffect, useRef } from 'react'
import { Trash2 } from 'lucide-react'

/**
 * ContextMenu - Menú contextual para marcar actividades en el calendario
 * Se activa con click derecho en las celdas del calendario
 */
const ContextMenu = ({ 
  visible, 
  x, 
  y, 
  hasActivity, 
  onSelect, 
  onClose 
}) => {
  const menuRef = useRef(null)

  // Cerrar menú cuando se hace click fuera
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        onClose()
      }
    }

    if (visible) {
      document.addEventListener('mousedown', handleClickOutside)
      document.addEventListener('contextmenu', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('contextmenu', handleClickOutside)
    }
  }, [visible, onClose])

  // Cerrar con tecla Escape
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    if (visible) {
      document.addEventListener('keydown', handleEscape)
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }, [visible, onClose])

  if (!visible) return null

  const menuItems = [
    {
      code: 'V',
      label: 'Vacaciones',
      color: 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100',
      icon: '🟢'
    },
    {
      code: 'A',
      label: 'Ausencias',
      color: 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100',
      icon: '🟡'
    },
    {
      code: 'HLD',
      label: 'Horas Libre Disposición',
      color: 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100',
      icon: '🟢',
      requiresModal: true
    },
    {
      code: 'G',
      label: 'Guardia',
      color: 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100',
      icon: '🔵',
      requiresModal: true
    },
    {
      code: 'F',
      label: 'Formación',
      color: 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100',
      icon: '🟣',
      requiresModal: true
    },
    {
      code: 'C',
      label: 'Permiso/Otro',
      color: 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100',
      icon: '🔵'
    }
  ]

  const handleItemClick = (item) => {
    onSelect(item.code.toLowerCase())
    onClose()
  }

  const handleDelete = () => {
    onSelect('delete')
    onClose()
  }

  return (
    <div
      ref={menuRef}
      className="fixed bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 py-1 z-[9999] min-w-[240px]"
      style={{
        left: `${x}px`,
        top: `${y}px`,
        position: 'fixed'
      }}
    >
      {/* Opciones de actividad */}
      {menuItems.map((item) => (
        <button
          key={item.code}
          onClick={() => handleItemClick(item)}
          className={`w-full px-4 py-2 text-left text-sm flex items-center justify-between transition-colors ${item.color}`}
        >
          <div className="flex items-center space-x-2">
            <span className="text-base">{item.icon}</span>
            <span className="font-medium">{item.code}</span>
            <span>{item.label}</span>
          </div>
          {item.requiresModal && (
            <span className="text-gray-400">→</span>
          )}
        </button>
      ))}

      {/* Separador si hay actividad existente */}
      {hasActivity && (
        <>
          <div className="border-t border-gray-200 my-1"></div>
          <button
            onClick={handleDelete}
            className="w-full px-4 py-2 text-left text-sm flex items-center space-x-2 hover:bg-red-50 text-red-600 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            <span className="font-medium">Eliminar</span>
          </button>
        </>
      )}
    </div>
  )
}

export default ContextMenu

