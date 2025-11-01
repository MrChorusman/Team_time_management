"""
Comando CLI para actualizar festivos de años futuros
Uso: flask update-holidays --year 2026
"""
import click
from flask.cli import with_appcontext
from datetime import datetime
from services.holiday_service import HolidayService
from models.employee import Employee
from models.user import db

@click.command('update-holidays')
@click.option('--year', default=None, type=int, help='Año para actualizar (por defecto: próximo año)')
@click.option('--country', default=None, type=str, help='Código de país específico (ej: ES, MX)')
@click.option('--auto', is_flag=True, help='Carga automática de festivos para todos los países con empleados')
@with_appcontext
def update_holidays_command(year, country, auto):
    """
    Actualiza festivos para el próximo año
    
    Ejemplos de uso:
      flask update-holidays --year 2026
      flask update-holidays --year 2026 --country ES
      flask update-holidays --auto
    """
    holiday_service = HolidayService()
    
    # Determinar año a procesar
    if not year:
        year = datetime.now().year + 1
    
    click.echo('=' * 70)
    click.echo('🎉 ACTUALIZACIÓN DE FESTIVOS')
    click.echo('=' * 70)
    
    try:
        if auto:
            # Carga automática para todos los países con empleados
            click.echo(f'\n📅 Cargando festivos automáticamente para el año {year}...')
            results = holiday_service.refresh_holidays_for_year(year)
            
            click.echo(f'\n✅ Proceso completado')
            click.echo(f'   📊 Países procesados: {len(results["processed_countries"])}')
            click.echo(f'   🎉 Total festivos cargados: {results["total_holidays_loaded"]}')
            
            # Mostrar detalles por país
            click.echo('\n📋 Detalles por país:')
            for country_result in results['processed_countries']:
                status = '✅' if country_result['holidays_loaded'] > 0 else '⚠️'
                click.echo(f'   {status} {country_result["country"]}: {country_result["holidays_loaded"]} festivos')
                if country_result.get('errors'):
                    for error in country_result['errors'][:2]:
                        click.echo(f'      ⚠️  {error}')
            
            if results['errors']:
                click.echo(f'\n⚠️  Errores totales: {len(results["errors"])}')
                click.echo('   Primeros 5 errores:')
                for error in results['errors'][:5]:
                    click.echo(f'   - {error}')
        
        elif country:
            # Cargar festivos de un país específico
            click.echo(f'\n📅 Cargando festivos para {country} ({year})...')
            created, errors = holiday_service.load_holidays_for_country(country, year)
            
            if created > 0:
                click.echo(f'\n✅ {created} festivos cargados para {country} ({year})')
            else:
                click.echo(f'\n⚠️  No se cargaron festivos para {country}')
            
            if errors:
                click.echo(f'\n⚠️  Errores encontrados: {len(errors)}')
                for error in errors[:5]:
                    click.echo(f'   - {error}')
        
        else:
            # Sin flags, mostrar ayuda
            click.echo('\n⚠️  Debes especificar --auto o --country CODE')
            click.echo('\nEjemplos de uso:')
            click.echo('  flask update-holidays --year 2026 --auto')
            click.echo('  flask update-holidays --year 2026 --country ES')
            click.echo('  flask update-holidays --auto  # Año próximo por defecto')
            return
        
        # Mostrar estadísticas finales
        click.echo('\n' + '=' * 70)
        click.echo('📊 ESTADÍSTICAS FINALES')
        click.echo('=' * 70)
        
        summary = holiday_service.get_holidays_summary()
        click.echo(f'\n📈 Total festivos en base de datos: {summary["total_holidays"]}')
        click.echo(f'🌍 Países con festivos: {summary["countries_with_holidays"]}')
        click.echo(f'🎯 Tipos de festivos:')
        for type_stat in summary['type_stats']:
            click.echo(f'   - {type_stat["type"]}: {type_stat["count"]}')
        
        if summary.get('missing_countries'):
            click.echo(f'\n⚠️  Países sin festivos: {len(summary["missing_countries"])}')
            for missing_country in summary['missing_countries'][:5]:
                click.echo(f'   - {missing_country}')
        
        click.echo('\n✅ Actualización completada exitosamente\n')
    
    except Exception as e:
        click.echo(f'\n❌ Error durante la actualización: {e}')
        click.echo(f'   Tipo de error: {type(e).__name__}')
        import traceback
        click.echo(f'\n   Detalles técnicos:')
        click.echo(traceback.format_exc())
        raise


def init_app(app):
    """Registra el comando en la aplicación Flask"""
    app.cli.add_command(update_holidays_command)


