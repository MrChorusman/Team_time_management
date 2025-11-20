import { useState, useEffect } from 'react'
import { 
  Settings, 
  Users, 
  Database, 
  Shield, 
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Download,
  Upload,
  Trash2,
  RefreshCw,
  Server,
  Mail,
  Globe,
  HardDrive,
  Cpu,
  BarChart3,
  Edit,
  XCircle,
  Search,
  Building,
  UserPlus,
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { StatsCard } from '../components/ui/stats-card'
import { Progress } from '../components/ui/progress'
import { Switch } from '../components/ui/switch'
import { Label } from '../components/ui/label'
import { Input } from '../components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table'
import { Alert, AlertDescription } from '../components/ui/alert'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../components/ui/dialog'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '../components/ui/dropdown-menu'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import { useToast } from '../components/ui/use-toast'

const AdminPage = () => {
  const { user, isAdmin } = useAuth()
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState(null)
  const [users, setUsers] = useState([])
  const [teams, setTeams] = useState([])
  const [roles, setRoles] = useState([])
  const [usersLoading, setUsersLoading] = useState(false)
  const [usersPage, setUsersPage] = useState(1)
  const [usersPerPage] = useState(20)
  const [usersTotal, setUsersTotal] = useState(0)
  const [usersFilter, setUsersFilter] = useState({ role: '', active_only: false })
  const [usersSearch, setUsersSearch] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [showUserDialog, setShowUserDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showRoleDialog, setShowRoleDialog] = useState(false)
  const [showTeamDialog, setShowTeamDialog] = useState(false)
  const [companies, setCompanies] = useState([])
  const [companiesLoading, setCompaniesLoading] = useState(false)
  const [selectedCompany, setSelectedCompany] = useState(null)
  const [showCompanyDialog, setShowCompanyDialog] = useState(false)
  const [showDeleteCompanyDialog, setShowDeleteCompanyDialog] = useState(false)
  const [companyForm, setCompanyForm] = useState({
    name: '',
    billing_period_start_day: 1,
    billing_period_end_day: 31,
    active: true
  })
  const [activeTab, setActiveTab] = useState('overview')
  const [systemSettings, setSystemSettings] = useState({
    maintenance_mode: false,
    user_registration: true,
    email_notifications: true,
    automatic_backups: true,
    holiday_sync: true,
    max_vacation_days: 25,
    max_hld_hours: 80,
    summer_hours: 7
  })
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    if (!isAdmin()) {
      return
    }
    loadDashboardData()
    loadTeams()
    loadRoles()
    loadCompanies()
  }, [])

  useEffect(() => {
    if (isAdmin()) {
      loadUsers()
    }
  }, [usersPage, usersFilter])

  const loadDashboardData = async (options = {}) => {
    if (!options.silent) {
      setLoading(true)
    }
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/dashboard`, {
        credentials: 'include'
      })
      
      if (!response.ok) {
        throw new Error('Error cargando dashboard')
      }
      
      const data = await response.json()
      setDashboardData(data.dashboard)
      return data.dashboard
    } catch (error) {
      console.error('Error cargando datos del sistema:', error)
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los datos del sistema',
        variant: 'destructive'
      })
      return null
    } finally {
      if (!options.silent) {
        setLoading(false)
      }
    }
  }

  const loadUsers = async () => {
    setUsersLoading(true)
    try {
      const params = new URLSearchParams({
        page: usersPage.toString(),
        per_page: usersPerPage.toString()
      })
      
      if (usersFilter.role) {
        params.append('role', usersFilter.role)
      }
      
      if (usersFilter.active_only) {
        params.append('active_only', 'true')
      }

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/users?${params}`, {
        credentials: 'include'
      })
      
      if (!response.ok) {
        throw new Error('Error cargando usuarios')
      }
      
      const data = await response.json()
      setUsers(data.users)
      setUsersTotal(data.pagination.total)
    } catch (error) {
      console.error('Error cargando usuarios:', error)
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los usuarios',
        variant: 'destructive'
      })
    } finally {
      setUsersLoading(false)
    }
  }

  const loadTeams = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/teams`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setTeams(data.teams || [])
      }
    } catch (error) {
      console.error('Error cargando equipos:', error)
    }
  }

  const loadRoles = async () => {
    // Roles comunes del sistema
    setRoles([
      { name: 'admin', description: 'Administrador' },
      { name: 'manager', description: 'Manager' },
      { name: 'employee', description: 'Empleado' },
      { name: 'viewer', description: 'Visualizador' }
    ])
  }

  const loadCompanies = async () => {
    setCompaniesLoading(true)
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/companies`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setCompanies(data.companies || [])
        }
      }
    } catch (error) {
      console.error('Error cargando empresas:', error)
      toast({
        title: 'Error',
        description: 'Error cargando empresas',
        variant: 'destructive'
      })
    } finally {
      setCompaniesLoading(false)
    }
  }

  const handleRefreshAll = async () => {
    setRefreshing(true)
    try {
      await Promise.all([
        loadDashboardData({ silent: true }),
        loadUsers(),
        loadCompanies(),
        loadTeams()
      ])
    } catch (error) {
      console.error('Error actualizando panel de administración:', error)
      toast({
        title: 'Error',
        description: 'No se pudo actualizar el panel. Intenta de nuevo.',
        variant: 'destructive'
      })
    } finally {
      setRefreshing(false)
    }
  }

  const handleCreateCompany = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/companies`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(companyForm)
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.message || 'Error creando empresa')
      }
      
      const data = await response.json()
      toast({
        title: 'Éxito',
        description: data.message || 'Empresa creada exitosamente'
      })
      
      setShowCompanyDialog(false)
      setCompanyForm({
        name: '',
        billing_period_start_day: 1,
        billing_period_end_day: 31,
        active: true
      })
      loadCompanies()
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const handleUpdateCompany = async () => {
    if (!selectedCompany) return
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/companies/${selectedCompany.id}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(companyForm)
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.message || 'Error actualizando empresa')
      }
      
      const data = await response.json()
      toast({
        title: 'Éxito',
        description: data.message || 'Empresa actualizada exitosamente'
      })
      
      setShowCompanyDialog(false)
      setSelectedCompany(null)
      setCompanyForm({
        name: '',
        billing_period_start_day: 1,
        billing_period_end_day: 31,
        active: true
      })
      loadCompanies()
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const handleDeleteCompany = async () => {
    if (!selectedCompany) return
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/companies/${selectedCompany.id}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.message || 'Error eliminando empresa')
      }
      
      const data = await response.json()
      toast({
        title: 'Éxito',
        description: data.message || 'Empresa desactivada exitosamente'
      })
      
      setShowDeleteCompanyDialog(false)
      setSelectedCompany(null)
      loadCompanies()
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const openCompanyDialog = (company = null) => {
    if (company) {
      setSelectedCompany(company)
      setCompanyForm({
        name: company.name,
        billing_period_start_day: company.billing_period_start_day,
        billing_period_end_day: company.billing_period_end_day,
        active: company.active
      })
    } else {
      setSelectedCompany(null)
      setCompanyForm({
        name: '',
        billing_period_start_day: 1,
        billing_period_end_day: 31,
        active: true
      })
    }
    setShowCompanyDialog(true)
  }

  const handleToggleUserActive = async (userId) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/users/${userId}/toggle-active`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.message || 'Error activando/desactivando usuario')
      }
      
      const data = await response.json()
      toast({
        title: 'Éxito',
        description: data.message
      })
      
      loadUsers()
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const handleUpdateRoles = async (userId, roleNames) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/users/${userId}/roles`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role_names: roleNames })
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.message || 'Error actualizando roles')
      }
      
      const data = await response.json()
      toast({
        title: 'Éxito',
        description: data.message
      })
      
      setShowRoleDialog(false)
      setSelectedUser(null)
      loadUsers()
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const handleDeleteUser = async () => {
    if (!selectedUser) return
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/users/${selectedUser.id}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.message || 'Error eliminando usuario')
      }
      
      const data = await response.json()
      toast({
        title: 'Éxito',
        description: data.message
      })
      
      setShowDeleteDialog(false)
      setSelectedUser(null)
      loadUsers()
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const handleApproveEmployee = async (employeeId) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees/${employeeId}/approve`, {
        method: 'POST',
        credentials: 'include'
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.message || 'Error aprobando empleado')
      }
      
      const data = await response.json()
      toast({
        title: 'Éxito',
        description: data.message || 'Empleado aprobado exitosamente'
      })
      
      loadUsers()
      loadDashboardData()
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const handleChangeTeam = async (employeeId, teamId) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees/${employeeId}/change-team`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ team_id: teamId })
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.message || 'Error cambiando equipo')
      }
      
      const data = await response.json()
      toast({
        title: 'Éxito',
        description: data.message
      })
      
      setShowTeamDialog(false)
      setSelectedUser(null)
      loadUsers()
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const handleSettingChange = async (setting, value) => {
    setSystemSettings(prev => ({
      ...prev,
      [setting]: value
    }))
    
    // TODO: Implementar guardado real de configuración
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
      console.log(`Configuración ${setting} actualizada a:`, value)
    } catch (error) {
      console.error('Error actualizando configuración:', error)
    }
  }

  const handleSystemAction = async (action) => {
    setLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      switch (action) {
        case 'backup':
          console.log('Backup manual iniciado')
          break
        case 'sync_holidays':
          console.log('Sincronización de festivos iniciada')
          break
        case 'clear_cache':
          console.log('Cache limpiado')
          break
        case 'export_data':
          console.log('Exportación de datos iniciada')
          break
        default:
          console.log('Acción desconocida:', action)
      }
    } catch (error) {
      console.error('Error ejecutando acción:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    const colors = {
      success: 'text-green-600',
      info: 'text-blue-600',
      warning: 'text-yellow-600',
      error: 'text-red-600'
    }
    return colors[severity] || colors.info
  }

  const getSeverityIcon = (severity) => {
    const icons = {
      success: <CheckCircle className="w-4 h-4" />,
      info: <Activity className="w-4 h-4" />,
      warning: <AlertTriangle className="w-4 h-4" />,
      error: <AlertTriangle className="w-4 h-4" />
    }
    return icons[severity] || icons.info
  }

  const filteredUsers = users.filter(u => {
    if (usersSearch) {
      const searchLower = usersSearch.toLowerCase()
      return (
        u.email?.toLowerCase().includes(searchLower) ||
        u.full_name?.toLowerCase().includes(searchLower) ||
        u.employee?.full_name?.toLowerCase().includes(searchLower) ||
        u.employee?.team?.name?.toLowerCase().includes(searchLower)
      )
    }
    return true
  })

  if (!isAdmin()) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Alert className="max-w-md">
          <Shield className="h-4 w-4" />
          <AlertDescription>
            No tienes permisos para acceder a esta página. Solo los administradores pueden ver el panel de administración.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  if (loading && !dashboardData) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Administración</h1>
        </div>
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" text="Cargando panel de administración..." />
        </div>
      </div>
    )
  }

  const stats = dashboardData?.statistics || {}
  const recentActivity = dashboardData?.recent_activity || []
  const roleDistribution = dashboardData?.role_distribution || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Panel de Administración</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestión del sistema y configuración global
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => handleSystemAction('backup')} disabled={loading}>
            {loading ? <LoadingSpinner size="sm" /> : <Download className="w-4 h-4 mr-2" />}
            Backup Manual
          </Button>
          <Button variant="outline" onClick={handleRefreshAll} disabled={refreshing}>
            {refreshing ? <LoadingSpinner size="sm" /> : <RefreshCw className="w-4 h-4 mr-2" />}
            {refreshing ? 'Actualizando...' : 'Actualizar'}
          </Button>
        </div>
      </div>

      {/* Contenido principal */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Resumen</TabsTrigger>
          <TabsTrigger value="users">Usuarios</TabsTrigger>
          <TabsTrigger value="companies">Empresas</TabsTrigger>
          <TabsTrigger value="system">Sistema</TabsTrigger>
          <TabsTrigger value="settings">Configuración</TabsTrigger>
        </TabsList>

        {/* Pestaña de Resumen */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Estadísticas del sistema */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Estadísticas del Sistema
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData ? (
                    <>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Usuarios Totales</span>
                          <span className="text-sm font-medium">{stats.users?.total || 0} ({stats.users?.active || 0} activos)</span>
                  </div>
                        <Progress value={stats.users?.total > 0 ? ((stats.users?.active || 0) / stats.users.total) * 100 : 0} className="h-2" />
                  </div>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Empleados</span>
                          <span className="text-sm font-medium">{stats.employees?.total || 0} ({stats.employees?.approved || 0} aprobados)</span>
                  </div>
                        <Progress value={stats.employees?.total > 0 ? ((stats.employees?.approved || 0) / stats.employees.total) * 100 : 0} className="h-2" />
                </div>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Equipos</span>
                          <span className="text-sm font-medium">{stats.teams?.total || 0} ({stats.teams?.with_manager || 0} con manager)</span>
                    </div>
                        <Progress value={stats.teams?.total > 0 ? ((stats.teams?.with_manager || 0) / stats.teams.total) * 100 : 0} className="h-2" />
                    </div>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Aprobaciones Pendientes</span>
                          <span className="text-sm font-medium">{stats.employees?.pending_approval || 0}</span>
                  </div>
                        <Progress value={stats.employees?.pending_approval > 0 ? Math.min((stats.employees.pending_approval / (stats.employees?.total || 1)) * 100, 100) : 0} className="h-2" />
                      </div>
                    </>
                  ) : (
                    <p className="text-sm text-gray-500">Cargando datos...</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Distribución de roles */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  Distribución de Roles
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {roleDistribution.length > 0 ? (
                    roleDistribution.map((role) => {
                      const total = stats.users?.total || 1
                      const percentage = (role.user_count / total) * 100
                      return (
                        <div key={role.role} className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm capitalize">{role.description || role.role}</span>
                            <span className="text-sm font-medium">{role.user_count} usuarios</span>
                          </div>
                          <Progress value={percentage} className="h-2" />
                        </div>
                      )
                    })
                  ) : (
                    <p className="text-sm text-gray-500">No hay datos disponibles</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Actividad reciente */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="w-5 h-5 mr-2" />
                  Actividad Reciente
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentActivity.length > 0 ? (
                    recentActivity.slice(0, 5).map((activity, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className={`mt-1 ${getSeverityColor(activity.severity || 'info')}`}>
                          {getSeverityIcon(activity.severity || 'info')}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{activity.description}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(activity.timestamp).toLocaleString('es-ES')}
                        </p>
                      </div>
                    </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500">No hay actividad reciente</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Pestaña de Usuarios */}
        <TabsContent value="users" className="space-y-6">
          {/* Gestión de Usuarios - PRIMERO */}
          <Card>
            <CardHeader>
              <CardTitle>Gestión de Usuarios</CardTitle>
              <CardDescription>
                Administra usuarios, roles y equipos del sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Filtros y búsqueda */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="Buscar por email, nombre o equipo..."
                      value={usersSearch}
                      onChange={(e) => setUsersSearch(e.target.value)}
                      className="pl-10"
                    />
                </div>
                </div>
                
                <Select 
                  value={usersFilter.role || "all"} 
                  onValueChange={(value) => setUsersFilter(prev => ({ ...prev, role: value === "all" ? "" : value }))}
                >
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Filtrar por rol" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los roles</SelectItem>
                    {roles.map(role => (
                      <SelectItem key={role.name} value={role.name}>
                        {role.description}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                <Button
                  variant={usersFilter.active_only ? "default" : "outline"}
                  onClick={() => setUsersFilter(prev => ({ ...prev, active_only: !prev.active_only }))}
                >
                  {usersFilter.active_only ? 'Solo activos' : 'Todos'}
                </Button>
                </div>

              {/* Tabla de usuarios */}
              {usersLoading ? (
                <div className="flex justify-center py-8">
                  <LoadingSpinner />
                </div>
              ) : filteredUsers.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-500">No se encontraron usuarios</p>
                </div>
              ) : (
                <>
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Usuario</TableHead>
                          <TableHead>Email</TableHead>
                          <TableHead>Roles</TableHead>
                          <TableHead>Empleado</TableHead>
                          <TableHead>Equipo</TableHead>
                          <TableHead>Estado</TableHead>
                          <TableHead className="text-right">Acciones</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredUsers.map((u) => (
                          <TableRow key={u.id}>
                            <TableCell className="font-medium">
                              {u.full_name || u.username || 'N/A'}
                            </TableCell>
                            <TableCell>{u.email}</TableCell>
                            <TableCell>
                              <div className="flex flex-wrap gap-1">
                                {u.roles?.map((role, idx) => (
                                  <Badge key={idx} variant="outline">
                                    {role}
                                  </Badge>
                                ))}
                              </div>
                            </TableCell>
                            <TableCell>
                              {u.employee ? (
                                <Badge variant="secondary">{u.employee.full_name}</Badge>
                              ) : (
                                <span className="text-gray-400">-</span>
                              )}
                            </TableCell>
                            <TableCell>
                              {u.employee?.team?.name ? (
                                <Badge variant="outline">{u.employee.team.name}</Badge>
                              ) : (
                                <span className="text-gray-400">-</span>
                              )}
                            </TableCell>
                            <TableCell>
                              {u.active ? (
                                <Badge variant="default" className="bg-green-500">Activo</Badge>
                              ) : (
                                <Badge variant="secondary">Inactivo</Badge>
                              )}
                            </TableCell>
                            <TableCell className="text-right">
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="sm">
                                    <Edit className="w-4 h-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                                  <DropdownMenuSeparator />
                                  <DropdownMenuItem
                                    onSelect={(e) => {
                                      e.preventDefault()
                                      setSelectedUser(u)
                                      setShowRoleDialog(true)
                                    }}
                                  >
                                    <Edit className="w-4 h-4 mr-2" />
                                    Modificar Roles
                                  </DropdownMenuItem>
                                  {u.employee && (
                                    <>
                                      <DropdownMenuItem
                                        onSelect={(e) => {
                                          e.preventDefault()
                                          setSelectedUser(u)
                                          setShowTeamDialog(true)
                                        }}
                                      >
                                        <Building className="w-4 h-4 mr-2" />
                                        Cambiar Equipo
                                      </DropdownMenuItem>
                                      {u.employee.approved === false && (
                                        <DropdownMenuItem
                                          onSelect={(e) => {
                                            e.preventDefault()
                                            handleApproveEmployee(u.employee.id)
                                          }}
                                        >
                                          <CheckCircle className="w-4 h-4 mr-2" />
                                          Aprobar Empleado
                                        </DropdownMenuItem>
                                      )}
                                    </>
                                  )}
                                  <DropdownMenuItem
                                    onSelect={(e) => {
                                      e.preventDefault()
                                      handleToggleUserActive(u.id)
                                    }}
                                    disabled={u.id === user?.id}
                                  >
                                    {u.active ? (
                                      <>
                                        <XCircle className="w-4 h-4 mr-2" />
                                        Desactivar
                                      </>
                                    ) : (
                                      <>
                                        <CheckCircle className="w-4 h-4 mr-2" />
                                        Activar
                                      </>
                                    )}
                                  </DropdownMenuItem>
                                  <DropdownMenuSeparator />
                                  <DropdownMenuItem
                                    onSelect={(e) => {
                                      e.preventDefault()
                                      setSelectedUser(u)
                                      setShowDeleteDialog(true)
                                    }}
                                    disabled={u.id === user?.id}
                                    className="text-red-600"
                                  >
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Eliminar
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>

                  {/* Paginación */}
                  {usersTotal > usersPerPage && (
                    <div className="flex items-center justify-between mt-4">
                      <p className="text-sm text-gray-500">
                        Mostrando {((usersPage - 1) * usersPerPage) + 1} - {Math.min(usersPage * usersPerPage, usersTotal)} de {usersTotal} usuarios
                      </p>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setUsersPage(prev => Math.max(1, prev - 1))}
                          disabled={usersPage === 1}
                        >
                          Anterior
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setUsersPage(prev => prev + 1)}
                          disabled={usersPage * usersPerPage >= usersTotal}
                        >
                          Siguiente
                        </Button>
                </div>
              </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>

          {/* Estadísticas de usuarios en formato de barras */}
            <Card>
              <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Estadísticas de Usuarios
              </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                {dashboardData ? (
                  <>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Usuarios Totales</span>
                        <span className="text-sm font-medium">{stats.users?.total || 0} ({stats.users?.active || 0} activos)</span>
                      </div>
                      <Progress value={stats.users?.total > 0 ? ((stats.users?.active || 0) / stats.users.total) * 100 : 0} className="h-2" />
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Empleados</span>
                        <span className="text-sm font-medium">{stats.employees?.total || 0} ({stats.employees?.approved || 0} aprobados)</span>
                      </div>
                      <Progress value={stats.employees?.total > 0 ? ((stats.employees?.approved || 0) / stats.employees.total) * 100 : 0} className="h-2" />
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Aprobaciones Pendientes</span>
                        <span className="text-sm font-medium">{stats.employees?.pending_approval || 0}</span>
                      </div>
                      <Progress value={stats.employees?.pending_approval > 0 ? Math.min((stats.employees.pending_approval / (stats.employees?.total || 1)) * 100, 100) : 0} className="h-2" />
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-gray-500">Cargando datos...</p>
                )}
                </div>
              </CardContent>
            </Card>
        </TabsContent>

        {/* Pestaña de Empresas */}
        <TabsContent value="companies" className="space-y-6">
            <Card>
              <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Gestión de Empresas</CardTitle>
                  <CardDescription>
                    Administra las empresas/clientes y sus períodos de facturación para el cálculo de forecast
                  </CardDescription>
                </div>
                <Button onClick={() => openCompanyDialog()}>
                  <Building className="w-4 h-4 mr-2" />
                  Nueva Empresa
                </Button>
              </div>
              </CardHeader>
              <CardContent>
              {companiesLoading ? (
                <div className="flex items-center justify-center py-12">
                  <LoadingSpinner />
                    </div>
              ) : companies.length === 0 ? (
                <Alert>
                  <AlertTriangle className="w-4 h-4" />
                  <AlertDescription>
                    No hay empresas registradas. Crea una nueva empresa para comenzar a usar el sistema de forecast.
                  </AlertDescription>
                </Alert>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nombre</TableHead>
                      <TableHead>Período de Facturación</TableHead>
                      <TableHead>Estado</TableHead>
                      <TableHead className="text-right">Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {companies.map((company) => (
                      <TableRow key={company.id}>
                        <TableCell className="font-medium">{company.name}</TableCell>
                        <TableCell>
                          <div className="text-sm">
                            Día {company.billing_period_start_day} - Día {company.billing_period_end_day}
                            {company.billing_period_start_day > company.billing_period_end_day && (
                              <span className="text-gray-500 ml-1">(cruza meses)</span>
                            )}
                </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={company.active ? 'default' : 'secondary'}>
                            {company.active ? 'Activa' : 'Inactiva'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end space-x-2">
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => openCompanyDialog(company)}
                              aria-label={`Editar empresa ${company.name}`}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="text-red-600 hover:text-red-700"
                              onClick={() => {
                                setSelectedCompany(company)
                                setShowDeleteCompanyDialog(true)
                              }}
                              aria-label={`Desactivar empresa ${company.name}`}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
              </CardContent>
            </Card>
        </TabsContent>

        {/* Pestaña de Sistema */}
        <TabsContent value="system" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Acciones del Sistema</CardTitle>
                <CardDescription>
                  Operaciones de mantenimiento y administración
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleSystemAction('backup')}
                  disabled={loading}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Crear Backup Manual
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleSystemAction('sync_holidays')}
                  disabled={loading}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Sincronizar Festivos
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleSystemAction('clear_cache')}
                  disabled={loading}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Limpiar Cache
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleSystemAction('export_data')}
                  disabled={loading}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Exportar Datos
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Información del Sistema</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Versión</p>
                    <p className="font-medium">v2.1.0</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Entorno</p>
                    <p className="font-medium">Producción</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Base de Datos</p>
                    <p className="font-medium">PostgreSQL 15</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Servidor</p>
                    <p className="font-medium">Render</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Pestaña de Configuración */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configuración del Sistema</CardTitle>
              <CardDescription>
                Ajustes globales de la aplicación
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-medium">Configuración General</h4>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="maintenance_mode">Modo Mantenimiento</Label>
                      <p className="text-sm text-gray-500">Deshabilitar acceso temporal</p>
                    </div>
                    <Switch
                      id="maintenance_mode"
                      checked={systemSettings.maintenance_mode}
                      onCheckedChange={(checked) => handleSettingChange('maintenance_mode', checked)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="user_registration">Registro de Usuarios</Label>
                      <p className="text-sm text-gray-500">Permitir nuevos registros</p>
                    </div>
                    <Switch
                      id="user_registration"
                      checked={systemSettings.user_registration}
                      onCheckedChange={(checked) => handleSettingChange('user_registration', checked)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="email_notifications">Notificaciones Email</Label>
                      <p className="text-sm text-gray-500">Sistema de emails automático</p>
                    </div>
                    <Switch
                      id="email_notifications"
                      checked={systemSettings.email_notifications}
                      onCheckedChange={(checked) => handleSettingChange('email_notifications', checked)}
                    />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-medium">Configuración de Negocio</h4>
                  
                  <div>
                    <Label htmlFor="max_vacation_days">Días de Vacaciones Máximos</Label>
                    <Input
                      id="max_vacation_days"
                      type="number"
                      value={systemSettings.max_vacation_days}
                      onChange={(e) => handleSettingChange('max_vacation_days', parseInt(e.target.value))}
                      className="mt-1"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="max_hld_hours">Horas HLD Máximas</Label>
                    <Input
                      id="max_hld_hours"
                      type="number"
                      value={systemSettings.max_hld_hours}
                      onChange={(e) => handleSettingChange('max_hld_hours', parseInt(e.target.value))}
                      className="mt-1"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="summer_hours">Horas de Verano (Julio-Agosto)</Label>
                    <Input
                      id="summer_hours"
                      type="number"
                      value={systemSettings.summer_hours}
                      onChange={(e) => handleSettingChange('summer_hours', parseInt(e.target.value))}
                      className="mt-1"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Dialog para modificar roles */}
      <Dialog open={showRoleDialog} onOpenChange={setShowRoleDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Modificar Roles</DialogTitle>
            <DialogDescription>
              Selecciona los roles para {selectedUser?.email}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {roles.map(role => {
              const isSelected = selectedUser?.roles?.includes(role.name)
              return (
                <div key={role.name} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={`role-${role.name}`}
                    checked={isSelected}
                    onChange={(e) => {
                      const currentRoles = selectedUser?.roles || []
                      if (e.target.checked) {
                        setSelectedUser({
                          ...selectedUser,
                          roles: [...currentRoles, role.name]
                        })
                      } else {
                        setSelectedUser({
                          ...selectedUser,
                          roles: currentRoles.filter(r => r !== role.name)
                        })
                      }
                    }}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor={`role-${role.name}`} className="cursor-pointer">
                    {role.description}
                  </Label>
                          </div>
              )
            })}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRoleDialog(false)}>
              Cancelar
            </Button>
            <Button
              onClick={() => {
                if (selectedUser) {
                  handleUpdateRoles(selectedUser.id, selectedUser.roles || [])
                }
              }}
            >
              Guardar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog para eliminar usuario */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Eliminar Usuario</DialogTitle>
            <DialogDescription>
              ¿Estás seguro de que deseas eliminar a {selectedUser?.email}? Esta acción no se puede deshacer.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleDeleteUser}>
              Eliminar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog para cambiar equipo */}
      <Dialog open={showTeamDialog} onOpenChange={setShowTeamDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cambiar Equipo</DialogTitle>
            <DialogDescription>
              Selecciona el nuevo equipo para {selectedUser?.employee?.full_name || selectedUser?.email}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Select
              defaultValue={selectedUser?.employee?.team_id?.toString()}
              onValueChange={(value) => {
                if (selectedUser?.employee?.id) {
                  handleChangeTeam(selectedUser.employee.id, parseInt(value))
                }
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecciona un equipo" />
              </SelectTrigger>
              <SelectContent>
                {teams.map(team => (
                  <SelectItem key={team.id} value={team.id.toString()}>
                    {team.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
              </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowTeamDialog(false)}>
              Cerrar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog para crear/editar empresa */}
      <Dialog open={showCompanyDialog} onOpenChange={setShowCompanyDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{selectedCompany ? 'Editar Empresa' : 'Nueva Empresa'}</DialogTitle>
            <DialogDescription>
              {selectedCompany 
                ? 'Modifica los datos de la empresa y su período de facturación'
                : 'Crea una nueva empresa con su período de facturación personalizado'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="company-name">Nombre de la Empresa</Label>
              <Input
                id="company-name"
                value={companyForm.name}
                onChange={(e) => setCompanyForm({ ...companyForm, name: e.target.value })}
                placeholder="Ej: Cliente ABC S.L."
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="billing-start">Día de Inicio</Label>
                <Input
                  id="billing-start"
                  type="number"
                  min="1"
                  max="31"
                  value={companyForm.billing_period_start_day}
                  onChange={(e) => setCompanyForm({ ...companyForm, billing_period_start_day: parseInt(e.target.value) || 1 })}
                />
                <p className="text-xs text-gray-500">Día del mes (1-31)</p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="billing-end">Día de Fin</Label>
                <Input
                  id="billing-end"
                  type="number"
                  min="1"
                  max="31"
                  value={companyForm.billing_period_end_day}
                  onChange={(e) => setCompanyForm({ ...companyForm, billing_period_end_day: parseInt(e.target.value) || 31 })}
                />
                <p className="text-xs text-gray-500">Día del mes (1-31)</p>
              </div>
            </div>
            
            {companyForm.billing_period_start_day > companyForm.billing_period_end_day && (
              <Alert>
                <AlertTriangle className="w-4 h-4" />
                <AlertDescription>
                  El período cruza meses. Ejemplo: Día {companyForm.billing_period_start_day} del mes anterior al Día {companyForm.billing_period_end_day} del mes actual.
                </AlertDescription>
              </Alert>
            )}
            
            <div className="flex items-center space-x-2">
              <Switch
                id="company-active"
                checked={companyForm.active}
                onCheckedChange={(checked) => setCompanyForm({ ...companyForm, active: checked })}
              />
              <Label htmlFor="company-active">Empresa activa</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCompanyDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={selectedCompany ? handleUpdateCompany : handleCreateCompany}>
              {selectedCompany ? 'Actualizar' : 'Crear'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog para eliminar empresa */}
      <Dialog open={showDeleteCompanyDialog} onOpenChange={setShowDeleteCompanyDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Desactivar Empresa</DialogTitle>
            <DialogDescription>
              ¿Estás seguro de que deseas desactivar la empresa "{selectedCompany?.name}"? 
              Esta acción no eliminará los datos históricos de forecast, pero la empresa no aparecerá en los listados activos.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteCompanyDialog(false)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleDeleteCompany}>
              Desactivar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default AdminPage
