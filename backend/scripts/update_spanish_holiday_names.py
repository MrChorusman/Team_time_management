import os
from typing import List

from main import create_app
from models import db
from models.holiday import Holiday


SPANISH_COUNTRY_NAMES: List[str] = [
    'España', 'Spain', 'México', 'Mexico', 'Argentina', 'Colombia', 'Chile',
    'Perú', 'Uruguay', 'Paraguay', 'Bolivia', 'Venezuela', 'Costa Rica',
    'República Dominicana', 'Dominican Republic', 'Ecuador', 'Guatemala',
    'Honduras', 'Nicaragua', 'Panamá', 'Puerto Rico', 'El Salvador'
]


def looks_spanish(text: str) -> bool:
    if not text:
        return False

    lower = text.lower()
    spanish_keywords = [
        'día', 'navidad', 'virgen', 'constitución', 'reyes', 'santos',
        'independencia', 'patria', 'nacional', 'inmaculada', 'semana santa',
        'pascua', 'carnaval', 'asunción', 'san ', 'santa ', 'fiesta'
    ]

    has_accents = any(char in text for char in 'áéíóúñÁÉÍÓÚÑ')
    contains_keyword = any(keyword in lower for keyword in spanish_keywords)
    return has_accents or contains_keyword


def update_spanish_holiday_names():
    env = os.environ.get('FLASK_ENV')
    app = create_app(env)

    with app.app_context():
        holidays = Holiday.query.filter(Holiday.country.in_(SPANISH_COUNTRY_NAMES)).all()
        updated_names = 0
        updated_countries = 0

        for holiday in holidays:
            # Normalizar país a su versión en español
            if holiday.country == 'Spain':
                holiday.country = 'España'
                updated_countries += 1
            if holiday.country == 'Mexico':
                holiday.country = 'México'
                updated_countries += 1

            # Si la descripción está en español y el nombre no, sincronizar
            if holiday.description and looks_spanish(holiday.description) and not looks_spanish(holiday.name):
                holiday.name = holiday.description
                updated_names += 1

        if updated_names or updated_countries:
            db.session.commit()

        print(f"Festivos actualizados: nombres={updated_names}, paises={updated_countries}")


if __name__ == '__main__':
    update_spanish_holiday_names()

