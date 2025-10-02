from datetime import datetime, date, timedelta
from calendar import monthrange
from typing import Dict, List, Optional, Tuple
import logging

from models.employee import Employee
from models.team import Team
from models.calendar_activity import CalendarActivity
from models.holiday import Holiday

logger = logging.getLogger(__name__)

class HoursCalculator:
    """Servicio para cálculos avanzados de horas y eficiencia"""
    
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
        """Calcula las horas reales trabajadas en un período"""
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
        guard_hours = 0.0
        training_hours = 0.0
        other_days = 0
        
        current_date = start_date
        while current_date <= end_date:
            daily_theoretical = employee.get_daily_hours(current_date)
            
            if current_date in activities_dict:
                activity = activities_dict[current_date]
                
                if activity.activity_type == 'V':  # Vacaciones
                    vacation_days += 1
                elif activity.activity_type == 'A':  # Ausencias
                    absence_days += 1
                elif activity.activity_type == 'HLD':  # Horas Libre Disposición
                    hld_hours += activity.hours or 0
                    actual_hours += daily_theoretical - (activity.hours or 0)
                elif activity.activity_type == 'G':  # Guardia
                    guard_hours += activity.hours or 0
                    actual_hours += daily_theoretical + (activity.hours or 0)
                elif activity.activity_type == 'F':  # Formación
                    training_hours += activity.hours or 0
                    actual_hours += daily_theoretical - (activity.hours or 0)
                elif activity.activity_type == 'C':  # Otros
                    other_days += 1
                else:
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
            'guard_hours': guard_hours,
            'training_hours': training_hours,
            'other_days': other_days
        }
    
    @staticmethod
    def calculate_employee_efficiency(employee: Employee, year: int = None, month: int = None) -> Dict:
        """Calcula la eficiencia de un empleado"""
        if not year:
            year = datetime.now().year
        
        if month:
            start_date = date(year, month, 1)
            _, last_day = monthrange(year, month)
            end_date = date(year, month, last_day)
            period_name = f"{year}-{month:02d}"
        else:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            period_name = str(year)
        
        # Calcular horas teóricas
        theoretical_hours = HoursCalculator.calculate_theoretical_hours_for_period(
            employee, start_date, end_date
        )
        
        # Calcular horas reales y detalles
        actual_data = HoursCalculator.calculate_actual_hours_for_period(
            employee, start_date, end_date
        )
        
        # Calcular eficiencia
        efficiency = 0.0
        if theoretical_hours > 0:
            efficiency = (actual_data['actual_hours'] / theoretical_hours) * 100
        
        return {
            'employee_id': employee.id,
            'employee_name': employee.full_name,
            'period': period_name,
            'theoretical_hours': theoretical_hours,
            'actual_hours': actual_data['actual_hours'],
            'efficiency': round(efficiency, 2),
            'vacation_days': actual_data['vacation_days'],
            'absence_days': actual_data['absence_days'],
            'hld_hours': actual_data['hld_hours'],
            'guard_hours': actual_data['guard_hours'],
            'training_hours': actual_data['training_hours'],
            'other_days': actual_data['other_days'],
            'remaining_vacation_days': max(0, employee.annual_vacation_days - actual_data['vacation_days']),
            'remaining_hld_hours': max(0, employee.annual_hld_hours - actual_data['hld_hours'])
        }
    
    @staticmethod
    def calculate_team_efficiency(team: Team, year: int = None, month: int = None) -> Dict:
        """Calcula la eficiencia de un equipo completo"""
        if not year:
            year = datetime.now().year
        
        period_name = f"{year}-{month:02d}" if month else str(year)
        
        team_summary = {
            'team_id': team.id,
            'team_name': team.name,
            'period': period_name,
            'total_theoretical_hours': 0.0,
            'total_actual_hours': 0.0,
            'total_vacation_days': 0,
            'total_absence_days': 0,
            'total_hld_hours': 0.0,
            'total_guard_hours': 0.0,
            'total_training_hours': 0.0,
            'total_other_days': 0,
            'employees': [],
            'efficiency': 0.0,
            'employee_count': 0
        }
        
        active_employees = team.active_employees
        
        for employee in active_employees:
            emp_efficiency = HoursCalculator.calculate_employee_efficiency(employee, year, month)
            
            team_summary['total_theoretical_hours'] += emp_efficiency['theoretical_hours']
            team_summary['total_actual_hours'] += emp_efficiency['actual_hours']
            team_summary['total_vacation_days'] += emp_efficiency['vacation_days']
            team_summary['total_absence_days'] += emp_efficiency['absence_days']
            team_summary['total_hld_hours'] += emp_efficiency['hld_hours']
            team_summary['total_guard_hours'] += emp_efficiency['guard_hours']
            team_summary['total_training_hours'] += emp_efficiency['training_hours']
            team_summary['total_other_days'] += emp_efficiency['other_days']
            
            team_summary['employees'].append(emp_efficiency)
        
        # Calcular eficiencia del equipo
        if team_summary['total_theoretical_hours'] > 0:
            team_summary['efficiency'] = round(
                (team_summary['total_actual_hours'] / team_summary['total_theoretical_hours']) * 100, 2
            )
        
        team_summary['employee_count'] = len(active_employees)
        
        return team_summary
    
    @staticmethod
    def calculate_global_efficiency(year: int = None, month: int = None) -> Dict:
        """Calcula la eficiencia global de toda la empresa"""
        if not year:
            year = datetime.now().year
        
        period_name = f"{year}-{month:02d}" if month else str(year)
        
        global_summary = {
            'period': period_name,
            'total_theoretical_hours': 0.0,
            'total_actual_hours': 0.0,
            'total_vacation_days': 0,
            'total_absence_days': 0,
            'total_hld_hours': 0.0,
            'total_guard_hours': 0.0,
            'total_training_hours': 0.0,
            'total_other_days': 0,
            'teams': [],
            'efficiency': 0.0,
            'total_employees': 0,
            'total_teams': 0
        }
        
        teams = Team.query.filter(Team.active == True).all()
        
        for team in teams:
            team_efficiency = HoursCalculator.calculate_team_efficiency(team, year, month)
            
            global_summary['total_theoretical_hours'] += team_efficiency['total_theoretical_hours']
            global_summary['total_actual_hours'] += team_efficiency['total_actual_hours']
            global_summary['total_vacation_days'] += team_efficiency['total_vacation_days']
            global_summary['total_absence_days'] += team_efficiency['total_absence_days']
            global_summary['total_hld_hours'] += team_efficiency['total_hld_hours']
            global_summary['total_guard_hours'] += team_efficiency['total_guard_hours']
            global_summary['total_training_hours'] += team_efficiency['total_training_hours']
            global_summary['total_other_days'] += team_efficiency['total_other_days']
            global_summary['total_employees'] += team_efficiency['employee_count']
            
            global_summary['teams'].append(team_efficiency)
        
        # Calcular eficiencia global
        if global_summary['total_theoretical_hours'] > 0:
            global_summary['efficiency'] = round(
                (global_summary['total_actual_hours'] / global_summary['total_theoretical_hours']) * 100, 2
            )
        
        global_summary['total_teams'] = len(teams)
        
        return global_summary
    
    @staticmethod
    def calculate_monthly_projections(employee: Employee, year: int = None) -> List[Dict]:
        """Calcula proyecciones mensuales para un empleado"""
        if not year:
            year = datetime.now().year
        
        projections = []
        current_month = datetime.now().month if year == datetime.now().year else 1
        
        for month in range(1, 13):
            start_date = date(year, month, 1)
            _, last_day = monthrange(year, month)
            end_date = date(year, month, last_day)
            
            theoretical_hours = HoursCalculator.calculate_theoretical_hours_for_period(
                employee, start_date, end_date
            )
            
            # Si es mes pasado o actual, calcular datos reales
            if month <= current_month and year <= datetime.now().year:
                actual_data = HoursCalculator.calculate_actual_hours_for_period(
                    employee, start_date, end_date
                )
                efficiency = (actual_data['actual_hours'] / theoretical_hours * 100) if theoretical_hours > 0 else 0
                
                projection = {
                    'month': month,
                    'month_name': start_date.strftime('%B'),
                    'theoretical_hours': theoretical_hours,
                    'actual_hours': actual_data['actual_hours'],
                    'efficiency': round(efficiency, 2),
                    'is_projection': False,
                    'vacation_days': actual_data['vacation_days'],
                    'absence_days': actual_data['absence_days']
                }
            else:
                # Proyección basada en promedio de meses anteriores
                avg_efficiency = HoursCalculator.get_average_efficiency(employee, year, month - 1)
                projected_hours = theoretical_hours * (avg_efficiency / 100)
                
                projection = {
                    'month': month,
                    'month_name': start_date.strftime('%B'),
                    'theoretical_hours': theoretical_hours,
                    'projected_hours': projected_hours,
                    'projected_efficiency': avg_efficiency,
                    'is_projection': True
                }
            
            projections.append(projection)
        
        return projections
    
    @staticmethod
    def get_average_efficiency(employee: Employee, year: int, up_to_month: int) -> float:
        """Calcula la eficiencia promedio hasta un mes específico"""
        if up_to_month <= 0:
            return 100.0  # Eficiencia base para proyecciones
        
        total_theoretical = 0.0
        total_actual = 0.0
        
        for month in range(1, up_to_month + 1):
            start_date = date(year, month, 1)
            _, last_day = monthrange(year, month)
            end_date = date(year, month, last_day)
            
            theoretical = HoursCalculator.calculate_theoretical_hours_for_period(
                employee, start_date, end_date
            )
            actual_data = HoursCalculator.calculate_actual_hours_for_period(
                employee, start_date, end_date
            )
            
            total_theoretical += theoretical
            total_actual += actual_data['actual_hours']
        
        if total_theoretical > 0:
            return (total_actual / total_theoretical) * 100
        
        return 100.0
    
    @staticmethod
    def get_efficiency_trends(employee: Employee, months: int = 6) -> Dict:
        """Obtiene tendencias de eficiencia de los últimos meses"""
        end_date = date.today()
        trends = []
        
        for i in range(months):
            # Calcular fecha del mes
            if end_date.month - i <= 0:
                month = 12 + (end_date.month - i)
                year = end_date.year - 1
            else:
                month = end_date.month - i
                year = end_date.year
            
            efficiency_data = HoursCalculator.calculate_employee_efficiency(employee, year, month)
            trends.insert(0, {  # Insertar al principio para orden cronológico
                'year': year,
                'month': month,
                'month_name': date(year, month, 1).strftime('%B %Y'),
                'efficiency': efficiency_data['efficiency'],
                'actual_hours': efficiency_data['actual_hours'],
                'theoretical_hours': efficiency_data['theoretical_hours']
            })
        
        # Calcular tendencia (mejorando/empeorando)
        if len(trends) >= 2:
            recent_avg = sum(t['efficiency'] for t in trends[-3:]) / min(3, len(trends))
            older_avg = sum(t['efficiency'] for t in trends[:-3]) / max(1, len(trends) - 3)
            trend_direction = 'improving' if recent_avg > older_avg else 'declining'
        else:
            trend_direction = 'stable'
        
        return {
            'trends': trends,
            'trend_direction': trend_direction,
            'average_efficiency': sum(t['efficiency'] for t in trends) / len(trends) if trends else 0,
            'best_month': max(trends, key=lambda x: x['efficiency']) if trends else None,
            'worst_month': min(trends, key=lambda x: x['efficiency']) if trends else None
        }
