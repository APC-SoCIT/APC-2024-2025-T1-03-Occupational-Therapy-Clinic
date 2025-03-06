import requests
from django.core.management.base import BaseCommand
from accounts.models import Province, Municipality

PSGC_BASE_URL = "https://psgc.gitlab.io/api"

class Command(BaseCommand):
    help = "Fetch and populate Province and Municipality from PSGC API"

    def handle(self, *args, **kwargs):
        self.populate_provinces()
        self.populate_municipalities()
        self.stdout.write(self.style.SUCCESS("Successfully populated all geographic data."))

    def populate_provinces(self):
        response = requests.get(f"{PSGC_BASE_URL}/provinces.json")
        if response.status_code == 200:
            data = response.json()
            provinces = [Province(code=item['code'], name=item['name']) for item in data]
            Province.objects.bulk_create(provinces, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Provinces populated: {len(provinces)}"))
        else:
            self.stderr.write(self.style.ERROR("Failed to fetch provinces"))

    def populate_municipalities(self):
        response = requests.get(f"{PSGC_BASE_URL}/cities-municipalities.json")
        if response.status_code == 200:
            data = response.json()
            municipalities = []
            for item in data:
                province = Province.objects.filter(code=item['provinceCode']).first()
                if province:
                    municipalities.append(Municipality(code=item['code'], name=item['name'], province=province))
            Municipality.objects.bulk_create(municipalities, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Municipalities populated: {len(municipalities)}"))
        else:
            self.stderr.write(self.style.ERROR("Failed to fetch municipalities"))

