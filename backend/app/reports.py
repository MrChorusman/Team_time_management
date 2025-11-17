from flask import Blueprint, request, jsonify, send_file
from flask_security import auth_required, current_user
from datetime import datetime, date
import logging
import io
import csv
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from models.employee import Employee
from models.team import Team
from models.calendar_activity import CalendarActivity
from services.hours_calculator import HoursCalculator
from utils.decorators import employee_or_above_required

logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/employee/<int:employee_id>', methods=['GET'])
@auth_required()
@employee_or_above_required()
def get_employee_report(employee_id):
    """Genera reporte de un empleado específico (solo el empleado, su manager o admin)"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado'
            }), 404
        
        # Verificar permisos
        if not current_user.is_admin() and not current_user.can_manage_employee(employee):
            if not (current_user.employee and current_user.employee.id == employee_id):
                return jsonify({
                    'success': False,
                    'message': 'Acceso denegado'
                }), 403
        
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', type=int)
        
        # Generar reporte
        report_data = {
            'employee': employee.to_dict(include_summary=True),
            'period': {
                'year': year,
                'month': month
            }
        }
        
        if month:
            # Reporte mensual
            monthly_summary = employee.get_hours_summary(year, month)
            report_data['monthly_summary'] = monthly_summary
            
            # Actividades del mes
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            
            activities = CalendarActivity.query.filter(
                CalendarActivity.employee_id == employee_id,
                CalendarActivity.date >= start_date,
                CalendarActivity.date < end_date
            ).order_by(CalendarActivity.date).all()
            
            report_data['activities'] = [activity.to_dict() for activity in activities]
            report_data['report_type'] = 'monthly'
        
        else:
            # Reporte anual
            annual_summary = employee.get_annual_summary(year)
            report_data['annual_summary'] = annual_summary
            
            # Resumen por meses
            monthly_summaries = []
            for month_num in range(1, 13):
                month_summary = employee.get_hours_summary(year, month_num)
                month_summary['month'] = month_num
                month_summary['month_name'] = date(year, month_num, 1).strftime('%B')
                monthly_summaries.append(month_summary)
            
            report_data['monthly_summaries'] = monthly_summaries
            report_data['report_type'] = 'annual'
        
        return jsonify({
            'success': True,
            'report': report_data
        })
        
    except Exception as e:
        logger.error(f"Error generando reporte de empleado {employee_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error generando reporte'
        }), 500

@reports_bp.route('/team/<int:team_id>', methods=['GET'])
@auth_required()
def get_team_report(team_id):
    """Genera reporte de un equipo específico"""
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado'
            }), 404
        
        # Verificar permisos
        can_access = False
        if current_user.is_admin():
            can_access = True
        elif current_user.is_manager():
            managed_teams = current_user.get_managed_teams()
            can_access = team in managed_teams
        
        if not can_access:
            return jsonify({
                'success': False,
                'message': 'Acceso denegado'
            }), 403
        
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', type=int)
        
        # Generar reporte del equipo
        team_summary = HoursCalculator.calculate_team_efficiency(team, year, month)
        
        report_data = {
            'team': team.to_dict(include_employees=True),
            'period': {
                'year': year,
                'month': month
            },
            'team_summary': team_summary,
            'report_type': 'monthly' if month else 'annual'
        }
        
        # Reportes individuales de empleados
        employee_reports = []
        for employee in team.active_employees:
            if month:
                emp_summary = employee.get_hours_summary(year, month)
            else:
                emp_summary = employee.get_annual_summary(year)
            
            employee_reports.append({
                'employee': employee.to_dict(),
                'summary': emp_summary
            })
        
        report_data['employee_reports'] = employee_reports
        
        return jsonify({
            'success': True,
            'report': report_data
        })
        
    except Exception as e:
        logger.error(f"Error generando reporte de equipo {team_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error generando reporte'
        }), 500

@reports_bp.route('/dashboard', methods=['GET'])
@auth_required()
@employee_or_above_required()
def get_dashboard_report():
    """Genera reporte para el dashboard según el rol del usuario (employee o superior)"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        logger.info(f"Generando dashboard para usuario {current_user.id}, rol: {current_user.get_primary_role()}")
        
        report_data = {
            'period': {
                'year': year,
                'month': month
            },
            'user_role': current_user.get_primary_role()
        }
        
        if current_user.is_admin():
            # Dashboard de administrador - vista global
            from models.user import User
            
            # Estadísticas generales - contar TODOS los empleados activos (sin filtro de approved)
            try:
                total_employees = Employee.query.filter(Employee.active == True).count()
                logger.info(f"Total empleados activos: {total_employees}")
            except Exception as e:
                logger.error(f"Error contando empleados: {e}")
                total_employees = 0
            
            try:
                total_teams = Team.query.count()  # Todos los equipos (no hay columna active)
                logger.info(f"Total equipos: {total_teams}")
            except Exception as e:
                logger.error(f"Error contando equipos: {e}")
                total_teams = 0
            
            try:
                pending_approvals = Employee.query.filter(
                    Employee.active == True,
                    Employee.approved == False
                ).count()
                logger.info(f"Pendientes de aprobación: {pending_approvals}")
            except Exception as e:
                logger.error(f"Error contando aprobaciones pendientes: {e}")
                pending_approvals = 0
            
            # Eficiencia global
            try:
                all_teams = Team.query.all()  # Todos los equipos (no hay columna active)
                logger.info(f"Equipos encontrados: {len(all_teams)}")
            except Exception as e:
                logger.error(f"Error obteniendo equipos: {e}")
                all_teams = []
            
            global_efficiency = 0
            team_summaries = []
            teams_with_efficiency = 0
            
            for team in all_teams:
                try:
                    team_summary = HoursCalculator.calculate_team_efficiency(team, year, month)
                    team_dict = team.to_dict()
                    team_summaries.append({
                        'team': team_dict,
                        'summary': team_summary
                    })
                    team_efficiency = team_summary.get('efficiency', team_summary.get('average_efficiency', 0))
                    if team_efficiency > 0:
                        global_efficiency += team_efficiency
                        teams_with_efficiency += 1
                except Exception as e:
                    logger.error(f"Error calculando eficiencia del equipo {team.id if team else 'Unknown'}: {e}", exc_info=True)
                    # Continuar con el siguiente equipo aunque falle uno
                    continue
            
            if teams_with_efficiency > 0:
                global_efficiency = global_efficiency / teams_with_efficiency
            else:
                global_efficiency = 0
            
            report_data.update({
                'dashboard_type': 'admin',
                'type': 'admin',  # Formato esperado por frontend
                'statistics': {
                    'total_employees': total_employees,
                    'total_teams': total_teams,
                    'pending_approvals': pending_approvals,
                    'global_efficiency': round(global_efficiency, 2)
                },
                'team_summaries': team_summaries
            })
        
        elif current_user.is_manager():
            # Dashboard de manager - equipos gestionados
            managed_teams = current_user.get_managed_teams()
            
            # Incluir también el equipo del manager si es miembro de uno
            if current_user.employee and current_user.employee.team_id:
                manager_team = Team.query.get(current_user.employee.team_id)
                if manager_team and manager_team not in managed_teams:
                    managed_teams.append(manager_team)
            
            team_summaries = []
            team_performance = []
            total_employees = 0
            total_efficiency_sum = 0
            total_efficiency_count = 0
            
            for team in managed_teams:
                team_summary = HoursCalculator.calculate_team_efficiency(team, year, month)
                
                # Usar el employee_count del summary que ya incluye al manager si está en el equipo
                employee_count = team_summary.get('employee_count', 0)
                
                team_summaries.append({
                    'team': team.to_dict(include_employees=True),
                    'summary': team_summary
                })
                
                # Preparar datos para team_performance (formato esperado por frontend)
                team_performance.append({
                    'team_name': team.name,
                    'team_id': team.id,
                    'members_count': employee_count,
                    'efficiency': team_summary.get('efficiency', team_summary.get('average_efficiency', 0))
                })
                
                total_employees += employee_count
                
                # Calcular eficiencia promedio (incluyendo al manager si está en el equipo)
                team_efficiency = team_summary.get('efficiency', team_summary.get('average_efficiency', 0))
                if team_efficiency > 0:
                    total_efficiency_sum += team_efficiency
                    total_efficiency_count += 1
            
            # Calcular eficiencia promedio
            average_efficiency = (total_efficiency_sum / total_efficiency_count) if total_efficiency_count > 0 else 0
            
            # Empleados pendientes de aprobación
            team_ids = [team.id for team in managed_teams]
            pending_approvals = Employee.query.filter(
                Employee.team_id.in_(team_ids),
                Employee.active == True,
                Employee.approved == False
            ).count()
            
            report_data.update({
                'dashboard_type': 'manager',
                'type': 'manager',  # Formato esperado por frontend
                'statistics': {
                    'managed_teams': len(managed_teams),
                    'total_employees': total_employees,
                    'pending_approvals': pending_approvals,
                    'average_efficiency': round(average_efficiency, 2)
                },
                'team_summaries': team_summaries,
                'team_performance': team_performance,  # Formato esperado por frontend
                'pending_requests': []  # Inicializar como array vacío
            })
        
        elif current_user.is_employee():
            # Dashboard de empleado - vista personal
            if not current_user.employee:
                return jsonify({
                    'success': False,
                    'message': 'No tienes un perfil de empleado registrado'
                }), 404
            
            employee = current_user.employee
            
            # Resumen personal
            monthly_summary = employee.get_hours_summary(year, month)
            annual_summary = employee.get_annual_summary(year)
            
            # Resumen del equipo si pertenece a uno
            team_summary = None
            if employee.team:
                team_summary = HoursCalculator.calculate_team_efficiency(employee.team, year, month)
            
            report_data.update({
                'dashboard_type': 'employee',
                'employee': employee.to_dict(include_summary=True),
                'monthly_summary': monthly_summary,
                'annual_summary': annual_summary,
                'team_summary': team_summary
            })
        
        else:
            # Usuario viewer - acceso limitado
            report_data.update({
                'dashboard_type': 'viewer',
                'message': 'Completa tu registro de empleado para acceder al dashboard completo'
            })
        
        return jsonify({
            'success': True,
            'report': report_data
        })
        
    except Exception as e:
        logger.error(f"Error generando reporte de dashboard: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Error generando reporte de dashboard: {str(e)}'
        }), 500

