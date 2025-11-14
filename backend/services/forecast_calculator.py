from datetime import datetime, date, timedelta
from calendar import monthrange
from typing import Dict, List, Optional, Tuple
import logging

from models.employee import Employee
from models.team import Team
from models.company import Company
from models.calendar_activity import CalendarActivity

logger = logging.getLogger(__name__)

class ForecastCalculator:
    """
    Servicio para cálculos de Forecast con períodos de facturación personalizados.
    
    IMPORTANTE: Las guardias (G) NO se suman a las horas reales para el cálculo de forecast.
    Solo se registran como información adicional para el manager.
    """
    
    @staticmethod
    def calculate_theoretical_hours_for_period(employee: Employee, start_date: date, end_date: date) -> float:
        """Calcula las horas teóricas para un período específico"""
        total_hours = 0.0
        current_date = start_date
        
        while current_date <= end_date:
            daily_hours = employee.get_daily_hours(current_date)
            total_hours += daily_hours
            current_date += timedelta(days=1)
        
        return total_hours
    
    @staticmethod
    def calculate_actual_hours_for_period(employee: Employee, start_date: date, end_date: date) -> Dict:
        """
        Calcula las horas reales trabajadas en un período.
        
        IMPORTANTE: Las guardias NO se suman a las horas reales.
        Solo se registran como información adicional.
        """
        # Obtener actividades del período
        activities = CalendarActivity.query.filter(
            CalendarActivity.employee_id == employee.id,
            CalendarActivity.date >= start_date,
            CalendarActivity.date <= end_date
        ).all()
        
        # Crear diccionario de actividades por fecha
        activities_dict = {activity.date: activity for activity in activities}
        
        # Contadores
        actual_hours = 0.0
        vacation_days = 0
        absence_days = 0
        hld_hours = 0.0
        guard_hours = 0.0  # Solo informativo, NO se suma a actual_hours
        training_hours = 0.0
        other_days = 0
        
        current_date = start_date
        while current_date <= end_date:
            daily_theoretical = employee.get_daily_hours(current_date)
            
            if current_date in activities_dict:
                activity = activities_dict[current_date]
                
                if activity.activity_type == 'V':  # Vacaciones
                    vacation_days += 1
                    # No suma horas reales (0 horas)
                elif activity.activity_type == 'A':  # Ausencias
                    absence_days += 1
                    # No suma horas reales (0 horas)
                elif activity.activity_type == 'HLD':  # Horas Libre Disposición
                    hld_hours += activity.hours or 0
                    actual_hours += daily_theoretical - (activity.hours or 0)
                elif activity.activity_type == 'G':  # Guardia
                    # IMPORTANTE: Las guardias NO se suman a las horas reales
                    # Solo se registran como información para el manager
                    guard_hours += activity.hours or 0
                    # Las horas reales son las teóricas del día (sin sumar guardias)
                    actual_hours += daily_theoretical
                elif activity.activity_type == 'F':  # Formación
                    training_hours += activity.hours or 0
                    actual_hours += daily_theoretical - (activity.hours or 0)
                elif activity.activity_type == 'C':  # Otros
                    other_days += 1
                    # No suma horas reales (0 horas)
                else:
                    # Día normal con actividad desconocida
                    actual_hours += daily_theoretical
            else:
                # Día normal sin actividades
                if daily_theoretical > 0:
                    actual_hours += daily_theoretical
            
            current_date += timedelta(days=1)
        
        return {
            'actual_hours': actual_hours,
            'vacation_days': vacation_days,
            'absence_days': absence_days,
            'hld_hours': hld_hours,
            'guard_hours': guard_hours,  # Solo informativo
            'training_hours': training_hours,
            'other_days': other_days
        }
    
    @staticmethod
    def calculate_forecast_for_employee(
        employee: Employee, 
        company: Company, 
        year: int, 
        month: int
    ) -> Dict:
        """
        Calcula el forecast de un empleado para un período de facturación específico de una empresa.
        
        Args:
            employee: Empleado
            company: Empresa con período de facturación
            year: Año del mes de referencia
            month: Mes de referencia (el período puede cruzar meses)
        
        Returns:
            Dict con métricas de forecast
        """
        # Obtener fechas del período de facturación
        start_date, end_date = company.get_billing_period_dates(year, month)
        
        # Calcular horas teóricas
        theoretical_hours = ForecastCalculator.calculate_theoretical_hours_for_period(
            employee, start_date, end_date
        )
        
        # Calcular horas reales (sin incluir guardias en el cálculo)
        actual_data = ForecastCalculator.calculate_actual_hours_for_period(
            employee, start_date, end_date
        )
        
        # Calcular eficiencia
        efficiency = 0.0
        if theoretical_hours > 0:
            efficiency = (actual_data['actual_hours'] / theoretical_hours) * 100
        
        # Determinar estado del rendimiento
        if efficiency >= 95:
            performance_status = 'excellent'
            performance_label = 'Excelente'
        elif efficiency >= 85:
            performance_status = 'good'
            performance_label = 'Bueno'
        else:
            performance_status = 'needs_improvement'
            performance_label = 'Mejorable'
        
        # Calcular valor económico (solo si hay tarifa)
        economic_value = None
        if employee.hourly_rate:
            economic_value = actual_data['actual_hours'] * employee.hourly_rate
        
        return {
            'employee_id': employee.id,
            'employee_name': employee.full_name,
            'company_id': company.id,
            'company_name': company.name,
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'theoretical_hours': round(theoretical_hours, 2),
            'actual_hours': round(actual_data['actual_hours'], 2),
            'efficiency': round(efficiency, 2),
            'performance_status': performance_status,
            'performance_label': performance_label,
            'economic_value': round(economic_value, 2) if economic_value else None,
            'hourly_rate': employee.hourly_rate,
            'breakdown': {
                'vacation_days': actual_data['vacation_days'],
                'absence_days': actual_data['absence_days'],
                'hld_hours': round(actual_data['hld_hours'], 2),
                'guard_hours': round(actual_data['guard_hours'], 2),  # Solo informativo
                'training_hours': round(actual_data['training_hours'], 2),
                'other_days': actual_data['other_days']
            }
        }
    
    @staticmethod
    def calculate_forecast_for_team(
        team: Team,
        company: Company,
        year: int,
        month: int
    ) -> Dict:
        """Calcula el forecast consolidado de un equipo para un período de facturación"""
        team_forecast = {
            'team_id': team.id,
            'team_name': team.name,
            'company_id': company.id,
            'company_name': company.name,
            'total_theoretical_hours': 0.0,
            'total_actual_hours': 0.0,
            'total_economic_value': 0.0,
            'total_guard_hours': 0.0,  # Solo informativo
            'employees': [],
            'efficiency': 0.0,
            'performance_status': None,
            'performance_label': None,
            'employee_count': 0
        }
        
        active_employees = team.active_employees
        
        for employee in active_employees:
            emp_forecast = ForecastCalculator.calculate_forecast_for_employee(
                employee, company, year, month
            )
            
            team_forecast['total_theoretical_hours'] += emp_forecast['theoretical_hours']
            team_forecast['total_actual_hours'] += emp_forecast['actual_hours']
            team_forecast['total_guard_hours'] += emp_forecast['breakdown']['guard_hours']
            
            if emp_forecast['economic_value']:
                team_forecast['total_economic_value'] += emp_forecast['economic_value']
            
            team_forecast['employees'].append(emp_forecast)
        
        # Calcular eficiencia del equipo
        if team_forecast['total_theoretical_hours'] > 0:
            team_forecast['efficiency'] = round(
                (team_forecast['total_actual_hours'] / team_forecast['total_theoretical_hours']) * 100, 2
            )
            
            # Determinar estado del rendimiento del equipo
            if team_forecast['efficiency'] >= 95:
                team_forecast['performance_status'] = 'excellent'
                team_forecast['performance_label'] = 'Excelente'
            elif team_forecast['efficiency'] >= 85:
                team_forecast['performance_status'] = 'good'
                team_forecast['performance_label'] = 'Bueno'
            else:
                team_forecast['performance_status'] = 'needs_improvement'
                team_forecast['performance_label'] = 'Mejorable'
        
        team_forecast['employee_count'] = len(active_employees)
        
        return team_forecast
    
    @staticmethod
    def calculate_forecast_global(
        company: Company,
        year: int,
        month: int
    ) -> Dict:
        """Calcula el forecast global de todos los empleados para un período de facturación"""
        from models.team import Team
        
        global_forecast = {
            'company_id': company.id,
            'company_name': company.name,
            'total_theoretical_hours': 0.0,
            'total_actual_hours': 0.0,
            'total_economic_value': 0.0,
            'total_guard_hours': 0.0,  # Solo informativo
            'teams': [],
            'efficiency': 0.0,
            'performance_status': None,
            'performance_label': None,
            'total_employees': 0,
            'total_teams': 0
        }
        
        teams = Team.query.all()
        
        for team in teams:
            team_forecast = ForecastCalculator.calculate_forecast_for_team(
                team, company, year, month
            )
            
            global_forecast['total_theoretical_hours'] += team_forecast['total_theoretical_hours']
            global_forecast['total_actual_hours'] += team_forecast['total_actual_hours']
            global_forecast['total_economic_value'] += team_forecast['total_economic_value']
            global_forecast['total_guard_hours'] += team_forecast['total_guard_hours']
            global_forecast['total_employees'] += team_forecast['employee_count']
            
            global_forecast['teams'].append(team_forecast)
        
        # Calcular eficiencia global
        if global_forecast['total_theoretical_hours'] > 0:
            global_forecast['efficiency'] = round(
                (global_forecast['total_actual_hours'] / global_forecast['total_theoretical_hours']) * 100, 2
            )
            
            # Determinar estado del rendimiento global
            if global_forecast['efficiency'] >= 95:
                global_forecast['performance_status'] = 'excellent'
                global_forecast['performance_label'] = 'Excelente'
            elif global_forecast['efficiency'] >= 85:
                global_forecast['performance_status'] = 'good'
                global_forecast['performance_label'] = 'Bueno'
            else:
                global_forecast['performance_status'] = 'needs_improvement'
                global_forecast['performance_label'] = 'Mejorable'
        
        global_forecast['total_teams'] = len(teams)
        
        return global_forecast

