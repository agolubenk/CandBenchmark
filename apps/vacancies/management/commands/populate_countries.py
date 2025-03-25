# файл: vacancies/management/commands/populate_countries.py

from django.core.management.base import BaseCommand
from apps.vacancies.models import Country

class Command(BaseCommand):
    help = "Populate the Country model with CIS and European countries (with alias typos)"

    # Для демонстрации я подготовил словарь { code: {name_ru, alias, flag_svg} }
    # flag_svg - можно поставить реальный Base64 (полученный через https://www.base64-image.de/ или аналог),
    # а пока для упрощения будут флаги-заглушки (просто цветные прямоугольники).
    CIS_EUROPE_COUNTRIES = {
        # СНГ
        'BY': {
            'name_ru': 'Беларусь',
            'alias': 'Belarus, РБ, Hjccfk, Hjccfkm, Белорусь',  # добавили опечатки
            'flag_svg': 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIj8+Cjxzdmcgdmlld0JveD0iMCAwIDQwIDI0IiB3aWR0aD0iNDAiIGhlaWdodD0iMjQiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnL3N2ZyI+PHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjI0IiBmaWxsPSIjZmYwMDAwIi8+PHJlY3QgeT0iMTYiIHdpZHRoPSI0MCIgaGVpZ2h0PSI4IiBmaWxsPSIjMDA4MDAwIi8+PC9zdmc+'
        },
        'RU': {
            'name_ru': 'Россия',
            'alias': 'Russia, РФ, Hjccbz',
            'flag_svg': 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIj8+Cjxzdmcgdmlld0JveD0iMCAwIDQwIDI0IiB3aWR0aD0iNDAiIGhlaWdodD0iMjQiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnL3N2ZyI+PHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjI0IiBmaWxsPSIjZmZmIi8+PHJlY3QgeT0iOCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjgiIGZpbGw9IiNiYzAwMDQiLz48cmVjdCB5PSIxNiIgd2lkdGg9IjQwIiBoZWlnaHQ9IjgiIGZpbGw9IiNmZjAwMDAiLz48L3N2Zz4='
        },
        'KZ': {
            'name_ru': 'Казахстан',
            'alias': 'Kazakhstan, Qazaqstan, Hjccfcnfyf',
            'flag_svg': 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIj8+PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCA0MCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnL3N2ZyI+PHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjI0IiBmaWxsPSIjMDBjY2NjIi8+PC9zdmc+'
        },
        'UA': {
            'name_ru': 'Украина',
            'alias': 'Ukraine, Ycrajkf, Hjccrktyf, Ukraїna',
            'flag_svg': 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIj8+PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCA0MCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnL3N2ZyI+PGc+PHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjEyIiBmaWxsPSIjZmZmMzAwIi8+PHJlY3QgeT0iMTIiIHdpZHRoPSI0MCIgaGVpZ2h0PSIxMiIgZmlsbD0iIzAwM2FiNyIvPjwvZz48L3N2Zz4='
        },
        'MD': {
            'name_ru': 'Молдова',
            'alias': 'Moldova, Vjkjljdf, Hjcckjdf, Moldova',
            'flag_svg': 'data:image/svg+xml;base64,PD94bWwg...'  # заглушка
        },
        'AZ': {
            'name_ru': 'Азербайджан',
            'alias': 'Azerbaijan, Fpth,kfzafy, Hjcc,kfzafy',
            'flag_svg': 'data:image/svg+xml;base64,PD94bWwg...'  # заглушка
        },
        # ... добавьте остальные страны СНГ, если нужно ...

        # Несколько стран Европы
        'PL': {
            'name_ru': 'Польша',
            'alias': 'Poland, Gjkifly, Hjccifly, Polska',
            'flag_svg': 'data:image/svg+xml;base64,PD94bWwg...'  # заглушка
        },
        'DE': {
            'name_ru': 'Германия',
            'alias': 'Germany, Uthvfyz, Hjccvfyz, Deutschland',
            'flag_svg': 'data:image/svg+xml;base64,PD94bWwg...'  # заглушка
        },
        'FR': {
            'name_ru': 'Франция',
            'alias': 'France, Ahyfwtz, Hjccwtz, Republique',
            'flag_svg': 'data:image/svg+xml;base64,PD94bWwg...'  # заглушка
        },
        'ES': {
            'name_ru': 'Испания',
            'alias': 'Spain, Cgfybqz, Hjccybqz, Espana',
            'flag_svg': 'data:image/svg+xml;base64,PD94bWwg...'  # заглушка
        },
        'IT': {
            'name_ru': 'Италия',
            'alias': 'Italy, Bnfkbz, Hjcckbz, Italia',
            'flag_svg': 'data:image/svg+xml;base64,PD94bWwg...'  # заглушка
        },
        # ... при желании добавьте и другие страны Европы ...
    }

    def handle(self, *args, **options):
        # Создаем/обновляем записи
        for code, data in self.CIS_EUROPE_COUNTRIES.items():
            obj, created = Country.objects.update_or_create(
                code=code,
                defaults={
                    'name_ru': data['name_ru'],
                    'alias': data['alias'],
                    'flag_svg': data['flag_svg']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Country: {obj}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated Country: {obj}"))