@reports_bp.route('/export/employee/<int:employee_id>', methods=['GET'])
@auth_required()
def export_employee_report(employee_id):
    """Exporta reporte de empleado a PDF o CSV"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado'
            }), 404
        
        # Verificar permisos
        if not current_user.is_admin() and not current_user.can_manage_employee(employee):
            if not (current_user.employee and current_user.employee.id == employee_id):
                return jsonify({
                    'success': False,
                    'message': 'Acceso denegado'
                }), 403
        
        format_type = request.args.get('format', 'pdf').lower()
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', type=int)
        
        if format_type == 'csv':
            return _export_employee_csv(employee, year, month)
        else:
            return _export_employee_pdf(employee, year, month)
        
    except Exception as e:
        logger.error(f"Error exportando reporte de empleado {employee_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error exportando reporte'
        }), 500

@reports_bp.route('/export/team/<int:team_id>', methods=['GET'])
@auth_required()
def export_team_report(team_id):
    """Exporta reporte de equipo a PDF o CSV"""
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': 'Equipo no encontrado'
            }), 404
        
        # Verificar permisos
        can_access = False
        if current_user.is_admin():
            can_access = True
        elif current_user.is_manager():
            managed_teams = current_user.get_managed_teams()
            can_access = team in managed_teams
        
        if not can_access:
            return jsonify({
                'success': False,
                'message': 'Acceso denegado'
            }), 403
        
        format_type = request.args.get('format', 'pdf').lower()
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', type=int)
        
        if format_type == 'csv':
            return _export_team_csv(team, year, month)
        else:
            return _export_team_pdf(team, year, month)
        
    except Exception as e:
        logger.error(f"Error exportando reporte de equipo {team_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error exportando reporte'
        }), 500

def _export_employee_csv(employee, year, month=None):
    """Exporta reporte de empleado a CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Encabezados
    writer.writerow(['Reporte de Empleado'])
    writer.writerow(['Empleado:', employee.full_name])
    writer.writerow(['Equipo:', employee.team.name if employee.team else 'N/A'])
    writer.writerow(['Período:', f"{year}" + (f"/{month:02d}" if month else "")])
    writer.writerow([])
    
    if month:
        # Reporte mensual
        summary = employee.get_hours_summary(year, month)
        writer.writerow(['Resumen Mensual'])
        writer.writerow(['Métrica', 'Valor'])
        writer.writerow(['Horas Teóricas', summary['theoretical_hours']])
        writer.writerow(['Horas Reales', summary['actual_hours']])
        writer.writerow(['Eficiencia (%)', summary['efficiency']])
        writer.writerow(['Días de Vacaciones', summary['vacation_days']])
        writer.writerow(['Días de Ausencia', summary['absence_days']])
        writer.writerow(['Horas HLD', summary['hld_hours']])
        writer.writerow(['Horas de Guardia', summary['guard_hours']])
        writer.writerow([])
        
        # Actividades del mes
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        activities = CalendarActivity.query.filter(
            CalendarActivity.employee_id == employee.id,
            CalendarActivity.date >= start_date,
            CalendarActivity.date < end_date
        ).order_by(CalendarActivity.date).all()
        
        writer.writerow(['Actividades del Mes'])
        writer.writerow(['Fecha', 'Tipo', 'Horas', 'Descripción'])
        for activity in activities:
            writer.writerow([
                activity.date.strftime('%Y-%m-%d'),
                activity.get_display_text(),
                activity.hours or 0,
                activity.description or ''
            ])
    
    else:
        # Reporte anual
        annual_summary = employee.get_annual_summary(year)
        writer.writerow(['Resumen Anual'])
        writer.writerow(['Métrica', 'Valor'])
        for key, value in annual_summary.items():
            writer.writerow([key.replace('_', ' ').title(), value])
    
    # Preparar respuesta
    output.seek(0)
    filename = f"reporte_empleado_{employee.id}_{year}" + (f"_{month:02d}" if month else "") + ".csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

