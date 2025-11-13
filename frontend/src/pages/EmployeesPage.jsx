import { useState, useEffect } from 'react'
import { 
  Users, 
  Search, 
  Filter, 
  Plus,
  Download,
  Eye,
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
  Shield
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
import LoadingSpinner from '../components/ui/LoadingSpinner'
import InviteEmployeeModal from '../components/employees/InviteEmployeeModal'

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

  useEffect(() => {
    loadEmployees()
  }, [statusFilter, teamFilter])

  const loadEmployees = async () => {
    setLoading(true)
    try {
      // Los administradores deben ver todos los empleados (aprobados y pendientes)
      const approvedOnly = isAdmin() ? 'false' : 'true'
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
      setLoading(false)
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
    const teamName = employee.team_name || employee.team?.name || ''
    const matchesSearch = employee.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         employee.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         teamName.toLowerCase().includes(searchTerm.toLowerCase())
    
    // Convertir boolean a string para comparar con el filtro
    let employeeStatus = 'pending'
    if (employee.approved === true) {
      employeeStatus = 'approved'
    } else if (employee.approved === false) {
      employeeStatus = 'pending'
    }
    
    const matchesStatus = statusFilter === 'all' || employeeStatus === statusFilter
    const matchesTeam = teamFilter === 'all' || teamName === teamFilter
    
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
          alert('El empleado ya está aprobado o hay un conflicto. Recargando datos...')
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
      }
    } catch (error) {
      console.error('Error aprobando empleado:', error)
      alert(`Error al aprobar empleado: ${error.message}. Por favor, intenta de nuevo.`)
    }
  }

  const handleChangeRole = async (employee, newRole) => {
    if (!employee.user_id) {
      alert('No se puede cambiar el rol: usuario no encontrado')
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
        alert('Rol actualizado exitosamente')
      }
    } catch (error) {
      console.error('Error cambiando rol:', error)
      alert(`Error al cambiar rol: ${error.message}`)
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
                <SelectItem value="Frontend Development">Frontend Development</SelectItem>
                <SelectItem value="Backend Development">Backend Development</SelectItem>
                <SelectItem value="QA Testing">QA Testing</SelectItem>
                <SelectItem value="UI/UX Design">UI/UX Design</SelectItem>
                <SelectItem value="DevOps">DevOps</SelectItem>
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
                    
                    <TableCell>
                      <Badge variant="outline">
                        {employee.team_name || employee.team?.name || 'Sin equipo'}
                      </Badge>
                    </TableCell>
                    
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
                          onClick={() => {
                            setSelectedEmployee(employee)
                            setShowEmployeeDetail(true)
                          }}
                        >
                          <Eye className="w-4 h-4" />
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
                      <div className="flex items-center space-x-3">
                        <Mail className="w-4 h-4 text-gray-400" />
                        <span>{selectedEmployee.email}</span>
                      </div>
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
                        <span>Inicio: {new Date(selectedEmployee.start_date).toLocaleDateString('es-ES')}</span>
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
                    </CardContent>
                  </Card>
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
                          <span className="font-medium">{selectedEmployee.annual_stats?.total_actual_hours || 0}h</span>
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

      {/* Modal de invitación */}
      <InviteEmployeeModal
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        onInviteSuccess={(invitation) => {
          console.log('Invitación enviada:', invitation)
          // Opcional: mostrar toast de éxito
          loadEmployees() // Recargar lista si es necesario
        }}
      />
    </div>
  )
}

export default EmployeesPage
