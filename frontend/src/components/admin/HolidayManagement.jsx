import { useState, useEffect } from 'react'
import { RefreshCw, Calendar, AlertCircle, CheckCircle, Loader2, Info, AlertTriangle } from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Alert, AlertDescription } from '../ui/alert'
import { useToast } from '../ui/use-toast'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Badge } from '../ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../ui/dialog'

const HolidayManagement = () => {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [year, setYear] = useState(new Date().getFullYear())
  const [statistics, setStatistics] = useState(null)
  const [loadingStats, setLoadingStats] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(null)
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)

  useEffect(() => {
    loadStatistics()
  }, [year])

  const loadStatistics = async () => {
    try {
      setLoadingStats(true)
      const token = localStorage.getItem('auth_token') || localStorage.getItem('token')
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL}/holidays/statistics?year=${year}`, {
        credentials: 'include',
        headers: {
          'Authorization': token ? `Bearer ${token}` : undefined,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setStatistics(data.statistics)
        }
      }
    } catch (error) {
      console.error('Error cargando estadísticas:', error)
    } finally {
      setLoadingStats(false)
    }
  }

  const handleRefreshAll = () => {
    setShowConfirmDialog(true)
  }

  const confirmRefreshAll = async () => {
    setShowConfirmDialog(false)
    setLoading(true)
    try {
      const token = localStorage.getItem('auth_token') || localStorage.getItem('token')
      const headers = {
        'Content-Type': 'application/json'
      }
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL}/holidays/refresh-all`, {
        method: 'POST',
        credentials: 'include',
        headers,
        body: JSON.stringify({ 
          year,
          clean_before_load: true  // Siempre limpiar antes de cargar para evitar festivos obsoletos
        })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        toast({
          title: "✅ Festivos recargados",
          description: `Se han cargado ${data.results.total_loaded} festivos para ${year}`,
        })
        
        setLastRefresh({
          year,
          timestamp: new Date(),
          results: data.results
        })
        
        // Recargar estadísticas
        await loadStatistics()
      } else {
        toast({
          title: "❌ Error",
          description: data.message || "No se pudieron recargar los festivos",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('Error recargando festivos:', error)
      toast({
        title: "❌ Error",
        description: "Error de conexión al recargar festivos",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="w-5 h-5 mr-2" />
            Gestión de Festivos
          </CardTitle>
          <CardDescription>
            Recarga festivos nacionales, autonómicos y locales desde fuentes oficiales
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Selector de año */}
          <div className="space-y-2">
            <Label htmlFor="year">Año</Label>
            <Input
              id="year"
              type="number"
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value) || new Date().getFullYear())}
              min="2020"
              max="2030"
              className="w-32"
            />
          </div>

          {/* Estadísticas actuales */}
          {loadingStats ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
          ) : statistics ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-4 border rounded-lg">
                <div className="text-sm text-muted-foreground">Total</div>
                <div className="text-2xl font-bold">{statistics.total}</div>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="text-sm text-muted-foreground">Nacionales</div>
                <div className="text-2xl font-bold">{statistics.national}</div>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="text-sm text-muted-foreground">Autonómicos</div>
                <div className="text-2xl font-bold">{statistics.regional}</div>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="text-sm text-muted-foreground">Locales</div>
                <div className="text-2xl font-bold">{statistics.local}</div>
              </div>
            </div>
          ) : null}

          {/* Información sobre la recarga */}
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              La recarga cargará festivos desde:
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li><strong>Nacionales y Autonómicos:</strong> API Nager.Date</li>
                <li><strong>Locales:</strong> Boletín Oficial del Estado (BOE)</li>
              </ul>
              Los duplicados se evitarán automáticamente.
            </AlertDescription>
          </Alert>

          {/* Botón de recarga */}
          <Button
            onClick={handleRefreshAll}
            disabled={loading}
            className="w-full md:w-auto"
            size="lg"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Recargando...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4 mr-2" />
                Recargar Todos los Festivos
              </>
            )}
          </Button>

          {/* Resultados de la última recarga */}
          {lastRefresh && (
            <div className="space-y-2 p-4 border rounded-lg bg-muted/50">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Última recarga</span>
                <Badge variant="outline">
                  {lastRefresh.timestamp.toLocaleString('es-ES')}
                </Badge>
              </div>
              {lastRefresh.results.cleaned > 0 && (
                <div className="text-xs text-muted-foreground mb-2">
                  🧹 Se eliminaron {lastRefresh.results.cleaned} festivos anteriores antes de cargar
                </div>
              )}
              <div className="grid grid-cols-2 gap-4 mt-2">
                <div>
                  <div className="text-xs text-muted-foreground">Nacionales/Autonómicos</div>
                  <div className="text-lg font-semibold">
                    {lastRefresh.results.national_regional?.loaded || 0}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">Locales</div>
                  <div className="text-lg font-semibold">
                    {lastRefresh.results.local?.loaded || 0}
                  </div>
                </div>
              </div>
              {lastRefresh.results.errors && lastRefresh.results.errors.length > 0 && (
                <Alert variant="destructive" className="mt-2">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    <div className="text-sm font-medium mb-1">Errores:</div>
                    <ul className="list-disc list-inside text-xs">
                      {lastRefresh.results.errors.slice(0, 3).map((error, idx) => (
                        <li key={idx}>{error}</li>
                      ))}
                      {lastRefresh.results.errors.length > 3 && (
                        <li>... y {lastRefresh.results.errors.length - 3} más</li>
                      )}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Diálogo de confirmación */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent className="max-w-3xl max-h-[85vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-xl">
              <AlertTriangle className="w-6 h-6 text-yellow-500 fill-yellow-500" />
              Aviso Importante
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <ul className="list-disc list-inside space-y-2 text-sm">
                <li>Se <strong>ELIMINARÁN</strong> todos los festivos existentes del año {year}</li>
                <li>Se cargarán nuevos desde las fuentes oficiales</li>
                <li>Esto asegura que festivos que cambiaron de tipo se actualicen correctamente</li>
              </ul>
            </div>
            
            <div className="pt-3 border-t">
              <p className="font-medium mb-2 text-sm">Esto cargará:</p>
              <ul className="list-disc list-inside space-y-1 text-sm ml-2">
                <li>Festivos nacionales y autonómicos</li>
                <li>Festivos locales desde el BOE</li>
                <li>Festivos locales desde Boletines de CCAA</li>
              </ul>
            </div>
          </div>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button
              variant="outline"
              onClick={() => setShowConfirmDialog(false)}
            >
              Cancelar
            </Button>
            <Button
              onClick={confirmRefreshAll}
              className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white dark:text-white"
            >
              Aceptar y Continuar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default HolidayManagement