def _export_employee_pdf(employee, year, month=None):
    """Exporta reporte de empleado a PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    period_text = f"{year}" + (f"/{month:02d}" if month else "")
    title = Paragraph(f"Reporte de Empleado - {period_text}", title_style)
    story.append(title)
    
    # Información del empleado
    employee_info = [
        ['Empleado:', employee.full_name],
        ['Equipo:', employee.team.name if employee.team else 'N/A'],
        ['País:', employee.country],
        ['Horas L-J:', f"{employee.hours_monday_thursday}h"],
        ['Horas Viernes:', f"{employee.hours_friday}h"]
    ]
    
    employee_table = Table(employee_info, colWidths=[2*inch, 3*inch])
    employee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(employee_table)
    story.append(Spacer(1, 20))
    
    if month:
        # Resumen mensual
        summary = employee.get_hours_summary(year, month)
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Horas Teóricas', f"{summary['theoretical_hours']:.1f}h"],
            ['Horas Reales', f"{summary['actual_hours']:.1f}h"],
            ['Eficiencia', f"{summary['efficiency']:.1f}%"],
            ['Días de Vacaciones', summary['vacation_days']],
            ['Días de Ausencia', summary['absence_days']],
            ['Horas HLD', f"{summary['hld_hours']:.1f}h"],
            ['Horas de Guardia', f"{summary['guard_hours']:.1f}h"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Resumen Mensual", styles['Heading2']))
        story.append(summary_table)
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    
    filename = f"reporte_empleado_{employee.id}_{year}" + (f"_{month:02d}" if month else "") + ".pdf"
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

def _export_team_csv(team, year, month=None):
    """Exporta reporte de equipo a CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Encabezados
    writer.writerow(['Reporte de Equipo'])
    writer.writerow(['Equipo:', team.name])
    writer.writerow(['Manager:', team.manager.full_name if team.manager else 'N/A'])
    writer.writerow(['Período:', f"{year}" + (f"/{month:02d}" if month else "")])
    writer.writerow([])
    
    # Resumen del equipo
    team_summary = HoursCalculator.calculate_team_efficiency(team, year, month)
    writer.writerow(['Resumen del Equipo'])
    writer.writerow(['Métrica', 'Valor'])
    for key, value in team_summary.items():
        writer.writerow([key.replace('_', ' ').title(), value])
    
    writer.writerow([])
    
    # Empleados del equipo
    writer.writerow(['Empleados del Equipo'])
    writer.writerow(['Empleado', 'Horas Teóricas', 'Horas Reales', 'Eficiencia (%)', 'Vacaciones', 'Ausencias'])
    
    for employee in team.active_employees:
        if month:
            emp_summary = employee.get_hours_summary(year, month)
        else:
            emp_summary = employee.get_annual_summary(year)
        
        writer.writerow([
            employee.full_name,
            emp_summary.get('theoretical_hours', 0),
            emp_summary.get('actual_hours', 0),
            emp_summary.get('efficiency', 0),
            emp_summary.get('vacation_days', 0),
            emp_summary.get('absence_days', 0)
        ])
    
    # Preparar respuesta
    output.seek(0)
    filename = f"reporte_equipo_{team.id}_{year}" + (f"_{month:02d}" if month else "") + ".csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

