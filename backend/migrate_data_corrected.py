#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migración de datos CORREGIDO según estructuras reales de tablas
"""

import psycopg2
import sys
from datetime import datetime

class DataMigratorCorrected:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.database_url = "postgresql://postgres.xmaxohyxgsthligskjvg:Littletosti29.@aws-0-eu-west-3.pooler.supabase.com:6543/postgres"
        
    def connect(self):
        """Conectar a la base de datos"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor()
            print("✅ Conexión a Supabase establecida")
            return True
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def disconnect(self):
        """Desconectar de la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Desconectado de Supabase")
    
    def migrate_roles(self):
        """Migrar datos de roles → role"""
        print("\n🔄 MIGRANDO ROLES: roles → role")
        print("=" * 60)
        
        try:
            # Verificar datos existentes
            self.cursor.execute("SELECT COUNT(*) FROM roles")
            count_old = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM role")
            count_new = self.cursor.fetchone()[0]
            
            print(f"📊 roles: {count_old} registros")
            print(f"📊 role: {count_new} registros")
            
            if count_old > 0 and count_new == 0:
                # Migrar datos - roles no tiene created_at/updated_at
                self.cursor.execute("""
                    INSERT INTO role (id, name, description)
                    SELECT id, name, description 
                    FROM roles
                """)
                self.conn.commit()
                print(f"✅ Migrados {count_old} roles")
                
                # Verificar migración
                self.cursor.execute("SELECT COUNT(*) FROM role")
                count_after = self.cursor.fetchone()[0]
                print(f"✅ Verificación: {count_after} roles en tabla role")
                
                return True
            elif count_new > 0:
                print("⚠️  La tabla role ya tiene datos. No se migra.")
                return True
            else:
                print("⚠️  No hay datos en roles para migrar.")
                return True
                
        except Exception as e:
            print(f"❌ Error migrando roles: {e}")
            self.conn.rollback()
            return False
    
    def migrate_users(self):
        """Migrar datos de users → user"""
        print("\n🔄 MIGRANDO USUARIOS: users → user")
        print("=" * 60)
        
        try:
            # Verificar datos existentes
            self.cursor.execute("SELECT COUNT(*) FROM users")
            count_old = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM "user"')
            count_new = self.cursor.fetchone()[0]
            
            print(f"📊 users: {count_old} registros")
            print(f"📊 user: {count_new} registros")
            
            if count_old > 0 and count_new == 0:
                # Migrar datos - users usa full_name, user usa first_name/last_name
                self.cursor.execute("""
                    INSERT INTO "user" (
                        id, email, password, active, confirmed_at, fs_uniquifier,
                        first_name, last_name, created_at, updated_at
                    )
                    SELECT 
                        id, email, password, active, confirmed_at, fs_uniquifier,
                        CASE 
                            WHEN full_name IS NOT NULL AND full_name != '' 
                            THEN SPLIT_PART(full_name, ' ', 1)
                            ELSE NULL 
                        END as first_name,
                        CASE 
                            WHEN full_name IS NOT NULL AND full_name != '' AND POSITION(' ' IN full_name) > 0
                            THEN SUBSTRING(full_name FROM POSITION(' ' IN full_name) + 1)
                            ELSE NULL 
                        END as last_name,
                        created_at, updated_at
                    FROM users
                """)
                self.conn.commit()
                print(f"✅ Migrados {count_old} usuarios")
                
                # Verificar migración
                self.cursor.execute('SELECT COUNT(*) FROM "user"')
                count_after = self.cursor.fetchone()[0]
                print(f"✅ Verificación: {count_after} usuarios en tabla user")
                
                return True
            elif count_new > 0:
                print("⚠️  La tabla user ya tiene datos. No se migra.")
                return True
            else:
                print("⚠️  No hay datos en users para migrar.")
                return True
                
        except Exception as e:
            print(f"❌ Error migrando usuarios: {e}")
            self.conn.rollback()
            return False
    
    def migrate_holidays(self):
        """Migrar datos de holidays_new → holiday"""
        print("\n🔄 MIGRANDO FESTIVOS: holidays_new → holiday")
        print("=" * 60)
        
        try:
            # Verificar datos existentes
            self.cursor.execute("SELECT COUNT(*) FROM holidays_new")
            count_old = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM holiday")
            count_new = self.cursor.fetchone()[0]
            
            print(f"📊 holidays_new: {count_old} registros")
            print(f"📊 holiday: {count_new} registros")
            
            if count_old > 0 and count_new == 0:
                # Necesitamos obtener los nombres de países/regiones/ciudades desde las tablas de referencia
                print("🔍 Obteniendo información geográfica...")
                
                # Crear un mapeo de IDs a nombres
                country_map = {}
                region_map = {}
                city_map = {}
                
                try:
                    self.cursor.execute("SELECT id, name FROM countries")
                    country_map = dict(self.cursor.fetchall())
                    
                    self.cursor.execute("SELECT id, name FROM autonomous_communities")
                    region_map = dict(self.cursor.fetchall())
                    
                    self.cursor.execute("SELECT id, name FROM cities")
                    city_map = dict(self.cursor.fetchall())
                    
                    print(f"📊 Países: {len(country_map)}, Regiones: {len(region_map)}, Ciudades: {len(city_map)}")
                    
                except Exception as e:
                    print(f"⚠️  Error obteniendo datos geográficos: {e}")
                
                # Migrar datos con mapeo geográfico
                self.cursor.execute("""
                    INSERT INTO holiday (
                        name, date, country, region, city, holiday_type, 
                        description, is_fixed, active, created_at, updated_at
                    )
                    SELECT 
                        h.name, h.date, 
                        COALESCE(c.name, 'Unknown') as country,
                        COALESCE(ac.name, NULL) as region,
                        COALESCE(ci.name, NULL) as city,
                        h.holiday_type,
                        h.description,
                        true as is_fixed,
                        h.is_active as active,
                        h.created_at, h.updated_at
                    FROM holidays_new h
                    LEFT JOIN countries c ON h.country_id = c.id
                    LEFT JOIN autonomous_communities ac ON h.autonomous_community_id = ac.id
                    LEFT JOIN cities ci ON h.city_id = ci.id
                """)
                self.conn.commit()
                print(f"✅ Migrados {count_old} festivos")
                
                # Verificar migración
                self.cursor.execute("SELECT COUNT(*) FROM holiday")
                count_after = self.cursor.fetchone()[0]
                print(f"✅ Verificación: {count_after} festivos en tabla holiday")
                
                return True
            elif count_new > 0:
                print("⚠️  La tabla holiday ya tiene datos. No se migra.")
                return True
            else:
                print("⚠️  No hay datos en holidays_new para migrar.")
                return True
                
        except Exception as e:
            print(f"❌ Error migrando festivos: {e}")
            self.conn.rollback()
            return False
    
    def migrate_employees(self):
        """Migrar datos de employees → employee"""
        print("\n🔄 MIGRANDO EMPLEADOS: employees → employee")
        print("=" * 60)
        
        try:
            # Verificar datos existentes
            self.cursor.execute("SELECT COUNT(*) FROM employees")
            count_old = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM employee")
            count_new = self.cursor.fetchone()[0]
            
            print(f"📊 employees: {count_old} registros")
            print(f"📊 employee: {count_new} registros")
            
            if count_old > 0 and count_new == 0:
                # Primero necesitamos crear equipos para los empleados
                print("🔍 Creando equipos...")
                
                # Obtener equipos únicos
                self.cursor.execute("SELECT DISTINCT team_name FROM employees")
                teams = self.cursor.fetchall()
                
                team_map = {}
                for team_name, in teams:
                    # Crear equipo si no existe
                    self.cursor.execute("""
                        INSERT INTO team (name, description) 
                        VALUES (%s, 'Migrado automáticamente')
                        ON CONFLICT (name) DO NOTHING
                        RETURNING id
                    """, (team_name,))
                    
                    result = self.cursor.fetchone()
                    if result:
                        team_id = result[0]
                    else:
                        # Si ya existe, obtener su ID
                        self.cursor.execute("SELECT id FROM team WHERE name = %s", (team_name,))
                        team_id = self.cursor.fetchone()[0]
                    
                    team_map[team_name] = team_id
                    print(f"  ✅ Equipo '{team_name}' -> ID {team_id}")
                
                # Obtener información geográfica
                country_map = {}
                region_map = {}
                city_map = {}
                
                try:
                    self.cursor.execute("SELECT id, name FROM countries")
                    country_map = dict(self.cursor.fetchall())
                    
                    self.cursor.execute("SELECT id, name FROM autonomous_communities")
                    region_map = dict(self.cursor.fetchall())
                    
                    self.cursor.execute("SELECT id, name FROM cities")
                    city_map = dict(self.cursor.fetchall())
                    
                except Exception as e:
                    print(f"⚠️  Error obteniendo datos geográficos: {e}")
                
                # Migrar empleados
                self.cursor.execute("""
                    INSERT INTO employee (
                        id, full_name, team_id, hours_monday_thursday, hours_friday,
                        annual_vacation_days, annual_hld_hours, country, region, city,
                        active, approved, created_at, updated_at
                    )
                    SELECT 
                        e.id, e.full_name, %s as team_id,
                        e.hours_mon_thu as hours_monday_thursday,
                        e.hours_fri as hours_friday,
                        e.vacation_days as annual_vacation_days,
                        e.free_hours as annual_hld_hours,
                        COALESCE(c.name, e.autonomous_community) as country,
                        COALESCE(ac.name, NULL) as region,
                        COALESCE(ci.name, e.local_city) as city,
                        true as active, false as approved,
                        e.created_at, e.updated_at
                    FROM employees e
                    LEFT JOIN countries c ON e.country_id = c.id
                    LEFT JOIN autonomous_communities ac ON e.autonomous_community_id = ac.id
                    LEFT JOIN cities ci ON e.city_id = ci.id
                    WHERE e.team_name = %s
                """, (team_map.get('team_name', 1), 'team_name'))
                
                # Ejecutar para cada equipo
                for team_name, team_id in team_map.items():
                    self.cursor.execute("""
                        INSERT INTO employee (
                            id, full_name, team_id, hours_monday_thursday, hours_friday,
                            annual_vacation_days, annual_hld_hours, country, region, city,
                            active, approved, created_at, updated_at
                        )
                        SELECT 
                            e.id, e.full_name, %s as team_id,
                            e.hours_mon_thu as hours_monday_thursday,
                            e.hours_fri as hours_friday,
                            e.vacation_days as annual_vacation_days,
                            e.free_hours as annual_hld_hours,
                            COALESCE(c.name, e.autonomous_community) as country,
                            COALESCE(ac.name, NULL) as region,
                            COALESCE(ci.name, e.local_city) as city,
                            true as active, false as approved,
                            e.created_at, e.updated_at
                        FROM employees e
                        LEFT JOIN countries c ON e.country_id = c.id
                        LEFT JOIN autonomous_communities ac ON e.autonomous_community_id = ac.id
                        LEFT JOIN cities ci ON e.city_id = ci.id
                        WHERE e.team_name = %s
                    """, (team_id, team_name))
                
                self.conn.commit()
                print(f"✅ Migrados {count_old} empleados")
                
                # Verificar migración
                self.cursor.execute("SELECT COUNT(*) FROM employee")
                count_after = self.cursor.fetchone()[0]
                print(f"✅ Verificación: {count_after} empleados en tabla employee")
                
                return True
            elif count_new > 0:
                print("⚠️  La tabla employee ya tiene datos. No se migra.")
                return True
            else:
                print("⚠️  No hay datos en employees para migrar.")
                return True
                
        except Exception as e:
            print(f"❌ Error migrando empleados: {e}")
            self.conn.rollback()
            return False
    
    def verify_migration(self):
        """Verificar que la migración fue exitosa"""
        print("\n🔍 VERIFICACIÓN FINAL DE MIGRACIÓN")
        print("=" * 60)
        
        tables_to_check = [
            ('role', 'Roles'),
            ('"user"', 'Usuarios'),
            ('holiday', 'Festivos'),
            ('employee', 'Empleados'),
            ('team', 'Equipos')
        ]
        
        all_good = True
        
        for table, name in tables_to_check:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                if count > 0:
                    print(f"✅ {name:<15} - {count:>6} registros")
                else:
                    print(f"⚠️  {name:<15} - {count:>6} registros (vacía)")
                    all_good = False
            except Exception as e:
                print(f"❌ {name:<15} - Error: {e}")
                all_good = False
        
        return all_good
    
    def run_migration(self):
        """Ejecutar migración completa"""
        print("🚀 INICIANDO MIGRACIÓN DE DATOS CORREGIDA")
        print("=" * 80)
        print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.connect():
            return False
        
        try:
            # Paso 1: Migrar roles
            if not self.migrate_roles():
                return False
            
            # Paso 2: Migrar festivos
            if not self.migrate_holidays():
                return False
            
            # Paso 3: Migrar usuarios
            if not self.migrate_users():
                return False
            
            # Paso 4: Migrar empleados
            if not self.migrate_employees():
                return False
            
            # Paso 5: Verificar migración
            if self.verify_migration():
                print("\n🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
                print("✅ Todas las tablas tienen datos migrados")
                return True
            else:
                print("\n⚠️  MIGRACIÓN COMPLETADA CON ADVERTENCIAS")
                print("⚠️  Algunas tablas están vacías")
                return False
                
        except Exception as e:
            print(f"\n❌ ERROR EN MIGRACIÓN: {e}")
            return False
        finally:
            self.disconnect()

if __name__ == '__main__':
    migrator = DataMigratorCorrected()
    success = migrator.run_migration()
    sys.exit(0 if success else 1)
