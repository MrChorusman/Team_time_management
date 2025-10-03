#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migración de datos de tablas antiguas a nuevas
"""

import psycopg2
import sys
from datetime import datetime

class DataMigrator:
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
    
    def validate_reference_tables(self):
        """Validar tablas de referencia geográfica"""
        print("\n🔍 VALIDANDO TABLAS DE REFERENCIA GEOGRÁFICA")
        print("=" * 60)
        
        reference_tables = ['countries', 'cities', 'autonomous_communities', 'provinces']
        
        for table in reference_tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"✅ {table:<25} - {count:>6} registros")
            except Exception as e:
                print(f"❌ {table:<25} - Error: {e}")
        
        print("\n📝 CONCLUSIÓN: Estas tablas NO se usan en el código actual.")
        print("   El código usa campos de texto simples (country, region, city)")
        print("   Se pueden mantener para futuras mejoras o eliminar si no se necesitan.")
    
    def migrate_roles(self):
        """Migrar datos de roles → role"""
        print("\n🔄 MIGRANDO ROLES: roles → role")
        print("=" * 60)
        
        try:
            # Verificar si hay datos en roles
            self.cursor.execute("SELECT COUNT(*) FROM roles")
            count_old = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM role")
            count_new = self.cursor.fetchone()[0]
            
            print(f"📊 roles: {count_old} registros")
            print(f"📊 role: {count_new} registros")
            
            if count_old > 0 and count_new == 0:
                # Migrar datos
                self.cursor.execute("""
                    INSERT INTO role (id, name, description, created_at, updated_at)
                    SELECT id, name, description, created_at, updated_at 
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
            
            self.cursor.execute("SELECT COUNT(*) FROM \"user\"")
            count_new = self.cursor.fetchone()[0]
            
            print(f"📊 users: {count_old} registros")
            print(f"📊 user: {count_new} registros")
            
            if count_old > 0 and count_new == 0:
                # Obtener estructura de ambas tablas
                self.cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND table_schema = 'public'
                    ORDER BY ordinal_position
                """)
                users_columns = self.cursor.fetchall()
                
                self.cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'user' AND table_schema = 'public'
                    ORDER BY ordinal_position
                """)
                user_columns = self.cursor.fetchall()
                
                print("📋 Columnas en users:", [col[0] for col in users_columns])
                print("📋 Columnas en user:", [col[0] for col in user_columns])
                
                # Migrar datos (solo columnas comunes)
                common_columns = ['id', 'email', 'username', 'password', 'active', 'confirmed_at', 
                                'fs_uniquifier', 'first_name', 'last_name', 'last_login_at', 
                                'current_login_at', 'last_login_ip', 'current_login_ip', 
                                'login_count', 'created_at', 'updated_at']
                
                columns_str = ', '.join(common_columns)
                
                self.cursor.execute(f"""
                    INSERT INTO "user" ({columns_str})
                    SELECT {columns_str}
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
                # Migrar datos
                self.cursor.execute("""
                    INSERT INTO holiday (
                        name, date, country, region, city, holiday_type, 
                        description, is_fixed, source, source_id, active, 
                        created_at, updated_at
                    )
                    SELECT 
                        name, date, country, region, city, holiday_type,
                        description, is_fixed, source, source_id, active,
                        created_at, updated_at
                    FROM holidays_new
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
                # Migrar datos (ajustar nombres de columnas según sea necesario)
                self.cursor.execute("""
                    INSERT INTO employee (
                        id, user_id, full_name, team_id, hours_monday_thursday, 
                        hours_friday, hours_summer, has_summer_schedule, summer_months,
                        annual_vacation_days, annual_hld_hours, country, region, city,
                        active, approved, created_at, updated_at, approved_at
                    )
                    SELECT 
                        id, user_id, full_name, team_id, hours_monday_thursday,
                        hours_friday, hours_summer, has_summer_schedule, summer_months,
                        annual_vacation_days, annual_hld_hours, country, region, city,
                        active, approved, created_at, updated_at, approved_at
                    FROM employees
                """)
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
            ('employee', 'Empleados')
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
        print("🚀 INICIANDO MIGRACIÓN DE DATOS")
        print("=" * 80)
        print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.connect():
            return False
        
        try:
            # Paso 1: Validar tablas de referencia
            self.validate_reference_tables()
            
            # Paso 2: Migrar roles
            if not self.migrate_roles():
                return False
            
            # Paso 3: Migrar festivos
            if not self.migrate_holidays():
                return False
            
            # Paso 4: Migrar usuarios
            if not self.migrate_users():
                return False
            
            # Paso 5: Migrar empleados
            if not self.migrate_employees():
                return False
            
            # Paso 6: Verificar migración
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
    migrator = DataMigrator()
    success = migrator.run_migration()
    sys.exit(0 if success else 1)
