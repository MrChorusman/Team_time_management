import { useState } from 'react'
import { Mail, Send, X, CheckCircle, AlertCircle } from 'lucide-react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../ui/dialog'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Textarea } from '../ui/textarea'
import { Alert, AlertDescription } from '../ui/alert'

const InviteEmployeeModal = ({ open, onClose, onSuccess }) => {
  const [email, setEmail] = useState('')
  const [customMessage, setCustomMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [emailError, setEmailError] = useState(null)

  // Validar email en tiempo real
  const validateEmail = (value) => {
    const trimmed = value.trim()
    if (!trimmed) {
      setEmailError(null)
      return
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(trimmed)) {
      setEmailError('Email inválido')
    } else {
      setEmailError(null)
    }
  }

  const handleEmailChange = (e) => {
    const value = e.target.value
    setEmail(value)
    validateEmail(value)
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validaciones
    if (!email.trim()) {
      setError('El email es requerido')
      return
    }

    if (emailError) {
      setError('Por favor corrige los errores antes de enviar')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          message: customMessage.trim() || null
        })
      })

      const data = await response.json()

      if (response.ok) {
        setSuccess(true)
        setEmail('')
        setCustomMessage('')
        
        // Esperar 2s para mostrar el mensaje de éxito
        setTimeout(() => {
          onSuccess && onSuccess(data.invitation)
          handleClose()
        }, 2000)
      } else {
        setError(data.error || 'Error al enviar la invitación')
      }
    } catch (err) {
      console.error('Error enviando invitación:', err)
      setError('Error de conexión. Por favor intenta nuevamente.')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    if (!loading) {
      setEmail('')
      setCustomMessage('')
      setError(null)
      setSuccess(false)
      setEmailError(null)
      onClose()
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <div className="h-10 w-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Mail className="h-5 w-5 text-white" />
            </div>
            <span>Invitar Empleado</span>
          </DialogTitle>
          <DialogDescription>
            Envía una invitación por email para que un nuevo empleado se una al equipo
          </DialogDescription>
        </DialogHeader>

        {success ? (
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <AlertDescription className="text-green-800 ml-2">
              <strong>¡Invitación enviada!</strong>
              <p className="mt-1">
                Se ha enviado un email a <strong>{email}</strong> con las instrucciones para completar su registro.
              </p>
            </AlertDescription>
          </Alert>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">
                Email del empleado <span className="text-red-500">*</span>
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  id="email"
                  type="email"
                  placeholder="nombre@empresa.com"
                  value={email}
                  onChange={handleEmailChange}
                  className={`pl-10 ${emailError ? 'border-red-300 focus:border-red-500' : ''}`}
                  disabled={loading}
                  required
                />
              </div>
              {emailError && (
                <p className="text-sm text-red-600 flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  {emailError}
                </p>
              )}
            </div>

            {/* Mensaje personalizado */}
            <div className="space-y-2">
              <Label htmlFor="message" className="text-sm font-medium">
                Mensaje personalizado (opcional)
              </Label>
              <Textarea
                id="message"
                placeholder="Ej: ¡Hola! Nos alegra que te unas al equipo. Completa tu registro para empezar..."
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                rows={4}
                className="resize-none"
                disabled={loading}
                maxLength={500}
              />
              <p className="text-xs text-gray-500 text-right">
                {customMessage.length}/500 caracteres
              </p>
            </div>

            {/* Error */}
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="ml-2">{error}</AlertDescription>
              </Alert>
            )}

            {/* Info */}
            <Alert className="bg-blue-50 border-blue-200">
              <AlertCircle className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800 text-sm ml-2">
                El empleado recibirá un email con un enlace único para completar su registro. El enlace expirará en 48 horas.
              </AlertDescription>
            </Alert>

            {/* Botones */}
            <div className="flex justify-end space-x-3 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={loading}
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                disabled={loading || !!emailError || !email.trim()}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                    Enviando...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Enviar Invitación
                  </>
                )}
              </Button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}

export default InviteEmployeeModal

