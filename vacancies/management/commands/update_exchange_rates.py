from django.core.management.base import BaseCommand
from django.utils import timezone
from vacancies.models import ExchangeRate
import requests
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Обновляет курсы валют из API НБРБ'

    def handle(self, *args, **options):
        try:
            response = requests.get('https://www.nbrb.by/api/exrates/rates?periodicity=0')
            if response.status_code == 200:
                data = response.json()
                updated_count = 0
                
                for rate_data in data:
                    currency = rate_data['Cur_Abbreviation']
                    rate = rate_data['Cur_OfficialRate'] / rate_data['Cur_Scale']
                    
                    exchange_rate, created = ExchangeRate.objects.update_or_create(
                        currency=currency,
                        defaults={'rate': rate}
                    )
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Обновлен курс {currency}: {rate} BYN')
                    )
                
                # Добавляем BYN как базовую валюту с курсом 1.0
                ExchangeRate.objects.update_or_create(
                    currency='BYN',
                    defaults={'rate': 1.0}
                )
                updated_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Всего успешно обновлено {updated_count} курсов валют')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка API: {response.status_code}')
                )
        except Exception as e:
            logger.error(f"Ошибка при получении курсов валют из БД: {e}")
            # В случае ошибки используем резервные значения
            rates = {'USD': 2.5, 'EUR': 2.6, 'RUB': 0.033, 'UZS': 0.00020}
            self.stdout.write(
                self.style.ERROR(f'Ошибка при обновлении курсов: {str(e)}')
            ) 