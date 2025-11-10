import { useState, useEffect } from 'react'
import { 
  Users, 
  Search, 
  Filter, 
  Plus,
  Download,
  Eye,
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
  AlertCircle
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

const EmployeesPage = () => {
  const { user, isAdmin, isManager, isEmployee } = useAuth()
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [teamFilter, setTeamFilter] = useState('all')
  const [selectedEmployee, setSelectedEmployee] = useState(null)
  const [showEmployeeDetail, setShowEmployeeDetail] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)

  useEffect(() => {
    loadEmployees()
  }, [statusFilter, teamFilter])

  const loadEmployees = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees`, {
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


  const getStatusColor = (status) => {
    const colors = {
      approved: 'bg-green-100 text-green-800 border-green-200',
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      rejected: 'bg-red-100 text-red-800 border-red-200'
    }
    return colors[status] || colors.pending
  }

  const getStatusLabel = (status) => {
    const labels = {
      approved: 'Aprobado',
      pending: 'Pendiente',
      rejected: 'Rechazado'
    }
    return labels[status] || 'Desconocido'
  }

  const getStatusIcon = (status) => {
    const icons = {
      approved: <CheckCircle className="w-4 h-4" />,
      pending: <Clock className="w-4 h-4" />,
      rejected: <XCircle className="w-4 h-4" />
    }
    return icons[status] || icons.pending
  }

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
  }

  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = employee.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         employee.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         employee.team.name.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === 'all' || employee.approved === statusFilter
    const matchesTeam = teamFilter === 'all' || employee.team.name === teamFilter
    
    return matchesSearch && matchesStatus && matchesTeam
  })

  const paginatedEmployees = filteredEmployees.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const totalPages = Math.ceil(filteredEmployees.length / itemsPerPage)

  const handleApproveEmployee = async (employeeId) => {
    try {
      // Simular aprobación
      setEmployees(prev => prev.map(emp => 
        emp.id === employeeId ? { ...emp, approved: 'approved' } : emp
      ))
    } catch (error) {
      console.error('Error aprobando empleado:', error)
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

  const getEmployeeStats = () => {
    const total = employees.length
    const approved = employees.filter(e => e.approved === 'approved').length
    const pending = employees.filter(e => e.approved === 'pending').length
    const rejected = employees.filter(e => e.approved === 'rejected').length
    
    return { total, approved, pending, rejected }
  }

  const stats = getEmployeeStats()

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
    <div className="space-y-6">
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
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Invitar Empleado
            </Button>
          )}
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatsCard
          title="Total Empleados"
          value={stats.total}
          subtitle="Registrados en el sistema"
          icon={Users}
          variant="info"
        />
        <StatsCard
          title="Aprobados"
          value={stats.approved}
          subtitle="Empleados activos"
          icon={CheckCircle}
          variant="success"
        />
        <StatsCard
          title="Pendientes"
          value={stats.pending}
          subtitle="Esperando aprobación"
          icon={Clock}
          variant="warning"
        />
        <StatsCard
          title="Rechazados"
          value={stats.rejected}
          subtitle="Registros rechazados"
          icon={XCircle}
          variant="danger"
        />
      </div>

      {/* Filtros y búsqueda */}
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
                  <TableHead>Última Actividad</TableHead>
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
                        {employee.team.name}
                      </Badge>
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                        <MapPin className="w-4 h-4 mr-1" />
                        {employee.city}, {employee.country}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <Badge className={getStatusColor(employee.approved)}>
                        {getStatusIcon(employee.approved)}
                        <span className="ml-1">{getStatusLabel(employee.approved)}</span>
                      </Badge>
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <div className="w-16">
                          <Progress value={employee.monthly_stats.efficiency} className="h-2" />
                        </div>
                        <span className="text-sm font-medium">
                          {employee.monthly_stats.efficiency}%
                        </span>
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {new Date(employee.last_activity).toLocaleDateString('es-ES')}
                      </span>
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
                        
                        {(isAdmin() || isManager()) && employee.approved === 'pending' && (
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
                        
                        {(isAdmin() || isManager()) && (
                          <Button variant="ghost" size="sm">
                            <Edit className="w-4 h-4" />
                          </Button>
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
                        <span>{selectedEmployee.team.name}</span>
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
                        <Badge className={getStatusColor(selectedEmployee.approved)}>
                          {getStatusIcon(selectedEmployee.approved)}
                          <span className="ml-1">{getStatusLabel(selectedEmployee.approved)}</span>
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
                          <span className="font-medium">{selectedEmployee.monthly_stats.theoretical_hours}h</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Horas Reales:</span>
                          <span className="font-medium">{selectedEmployee.monthly_stats.actual_hours}h</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Eficiencia:</span>
                          <span className="font-medium">{selectedEmployee.monthly_stats.efficiency}%</span>
                        </div>
                        <Progress value={selectedEmployee.monthly_stats.efficiency} className="h-2" />
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
                          <span className="font-medium">{selectedEmployee.annual_stats.total_actual_hours}h</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Eficiencia Anual:</span>
                          <span className="font-medium">{selectedEmployee.annual_stats.total_efficiency}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Vacaciones Restantes:</span>
                          <span className="font-medium">{selectedEmployee.annual_stats.remaining_vacation_days} días</span>
                        </div>
                        <div className="flex justify-between">
                          <span>HLD Restantes:</span>
                          <span className="font-medium">{selectedEmployee.annual_stats.remaining_hld_hours}h</span>
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
                            {new Date(selectedEmployee.last_activity).toLocaleDateString('es-ES')}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
            
            {(isAdmin() || isManager()) && selectedEmployee.approved === 'pending' && (
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
    </div>
  )
}

export default EmployeesPage
