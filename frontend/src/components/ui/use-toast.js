// Hook simple para mostrar toasts
// Usando el sistema de notificaciones nativo del navegador por ahora

export const useToast = () => {
  const toast = ({ title, description, variant = "default" }) => {
    // Si el navegador soporta notificaciones, usarlas
    if ("Notification" in window && Notification.permission === "granted") {
      new Notification(title, {
        body: description,
        icon: variant === "destructive" ? "❌" : "✅"
      })
    } else {
      // Fallback a console y alert visual
      console.log(`[TOAST ${variant}]`, title, description)
      
      // Crear elemento de toast visual
      const toastElement = document.createElement('div')
      toastElement.className = `fixed top-4 right-4 z-50 max-w-md p-4 rounded-lg shadow-lg transition-all duration-300 ${
        variant === "destructive" 
          ? "bg-red-100 border-2 border-red-300 text-red-900" 
          : "bg-green-100 border-2 border-green-300 text-green-900"
      }`
      toastElement.innerHTML = `
        <div class="font-bold mb-1">${title}</div>
        <div class="text-sm">${description}</div>
      `
      document.body.appendChild(toastElement)
      
      // Eliminar después de 3 segundos
      setTimeout(() => {
        toastElement.style.opacity = '0'
        setTimeout(() => {
          document.body.removeChild(toastElement)
        }, 300)
      }, 3000)
    }
  }

  return { toast }
}