def _export_team_pdf(team, year, month=None):
    """Exporta reporte de equipo a PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1
    )
    
    period_text = f"{year}" + (f"/{month:02d}" if month else "")
    title = Paragraph(f"Reporte de Equipo - {period_text}", title_style)
    story.append(title)
    
    # Información del equipo
    team_info = [
        ['Equipo:', team.name],
        ['Manager:', team.manager.full_name if team.manager else 'N/A'],
        ['Empleados Activos:', len(team.active_employees)],
        ['Descripción:', team.description or 'N/A']
    ]
    
    team_table = Table(team_info, colWidths=[2*inch, 4*inch])
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(team_table)
    story.append(Spacer(1, 20))
    
    # Resumen del equipo
    team_summary = HoursCalculator.calculate_team_efficiency(team, year, month)
    
    summary_data = [['Métrica', 'Valor']]
    for key, value in team_summary.items():
        summary_data.append([key.replace('_', ' ').title(), str(value)])
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(Paragraph("Resumen del Equipo", styles['Heading2']))
    story.append(summary_table)
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    
    filename = f"reporte_equipo_{team.id}_{year}" + (f"_{month:02d}" if month else "") + ".pdf"
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@reports_bp.route('/summary', methods=['GET'])
@auth_required()
def get_reports_summary():
    """Obtiene resumen de reportes disponibles"""
    try:
        summary = {
            'available_reports': [],
            'user_role': current_user.get_primary_role(),
            'permissions': {
                'can_view_all_employees': current_user.is_admin(),
                'can_view_team_reports': current_user.is_admin() or current_user.is_manager(),
                'can_export_reports': True
            }
        }
        
        # Reportes disponibles según el rol
        if current_user.is_admin():
            summary['available_reports'] = [
                'dashboard', 'all_employees', 'all_teams', 'global_statistics'
            ]
        elif current_user.is_manager():
            managed_teams = current_user.get_managed_teams()
            summary['available_reports'] = [
                'dashboard', 'managed_teams', 'team_employees'
            ]
            summary['managed_teams_count'] = len(managed_teams)
        elif current_user.is_employee():
            summary['available_reports'] = [
                'dashboard', 'personal_report', 'team_view'
            ]
        else:
            summary['available_reports'] = ['registration_required']
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de reportes: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo resumen'
        }), 500
