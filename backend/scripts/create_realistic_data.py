"""
Script para generar datos realistas de equipos y empleados
Reemplaza los datos de prueba con información más realista
"""

import os
import sys
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, User, Role, Employee, Team, Holiday, CalendarActivity, Notification
from services.holiday_service import HolidayService

class RealisticDataGenerator:
    """Generador de datos realistas para el sistema"""
    
    def __init__(self):
        self.teams_data = [
            {
                'name': 'Desarrollo Frontend',
                'description': 'Equipo responsable del desarrollo de interfaces de usuario',
                'manager_name': 'Ana García',
                'manager_email': 'ana.garcia@company.com'
            },
            {
                'name': 'Desarrollo Backend',
                'description': 'Equipo responsable de la lógica de negocio y APIs',
                'manager_name': 'Carlos Rodríguez',
                'manager_email': 'carlos.rodriguez@company.com'
            },
            {
                'name': 'DevOps',
                'description': 'Equipo responsable de infraestructura y despliegues',
                'manager_name': 'María López',
                'manager_email': 'maria.lopez@company.com'
            },
            {
                'name': 'Diseño UX/UI',
                'description': 'Equipo responsable del diseño de experiencia de usuario',
                'manager_name': 'David Martín',
                'manager_email': 'david.martin@company.com'
            },
            {
                'name': 'Marketing Digital',
                'description': 'Equipo responsable de estrategias de marketing online',
                'manager_name': 'Laura Sánchez',
                'manager_email': 'laura.sanchez@company.com'
            },
            {
                'name': 'Ventas',
                'description': 'Equipo responsable de ventas y relaciones con clientes',
                'manager_name': 'Roberto Fernández',
                'manager_email': 'roberto.fernandez@company.com'
            },
            {
                'name': 'Soporte Técnico',
                'description': 'Equipo responsable del soporte a usuarios y clientes',
                'manager_name': 'Isabel González',
                'manager_email': 'isabel.gonzalez@company.com'
            },
            {
                'name': 'Recursos Humanos',
                'description': 'Equipo responsable de gestión de personal y talento',
                'manager_name': 'Miguel Torres',
                'manager_email': 'miguel.torres@company.com'
            },
            {
                'name': 'Administración',
                'description': 'Equipo responsable de gestión administrativa y financiera',
                'manager_name': 'Carmen Ruiz',
                'manager_email': 'carmen.ruiz@company.com'
            },
            {
                'name': 'Dirección',
                'description': 'Equipo directivo y de toma de decisiones estratégicas',
                'manager_name': 'Alejandro Jiménez',
                'manager_email': 'alejandro.jimenez@company.com'
            }
        ]
        
        self.employee_names = [
            ('Ana', 'García'), ('Carlos', 'Rodríguez'), ('María', 'López'), ('David', 'Martín'),
            ('Laura', 'Sánchez'), ('Roberto', 'Fernández'), ('Isabel', 'González'), ('Miguel', 'Torres'),
            ('Carmen', 'Ruiz'), ('Alejandro', 'Jiménez'), ('Elena', 'Vargas'), ('Pablo', 'Moreno'),
            ('Sofia', 'Herrera'), ('Javier', 'Díaz'), ('Natalia', 'Castro'), ('Andrés', 'Mendoza'),
            ('Patricia', 'Romero'), ('Fernando', 'Álvarez'), ('Mónica', 'Silva'), ('Antonio', 'Ramos'),
            ('Cristina', 'Navarro'), ('Diego', 'Morales'), ('Raquel', 'Ortega'), ('Sergio', 'Delgado'),
            ('Beatriz', 'Vega'), ('Manuel', 'Herrero'), ('Teresa', 'Iglesias'), ('Francisco', 'Peña'),
            ('Rosa', 'Blanco'), ('José', 'Gutiérrez'), ('Pilar', 'Molina'), ('Juan', 'Cabrera'),
            ('Mercedes', 'Reyes'), ('Pedro', 'Aguilar'), ('Concepción', 'Santos'), ('Rafael', 'Cruz'),
            ('Dolores', 'Medina'), ('Ángel', 'Castillo'), ('Esperanza', 'Cortés'), ('Vicente', 'Garrido'),
            ('Encarnación', 'León'), ('José Antonio', 'Márquez'), ('María Carmen', 'Guerrero'),
            ('José Manuel', 'Lozano'), ('María Pilar', 'Ibáñez'), ('Francisco Javier', 'Muñoz'),
            ('María Dolores', 'Gallego'), ('Antonio José', 'Vázquez'), ('María Teresa', 'Sanz'),
            ('José Luis', 'Gil'), ('María Ángeles', 'Serrano'), ('Manuel José', 'Ramírez')
        ]
        
        self.countries = ['ES', 'FR', 'DE', 'IT', 'PT', 'GB', 'US', 'MX', 'AR', 'BR']
        self.cities = {
            'ES': ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza'],
            'FR': ['París', 'Lyon', 'Marsella', 'Toulouse', 'Niza'],
            'DE': ['Berlín', 'Múnich', 'Hamburgo', 'Colonia', 'Frankfurt'],
            'IT': ['Roma', 'Milán', 'Nápoles', 'Turín', 'Florencia'],
            'PT': ['Lisboa', 'Oporto', 'Coímbra', 'Braga', 'Faro'],
            'GB': ['Londres', 'Manchester', 'Birmingham', 'Liverpool', 'Leeds'],
            'US': ['Nueva York', 'Los Ángeles', 'Chicago', 'Houston', 'Phoenix'],
            'MX': ['Ciudad de México', 'Guadalajara', 'Monterrey', 'Puebla', 'Tijuana'],
            'AR': ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza', 'La Plata'],
            'BR': ['São Paulo', 'Río de Janeiro', 'Brasilia', 'Salvador', 'Fortaleza']
        }
        
        self.hour_configs = [
            {'daily_hours': 8.0, 'weekly_hours': 40.0, 'vacation_days': 22},
            {'daily_hours': 7.5, 'weekly_hours': 37.5, 'vacation_days': 20},
            {'daily_hours': 6.0, 'weekly_hours': 30.0, 'vacation_days': 18},
            {'daily_hours': 4.0, 'weekly_hours': 20.0, 'vacation_days': 15}
        ]
    
    def clean_existing_data(self, preserve_admins=True):
        """Limpia datos existentes preservando usuarios admin si se especifica"""
        print("🧹 Limpiando datos existentes...")
        
        # Eliminar actividades de calendario
        CalendarActivity.query.delete()
        print("   ✓ Actividades de calendario eliminadas")
        
        # Eliminar notificaciones
        Notification.query.delete()
        print("   ✓ Notificaciones eliminadas")
        
        # Eliminar empleados
        Employee.query.delete()
        print("   ✓ Empleados eliminados")
        
        # Eliminar equipos
        Team.query.delete()
        print("   ✓ Equipos eliminados")
        
        # Eliminar usuarios (preservando admins si se especifica)
        if preserve_admins:
            admin_users = User.query.join(User.roles).filter(Role.name == 'admin').all()
            admin_emails = [user.email for user in admin_users]
            User.query.filter(~User.email.in_(admin_emails)).delete()
            print(f"   ✓ Usuarios eliminados (preservando {len(admin_users)} admins)")
        else:
            User.query.delete()
            print("   ✓ Todos los usuarios eliminados")
        
        db.session.commit()
        print("✅ Datos limpiados exitosamente")
    
    def create_teams(self):
        """Crea equipos realistas"""
        print("👥 Creando equipos...")
        
        teams = []
        for team_data in self.teams_data:
            team = Team(
                name=team_data['name'],
                description=team_data['description'],
                active=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            db.session.add(team)
            teams.append(team)
        
        db.session.commit()
        print(f"✅ {len(teams)} equipos creados")
        return teams
    
    def create_managers(self, teams):
        """Crea usuarios manager para cada equipo"""
        print("👨‍💼 Creando managers...")
        
        managers = []
        manager_role = Role.query.filter_by(name='manager').first()
        
        for i, team in enumerate(teams):
            team_data = self.teams_data[i]
            
            # Crear usuario manager
            manager_user = User(
                email=team_data['manager_email'],
                password_hash=generate_password_hash('password123'),
                first_name=team_data['manager_name'].split()[0],
                last_name=team_data['manager_name'].split()[1],
                active=True,
                confirmed_at=datetime.utcnow(),
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            manager_user.roles.append(manager_role)
            db.session.add(manager_user)
            
            # Crear empleado manager
            manager_employee = Employee(
                user_id=manager_user.id,
                full_name=team_data['manager_name'],
                team_id=team.id,
                daily_hours=8.0,
                weekly_hours=40.0,
                vacation_days=25,
                country=random.choice(self.countries),
                city=random.choice(self.cities[random.choice(self.countries)]),
                active=True,
                approved=True,
                created_at=manager_user.created_at
            )
            db.session.add(manager_employee)
            
            # Asignar manager al equipo
            team.manager_id = manager_employee.id
            
            managers.append(manager_employee)
        
        db.session.commit()
        print(f"✅ {len(managers)} managers creados")
        return managers
    
    def create_employees(self, teams):
        """Crea empleados realistas distribuidos entre equipos"""
        print("👷 Creando empleados...")
        
        employees = []
        employee_role = Role.query.filter_by(name='employee').first()
        
        # Distribuir empleados entre equipos
        employees_per_team = len(self.employee_names) // len(teams)
        remaining_employees = len(self.employee_names) % len(teams)
        
        employee_index = 0
        for i, team in enumerate(teams):
            # Calcular número de empleados para este equipo
            team_employee_count = employees_per_team
            if i < remaining_employees:
                team_employee_count += 1
            
            for j in range(team_employee_count):
                if employee_index >= len(self.employee_names):
                    break
                
                first_name, last_name = self.employee_names[employee_index]
                email = f"{first_name.lower()}.{last_name.lower()}@company.com"
                
                # Crear usuario empleado
                employee_user = User(
                    email=email,
                    password_hash=generate_password_hash('password123'),
                    first_name=first_name,
                    last_name=last_name,
                    active=True,
                    confirmed_at=datetime.utcnow(),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 300))
                )
                employee_user.roles.append(employee_role)
                db.session.add(employee_user)
                
                # Configuración de horas aleatoria
                hour_config = random.choice(self.hour_configs)
                country = random.choice(self.countries)
                
                # Crear empleado
                employee = Employee(
                    user_id=employee_user.id,
                    full_name=f"{first_name} {last_name}",
                    team_id=team.id,
                    daily_hours=hour_config['daily_hours'],
                    weekly_hours=hour_config['weekly_hours'],
                    vacation_days=hour_config['vacation_days'],
                    country=country,
                    city=random.choice(self.cities[country]),
                    active=True,
                    approved=random.choice([True, True, True, False]),  # 75% aprobados
                    created_at=employee_user.created_at
                )
                db.session.add(employee)
                employees.append(employee)
                
                employee_index += 1
        
        db.session.commit()
        print(f"✅ {len(employees)} empleados creados")
        return employees
    
    def create_calendar_activities(self, employees):
        """Crea actividades de calendario realistas"""
        print("📅 Creando actividades de calendario...")
        
        activity_types = ['vacation', 'absence', 'hld', 'guard', 'training', 'others']
        activities = []
        
        for employee in employees:
            # Crear 5-15 actividades por empleado
            num_activities = random.randint(5, 15)
            
            for _ in range(num_activities):
                # Fecha aleatoria en los últimos 6 meses
                start_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))
                
                # Duración aleatoria (1-5 días para vacaciones, 1 día para otros)
                activity_type = random.choice(activity_types)
                if activity_type == 'vacation':
                    duration_days = random.randint(1, 5)
                else:
                    duration_days = 1
                
                end_date = start_date + timedelta(days=duration_days)
                
                activity = CalendarActivity(
                    employee_id=employee.id,
                    activity_type=activity_type,
                    start_date=start_date.date(),
                    end_date=end_date.date(),
                    description=f"Actividad de {activity_type} para {employee.full_name}",
                    approved=random.choice([True, True, False]),  # 66% aprobados
                    created_at=start_date
                )
                db.session.add(activity)
                activities.append(activity)
        
        db.session.commit()
        print(f"✅ {len(activities)} actividades de calendario creadas")
        return activities
    
    def create_notifications(self, employees):
        """Crea notificaciones realistas"""
        print("🔔 Creando notificaciones...")
        
        notification_types = ['system_alert', 'reminder', 'holiday_alert', 'vacation_reminder', 'hours_report']
        priorities = ['low', 'medium', 'high']
        notifications = []
        
        for employee in employees:
            # Crear 2-8 notificaciones por empleado
            num_notifications = random.randint(2, 8)
            
            for _ in range(num_notifications):
                notification_type = random.choice(notification_types)
                priority = random.choice(priorities)
                
                # Fecha aleatoria en los últimos 30 días
                created_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                
                notification = Notification(
                    user_id=employee.user_id,
                    title=f"Notificación de {notification_type}",
                    message=f"Esta es una notificación de {notification_type} para {employee.full_name}",
                    notification_type=notification_type,
                    priority=priority,
                    read=random.choice([True, True, False]),  # 66% leídas
                    send_email=random.choice([True, False]),  # 50% con email
                    email_sent=random.choice([True, False]),  # 50% emails enviados
                    created_at=created_at
                )
                db.session.add(notification)
                notifications.append(notification)
        
        db.session.commit()
        print(f"✅ {len(notifications)} notificaciones creadas")
        return notifications
    
    def load_holidays(self):
        """Carga festivos para los países de los empleados"""
        print("🎉 Cargando festivos...")
        
        holiday_service = HolidayService()
        countries_to_load = set()
        
        # Obtener países únicos de empleados
        employees = Employee.query.filter(Employee.active == True).all()
        for employee in employees:
            countries_to_load.add(employee.country)
        
        total_holidays = 0
        for country in countries_to_load:
            try:
                holidays = holiday_service.load_holidays_for_country(country, datetime.now().year)
                total_holidays += len(holidays)
                print(f"   ✓ {len(holidays)} festivos cargados para {country}")
            except Exception as e:
                print(f"   ⚠️ Error cargando festivos para {country}: {e}")
        
        print(f"✅ Total: {total_holidays} festivos cargados")
    
    def generate_all_data(self, preserve_admins=True):
        """Genera todos los datos realistas"""
        print("🚀 Iniciando generación de datos realistas...")
        print("=" * 50)
        
        try:
            # Limpiar datos existentes
            self.clean_existing_data(preserve_admins)
            
            # Crear equipos
            teams = self.create_teams()
            
            # Crear managers
            managers = self.create_managers(teams)
            
            # Crear empleados
            employees = self.create_employees(teams)
            
            # Crear actividades de calendario
            activities = self.create_calendar_activities(employees)
            
            # Crear notificaciones
            notifications = self.create_notifications(employees)
            
            # Cargar festivos
            self.load_holidays()
            
            print("=" * 50)
            print("✅ Generación de datos completada exitosamente!")
            print(f"📊 Resumen:")
            print(f"   • {len(teams)} equipos")
            print(f"   • {len(managers)} managers")
            print(f"   • {len(employees)} empleados")
            print(f"   • {len(activities)} actividades de calendario")
            print(f"   • {len(notifications)} notificaciones")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generando datos: {e}")
            db.session.rollback()
            return False

def main():
    """Función principal para ejecutar el script"""
    from flask import Flask
    from config import config
    
    # Crear aplicación Flask
    app = Flask(__name__)
    config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Inicializar base de datos
    db.init_app(app)
    
    with app.app_context():
        generator = RealisticDataGenerator()
        
        # Preservar admins por defecto en modo no interactivo
        preserve_admins = True
        
        # Generar datos
        success = generator.generate_all_data(preserve_admins)
        
        if success:
            print("\n🎉 ¡Datos realistas generados exitosamente!")
            print("💡 Puedes usar las credenciales:")
            print("   • Email: ana.garcia@company.com")
            print("   • Password: password123")
            print("   • Rol: Manager")
        else:
            print("\n❌ Error generando datos realistas")
            sys.exit(1)

if __name__ == '__main__':
    main()
