#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar tablas obsoletas tras migración exitosa
"""

import psycopg2

class TableCleanup:
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
    
    def verify_migration_before_cleanup(self):
        """Verificar que la migración está completa antes de eliminar"""
        print("\n🔍 VERIFICACIÓN PREVIA A LIMPIEZA")
        print("=" * 60)
        
        # Verificar que las tablas nuevas tienen datos
        new_tables = [
            ('role', 'Roles'),
            ('"user"', 'Usuarios'),
            ('holiday', 'Festivos'),
            ('employee', 'Empleados'),
            ('team', 'Equipos')
        ]
        
        all_good = True
        
        for table, name in new_tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                if count > 0:
                    print(f"✅ {name:<15} - {count:>6} registros")
                else:
                    print(f"❌ {name:<15} - {count:>6} registros (vacía - NO ELIMINAR)")
                    all_good = False
            except Exception as e:
                print(f"❌ {name:<15} - Error: {e}")
                all_good = False
        
        return all_good
    
    def cleanup_old_tables(self):
        """Eliminar tablas obsoletas"""
        print("\n🧹 ELIMINANDO TABLAS OBSOLETAS")
        print("=" * 60)
        
        old_tables = [
            'roles',
            'users', 
            'employees',
            'holidays_new'
        ]
        
        success_count = 0
        
        for table in old_tables:
            try:
                # Verificar que la tabla existe
                self.cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = %s AND table_schema = 'public'
                """, (table,))
                
                if self.cursor.fetchone()[0] > 0:
                    # Eliminar la tabla
                    self.cursor.execute(f"DROP TABLE {table} CASCADE")
                    print(f"✅ Tabla '{table}' eliminada")
                    success_count += 1
                else:
                    print(f"⚠️  Tabla '{table}' no existe")
                    
            except Exception as e:
                print(f"❌ Error eliminando tabla '{table}': {e}")
                self.conn.rollback()
        
        self.conn.commit()
        return success_count == len(old_tables)
    
    def verify_cleanup(self):
        """Verificar que las tablas fueron eliminadas correctamente"""
        print("\n🔍 VERIFICACIÓN POST-LIMPIEZA")
        print("=" * 60)
        
        old_tables = ['roles', 'users', 'employees', 'holidays_new']
        
        all_removed = True
        
        for table in old_tables:
            try:
                self.cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = %s AND table_schema = 'public'
                """, (table,))
                
                exists = self.cursor.fetchone()[0] > 0
                if exists:
                    print(f"❌ Tabla '{table}' aún existe")
                    all_removed = False
                else:
                    print(f"✅ Tabla '{table}' eliminada correctamente")
                    
            except Exception as e:
                print(f"❌ Error verificando tabla '{table}': {e}")
                all_removed = False
        
        return all_removed
    
    def show_final_table_list(self):
        """Mostrar lista final de tablas"""
        print("\n📋 TABLAS FINALES EN SUPABASE")
        print("=" * 60)
        
        try:
            self.cursor.execute("""
                SELECT table_name, 
                       pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = self.cursor.fetchall()
            
            print("Tablas activas:")
            for table, size in tables:
                print(f"  ✅ {table:<25} {size}")
            
            print(f"\n📊 Total de tablas: {len(tables)}")
            
        except Exception as e:
            print(f"❌ Error obteniendo lista de tablas: {e}")
    
    def run_cleanup(self):
        """Ejecutar limpieza completa"""
        print("🧹 INICIANDO LIMPIEZA DE TABLAS OBSOLETAS")
        print("=" * 80)
        
        if not self.connect():
            return False
        
        try:
            # Paso 1: Verificar migración
            if not self.verify_migration_before_cleanup():
                print("\n❌ NO SE PUEDE PROCEDER CON LA LIMPIEZA")
                print("❌ Las tablas nuevas no tienen datos suficientes")
                return False
            
            print("\n✅ Verificación exitosa - Procediendo con limpieza")
            
            # Paso 2: Eliminar tablas obsoletas
            if not self.cleanup_old_tables():
                print("\n⚠️  LIMPIEZA COMPLETADA CON ERRORES")
                return False
            
            # Paso 3: Verificar limpieza
            if not self.verify_cleanup():
                print("\n⚠️  ALGUNAS TABLAS NO FUERON ELIMINADAS")
                return False
            
            # Paso 4: Mostrar resultado final
            self.show_final_table_list()
            
            print("\n🎉 LIMPIEZA COMPLETADA EXITOSAMENTE")
            print("✅ Todas las tablas obsoletas eliminadas")
            print("✅ Base de datos limpia y optimizada")
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR EN LIMPIEZA: {e}")
            return False
        finally:
            self.disconnect()

if __name__ == '__main__':
    cleanup = TableCleanup()
    success = cleanup.run_cleanup()
    exit(0 if success else 1)
