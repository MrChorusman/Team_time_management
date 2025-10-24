#!/usr/bin/env python3
"""
Script para crear equipos específicos basados en la información de cobertura proporcionada
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Conectar a la base de datos Supabase"""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('SUPABASE_HOST'),
            port=os.environ.get('SUPABASE_PORT', '6543'),
            database=os.environ.get('SUPABASE_DB_NAME', 'postgres'),
            user=os.environ.get('SUPABASE_DB_USER', 'postgres'),
            password=os.environ.get('SUPABASE_DB_PASSWORD')
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def create_specific_teams():
    """Crear equipos específicos basados en la información de cobertura"""
    print("🏢 Creando equipos específicos según cobertura...")
    
    # Equipos basados en la información proporcionada
    teams_data = [
        # Sistemas base
        {
            "name": "ARES",
            "description": "Sistema ARES - Cobertura diaria hasta 19:00, viernes on call/presencial según calendario"
        },
        {
            "name": "SAP FICO",
            "description": "SAP FICO - Cobertura diaria hasta 19:00, viernes on call/presencial según calendario"
        },
        {
            "name": "SAP AA",
            "description": "SAP Asset Accounting - Cobertura diaria hasta 19:00, viernes on call/presencial según calendario"
        },
        {
            "name": "Fisterra",
            "description": "Sistema Fisterra - Cobertura diaria hasta 19:00, viernes on call/presencial según calendario"
        },
        
        # Excepciones
        {
            "name": "Interco",
            "description": "Intercompany - Siempre cobertura on call, día de cierre hasta 21:00"
        },
        {
            "name": "SFI Conta",
            "description": "SFI Contabilidad - Día de cierre presencial hasta 21:00"
        },
        
        # Transacciones
        {
            "name": "SAP RE",
            "description": "SAP Real Estate - Viernes on call siempre, salvo post-cierre sin cobertura"
        },
        {
            "name": "SAP DES",
            "description": "SAP Desarrollo - Siempre cobertura on call"
        },
        {
            "name": "SAP BI",
            "description": "SAP Business Intelligence - Siempre cobertura on call"
        },
        
        # Roll Out
        {
            "name": "Roll Out España",
            "description": "Roll Out España - Plan de cobertura base según calendario de cierre"
        },
        {
            "name": "Roll Out Filiales",
            "description": "Roll Out Filiales - Plan específico con equipo de arranque en primeros 2 cierres"
        },
        
        # Equipos de soporte
        {
            "name": "Soporte Transaccional",
            "description": "Equipo de soporte para transacciones especiales y cierres de cajas"
        },
        {
            "name": "Equipo de Arranque",
            "description": "Equipo especializado en arranques de nuevos cierres y filiales"
        }
    ]
    
    conn = get_db_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = conn.cursor()
        
        created_count = 0
        skipped_count = 0
        
        for team in teams_data:
            # Verificar si el equipo ya existe
            cursor.execute("SELECT id FROM team WHERE name = %s", (team["name"],))
            if cursor.fetchone():
                print(f"   ⚠️  Equipo '{team['name']}' ya existe, omitiendo...")
                skipped_count += 1
                continue
            
            # Crear el equipo
            cursor.execute("""
                INSERT INTO team (name, description, created_at, updated_at)
                VALUES (%s, %s, NOW(), NOW())
                RETURNING id
            """, (team["name"], team["description"]))
            
            team_id = cursor.fetchone()[0]
            print(f"   ✅ Creado: {team['name']} (ID: {team_id})")
            created_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n📊 RESUMEN:")
        print(f"   ✅ Equipos creados: {created_count}")
        print(f"   ⚠️  Equipos omitidos: {skipped_count}")
        print(f"   📋 Total equipos en BD: {created_count + skipped_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando equipos: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def list_all_teams():
    """Listar todos los equipos disponibles"""
    print("\n📋 EQUIPOS DISPONIBLES EN LA BASE DE DATOS:")
    print("=" * 60)
    
    conn = get_db_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM team ORDER BY name")
        teams = cursor.fetchall()
        
        for team in teams:
            print(f"   {team[0]:2d}. {team[1]:<20} - {team[2]}")
        
        print(f"\n   📊 Total: {len(teams)} equipos")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error listando equipos: {e}")
        if conn:
            conn.close()

def main():
    """Función principal"""
    print("🚀 CREACIÓN DE EQUIPOS ESPECÍFICOS")
    print("=" * 50)
    
    # Crear equipos específicos
    if not create_specific_teams():
        print("❌ Error creando equipos")
        return
    
    # Listar todos los equipos
    list_all_teams()
    
    print("\n🎉 CONFIGURACIÓN DE EQUIPOS COMPLETADA")
    print("=" * 50)
    print("📋 EQUIPOS CREADOS SEGÚN COBERTURA:")
    print("   🏢 Sistemas Base: ARES, SAP FICO, SAP AA, Fisterra")
    print("   ⚠️  Excepciones: Interco, SFI Conta")
    print("   💼 Transacciones: SAP RE, SAP DES, SAP BI")
    print("   🌍 Roll Out: España, Filiales")
    print("   🔧 Soporte: Transaccional, Equipo de Arranque")
    print("\n🚀 LISTO PARA REGISTRO DE EMPLEADOS")

if __name__ == "__main__":
    main()




