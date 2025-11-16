import React, { useState, useEffect } from 'react'
import { X, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'

/**
 * ActivityModal - Modal para crear actividades con diferentes variantes
 * 
 * Variantes:
 * 1. Simple (V, A, C): Solo notas opcionales
 * 2. Con horas (HLD, F): Horas + notas opcionales
 * 3. Guardia (G): Horario inicio/fin + cálculo automático + notas opcionales
 */
const ActivityModal = ({ 
  visible, 
  activityType, 
  date,
  employeeName,
  onSave, 
  onCancel 
}) => {
  const [hours, setHours] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [calculatedHours, setCalculatedHours] = useState(0)
  const [notes, setNotes] = useState('')
  const [error, setError] = useState('')

  // Información de tipos de actividad
  const activityInfo = {
    'vacation': { 
      icon: '🟢', 
      label: 'Vacaciones', 
      color: 'green',
      variant: 'simple'
    },
    'sick_leave': { 
      icon: '🟡', 
      label: 'Ausencias', 
      color: 'yellow',
      variant: 'simple'
    },
    'hld': { 
      icon: '🟢', 
      label: 'HLD - Horas Libre Disposición', 
      color: 'green',
      variant: 'hours'
    },
    'guard': { 
      icon: '🔵', 
      label: 'Guardia', 
      color: 'blue',
      variant: 'guard'
    },
    'training': { 
      icon: '🟣', 
      label: 'Formación', 
      color: 'purple',
      variant: 'hours'
    },
    'other': { 
      icon: '🔵', 
      label: 'Permiso/Otro', 
      color: 'sky',
      variant: 'simple'
    }
  }

  const currentActivity = activityInfo[activityType] || activityInfo['other']

  // Calcular horas de guardia automáticamente
  useEffect(() => {
    if (activityType === 'guard' && startTime && endTime) {
      const calculated = calculateGuardHours(startTime, endTime)
      setCalculatedHours(calculated)
    }
  }, [startTime, endTime, activityType])

  // Limpiar formulario cuando cambia el tipo de actividad
  useEffect(() => {
    setHours('')
    setStartTime('')
    setEndTime('')
    setCalculatedHours(0)
    setNotes('')
    setError('')
  }, [activityType, visible])

  const calculateGuardHours = (start, end) => {
    if (!start || !end) return 0

    const [startHour, startMin] = start.split(':').map(Number)
    const [endHour, endMin] = end.split(':').map(Number)

    let startMinutes = startHour * 60 + startMin
    let endMinutes = endHour * 60 + endMin

    // Si el horario de fin es menor que el de inicio, cruzó medianoche
    if (endMinutes < startMinutes) {
      endMinutes += 24 * 60 // Añadir 24 horas
    }

    const diffMinutes = endMinutes - startMinutes
    return parseFloat((diffMinutes / 60).toFixed(2))
  }

  const validateForm = () => {
    setError('')

    // Validar horas para HLD y Formación
    if (currentActivity.variant === 'hours') {
      const hoursNum = parseFloat(hours)
      if (!hours || isNaN(hoursNum)) {
        setError('Debes ingresar las horas')
        return false
      }
      if (hoursNum <= 0 || hoursNum > 12) {
        setError('Las horas deben estar entre 0.5 y 12')
        return false
      }
    }

    // Validar guardias
    if (currentActivity.variant === 'guard') {
      if (!startTime || !endTime) {
        setError('Debes ingresar horario de inicio y fin')
        return false
      }
      if (calculatedHours <= 0) {
        setError('El horario de fin debe ser posterior al de inicio')
        return false
      }
      if (calculatedHours > 24) {
        setError('La guardia no puede durar más de 24 horas')
        return false
      }
    }

    return true
  }

  const handleSave = () => {
    if (!validateForm()) return

    const activityData = {
      activityType,
      notes: notes.trim(),
      date
    }

    // Agregar datos específicos según variante
    if (currentActivity.variant === 'hours') {
      activityData.hours = parseFloat(hours)
    } else if (currentActivity.variant === 'guard') {
      activityData.hours = calculatedHours
      activityData.startTime = startTime
      activityData.endTime = endTime
    }

    onSave(activityData)
  }

  const formatDate = (dateString) => {
    const d = new Date(dateString)
    return d.toLocaleDateString('es-ES', { 
      day: 'numeric', 
      month: 'long', 
      year: 'numeric' 
    })
  }

  if (!visible) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        {/* Header */}
        <div className={`px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-${currentActivity.color}-50`}>
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{currentActivity.icon}</span>
            <h3 className="text-lg font-semibold text-gray-900">
              {currentActivity.label}
            </h3>
          </div>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-4 space-y-4">
          {/* Fecha */}
          <div>
            <Label className="text-sm text-gray-600">Fecha</Label>
            <p className="text-sm font-medium text-gray-900">{formatDate(date)}</p>
            {employeeName && (
              <p className="text-xs text-gray-500 mt-1">Para: {employeeName}</p>
            )}
            {/* Aviso si la fecha es pasada */}
            {date && new Date(date + 'T00:00:00') < new Date(new Date().setHours(0, 0, 0, 0)) && (
              <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
                <p className="text-xs text-yellow-800">
                  ⚠️ Esta es una fecha pasada. Se permitirá marcar para ajustar el calendario.
                </p>
              </div>
            )}
          </div>

          {/* Variante: Horas (HLD, Formación) */}
          {currentActivity.variant === 'hours' && (
            <div>
              <Label htmlFor="hours">¿Cuántas horas?</Label>
              <div className="flex items-center space-x-2 mt-1">
                <Input
                  id="hours"
                  type="number"
                  step="0.5"
                  min="0.5"
                  max="12"
                  value={hours}
                  onChange={(e) => setHours(e.target.value)}
                  placeholder="2"
                  className="w-24"
                  autoFocus
                />
                <span className="text-sm text-gray-600">horas</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Entre 0.5 y 12 horas
              </p>
            </div>
          )}

          {/* Variante: Guardia (horario inicio/fin) */}
          {currentActivity.variant === 'guard' && (
            <div className="space-y-3">
              <div>
                <Label htmlFor="startTime">Horario de inicio</Label>
                <div className="flex items-center space-x-2 mt-1">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <Input
                    id="startTime"
                    type="time"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="flex-1"
                    autoFocus
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="endTime">Horario de fin</Label>
                <div className="flex items-center space-x-2 mt-1">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <Input
                    id="endTime"
                    type="time"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="flex-1"
                  />
                </div>
              </div>

              {/* Duración calculada */}
              {calculatedHours > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3">
                  <p className="text-sm font-semibold text-blue-900">
                    ⚡ Duración calculada: {calculatedHours} horas
                  </p>
                  {calculatedHours > 12 && (
                    <p className="text-xs text-blue-700 mt-1">
                      ℹ️ Guardia de {calculatedHours}h (incluye cruce de medianoche)
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Campo de notas (para TODAS las variantes) */}
          <div>
            <Label htmlFor="notes">Motivo (opcional)</Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder={
                activityType === 'vacation' ? 'Ej: Vacaciones familiares' :
                activityType === 'sick_leave' ? 'Ej: Cita médica' :
                activityType === 'hld' ? 'Ej: Trámites DNI' :
                activityType === 'guard' ? 'Ej: Guardia programada' :
                activityType === 'training' ? 'Ej: Curso de React' :
                'Ej: Asuntos personales'
              }
              rows={2}
              className="resize-none"
            />
            <p className="text-xs text-gray-500 mt-1">
              Esta nota aparecerá al pasar el cursor sobre la actividad
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
          <Button
            variant="outline"
            onClick={onCancel}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleSave}
          >
            Guardar
          </Button>
        </div>
      </div>
    </div>
  )
}

export default ActivityModal

