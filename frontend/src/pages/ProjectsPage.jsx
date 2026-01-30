import { useEffect, useMemo, useState } from 'react'
import { toast } from 'sonner'
import {
  Layers,
  Briefcase,
  Search,
  Filter,
  Users,
  Edit,
  Trash2,
  Plus
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Textarea } from '../components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Badge } from '../components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import teamService from '../services/teamService'
import projectService from '../services/projectService'
import { Label } from '../components/ui/label'

const statusOptions = [
  { value: 'planned', label: 'Planificado' },
  { value: 'in_progress', label: 'En progreso' },
  { value: 'paused', label: 'Pausado' },
  { value: 'closed', label: 'Cerrado' }
]

const statusStyles = {
  planned: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-green-100 text-green-800',
  paused: 'bg-yellow-100 text-yellow-800',
  closed: 'bg-gray-200 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
}

const initialFormState = {
  code: '',
  name: '',
  description: '',
  client_name: '',
  status: 'planned',
  service_line: '',
  billing_model: '',
  start_date: '',
  end_date: '',
  manager_id: '',
  budget_hours: '',
  budget_amount: '',
  team_ids: []
}

const initialAssignmentState = {
  employeeId: '',
  teamId: '',
  allocationPercent: '',
  role: ''
}

const ProjectsPage = () => {
  const { isAdmin, isManager } = useAuth()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ status: 'all', search: '', client: '' })
  const [showProjectDialog, setShowProjectDialog] = useState(false)
  const [currentProject, setCurrentProject] = useState(null)
  const [formData, setFormData] = useState(initialFormState)
  const [availableTeams, setAvailableTeams] = useState([])
  const [employeesOptions, setEmployeesOptions] = useState([])
  const [assignmentForm, setAssignmentForm] = useState(initialAssignmentState)
  const [savingProject, setSavingProject] = useState(false)
  const [savingAssignment, setSavingAssignment] = useState(false)

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

  useEffect(() => {
    loadProjects()
    loadTeams()
    loadEmployeesOptions()
  }, [])

  const hasAccess = isAdmin() || isManager()

  const filteredProjects = useMemo(() => {
    return projects.filter((project) => {
      const matchesStatus = filters.status === 'all' || project.status === filters.status
      const matchesClient = filters.client === '' || (project.client_name || '').toLowerCase().includes(filters.client.toLowerCase())
      const haystack = `${project.name} ${project.code || ''} ${project.client_name || ''}`.toLowerCase()
      const matchesSearch = filters.search === '' || haystack.includes(filters.search.toLowerCase())
      return matchesStatus && matchesClient && matchesSearch
    })
  }, [projects, filters])

  const loadProjects = async () => {
    try {
      setLoading(true)
      const response = await projectService.list({ include_assignments: true })
      if (response.success) {
        setProjects(response.projects || [])
        if (currentProject) {
          const updated = (response.projects || []).find((project) => project.id === currentProject.id)
          if (updated) {
            setCurrentProject(updated)
          }
        }
      }
    } catch (error) {
      console.error('Error cargando proyectos:', error)
      toast.error('Error al cargar proyectos')
    } finally {
      setLoading(false)
    }
  }

  const loadTeams = async () => {
    try {
      const response = await teamService.getAllTeams()
      if (response.success && response.teams) {
        setAvailableTeams(response.teams)
      }
    } catch (error) {
      console.error('Error cargando equipos:', error)
    }
  }

  const loadEmployeesOptions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/employees?approved_only=false&per_page=200`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setEmployeesOptions(data.employees || [])
        }
      }
    } catch (error) {
      console.error('Error cargando empleados:', error)
    }
  }

  const openProjectDialog = (project = null) => {
    if (project) {
      setCurrentProject(project)
      setFormData({
        code: project.code || '',
        name: project.name || '',
        description: project.description || '',
        client_name: project.client_name || '',
        status: project.status || 'planned',
        service_line: project.service_line || '',
        billing_model: project.billing_model || '',
        start_date: project.start_date || '',
        end_date: project.end_date || '',
        manager_id: project.manager_id ? project.manager_id.toString() : 'none',
        budget_hours: project.budget_hours ?? '',
        budget_amount: project.budget_amount ?? '',
        team_ids: (project.teams || []).map((team) => team.id)
      })
    } else {
      setCurrentProject(null)
      setFormData(initialFormState)
    }
    setShowProjectDialog(true)
  }

  const handleFormChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value
    }))
  }

  const toggleTeamSelection = (teamId) => {
    setFormData((prev) => {
      const exists = prev.team_ids.includes(teamId)
      return {
        ...prev,
        team_ids: exists ? prev.team_ids.filter((id) => id !== teamId) : [...prev.team_ids, teamId]
      }
    })
  }

  const handleSaveProject = async () => {
    if (!formData.code.trim() || !formData.name.trim()) {
      toast.error('El código y el nombre son obligatorios')
      return
    }

    const payload = {
      code: formData.code.trim(),
      name: formData.name.trim(),
      description: formData.description || null,
      client_name: formData.client_name || null,
      status: formData.status,
      service_line: formData.service_line || null,
      billing_model: formData.billing_model || null,
      start_date: formData.start_date || null,
      end_date: formData.end_date || null,
      manager_id: formData.manager_id && formData.manager_id !== 'none' ? parseInt(formData.manager_id, 10) : null,
      budget_hours: formData.budget_hours !== '' ? parseFloat(formData.budget_hours) : null,
      budget_amount: formData.budget_amount !== '' ? parseFloat(formData.budget_amount) : null,
      team_ids: formData.team_ids
    }

    try {
      setSavingProject(true)
      if (currentProject) {
        await projectService.update(currentProject.id, payload)
        toast.success('Proyecto actualizado')
      } else {
        await projectService.create(payload)
        toast.success('Proyecto creado')
      }
      setShowProjectDialog(false)
      loadProjects()
    } catch (error) {
      console.error('Error guardando proyecto:', error)
      toast.error('No se pudo guardar el proyecto', {
        description: error.response?.data?.message
      })
    } finally {
      setSavingProject(false)
    }
  }

  const handleDeleteProject = async (project) => {
    try {
      const confirmed = window.confirm(`¿Eliminar el proyecto ${project.name}?`)
      if (!confirmed) return
      await projectService.remove(project.id)
      toast.success('Proyecto eliminado')
      loadProjects()
    } catch (error) {
      console.error('Error eliminando proyecto:', error)
      toast.error('No se pudo eliminar el proyecto')
    }
  }

  const refreshCurrentProject = (updatedId) => {
    const project = projects.find((item) => item.id === updatedId)
    if (project) {
      setCurrentProject(project)
    }
  }

  const handleAssignmentChange = (field, value) => {
    setAssignmentForm((prev) => ({
      ...prev,
      [field]: value
    }))
  }

  const handleAddAssignment = async () => {
    if (!currentProject) return
    if (!assignmentForm.employeeId) {
      toast.error('Selecciona un empleado')
      return
    }

    const payload = {
      employee_id: parseInt(assignmentForm.employeeId, 10),
      team_id: assignmentForm.teamId ? parseInt(assignmentForm.teamId, 10) : null,
      role: assignmentForm.role || null,
      allocation_percent: assignmentForm.allocationPercent !== ''
        ? parseFloat(assignmentForm.allocationPercent)
        : null
    }

    try {
      setSavingAssignment(true)
      await projectService.addAssignment(currentProject.id, payload)
      toast.success('Asignación creada')
      setAssignmentForm(initialAssignmentState)
      await loadProjects()
    } catch (error) {
      console.error('Error creando asignación:', error)
      toast.error('No se pudo crear la asignación', {
        description: error.response?.data?.message
      })
    } finally {
      setSavingAssignment(false)
    }
  }

  const handleUpdateAssignment = async (assignmentId, allocationPercent) => {
    if (!currentProject) return
    try {
      await projectService.updateAssignment(currentProject.id, assignmentId, {
        allocation_percent: allocationPercent !== '' ? parseFloat(allocationPercent) : null
      })
      toast.success('Asignación actualizada')
      await loadProjects()
    } catch (error) {
      console.error('Error actualizando asignación:', error)
      toast.error('No se pudo actualizar la asignación')
    }
  }

  const handleRemoveAssignment = async (assignmentId) => {
    if (!currentProject) return
    try {
      await projectService.deleteAssignment(currentProject.id, assignmentId)
      toast.success('Asignación eliminada')
      await loadProjects()
    } catch (error) {
      console.error('Error eliminando asignación:', error)
      toast.error('No se pudo eliminar la asignación')
    }
  }

  const formatDate = (value) => {
    if (!value) return 'N/A'
    try {
      return new Date(value).toLocaleDateString('es-ES')
    } catch {
      return value
    }
  }

  if (!hasAccess) {
    return (
      <div className="px-6">
        <Card>
          <CardHeader>
            <CardTitle>Acceso restringido</CardTitle>
            <CardDescription>
              Solo los administradores o managers pueden gestionar proyectos.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6 px-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Proyectos</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestiona la cartera de proyectos y las asignaciones de empleados.
          </p>
        </div>
        <Button onClick={() => openProjectDialog()}>
          <Plus className="w-4 h-4 mr-2" />
          Nuevo Proyecto
        </Button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Filter className="w-5 h-5 mr-2" />
                Filtros
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Buscar</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="Nombre, código o cliente"
                    value={filters.search}
                    onChange={(e) => setFilters((prev) => ({ ...prev, search: e.target.value }))}
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Cliente</Label>
                <Input
                  placeholder="Nombre del cliente"
                  value={filters.client}
                  onChange={(e) => setFilters((prev) => ({ ...prev, client: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label>Estado</Label>
                <Select
                  value={filters.status}
                  onValueChange={(value) => setFilters((prev) => ({ ...prev, status: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos</SelectItem>
                    {statusOptions.map((status) => (
                      <SelectItem key={status.value} value={status.value}>
                        {status.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="xl:col-span-2 space-y-4">
          {loading ? (
            <div className="py-24 text-center">
              <LoadingSpinner size="lg" text="Cargando proyectos..." />
            </div>
          ) : filteredProjects.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center text-gray-500">
                No se encontraron proyectos con los filtros actuales.
              </CardContent>
            </Card>
          ) : (
            filteredProjects.map((project) => (
              <Card key={project.id}>
                <CardHeader className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <CardTitle className="flex items-center gap-2 text-xl">
                      <Briefcase className="w-5 h-5 text-blue-500" />
                      {project.name}
                    </CardTitle>
                    <CardDescription>Código: {project.code}</CardDescription>
                  </div>
                  <Badge className={statusStyles[project.status] || 'bg-gray-100 text-gray-800'}>
                    {statusOptions.find((option) => option.value === project.status)?.label || project.status}
                  </Badge>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <p className="text-sm text-gray-500">Cliente</p>
                      <p className="font-medium">{project.client_name || 'No especificado'}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-gray-500">Manager</p>
                      <p className="font-medium">{project.manager_name || 'Sin asignar'}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-gray-500">Servicio</p>
                      <p className="font-medium">{project.service_line || 'No especificado'}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-gray-500">Modelo</p>
                      <p className="font-medium">{project.billing_model || 'No especificado'}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-gray-500">Inicio</p>
                      <p className="font-medium">{formatDate(project.start_date)}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-gray-500">Fin</p>
                      <p className="font-medium">{formatDate(project.end_date)}</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm text-gray-500 flex items-center gap-2">
                      <Users className="w-4 h-4" /> Equipos involucrados
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {(project.teams || []).length > 0 ? (
                        project.teams.map((team) => (
                          <Badge key={team.id} variant="outline">
                            {team.name}
                          </Badge>
                        ))
                      ) : (
                        <span className="text-sm text-gray-500">Sin equipos asignados</span>
                      )}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm text-gray-500 flex items-center gap-2">
                      <Layers className="w-4 h-4" /> Resumen
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {project.description || 'Sin descripción'}
                    </p>
                  </div>
                </CardContent>
                <div className="flex flex-wrap items-center justify-end gap-2 border-t border-gray-100 dark:border-gray-800 px-6 py-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openProjectDialog(project)}
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Editar
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-600 hover:text-red-700"
                    onClick={() => handleDeleteProject(project)}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Eliminar
                  </Button>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>

      <Dialog open={showProjectDialog} onOpenChange={setShowProjectDialog}>
        <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{currentProject ? 'Editar proyecto' : 'Nuevo proyecto'}</DialogTitle>
            <DialogDescription>
              Define la información general del proyecto y sus equipos asociados.
            </DialogDescription>
          </DialogHeader>
          <Tabs defaultValue="general">
            <TabsList>
              <TabsTrigger value="general">Información</TabsTrigger>
              {currentProject && <TabsTrigger value="assignments">Asignaciones</TabsTrigger>}
            </TabsList>
            <TabsContent value="general" className="space-y-3 pt-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="space-y-1.5">
                  <Label className="text-sm">Código *</Label>
                  <Input value={formData.code} onChange={(e) => handleFormChange('code', e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm">Nombre *</Label>
                  <Input value={formData.name} onChange={(e) => handleFormChange('name', e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm">Cliente</Label>
                  <Input value={formData.client_name} onChange={(e) => handleFormChange('client_name', e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm">Estado</Label>
                  <Select value={formData.status} onValueChange={(value) => handleFormChange('status', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Estado" />
                    </SelectTrigger>
                    <SelectContent>
                      {statusOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm">Línea de servicio</Label>
                  <Input value={formData.service_line} onChange={(e) => handleFormChange('service_line', e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm">Modelo de facturación</Label>
                  <Input value={formData.billing_model} onChange={(e) => handleFormChange('billing_model', e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm">Fecha de inicio</Label>
                  <Input type="date" value={formData.start_date} onChange={(e) => handleFormChange('start_date', e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm">Fecha de fin</Label>
                  <Input type="date" value={formData.end_date} onChange={(e) => handleFormChange('end_date', e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm">Manager</Label>
                  <Select 
                    value={formData.manager_id || 'none'} 
                    onValueChange={(value) => handleFormChange('manager_id', value === 'none' ? undefined : value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona un manager (opcional)" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">Sin asignar</SelectItem>
                      {employeesOptions
                        .filter(emp => emp.approved && emp.active)
                        .map((employee) => (
                          <SelectItem key={employee.id} value={employee.id.toString()}>
                            {employee.full_name}
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm">Horas presupuestadas</Label>
                  <Input
                    type="number"
                    min="0"
                    value={formData.budget_hours}
                    onChange={(e) => handleFormChange('budget_hours', e.target.value)}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm">Importe presupuestado (€)</Label>
                  <Input
                    type="number"
                    min="0"
                    value={formData.budget_amount}
                    onChange={(e) => handleFormChange('budget_amount', e.target.value)}
                  />
                </div>
              </div>
              <div className="space-y-1.5">
                <Label className="text-sm">Descripción</Label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => handleFormChange('description', e.target.value)}
                  rows={3}
                  placeholder="Detalles del proyecto, alcance u observaciones relevantes."
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-sm">Equipos asociados</Label>
                <div className="flex flex-wrap gap-2">
                  {availableTeams.map((team) => {
                    const selected = formData.team_ids.includes(team.id)
                    return (
                      <button
                        key={team.id}
                        type="button"
                        onClick={() => toggleTeamSelection(team.id)}
                        className={`px-3 py-1.5 text-sm rounded-lg border transition ${
                          selected
                            ? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-100'
                            : 'border-gray-200 dark:border-gray-700 hover:border-blue-200'
                        }`}
                      >
                        {team.name}
                      </button>
                    )
                  })}
                </div>
              </div>
            </TabsContent>
            {currentProject && (
              <TabsContent value="assignments" className="space-y-4 pt-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Asignaciones actuales</CardTitle>
                    <CardDescription>Empleados vinculados al proyecto</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {currentProject.assignments && currentProject.assignments.length > 0 ? (
                      currentProject.assignments.map((assignment) => (
                        <div key={assignment.id} className="border rounded-lg p-3 space-y-2">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-semibold">{assignment.employee?.full_name || `Empleado ${assignment.employee_id}`}</p>
                              <p className="text-xs text-gray-500">
                                {assignment.team_name ? `Equipo: ${assignment.team_name}` : 'Sin equipo específico'}
                              </p>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-red-600 hover:text-red-700"
                              onClick={() => handleRemoveAssignment(assignment.id)}
                            >
                              <Trash2 className="w-4 h-4 mr-1" />
                              Eliminar
                            </Button>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                              <Label>Rol</Label>
                              <Input value={assignment.role || ''} disabled />
                            </div>
                            <div>
                              <Label>% dedicación</Label>
                              <Input
                                type="number"
                                min="0"
                                max="100"
                                defaultValue={assignment.allocation_percent ?? ''}
                                onBlur={(e) => handleUpdateAssignment(assignment.id, e.target.value)}
                              />
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-gray-500">Aún no hay empleados asignados a este proyecto.</p>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Agregar asignación</CardTitle>
                    <CardDescription>Asigna un empleado al proyecto con un porcentaje estimado.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <Label>Empleado</Label>
                        <Select
                          value={assignmentForm.employeeId}
                          onValueChange={(value) => handleAssignmentChange('employeeId', value)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecciona empleado" />
                          </SelectTrigger>
                          <SelectContent>
                            {employeesOptions.map((employee) => (
                              <SelectItem key={employee.id} value={employee.id.toString()}>
                                {employee.full_name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Equipo (opcional)</Label>
                        <Select
                          value={assignmentForm.teamId}
                          onValueChange={(value) => handleAssignmentChange('teamId', value)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecciona equipo" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">Sin especificar</SelectItem>
                            {availableTeams.map((team) => (
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
                          value={assignmentForm.allocationPercent}
                          onChange={(e) => handleAssignmentChange('allocationPercent', e.target.value)}
                          placeholder="Ej. 50"
                        />
                      </div>
                      <div>
                        <Label>Rol</Label>
                        <Input
                          value={assignmentForm.role}
                          onChange={(e) => handleAssignmentChange('role', e.target.value)}
                          placeholder="Responsable, Consultor..."
                        />
                      </div>
                    </div>
                    <div className="flex justify-end">
                      <Button onClick={handleAddAssignment} disabled={savingAssignment || !assignmentForm.employeeId}>
                        {savingAssignment ? 'Guardando...' : 'Agregar asignación'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            )}
          </Tabs>
          <DialogFooter className="flex flex-col sm:flex-row sm:justify-between">
            <Button variant="ghost" onClick={() => setShowProjectDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSaveProject} disabled={savingProject}>
              {savingProject ? 'Guardando...' : 'Guardar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default ProjectsPage

