import { useState, useEffect } from 'react'
import { RefreshCw, Calendar, AlertCircle, CheckCircle, Loader2, Info } from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Alert, AlertDescription } from '../ui/alert'
import { useToast } from '../ui/use-toast'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Badge } from '../ui/badge'

const HolidayManagement = () => {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [year, setYear] = useState(new Date().getFullYear())
  const [statistics, setStatistics] = useState(null)
  const [loadingStats, setLoadingStats] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(null)

  useEffect(() => {
    loadStatistics()
  }, [year])

  const loadStatistics = async () => {
    try {
      setLoadingStats(true)
      const token = localStorage.getItem('token')
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL}/api/holidays/statistics?year=${year}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
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

  const handleRefreshAll = async () => {
    if (!confirm(`¿Recargar todos los festivos para ${year}?\n\nEsto cargará:\n- Festivos nacionales y autonómicos\n- Festivos locales desde el BOE\n\nLos duplicados se evitarán automáticamente.`)) {
      return
    }

    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL}/api/holidays/refresh-all`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ year })
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
    </div>
  )
}

export default HolidayManagement
