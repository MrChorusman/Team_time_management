from flask import Blueprint, request, jsonify
from flask_security import auth_required
import logging

from models.location import Country, AutonomousCommunity, Province, City

logger = logging.getLogger(__name__)

locations_bp = Blueprint('locations', __name__)


@locations_bp.route('/countries', methods=['GET'])
@auth_required()
def get_countries():
    """Obtiene lista de países activos"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = Country.query
        if active_only:
            query = query.filter(Country.is_active == True)
        
        countries = query.order_by(Country.name).all()
        
        return jsonify({
            'success': True,
            'countries': [country.to_dict() for country in countries],
            'total_count': len(countries)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo países: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo países'
        }), 500


@locations_bp.route('/autonomous-communities', methods=['GET'])
@auth_required()
def get_autonomous_communities():
    """Obtiene comunidades autónomas, opcionalmente filtradas por país"""
    try:
        country_id = request.args.get('country_id', type=int)
        country_code = request.args.get('country_code')
        
        query = AutonomousCommunity.query
        
        # Filtrar por country_id si se proporciona
        if country_id:
            query = query.filter(AutonomousCommunity.country_id == country_id)
        # O filtrar por country_code
        elif country_code:
            country = Country.query.filter(Country.code == country_code).first()
            if country:
                query = query.filter(AutonomousCommunity.country_id == country.id)
        
        communities = query.order_by(AutonomousCommunity.name).all()
        
        return jsonify({
            'success': True,
            'autonomous_communities': [ac.to_dict() for ac in communities],
            'total_count': len(communities)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo comunidades autónomas: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo comunidades autónomas'
        }), 500


@locations_bp.route('/provinces', methods=['GET'])
@auth_required()
def get_provinces():
    """Obtiene provincias, opcionalmente filtradas por comunidad autónoma"""
    try:
        autonomous_community_id = request.args.get('autonomous_community_id', type=int)
        
        query = Province.query
        
        if autonomous_community_id:
            query = query.filter(Province.autonomous_community_id == autonomous_community_id)
        
        provinces = query.order_by(Province.name).all()
        
        return jsonify({
            'success': True,
            'provinces': [province.to_dict() for province in provinces],
            'total_count': len(provinces)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo provincias: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo provincias'
        }), 500


@locations_bp.route('/cities', methods=['GET'])
@auth_required()
def get_cities():
    """Obtiene ciudades, opcionalmente filtradas por comunidad autónoma o búsqueda"""
    try:
        autonomous_community_id = request.args.get('autonomous_community_id', type=int)
        search = request.args.get('search')
        limit = request.args.get('limit', 100, type=int)
        
        query = City.query
        
        # Filtrar por comunidad autónoma
        if autonomous_community_id:
            query = query.filter(City.autonomous_community_id == autonomous_community_id)
        
        # Buscar por nombre
        if search:
            query = query.filter(City.name.ilike(f'%{search}%'))
        
        # Limitar resultados para mejor performance
        cities = query.order_by(City.name).limit(min(limit, 100)).all()
        
        return jsonify({
            'success': True,
            'cities': [city.to_dict() for city in cities],
            'total_count': len(cities)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo ciudades: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo ciudades'
        }), 500


@locations_bp.route('/search', methods=['GET'])
@auth_required()
def search_locations():
    """Búsqueda unificada de ubicaciones"""
    try:
        search_term = request.args.get('q', '')
        location_type = request.args.get('type', 'all')  # all, country, community, city
        
        if not search_term or len(search_term) < 2:
            return jsonify({
                'success': False,
                'message': 'El término de búsqueda debe tener al menos 2 caracteres'
            }), 400
        
        results = {
            'countries': [],
            'autonomous_communities': [],
            'cities': []
        }
        
        # Buscar países
        if location_type in ['all', 'country']:
            countries = Country.query.filter(
                Country.name.ilike(f'%{search_term}%'),
                Country.is_active == True
            ).limit(10).all()
            results['countries'] = [c.to_dict() for c in countries]
        
        # Buscar comunidades autónomas
        if location_type in ['all', 'community']:
            communities = AutonomousCommunity.query.filter(
                AutonomousCommunity.name.ilike(f'%{search_term}%')
            ).limit(10).all()
            results['autonomous_communities'] = [ac.to_dict() for ac in communities]
        
        # Buscar ciudades
        if location_type in ['all', 'city']:
            cities = City.query.filter(
                City.name.ilike(f'%{search_term}%')
            ).limit(10).all()
            results['cities'] = [c.to_dict() for c in cities]
        
        return jsonify({
            'success': True,
            'results': results,
            'search_term': search_term
        })
        
    except Exception as e:
        logger.error(f"Error en búsqueda de ubicaciones: {e}")
        return jsonify({
            'success': False,
            'message': 'Error en búsqueda de ubicaciones'
        }), 500


