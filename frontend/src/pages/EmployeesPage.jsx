import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'
import { 
  Users, 
  Search, 
  Filter, 
  Plus,
  Download,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  MapPin,
  Building,
  Mail,
  Phone,
  Calendar,
  TrendingUp,
  AlertCircle,
  Shield,
  Briefcase,
  PlusCircle
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Alert, AlertDescription } from '../components/ui/alert'
import { Progress } from '../components/ui/progress'
import { StatsCard } from '../components/ui/stats-card'
import { Label } from '../components/ui/label'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import InviteEmployeeModal from '../components/employees/InviteEmployeeModal'
import { Checkbox } from '../components/ui/checkbox'
import teamService from '../services/teamService'

const EmployeesPage = () => {
  const { user, isAdmin, isManager, isEmployee } = useAuth()
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [teamFilter, setTeamFilter] = useState('all')
  const [selectedEmployee, setSelectedEmployee] = useState(null)
  const [showEmployeeDetail, setShowEmployeeDetail] = useState(false)
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)
  const [availableRoles] = useState(['admin', 'manager', 'employee', 'viewer'])
  const [availableTeams, setAvailableTeams] = useState([])
  const [memberships, setMemberships] = useState([])
  const [membershipEdits, setMembershipEdits] = useState({})
  const [loadingMemberships, setLoadingMemberships] = useState(false)
  const [showManageTeamsDialog, setShowManageTeamsDialog] = useState(false)
  const [newMembership, setNewMembership] = useState({
    teamId: '',
    allocationPercent: '',
    role: '',
    isPrimary: false
  })

  useEffect(() => {
    loadEmployees()
  }, [statusFilter, teamFilter])

  useEffect(() => {
    loadAvailableTeams()
  }, [])

  useEffect(() => {
    if (selectedEmployee?.id) {
      loadEmployeeMemberships(selectedEmployee.id)
    } else {
      setMemberships([])
    }
  }, [selectedEmployee?.id])

  useEffect(() => {
    if (!showEmployeeDetail) {
      setShowManageTeamsDialog(false)
    }
  }, [showEmployeeDetail])

  useEffect(() => {
    if (!showManageTeamsDialog) {
      setNewMembership({
        teamId: '',
        allocationPercent: '',
        role: '',
        isPrimary: false
      })
    }
  }, [showManageTeamsDialog])

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

  const loadEmployees = async ({ silent = false } = {}) => {
    if (!silent) {
      setLoading(true)
    }
    try {
      // Los administradores y managers deben ver todos los empleados (aprobados y pendientes)
      // para que los managers se vean a sí mismos
      const approvedOnly = (isAdmin() || isManager()) ? 'false' : 'true'
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees?approved_only=${approvedOnly}`, {
        credentials: 'include'
      })
      
      if (!response.ok) {
        throw new Error('Error cargando empleados')
      }
      
      const data = await response.json()
      
      // Usar datos reales del backend (vacío si no hay empleados)
      setEmployees(data.employees || [])
    } catch (error) {
      console.error('Error cargando empleados:', error)
      // En caso de error, mostrar lista vacía
      setEmployees([])
    } finally {
      if (!silent) {
        setLoading(false)
      }
    }
  }

  const loadAvailableTeams = async () => {
    try {
      const response = await teamService.getAllTeams()
      if (response.success && response.teams) {
        setAvailableTeams(response.teams)
      }
    } catch (error) {
      console.error('Error cargando equipos disponibles:', error)
    }
  }

  const buildMembershipEdits = (records) => {
    const initial = {}
    records.forEach((membership) => {
      if (membership.id) {
        initial[membership.id] = {
          allocation_percent: membership.allocation_percent ?? '',
          role: membership.role || ''
        }
      }
    })
    return initial
  }

  const loadEmployeeMemberships = async (employeeId) => {
    if (!employeeId) return
    try {
      setLoadingMemberships(true)
      const response = await fetch(`${API_BASE_URL}/employees/${employeeId}/memberships`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          const list = data.memberships || []
          setMemberships(list)
          setMembershipEdits(buildMembershipEdits(list))
          setSelectedEmployee((prev) => prev && prev.id === employeeId ? { ...prev, teams: list } : prev)
          setEmployees((prev) => prev.map((emp) => emp.id === employeeId ? { ...emp, teams: list } : emp))
        }
      }
    } catch (error) {
      console.error('Error cargando membresías:', error)
    } finally {
      setLoadingMemberships(false)
    }
  }

  const updateMembershipEdit = (membershipId, field, value) => {
    setMembershipEdits((prev) => ({
      ...prev,
      [membershipId]: {
        ...prev[membershipId],
        [field]: value
      }
    }))
  }

  const handleAddMembership = async () => {
    if (!selectedEmployee?.id || !newMembership.teamId) {
      toast.error('Selecciona un equipo para asignar')
      return
    }
    if (memberships.some((membership) => membership.team_id?.toString() === newMembership.teamId)) {
      toast.error('El empleado ya pertenece a ese equipo')
      return
    }

    const payload = {
      team_id: parseInt(newMembership.teamId, 10),
      role: newMembership.role || undefined,
      is_primary: newMembership.isPrimary,
      allocation_percent: newMembership.allocationPercent !== ''
        ? parseFloat(newMembership.allocationPercent)
        : null
    }

    try {
      const response = await fetch(`${API_BASE_URL}/employees/${selectedEmployee.id}/memberships`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || 'Error asignando equipo')
      }

      toast.success('Equipo asignado correctamente')
      setNewMembership({
        teamId: '',
        allocationPercent: '',
        role: '',
        isPrimary: false
      })
      await loadEmployeeMemberships(selectedEmployee.id)
    } catch (error) {
      console.error('Error asignando equipo:', error)
      toast.error('No se pudo asignar el equipo', {
        description: error.message
      })
    }
  }

  const handleSaveMembership = async (membershipId) => {
    if (!selectedEmployee?.id) return
    const edits = membershipEdits[membershipId]
    if (!edits) return

    const payload = {
      role: edits.role,
      allocation_percent: edits.allocation_percent !== ''
        ? parseFloat(edits.allocation_percent)
        : null
    }

    try {
      const response = await fetch(`${API_BASE_URL}/employees/${selectedEmployee.id}/memberships/${membershipId}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || 'Error actualizando membresía')
      }

      toast.success('Membresía actualizada')
      await loadEmployeeMemberships(selectedEmployee.id)
    } catch (error) {
      console.error('Error actualizando membresía:', error)
      toast.error('No se pudo actualizar la membresía', {
        description: error.message
      })
    }
  }

  const handleSetPrimaryMembership = async (membershipId) => {
    if (!selectedEmployee?.id) return
    try {
      const response = await fetch(`${API_BASE_URL}/employees/${selectedEmployee.id}/memberships/${membershipId}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_primary: true })
      })
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || 'Error actualizando membresía')
      }
      toast.success('Equipo principal actualizado')
      await loadEmployeeMemberships(selectedEmployee.id)
    } catch (error) {
      console.error('Error estableciendo equipo principal:', error)
      toast.error('No se pudo actualizar el equipo principal', {
        description: error.message
      })
    }
  }

  const handleRemoveMembership = async (membershipId) => {
    if (!selectedEmployee?.id) return
    try {
      const response = await fetch(`${API_BASE_URL}/employees/${selectedEmployee.id}/memberships/${membershipId}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || 'Error eliminando membresía')
      }
      toast.success('Membresía eliminada')
      await loadEmployeeMemberships(selectedEmployee.id)
    } catch (error) {
      console.error('Error eliminando membresía:', error)
      toast.error('No se pudo eliminar la membresía', {
        description: error.message
      })
    }
  }


  const getStatusLabel = (employee) => {
    if (employee.approved === true) return 'Aprobado'
    if (employee.approved === false && employee.active === true) return 'Pendiente'
    if (employee.approved === false && employee.active === false) return 'Rechazado'
    return 'Desconocido'
  }

  const getStatusIcon = (employee) => {
    if (employee.approved === true) return <CheckCircle className="w-4 h-4" />
    if (employee.approved === false && employee.active === true) return <Clock className="w-4 h-4" />
    if (employee.approved === false && employee.active === false) return <XCircle className="w-4 h-4" />
    return <Clock className="w-4 h-4" />
  }
  
  const getStatusColor = (employee) => {
    if (employee.approved === true) return 'bg-green-100 text-green-800 border-green-200'
    if (employee.approved === false && employee.active === true) return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    if (employee.approved === false && employee.active === false) return 'bg-red-100 text-red-800 border-red-200'
    return 'bg-yellow-100 text-yellow-800 border-yellow-200'
  }

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
  }

  const filteredEmployees = employees.filter(employee => {
    const teamNames = employee.teams?.map(team => team.team_name || team.name).filter(Boolean) || []
    const primaryTeamName = employee.team_name || employee.team?.name || ''
    const searchableTeams = [...teamNames, primaryTeamName].filter(Boolean).join(' ').toLowerCase()
    const employeeEmail = employee.email ? employee.email.toLowerCase() : ''
    const matchesSearch =
      employee.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employeeEmail.includes(searchTerm.toLowerCase()) ||
      searchableTeams.includes(searchTerm.toLowerCase())
    
    // Convertir boolean a string para comparar con el filtro
    let employeeStatus = 'pending'
    if (employee.approved === true) {
      employeeStatus = 'approved'
    } else if (employee.approved === false) {
      employeeStatus = 'pending'
    }
    
    const matchesStatus = statusFilter === 'all' || employeeStatus === statusFilter
    const matchesTeam = teamFilter === 'all' || teamNames.includes(teamFilter) || primaryTeamName === teamFilter
    
    return matchesSearch && matchesStatus && matchesTeam
  })

  const paginatedEmployees = filteredEmployees.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const totalPages = Math.ceil(filteredEmployees.length / itemsPerPage)

  const handleApproveEmployee = async (employeeId) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees/${employeeId}/approve`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        if (response.status === 409) {
          toast.error('El empleado ya está aprobado o hay un conflicto', {
            description: 'Recargando datos...'
          })
          loadEmployees()
          return
        } else {
          throw new Error(errorData.message || 'Error al aprobar empleado')
        }
      }
      
      const data = await response.json()
      
      if (data.success) {
        // Actualizar estado local
        setEmployees(prev => prev.map(emp => 
          emp.id === employeeId ? { ...emp, approved: true } : emp
        ))
        
        // Cerrar modal si está abierto
        if (selectedEmployee?.id === employeeId) {
          setShowEmployeeDetail(false)
          setSelectedEmployee(null)
        }
        
        // Recargar datos
        loadEmployees()
        toast.success('Empleado aprobado exitosamente')
      }
    } catch (error) {
      console.error('Error aprobando empleado:', error)
      toast.error('Error al aprobar empleado', {
        description: error.message || 'Por favor, intenta de nuevo.'
      })
    }
  }

  const handleChangeRole = async (employee, newRole) => {
    if (!employee.user_id) {
      toast.error('No se puede cambiar el rol', {
        description: 'Usuario no encontrado'
      })
      return
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/users/${employee.user_id}/roles`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          role_names: [newRole]
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || 'Error al cambiar rol')
      }

      const data = await response.json()
      
      if (data.success) {
        // Recargar datos
        loadEmployees()
        toast.success('Rol actualizado exitosamente', {
          description: `El rol del empleado ha sido cambiado a ${newRole.charAt(0).toUpperCase() + newRole.slice(1)}`
        })
      }
    } catch (error) {
      console.error('Error cambiando rol:', error)
      toast.error('Error al cambiar rol', {
        description: error.message || 'Por favor, intenta de nuevo.'
      })
    }
  }

  const handleRejectEmployee = async (employeeId) => {
    try {
      // Simular rechazo
      setEmployees(prev => prev.map(emp => 
        emp.id === employeeId ? { ...emp, approved: 'rejected' } : emp
      ))
    } catch (error) {
      console.error('Error rechazando empleado:', error)
    }
  }


  const renderTeamBadges = (employee) => {
    const list = employee.teams && employee.teams.length > 0
      ? employee.teams
      : (employee.team_name || employee.team?.name)
        ? [{
            team_id: employee.team_id,
            team_name: employee.team_name || employee.team?.name,
            allocation_percent: null,
            is_primary: true
          }]
        : []

    if (list.length === 0) {
      return (
        <Badge variant="outline">
          Sin equipo
        </Badge>
      )
    }

    return (
      <div className="flex flex-wrap gap-2">
        {list.slice(0, 2).map((team) => (
          <Badge
            key={`${employee.id}-${team.team_id || team.team_name}`}
            variant={team.is_primary ? 'default' : 'outline'}
            className="flex items-center space-x-1"
          >
            <span>{team.team_name || team.name}</span>
            {team.allocation_percent ? (
              <span className="text-xs opacity-80">{team.allocation_percent}%</span>
            ) : null}
          </Badge>
        ))}
        {list.length > 2 && (
          <Badge variant="secondary">+{list.length - 2}</Badge>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Empleados</h1>
        </div>
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" text="Cargando empleados..." />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 px-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Empleados</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestiona los empleados y sus perfiles
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
          
          {(isAdmin() || isManager()) && (
            <Button onClick={() => setShowInviteModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Invitar Empleado
            </Button>
          )}
        </div>
      </div>

      {/* Filtros y búsqueda - PRIMERO */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Buscar por nombre, email o equipo..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los estados</SelectItem>
                <SelectItem value="approved">Aprobados</SelectItem>
                <SelectItem value="pending">Pendientes</SelectItem>
                <SelectItem value="rejected">Rechazados</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={teamFilter} onValueChange={setTeamFilter}>
              <SelectTrigger className="w-48">
                <Building className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Equipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los equipos</SelectItem>
                {availableTeams.map((team) => (
                  <SelectItem key={team.id} value={team.name}>
                    {team.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabla de empleados */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Empleados</CardTitle>
          <CardDescription>
            {filteredEmployees.length} empleados encontrados
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Empleado</TableHead>
                  <TableHead>Equipo</TableHead>
                  <TableHead>Ubicación</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Eficiencia</TableHead>
                  <TableHead>Rol</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedEmployees.map((employee) => (
                  <TableRow key={employee.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <Avatar>
                          <AvatarImage src={`/avatars/${employee.id}.jpg`} />
                          <AvatarFallback>{getInitials(employee.full_name)}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {employee.full_name}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {employee.email}
                          </p>
                        </div>
                      </div>
                    </TableCell>
                    
                    <TableCell>{renderTeamBadges(employee)}</TableCell>
                    
                    <TableCell>
                      <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                        <MapPin className="w-4 h-4 mr-1" />
                        {employee.city}, {employee.country}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <Badge className={getStatusColor(employee)}>
                        {getStatusIcon(employee)}
                        <span className="ml-1">{getStatusLabel(employee)}</span>
                      </Badge>
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <div className="w-16">
                          <Progress value={employee.monthly_stats?.efficiency || 0} className="h-2" />
                        </div>
                        <span className="text-sm font-medium">
                          {employee.monthly_stats?.efficiency || 0}%
                        </span>
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      {isAdmin() ? (
                        <Select
                          value={employee.user_roles?.[0] || 'employee'}
                          onValueChange={(newRole) => handleChangeRole(employee, newRole)}
                        >
                          <SelectTrigger className="w-32">
                            <Shield className="w-4 h-4 mr-2" />
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {availableRoles.map(role => (
                              <SelectItem key={role} value={role}>
                                {role.charAt(0).toUpperCase() + role.slice(1)}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      ) : (
                        <Badge variant="outline">
                          {employee.user_roles?.[0] ? employee.user_roles[0].charAt(0).toUpperCase() + employee.user_roles[0].slice(1) : 'Sin rol'}
                        </Badge>
                      )}
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={async () => {
                            // Cargar datos completos del empleado
                            try {
                              const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees/${employee.id}`, {
                                credentials: 'include'
                              })
                              if (response.ok) {
                                const data = await response.json()
                                if (data.success) {
                                  setSelectedEmployee(data.employee)
                                  setShowEmployeeDetail(true)
                                }
                              } else {
                                // Si falla, usar datos de la lista
                                setSelectedEmployee(employee)
                                setShowEmployeeDetail(true)
                              }
                            } catch (error) {
                              console.error('Error cargando detalles del empleado:', error)
                              // Si falla, usar datos de la lista
                              setSelectedEmployee(employee)
                              setShowEmployeeDetail(true)
                            }
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        
                        {(isAdmin() || isManager()) && employee.approved === false && employee.active === true && (
                          <>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleApproveEmployee(employee.id)}
                              className="text-green-600 hover:text-green-700"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRejectEmployee(employee.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <XCircle className="w-4 h-4" />
                            </Button>
                          </>
                        )}
                        
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          
          {/* Paginación */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Mostrando {(currentPage - 1) * itemsPerPage + 1} a {Math.min(currentPage * itemsPerPage, filteredEmployees.length)} de {filteredEmployees.length} empleados
              </p>
              
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                >
                  Anterior
                </Button>
                
                <span className="text-sm">
                  Página {currentPage} de {totalPages}
                </span>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                >
                  Siguiente
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog de detalle del empleado */}
      {selectedEmployee && (
        <Dialog open={showEmployeeDetail} onOpenChange={setShowEmployeeDetail}>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-3">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={`/avatars/${selectedEmployee.id}.jpg`} />
                  <AvatarFallback>{getInitials(selectedEmployee.full_name)}</AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="text-lg font-semibold">{selectedEmployee.full_name}</h3>
                  <p className="text-sm text-gray-500">{selectedEmployee.email}</p>
                </div>
              </DialogTitle>
            </DialogHeader>
            
            <Tabs defaultValue="info" className="mt-6">
              <TabsList>
                <TabsTrigger value="info">Información</TabsTrigger>
                <TabsTrigger value="stats">Estadísticas</TabsTrigger>
                <TabsTrigger value="activity">Actividad</TabsTrigger>
              </TabsList>
              
              <TabsContent value="info" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Información Personal</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {selectedEmployee.email && (
                        <div className="flex items-center space-x-3">
                          <Mail className="w-4 h-4 text-gray-400" />
                          <span>{selectedEmployee.email}</span>
                        </div>
                      )}
                      <div className="flex items-center space-x-3">
                        <MapPin className="w-4 h-4 text-gray-400" />
                        <span>{selectedEmployee.city}, {selectedEmployee.region}, {selectedEmployee.country}</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <Building className="w-4 h-4 text-gray-400" />
                        <span>{selectedEmployee.team_name || selectedEmployee.team?.name || 'Sin equipo'}</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        <span>Inicio: {selectedEmployee.created_at ? new Date(selectedEmployee.created_at).toLocaleDateString('es-ES') : 'N/A'}</span>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Configuración Horaria</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex justify-between">
                        <span>Lunes - Jueves:</span>
                        <span className="font-medium">{selectedEmployee.hours_monday_thursday}h</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Viernes:</span>
                        <span className="font-medium">{selectedEmployee.hours_friday}h</span>
                      </div>
                      <div className="flex justify-between border-t pt-2">
                        <span>Total semanal:</span>
                        <span className="font-medium">
                          {(selectedEmployee.hours_monday_thursday * 4 + selectedEmployee.hours_friday)}h
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Estado:</span>
                        <Badge className={getStatusColor(selectedEmployee)}>
                          {getStatusIcon(selectedEmployee)}
                          <span className="ml-1">{getStatusLabel(selectedEmployee)}</span>
                        </Badge>
                      </div>
                      {isAdmin() && (
                        <div className="flex items-center justify-between border-t pt-2">
                          <Label htmlFor="hourly-rate">Tarifa por hora:</Label>
                          <div className="flex items-center space-x-2">
                            <Input
                              id="hourly-rate"
                              type="number"
                              step="0.01"
                              min="0"
                              className="w-32"
                              value={selectedEmployee.hourly_rate || ''}
                              onChange={async (e) => {
                                const newRate = e.target.value === '' ? null : parseFloat(e.target.value)
                                try {
                                  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees/${selectedEmployee.id}/hourly-rate`, {
                                    method: 'PUT',
                                    credentials: 'include',
                                    headers: {
                                      'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ hourly_rate: newRate })
                                  })
                                  
                                  if (response.ok) {
                                    const data = await response.json()
                                    if (data.success) {
                                      setSelectedEmployee({ ...selectedEmployee, hourly_rate: newRate })
                                      toast.success('Tarifa actualizada exitosamente')
                                    }
                                  } else {
                                    throw new Error('Error actualizando tarifa')
                                  }
                                } catch (error) {
                                  console.error('Error actualizando tarifa:', error)
                                  toast.error('Error al actualizar tarifa', {
                                    description: error.message || 'Por favor, intenta de nuevo.'
                                  })
                                }
                              }}
                              placeholder="0.00"
                            />
                            <span className="text-sm text-gray-500">€/h</span>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  <div className="md:col-span-2">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Equipos asignados</CardTitle>
                        <CardDescription>Distribución del empleado por equipos</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {loadingMemberships ? (
                          <div className="py-4 text-center">
                            <LoadingSpinner size="sm" text="Cargando equipos..." />
                          </div>
                        ) : memberships.length > 0 ? (
                          memberships.map((membership) => (
                            <div key={`${membership.team_id}-${membership.id || 'temp'}`} className="border rounded-lg p-3 flex flex-col gap-1">
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="font-semibold">{membership.team_name || 'Equipo sin nombre'}</p>
                                  {membership.role && (
                                    <p className="text-xs text-gray-500">{membership.role}</p>
                                  )}
                                </div>
                                <div className="flex items-center gap-2">
                                  {membership.allocation_percent !== null && (
                                    <Badge variant="secondary">{membership.allocation_percent}%</Badge>
                                  )}
                                  {membership.is_primary && (
                                    <Badge variant="outline">Principal</Badge>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="text-sm text-gray-500">
                            Sin asignaciones registradas. Usa el botón para gestionarlas.
                          </p>
                        )}

                        {(isAdmin() || isManager()) && (
                          <Button variant="outline" size="sm" onClick={() => setShowManageTeamsDialog(true)}>
                            <Users className="w-4 h-4 mr-2" />
                            Gestionar equipos
                          </Button>
                        )}
                      </CardContent>
                    </Card>
                  </div>

                  <div className="md:col-span-2">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Proyectos</CardTitle>
                        <CardDescription>Asignaciones y porcentajes por proyecto</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {selectedEmployee.projects && selectedEmployee.projects.length > 0 ? (
                          selectedEmployee.projects.map((project) => (
                            <div key={`${project.project_id}-${project.id || 'assignment'}`} className="border rounded-lg p-3 flex items-center justify-between">
                              <div>
                                <p className="font-semibold">{project.project_name || `Proyecto ${project.project_id}`}</p>
                                <p className="text-xs text-gray-500">
                                  {project.team_name ? `Equipo: ${project.team_name}` : 'Sin equipo asociado'}
                                </p>
                                {project.role && (
                                  <p className="text-xs text-gray-500">Rol: {project.role}</p>
                                )}
                              </div>
                              <div className="text-right">
                                {project.allocation_percent !== null && (
                                  <p className="text-sm font-semibold">{project.allocation_percent}%</p>
                                )}
                                <p className="text-xs text-gray-500">ID: {project.project_code || project.project_id}</p>
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="text-sm text-gray-500">Este empleado no tiene proyectos asignados.</p>
                        )}

                        <Button variant="outline" size="sm" asChild>
                          <Link to="/projects" className="flex items-center">
                            <Briefcase className="w-4 h-4 mr-2" />
                            Ver panel de proyectos
                          </Link>
                        </Button>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="stats" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Estadísticas Mensuales</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span>Horas Teóricas:</span>
                          <span className="font-medium">{selectedEmployee.monthly_stats?.theoretical_hours || 0}h</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Horas Reales:</span>
                          <span className="font-medium">{selectedEmployee.monthly_stats?.actual_hours || 0}h</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Eficiencia:</span>
                          <span className="font-medium">{selectedEmployee.monthly_stats?.efficiency || 0}%</span>
                        </div>
                        <Progress value={selectedEmployee.monthly_stats?.efficiency || 0} className="h-2" />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Estadísticas Anuales</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span>Horas Totales:</span>
                          <span className="font-medium">{selectedEmployee.annual_stats?.total_actual_hours || selectedEmployee.annual_stats?.total_theoretical_hours || 0}h</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Eficiencia Anual:</span>
                          <span className="font-medium">{selectedEmployee.annual_stats?.total_efficiency || 0}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Vacaciones Restantes:</span>
                          <span className="font-medium">{selectedEmployee.annual_stats?.remaining_vacation_days || 0} días</span>
                        </div>
                        <div className="flex justify-between">
                          <span>HLD Restantes:</span>
                          <span className="font-medium">{selectedEmployee.annual_stats?.remaining_hld_hours || 0}h</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              
              <TabsContent value="activity">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Actividad Reciente</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-blue-600 rounded-full mt-2" />
                        <div>
                          <p className="text-sm font-medium">Registro completado</p>
                          <p className="text-xs text-gray-500">
                            {new Date(selectedEmployee.created_at).toLocaleDateString('es-ES')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-green-600 rounded-full mt-2" />
                        <div>
                          <p className="text-sm font-medium">Última actividad</p>
                          <p className="text-xs text-gray-500">
                            {selectedEmployee.last_activity ? new Date(selectedEmployee.last_activity).toLocaleDateString('es-ES') : 'Sin actividad'}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
            
            {(isAdmin() || isManager()) && selectedEmployee.approved === false && selectedEmployee.active === true && (
              <div className="flex space-x-2 mt-6">
                <Button 
                  onClick={() => handleApproveEmployee(selectedEmployee.id)}
                  className="flex-1"
                >
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Aprobar Empleado
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => handleRejectEmployee(selectedEmployee.id)}
                  className="flex-1"
                >
                  <XCircle className="w-4 h-4 mr-2" />
                  Rechazar
                </Button>
              </div>
          )}
        </DialogContent>
        </Dialog>
      )}

      {/* Estadísticas como headers expandibles - AL FINAL */}

      <Dialog open={showManageTeamsDialog} onOpenChange={setShowManageTeamsDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Gestionar equipos de {selectedEmployee?.full_name || 'empleado'}</DialogTitle>
            <DialogDescription>
              Ajusta las asignaciones del empleado entre diferentes equipos y define los porcentajes de dedicación.
            </DialogDescription>
          </DialogHeader>
          {!selectedEmployee ? (
            <p className="text-sm text-gray-500">
              Selecciona un empleado para actualizar sus equipos.
            </p>
          ) : (
            <>
              {loadingMemberships ? (
                <div className="py-6 text-center">
                  <LoadingSpinner size="sm" text="Cargando equipos..." />
                </div>
              ) : (
                <div className="space-y-4 max-h-[45vh] overflow-y-auto pr-1">
                  {memberships.length > 0 ? memberships.map((membership) => (
                    <Card key={`${membership.team_id}-${membership.id || 'fallback'}`}>
                      <CardContent className="space-y-3 pt-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-semibold">{membership.team_name || 'Equipo sin nombre'}</p>
                            {membership.role && (
                              <p className="text-xs text-gray-500">{membership.role}</p>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            {membership.allocation_percent !== null && (
                              <Badge variant="secondary">{membership.allocation_percent}%</Badge>
                            )}
                            {membership.is_primary && (
                              <Badge variant="outline">Principal</Badge>
                            )}
                          </div>
                        </div>

                        {membership.id ? (
                          <>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              <div>
                                <Label>Rol</Label>
                                <Input
                                  value={membershipEdits[membership.id]?.role ?? ''}
                                  onChange={(e) => updateMembershipEdit(membership.id, 'role', e.target.value)}
                                  placeholder="Rol dentro del equipo"
                                />
                              </div>
                              <div>
                                <Label>% dedicación</Label>
                                <Input
                                  type="number"
                                  min="0"
                                  max="100"
                                  value={membershipEdits[membership.id]?.allocation_percent ?? ''}
                                  onChange={(e) => updateMembershipEdit(membership.id, 'allocation_percent', e.target.value)}
                                  placeholder="Ej. 50"
                                />
                              </div>
                            </div>
                            <div className="flex flex-wrap gap-2 justify-end">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleSetPrimaryMembership(membership.id)}
                                disabled={membership.is_primary}
                              >
                                Marcar principal
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleSaveMembership(membership.id)}
                              >
                                Guardar cambios
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-red-600 hover:text-red-700"
                                onClick={() => handleRemoveMembership(membership.id)}
                              >
                                <Trash2 className="w-4 h-4 mr-2" />
                                Eliminar
                              </Button>
                            </div>
                          </>
                        ) : (
                          <p className="text-xs text-yellow-600">
                            Registro histórico sin detalle. Añade nuevamente el equipo para habilitar la edición.
                          </p>
                        )}
                      </CardContent>
                    </Card>
                  )) : (
                    <p className="text-sm text-gray-500">
                      El empleado aún no tiene equipos asignados.
                    </p>
                  )}
                </div>
              )}

              <div className="border-t pt-4 space-y-3 mt-4">
                <div>
                  <Label className="font-semibold">Añadir equipo</Label>
                  <p className="text-xs text-gray-500">
                    Selecciona un nuevo equipo y define el porcentaje estimado de dedicación.
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <Label>Equipo</Label>
                    <Select
                      value={newMembership.teamId}
                      onValueChange={(value) => setNewMembership((prev) => ({ ...prev, teamId: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecciona equipo" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableTeams
                          .filter((team) => !memberships.some((membership) => membership.team_id === team.id))
                          .map((team) => (
                            <SelectItem key={team.id} value={team.id.toString()}>
                              {team.name}
                            </SelectItem>
                          ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>% dedicación</Label>
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      value={newMembership.allocationPercent}
                      onChange={(e) => setNewMembership((prev) => ({ ...prev, allocationPercent: e.target.value }))}
                      placeholder="Ej. 50"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <Label>Rol</Label>
                    <Input
                      value={newMembership.role}
                      onChange={(e) => setNewMembership((prev) => ({ ...prev, role: e.target.value }))}
                      placeholder="Rol dentro del equipo"
                    />
                  </div>
                  <div className="flex items-center space-x-2 pt-6">
                    <Checkbox
                      id="new-membership-primary"
                      checked={newMembership.isPrimary}
                      onCheckedChange={(checked) => setNewMembership((prev) => ({ ...prev, isPrimary: !!checked }))}
                    />
                    <Label htmlFor="new-membership-primary">Marcar como equipo principal</Label>
                  </div>
                </div>
                <div className="flex justify-end">
                  <Button onClick={handleAddMembership} disabled={!newMembership.teamId}>
                    <PlusCircle className="w-4 h-4 mr-2" />
                    Añadir equipo
                  </Button>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Modal de invitación */}
      <InviteEmployeeModal
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        onInviteSuccess={(invitation) => {
          setShowInviteModal(false)
          toast.success('Invitación enviada', {
            description: invitation?.email
              ? `Hemos enviado la invitación a ${invitation.email}`
              : 'El usuario recibirá un correo con las instrucciones.'
          })
          loadEmployees({ silent: true }) // Recargar sin bloquear la UI
        }}
      />
    </div>
  )
}

export default EmployeesPage
