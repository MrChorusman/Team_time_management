import { useState, useEffect } from 'react'
import { 
  Users, 
  Search, 
  Plus,
  Download,
  Eye,
  Edit,
  Trash2,
  TrendingUp,
  Target,
  Clock,
  Calendar,
  Award,
  UserPlus,
  Settings,
  BarChart3
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Progress } from '../components/ui/progress'
import { StatsCard } from '../components/ui/stats-card'
import { Label } from '../components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Textarea } from '../components/ui/textarea'
import { Alert, AlertDescription } from '../components/ui/alert'
import LoadingSpinner from '../components/ui/LoadingSpinner'

const TeamsPage = () => {
  const { user, isAdmin, isManager } = useAuth()
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [showTeamDetail, setShowTeamDetail] = useState(false)
  const [showNewTeamDialog, setShowNewTeamDialog] = useState(false)

  useEffect(() => {
    loadTeams()
  }, [])

  const loadTeams = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/teams`, {
        credentials: 'include'
      })
      
      if (!response.ok) {
        throw new Error('Error cargando equipos')
      }
      
      const data = await response.json()
      
      // Usar datos reales del backend (vacío si no hay equipos)
      setTeams(data.teams || [])
    } catch (error) {
      console.error('Error cargando equipos:', error)
      // En caso de error, mostrar lista vacía
      setTeams([])
    } finally {
      setLoading(false)
    }
  }

  const _generateMockTeams_REMOVED = () => {
    const managers = [
      { id: 1, name: 'Carlos Rodríguez', email: 'carlos@empresa.com' },
      { id: 2, name: 'Ana García', email: 'ana@empresa.com' },
      { id: 3, name: 'Luis Martín', email: 'luis@empresa.com' },
      { id: 4, name: 'María López', email: 'maria@empresa.com' },
      { id: 5, name: 'David González', email: 'david@empresa.com' }
    ]

    return [
      {
        id: 1,
        name: 'Frontend Development',
        description: 'Equipo encargado del desarrollo de interfaces de usuario y experiencia del cliente',
        manager: managers[0],
        created_at: '2023-01-15T00:00:00Z',
        employee_count: 8,
        active_projects: 3,
        metrics: {
          average_efficiency: 92.3,
          total_theoretical_hours: 1280,
          total_actual_hours: 1182,
          monthly_vacation_days: 12,
          monthly_hld_hours: 32,
          team_ranking: 1
        },
        members: [
          { id: 1, name: 'Juan Pérez', role: 'Senior Developer', efficiency: 94.5, avatar: null },
          { id: 2, name: 'Laura Fernández', role: 'Frontend Developer', efficiency: 91.2, avatar: null },
          { id: 3, name: 'Miguel Jiménez', role: 'UI Developer', efficiency: 89.8, avatar: null },
          { id: 4, name: 'Carmen Sánchez', role: 'Junior Developer', efficiency: 87.3, avatar: null },
          { id: 5, name: 'Antonio Herrera', role: 'Frontend Developer', efficiency: 93.1, avatar: null },
          { id: 6, name: 'Cristina Vargas', role: 'Senior Developer', efficiency: 95.7, avatar: null },
          { id: 7, name: 'Francisco Romero', role: 'Frontend Developer', efficiency: 90.4, avatar: null },
          { id: 8, name: 'Pilar Navarro', role: 'UI/UX Developer', efficiency: 92.8, avatar: null }
        ]
      },
      {
        id: 2,
        name: 'Backend Development',
        description: 'Desarrollo de APIs, servicios y arquitectura del servidor',
        manager: managers[1],
        created_at: '2023-02-01T00:00:00Z',
        employee_count: 12,
        active_projects: 5,
        metrics: {
          average_efficiency: 89.1,
          total_theoretical_hours: 1920,
          total_actual_hours: 1711,
          monthly_vacation_days: 18,
          monthly_hld_hours: 48,
          team_ranking: 2
        },
        members: [
          { id: 9, name: 'José Guerrero', role: 'Tech Lead', efficiency: 96.2, avatar: null },
          { id: 10, name: 'Rocío Medina', role: 'Senior Backend', efficiency: 91.8, avatar: null },
          { id: 11, name: 'Manuel Cortés', role: 'Backend Developer', efficiency: 88.5, avatar: null },
          { id: 12, name: 'Beatriz Iglesias', role: 'API Developer', efficiency: 87.9, avatar: null }
        ]
      },
      {
        id: 3,
        name: 'QA Testing',
        description: 'Aseguramiento de calidad y testing automatizado',
        manager: managers[2],
        created_at: '2023-01-20T00:00:00Z',
        employee_count: 6,
        active_projects: 4,
        metrics: {
          average_efficiency: 85.7,
          total_theoretical_hours: 960,
          total_actual_hours: 823,
          monthly_vacation_days: 8,
          monthly_hld_hours: 24,
          team_ranking: 3
        },
        members: [
          { id: 13, name: 'Alejandro Garrido', role: 'QA Lead', efficiency: 89.3, avatar: null },
          { id: 14, name: 'Natalia Cruz', role: 'QA Tester', efficiency: 84.7, avatar: null },
          { id: 15, name: 'Roberto Cabrera', role: 'Automation Tester', efficiency: 87.1, avatar: null }
        ]
      },
      {
        id: 4,
        name: 'UI/UX Design',
        description: 'Diseño de interfaces y experiencia de usuario',
        manager: managers[3],
        created_at: '2023-03-01T00:00:00Z',
        employee_count: 5,
        active_projects: 6,
        metrics: {
          average_efficiency: 88.4,
          total_theoretical_hours: 800,
          total_actual_hours: 707,
          monthly_vacation_days: 6,
          monthly_hld_hours: 20,
          team_ranking: 4
        },
        members: [
          { id: 16, name: 'Silvia Mendoza', role: 'Design Lead', efficiency: 92.1, avatar: null },
          { id: 17, name: 'Andrés Vázquez', role: 'UI Designer', efficiency: 86.8, avatar: null },
          { id: 18, name: 'Mónica Delgado', role: 'UX Designer', efficiency: 89.2, avatar: null }
        ]
      },
      {
        id: 5,
        name: 'DevOps',
        description: 'Infraestructura, despliegues y operaciones',
        manager: managers[4],
        created_at: '2023-02-15T00:00:00Z',
        employee_count: 4,
        active_projects: 2,
        metrics: {
          average_efficiency: 91.8,
          total_theoretical_hours: 640,
          total_actual_hours: 587,
          monthly_vacation_days: 4,
          monthly_hld_hours: 16,
          team_ranking: 5
        },
        members: [
          { id: 19, name: 'Fernando Castillo', role: 'DevOps Lead', efficiency: 94.3, avatar: null },
          { id: 20, name: 'Isabel Morales', role: 'Cloud Engineer', efficiency: 90.7, avatar: null }
        ]
      }
    ]
  }

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
  }

  const getRankingColor = (ranking) => {
    if (ranking === 1) return 'text-yellow-600'
    if (ranking <= 3) return 'text-gray-600'
    return 'text-bronze-600'
  }

  const getRankingIcon = (ranking) => {
    if (ranking === 1) return '🥇'
    if (ranking === 2) return '🥈'
    if (ranking === 3) return '🥉'
    return `#${ranking}`
  }

  const filteredTeams = teams.filter(team =>
    team.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    team.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (team.manager?.name?.toLowerCase().includes(searchTerm.toLowerCase()) || false)
  )

  const getTeamStats = () => {
    const totalTeams = teams.length
    const totalEmployees = teams.reduce((sum, team) => sum + (team.employee_count || 0), 0)
    const averageEfficiency = teams.length > 0 
      ? (teams.reduce((sum, team) => sum + (team.metrics?.average_efficiency || 0), 0) / teams.length).toFixed(1)
      : 'no hay datos'
    const totalProjects = teams.reduce((sum, team) => sum + (team.active_projects || 0), 0)
    
    return { totalTeams, totalEmployees, averageEfficiency, totalProjects }
  }

  const stats = getTeamStats()

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Equipos</h1>
        </div>
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" text="Cargando equipos..." />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 px-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Equipos</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestiona los equipos y su rendimiento
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
          
          {(isAdmin() || isManager()) && (
            <Dialog open={showNewTeamDialog} onOpenChange={setShowNewTeamDialog}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Nuevo Equipo
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Crear Nuevo Equipo</DialogTitle>
                  <DialogDescription>
                    Configura un nuevo equipo de trabajo
                  </DialogDescription>
                </DialogHeader>
                <NewTeamForm onClose={() => setShowNewTeamDialog(false)} />
              </DialogContent>
            </Dialog>
          )}
        </div>
      </div>

      {/* Búsqueda - PRIMERO */}
      <Card>
        <CardContent className="p-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Buscar equipos por nombre, descripción o manager..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Grid de equipos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTeams.map((team) => (
          <Card key={team.id} className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg flex items-center">
                    {team.name}
                    {team.metrics?.team_ranking && (
                      <Badge variant="outline" className="ml-2">
                        {getRankingIcon(team.metrics.team_ranking)}
                      </Badge>
                    )}
                  </CardTitle>
                  <CardDescription className="mt-2">
                    {team.description || 'Sin descripción'}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {/* Manager */}
              {team.manager && (
                <div className="flex items-center space-x-3">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={`/avatars/${team.manager.id}.jpg`} />
                    <AvatarFallback className="text-xs">
                      {getInitials(team.manager.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="text-sm font-medium">{team.manager.name}</p>
                    <p className="text-xs text-gray-500">Manager</p>
                  </div>
                </div>
              )}

              {/* Métricas */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Miembros</p>
                  <p className="font-semibold">{team.employee_count || 0}</p>
                </div>
                <div>
                  <p className="text-gray-500">Proyectos</p>
                  <p className="font-semibold">{team.active_projects || 0}</p>
                </div>
                {team.metrics?.average_efficiency !== undefined && (
                  <>
                    <div>
                      <p className="text-gray-500">Eficiencia</p>
                      <p className="font-semibold">{team.metrics.average_efficiency}%</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Ranking</p>
                      <p className={`font-semibold ${getRankingColor(team.metrics.team_ranking)}`}>
                        #{team.metrics.team_ranking}
                      </p>
                    </div>
                  </>
                )}
              </div>

              {/* Barra de progreso */}
              {team.metrics?.average_efficiency !== undefined && (
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Eficiencia del equipo</span>
                    <span>{team.metrics.average_efficiency}%</span>
                  </div>
                  <Progress value={team.metrics.average_efficiency} className="h-2" />
                </div>
              )}

              {/* Acciones */}
              <div className="flex space-x-2 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={() => {
                    setSelectedTeam(team)
                    setShowTeamDetail(true)
                  }}
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Ver Detalle
                </Button>
                
                {(isAdmin() || isManager()) && (
                  <Button variant="outline" size="sm">
                    <Edit className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Dialog de detalle del equipo */}
      {selectedTeam && (
        <Dialog open={showTeamDetail} onOpenChange={setShowTeamDetail}>
          <DialogContent className="max-w-6xl">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-3">
                <div className="h-10 w-10 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Users className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold">{selectedTeam.name}</h3>
                  <p className="text-sm text-gray-500">{selectedTeam.description}</p>
                </div>
              </DialogTitle>
            </DialogHeader>
            
            <Tabs defaultValue="overview" className="mt-6">
              <TabsList>
                <TabsTrigger value="overview">Resumen</TabsTrigger>
                <TabsTrigger value="members">Miembros</TabsTrigger>
                <TabsTrigger value="metrics">Métricas</TabsTrigger>
                <TabsTrigger value="projects">Proyectos</TabsTrigger>
              </TabsList>
              
              <TabsContent value="overview" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Información General</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {selectedTeam.manager ? (
                        <div className="flex items-center space-x-3">
                          <Avatar>
                            <AvatarImage src={`/avatars/${selectedTeam.manager.id}.jpg`} />
                            <AvatarFallback>{getInitials(selectedTeam.manager.name)}</AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">{selectedTeam.manager.name}</p>
                            <p className="text-sm text-gray-500">Team Manager</p>
                          </div>
                        </div>
                      ) : (
                        <div className="text-sm text-gray-500">
                          <p>Manager: No asignado</p>
                        </div>
                      )}
                      {selectedTeam.created_at && (
                        <div className="text-sm">
                          <p className="text-gray-500">Creado:</p>
                          <p>{new Date(selectedTeam.created_at).toLocaleDateString('es-ES')}</p>
                        </div>
                      )}
                      <div className="text-sm">
                        <p className="text-gray-500">Miembros:</p>
                        <p>{selectedTeam.employee_count || 0} empleados</p>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Rendimiento</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {selectedTeam.metrics ? (
                        <>
                          <div className="text-center">
                            <p className="text-3xl font-bold text-blue-600">
                              {selectedTeam.metrics.average_efficiency}%
                            </p>
                            <p className="text-sm text-gray-500">Eficiencia promedio</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-green-600">
                              #{selectedTeam.metrics.team_ranking}
                            </p>
                            <p className="text-sm text-gray-500">Ranking general</p>
                          </div>
                        </>
                      ) : (
                        <div className="text-center py-8 text-gray-400">
                          <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-30" />
                          <p>Sin datos de rendimiento aún</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Actividad</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm">Proyectos activos:</span>
                        <span className="font-medium">{selectedTeam.active_projects || 0}</span>
                      </div>
                      {selectedTeam.metrics ? (
                        <>
                          <div className="flex justify-between">
                            <span className="text-sm">Horas mensuales:</span>
                            <span className="font-medium">{selectedTeam.metrics.total_actual_hours}h</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm">Vacaciones:</span>
                            <span className="font-medium">{selectedTeam.metrics.monthly_vacation_days} días</span>
                          </div>
                        </>
                      ) : (
                        <div className="text-sm text-gray-400 text-center py-4">
                          Sin datos de actividad
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              
              <TabsContent value="members" className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Miembros del Equipo</h3>
                  {(isAdmin() || isManager()) && (
                    <Button size="sm">
                      <UserPlus className="w-4 h-4 mr-2" />
                      Añadir Miembro
                    </Button>
                  )}
                </div>
                
                {selectedTeam.members && selectedTeam.members.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {selectedTeam.members.map((member) => (
                    <Card key={member.id}>
                      <CardContent className="p-4">
                        <div className="flex items-center space-x-3">
                          <Avatar>
                            <AvatarImage src={`/avatars/${member.id}.jpg`} />
                            <AvatarFallback>{getInitials(member.name)}</AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <p className="font-medium">{member.name}</p>
                            <p className="text-sm text-gray-500">{member.role}</p>
                            <div className="flex items-center space-x-2 mt-2">
                              <div className="flex-1">
                                <Progress value={member.efficiency} className="h-1" />
                              </div>
                              <span className="text-xs font-medium">{member.efficiency}%</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-lg font-semibold text-gray-700 mb-2">Sin miembros asignados</p>
                    <p className="text-sm text-gray-500 mb-6">
                      Añade empleados a este equipo para empezar a gestionar su tiempo
                    </p>
                    {(isAdmin() || isManager()) && (
                      <Button>
                        <UserPlus className="w-4 h-4 mr-2" />
                        Añadir Miembro
                      </Button>
                    )}
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="metrics" className="space-y-6">
                {selectedTeam.metrics ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <BarChart3 className="w-5 h-5 mr-2" />
                          Métricas de Tiempo
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="flex justify-between">
                          <span>Horas Teóricas:</span>
                          <span className="font-medium">{selectedTeam.metrics.total_theoretical_hours}h</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Horas Reales:</span>
                          <span className="font-medium">{selectedTeam.metrics.total_actual_hours}h</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Eficiencia:</span>
                          <span className="font-medium">{selectedTeam.metrics.average_efficiency}%</span>
                        </div>
                        <Progress value={selectedTeam.metrics.average_efficiency} className="h-3" />
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <Calendar className="w-5 h-5 mr-2" />
                          Actividad Mensual
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="flex justify-between">
                          <span>Días de Vacaciones:</span>
                          <span className="font-medium">{selectedTeam.metrics.monthly_vacation_days}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Horas HLD:</span>
                          <span className="font-medium">{selectedTeam.metrics.monthly_hld_hours}h</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Ranking:</span>
                          <span className={`font-medium ${getRankingColor(selectedTeam.metrics.team_ranking)}`}>
                            #{selectedTeam.metrics.team_ranking}
                          </span>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-lg font-semibold text-gray-700 mb-2">Sin métricas disponibles</p>
                    <p className="text-sm text-gray-500">
                      Las métricas aparecerán cuando el equipo tenga empleados asignados y actividad registrada
                    </p>
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="projects">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Proyectos Activos</CardTitle>
                    <CardDescription>
                      {selectedTeam.active_projects} proyectos en desarrollo
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center py-8 text-gray-500">
                      <Award className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>Información de proyectos disponible próximamente</p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </DialogContent>
        </Dialog>
      )}

    </div>
  )
}

// Componente para el formulario de nuevo equipo
const NewTeamForm = ({ onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth-simple/teams/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })
      
      const data = await response.json()
      
      if (data.success) {
        console.log('Equipo creado:', data.team)
        onClose()
        // Recargar la lista de equipos
        window.location.reload()
      } else {
        setError(data.message || 'Error al crear el equipo')
      }
    } catch (error) {
      setError('Error de conexión')
      console.error('Error creando equipo:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      <div>
        <Label htmlFor="name">Nombre del Equipo *</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          placeholder="Ej: Frontend Development"
          required
          disabled={loading}
        />
      </div>

      <div>
        <Label htmlFor="description">Descripción</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          placeholder="Describe las responsabilidades del equipo"
          rows={3}
          disabled={loading}
        />
      </div>

      <div className="flex space-x-2 pt-4">
        <Button type="submit" className="flex-1" disabled={loading}>
          {loading ? 'Creando...' : 'Crear Equipo'}
        </Button>
        <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
          Cancelar
        </Button>
      </div>
    </form>
  )
}

export default TeamsPage
