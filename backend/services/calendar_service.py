from datetime import datetime, date, timedelta
from calendar import monthrange
from typing import List, Dict, Optional, Tuple
import logging

from models.employee import Employee
from models.team import Team
from models.calendar_activity import CalendarActivity
from models.holiday import Holiday
from models.user import db
from .notification_service import NotificationService

logger = logging.getLogger(__name__)

class CalendarService:
    """Servicio para gestión avanzada del calendario"""
    
    @staticmethod
    def get_calendar_data(employee_id: int = None, team_id: int = None, 
                         year: int = None, month: int = None) -> Dict:
        """Obtiene datos completos del calendario"""
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        try:
            # Determinar empleados a incluir
            if employee_id:
                employees = [Employee.query.get(employee_id)]
                if not employees[0]:
                    return {'error': 'Empleado no encontrado'}
            elif team_id:
                team = Team.query.get(team_id)
                if not team:
                    return {'error': 'Equipo no encontrado'}
                employees = team.active_employees
            else:
                employees = Employee.query.filter(Employee.active == True).all()
            
            # Generar estructura del calendario
            calendar_data = CalendarService._generate_calendar_structure(year, month)
            
            # Añadir datos de empleados
            calendar_data['employees'] = []
            
            for employee in employees:
                employee_data = CalendarService._get_employee_calendar_data(
                    employee, year, month
                )
                calendar_data['employees'].append(employee_data)
            
            # Añadir festivos del mes
            calendar_data['holidays'] = CalendarService._get_holidays_for_month(
                employees, year, month
            )
            
            # Añadir resumen del mes
            calendar_data['summary'] = CalendarService._calculate_month_summary(
                employees, year, month
            )
            
            return calendar_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos del calendario: {e}")
            return {'error': f'Error interno: {e}'}
    
    @staticmethod
    def _generate_calendar_structure(year: int, month: int) -> Dict:
        """Genera la estructura básica del calendario"""
        # Obtener información del mes
        first_day = date(year, month, 1)
        _, last_day = monthrange(year, month)
        last_date = date(year, month, last_day)
        
        # Generar lista de días
        days = []
        current_date = first_day
        
        while current_date <= last_date:
            day_info = {
                'date': current_date.isoformat(),
                'day': current_date.day,
                'weekday': current_date.weekday(),
                'weekday_name': current_date.strftime('%A'),
                'is_weekend': current_date.weekday() >= 5,
                'is_today': current_date == date.today()
            }
            days.append(day_info)
            current_date += timedelta(days=1)
        
        return {
            'year': year,
            'month': month,
            'month_name': first_day.strftime('%B'),
            'days_in_month': last_day,
            'first_weekday': first_day.weekday(),
            'days': days
        }
    
    @staticmethod
    def _get_employee_calendar_data(employee: Employee, year: int, month: int) -> Dict:
        """Obtiene datos del calendario para un empleado específico"""
        # Obtener actividades del mes
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)
        
        activities = CalendarActivity.query.filter(
            CalendarActivity.employee_id == employee.id,
            CalendarActivity.date >= start_date,
            CalendarActivity.date <= end_date
        ).all()
        
        # Crear diccionario de actividades por fecha
        activities_dict = {activity.date.isoformat(): activity.to_dict() for activity in activities}
        
        # Calcular resumen del empleado para el mes
        month_summary = employee.get_hours_summary(year, month)
        
        return {
            'employee': employee.to_dict(),
            'activities': activities_dict,
            'month_summary': month_summary,
            'remaining_benefits': employee.get_remaining_benefits(year)
        }
    
    @staticmethod
    def _get_holidays_for_month(employees: List[Employee], year: int, month: int) -> List[Dict]:
        """Obtiene festivos aplicables para los empleados en el mes"""
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)
        
        # Obtener países únicos de los empleados
        countries = list(set(emp.country for emp in employees if emp.country))
        
        holidays = []
        for country in countries:
            country_holidays = Holiday.query.filter(
                Holiday.country == country,
                Holiday.date >= start_date,
                Holiday.date <= end_date,
                Holiday.active == True
            ).all()
            
            for holiday in country_holidays:
                holidays.append(holiday.to_dict())
        
        return holidays
    
    @staticmethod
    def _calculate_month_summary(employees: List[Employee], year: int, month: int) -> Dict:
        """Calcula resumen del mes para todos los empleados"""
        summary = {
            'total_employees': len(employees),
            'total_theoretical_hours': 0.0,
            'total_actual_hours': 0.0,
            'total_vacation_days': 0,
            'total_absence_days': 0,
            'total_hld_hours': 0.0,
            'total_guard_hours': 0.0,
            'average_efficiency': 0.0
        }
        
        if not employees:
            return summary
        
        total_efficiency = 0.0
        
        for employee in employees:
            emp_summary = employee.get_hours_summary(year, month)
            
            summary['total_theoretical_hours'] += emp_summary['theoretical_hours']
            summary['total_actual_hours'] += emp_summary['actual_hours']
            summary['total_vacation_days'] += emp_summary['vacation_days']
            summary['total_absence_days'] += emp_summary['absence_days']
            summary['total_hld_hours'] += emp_summary['hld_hours']
            summary['total_guard_hours'] += emp_summary['guard_hours']
            total_efficiency += emp_summary['efficiency']
        
        # Calcular eficiencia promedio
        summary['average_efficiency'] = round(total_efficiency / len(employees), 2)
        
        # Calcular eficiencia global
        if summary['total_theoretical_hours'] > 0:
            summary['global_efficiency'] = round(
                (summary['total_actual_hours'] / summary['total_theoretical_hours']) * 100, 2
            )
        else:
            summary['global_efficiency'] = 0.0
        
        return summary
    
    @staticmethod
    def create_calendar_activity(employee_id: int, activity_date: date, 
                               activity_type: str, hours: float = None,
                               start_time: str = None, end_time: str = None,
                               description: str = None, created_by_user_id: int = None) -> Tuple[bool, str, Optional[CalendarActivity]]:
        """Crea una nueva actividad en el calendario"""
        try:
            from datetime import time as time_type
            
            employee = Employee.query.get(employee_id)
            if not employee:
                return False, "Empleado no encontrado", None
            
            # Verificar si ya existe una actividad para esa fecha
            existing = CalendarActivity.query.filter(
                CalendarActivity.employee_id == employee_id,
                CalendarActivity.date == activity_date
            ).first()
            
            if existing:
                return False, "Ya existe una actividad para esta fecha", None
            
            # Convertir start_time y end_time a objetos time si son strings
            start_time_obj = None
            end_time_obj = None
            if start_time:
                if isinstance(start_time, str):
                    hour, minute = start_time.split(':')
                    start_time_obj = time_type(int(hour), int(minute))
                else:
                    start_time_obj = start_time
            if end_time:
                if isinstance(end_time, str):
                    hour, minute = end_time.split(':')
                    end_time_obj = time_type(int(hour), int(minute))
                else:
                    end_time_obj = end_time
            
            # Crear nueva actividad
            activity = CalendarActivity(
                employee_id=employee_id,
                date=activity_date,
                activity_type=activity_type,
                hours=hours,
                start_time=start_time_obj,
                end_time=end_time_obj,
                description=description,
                created_by=created_by_user_id
            )
            
            # Validar actividad
            is_valid, validation_message = activity.validate_activity()
            if not is_valid:
                return False, validation_message, None
            
            # Verificar si puede crearse en la fecha
            can_create, date_message = activity.can_be_created_on_date()
            if not can_create:
                return False, date_message, None
            
            # Guardar actividad
            db.session.add(activity)
            db.session.commit()
            
            # Verificar conflictos de vacaciones si es necesario
            if activity_type == 'V' and employee.team_id:
                NotificationService.check_and_notify_vacation_conflicts(
                    employee.team_id, activity_date, employee_id
                )
            
            # Notificar cambios al manager si es necesario
            if created_by_user_id and employee.team and employee.team.manager:
                changes_summary = f"Añadida actividad: {activity.get_display_text()} el {activity_date.strftime('%d/%m/%Y')}"
                NotificationService.notify_calendar_changes(employee, changes_summary)
            
            logger.info(f"Actividad creada: {activity_type} para empleado {employee_id} en {activity_date}")
            
            return True, "Actividad creada exitosamente", activity
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando actividad: {e}")
            return False, f"Error interno: {e}", None
    
    @staticmethod
    def update_calendar_activity(activity_id: int, activity_type: str = None,
                               hours: float = None, description: str = None,
                               updated_by_user_id: int = None) -> Tuple[bool, str, Optional[CalendarActivity]]:
        """Actualiza una actividad existente del calendario"""
        try:
            activity = CalendarActivity.query.get(activity_id)
            if not activity:
                return False, "Actividad no encontrada", None
            
            # Guardar valores originales para notificación
            original_type = activity.activity_type
            original_hours = activity.hours
            
            # Actualizar campos
            if activity_type is not None:
                activity.activity_type = activity_type
            if hours is not None:
                activity.hours = hours
            if description is not None:
                activity.description = description
            
            activity.updated_at = datetime.utcnow()
            
            # Validar actividad actualizada
            is_valid, validation_message = activity.validate_activity()
            if not is_valid:
                return False, validation_message, None
            
            db.session.commit()
            
            # Notificar cambios al manager
            if updated_by_user_id and activity.employee.team and activity.employee.team.manager:
                changes = []
                if original_type != activity.activity_type:
                    changes.append(f"tipo cambiado de {original_type} a {activity.activity_type}")
                if original_hours != activity.hours:
                    changes.append(f"horas cambiadas de {original_hours or 0} a {activity.hours or 0}")
                
                if changes:
                    changes_summary = f"Modificada actividad del {activity.date.strftime('%d/%m/%Y')}: {', '.join(changes)}"
                    NotificationService.notify_calendar_changes(activity.employee, changes_summary)
            
            logger.info(f"Actividad {activity_id} actualizada")
            
            return True, "Actividad actualizada exitosamente", activity
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando actividad: {e}")
            return False, f"Error interno: {e}", None
    
    @staticmethod
    def delete_calendar_activity(activity_id: int, deleted_by_user_id: int = None) -> Tuple[bool, str]:
        """Elimina una actividad del calendario"""
        try:
            activity = CalendarActivity.query.get(activity_id)
            if not activity:
                return False, "Actividad no encontrada"
            
            # Guardar información para notificación
            employee = activity.employee
            activity_date = activity.date
            activity_display = activity.get_display_text()
            
            db.session.delete(activity)
            db.session.commit()
            
            # Notificar cambios al manager
            if deleted_by_user_id and employee.team and employee.team.manager:
                changes_summary = f"Eliminada actividad: {activity_display} del {activity_date.strftime('%d/%m/%Y')}"
                NotificationService.notify_calendar_changes(employee, changes_summary)
            
            logger.info(f"Actividad {activity_id} eliminada")
            
            return True, "Actividad eliminada exitosamente"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error eliminando actividad: {e}")
            return False, f"Error interno: {e}"
    
    @staticmethod
    def get_team_calendar_conflicts(team_id: int, start_date: date = None, 
                                  end_date: date = None) -> List[Dict]:
        """Obtiene conflictos de calendario en un equipo"""
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        conflicts = []
        current_date = start_date
        
        while current_date <= end_date:
            # Verificar conflictos de vacaciones
            conflict_count, conflict_activities = CalendarActivity.check_vacation_conflicts(
                team_id, current_date
            )
            
            if conflict_count >= 2:
                conflicts.append({
                    'date': current_date.isoformat(),
                    'type': 'vacation_conflict',
                    'count': conflict_count,
                    'employees': [
                        {
                            'id': activity.employee_id,
                            'name': activity.employee.full_name
                        }
                        for activity in conflict_activities
                    ]
                })
            
            current_date += timedelta(days=1)
        
        return conflicts
    
    @staticmethod
    def get_upcoming_activities(employee_id: int = None, team_id: int = None, 
                              days_ahead: int = 10) -> List[Dict]:
        """Obtiene actividades próximas"""
        start_date = date.today()
        end_date = start_date + timedelta(days=days_ahead)
        
        query = CalendarActivity.query.filter(
            CalendarActivity.date >= start_date,
            CalendarActivity.date <= end_date
        )
        
        if employee_id:
            query = query.filter(CalendarActivity.employee_id == employee_id)
        elif team_id:
            query = query.join(Employee).filter(Employee.team_id == team_id)
        
        activities = query.order_by(CalendarActivity.date).all()
        
        return [activity.to_dict() for activity in activities]
