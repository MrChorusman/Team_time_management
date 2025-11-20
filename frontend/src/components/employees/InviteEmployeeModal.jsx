import { useState } from 'react'
import { Mail, User, Send, AlertCircle, CheckCircle2 } from 'lucide-react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../ui/dialog'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Alert, AlertDescription } from '../ui/alert'

const InviteEmployeeModal = ({ isOpen, onClose, onInviteSuccess }) => {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [invitationLink, setInvitationLink] = useState('')

  const validateEmail = (email) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    return emailRegex.test(email)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccess(false)

    // Validar email
    if (!email || !email.trim()) {
      setError('Por favor ingresa un email')
      return
    }

    if (!validateEmail(email.trim())) {
      setError('Por favor ingresa un email válido')
      return
    }

    setLoading(true)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email: email.trim().toLowerCase() })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al enviar la invitación')
      }

      // Éxito
      setSuccess(true)
      setInvitationLink(data.invitation_link || '')
      
      // Notificar al padre
      if (onInviteSuccess) {
        onInviteSuccess(data)
      }

      // Cerrar automáticamente tras enviar
      handleClose()

    } catch (err) {
      console.error('Error invitando empleado:', err)
      setError(err.message || 'Error al enviar la invitación')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setEmail('')
    setError(null)
    setSuccess(false)
    setInvitationLink('')
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Mail className="h-5 w-5 text-white" />
            </div>
            <span>Invitar Empleado</span>
          </DialogTitle>
          <DialogDescription>
            Envía una invitación por email para que un nuevo empleado se una al sistema
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Campo de email */}
          <div className="space-y-2">
            <Label htmlFor="email" className="flex items-center gap-2">
              <User className="h-4 w-4 text-gray-500" />
              Email del empleado
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="empleado@empresa.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading || success}
              autoFocus
              className="w-full"
            />
            <p className="text-sm text-gray-500">
              Recibirá un link de invitación válido por 7 días
            </p>
          </div>

          {/* Mensaje de error */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Mensaje de éxito */}
          {success && (
            <Alert className="border-green-200 bg-green-50 text-green-800">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription>
                <p className="font-semibold">¡Invitación enviada exitosamente!</p>
                <p className="text-sm mt-1">
                  {email} recibirá un email con instrucciones para completar su registro.
                </p>
                {invitationLink && (
                  <div className="mt-3 p-2 bg-white rounded border border-green-200">
                    <p className="text-xs font-semibold mb-1">Link de invitación (modo desarrollo):</p>
                    <p className="text-xs break-all font-mono">{invitationLink}</p>
                  </div>
                )}
              </AlertDescription>
            </Alert>
          )}

          {/* Botones */}
          <div className="flex gap-3 justify-end">
            {success ? (
              <Button
                type="button"
                onClick={handleClose}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                <CheckCircle2 className="w-4 h-4 mr-2" />
                Aceptar
              </Button>
            ) : (
              <>
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
                  disabled={loading}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Enviar Invitación
                    </>
                  )}
                </Button>
              </>
            )}
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default InviteEmployeeModal

