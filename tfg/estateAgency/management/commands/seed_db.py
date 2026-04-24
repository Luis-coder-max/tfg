from django.core.management.base import BaseCommand
from estateAgency.models import (
    Source, Location, Property, Listing, PropertyFeature
)
import random
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed database with realistic test data'

    def handle(self, *args, **kwargs):
        Property.objects.all().delete()
        Location.objects.all().delete()
        Listing.objects.all().delete()
        PropertyFeature.objects.all().delete()
        Source.objects.all().delete()
        self.stdout.write("Seeding database...")

        source, _ = Source.objects.get_or_create(
            name="pisos.com",
            defaults={"base_url": "https://www.pisos.com"}
        )

        cityGroup = {
            'Spain': [
                ("Madrid", "Madrid", 40.4168, -3.7038),
                ("Barcelona", "Barcelona", 41.3874, 2.1686),
                ("Valencia", "Valencia", 39.4699, -0.3763),
            ],
            'England': [
                ("London", "Greater London", 51.5074, -0.1278),
                ("Manchester", "Greater Manchester", 53.4808, -2.2426),
                ("Birmingham", "West Midlands", 52.4862, -1.8904),
            ]
        }
        locations = []
        for country, cities in cityGroup.items():
            for city, province, lat, lon in cities:
                loc, _ = Location.objects.get_or_create(
                    country=country,
                    city=city,
                    province=province,
                    defaults={
                        "latitude": lat,
                        "longitude": lon
                    }
                )
                locations.append(loc)

        # 🔵 PROPERTIES
        properties = []

        for i in range(50):
            location = random.choice(locations)

            prop = Property.objects.create(
                external_id=f"prop_{i}",
                source=source,
                location=location,
                url=f"https://example.com/property/{i}",
                title=f"Piso en {location.city} #{i}",
                description="Piso bonito y bien ubicado",
                property_type="flat",
                operation_type="sale",
                rooms=random.randint(1, 5),
                bathrooms=random.randint(1, 3),
                size_m2=random.randint(50, 150),
                floor=str(random.randint(1, 10)),
                energy_rating=random.choice(["A", "B", "C", "D"])
            )

            properties.append(prop)

            # 🟠 FEATURES
            PropertyFeature.objects.create(
                property=prop,
                has_elevator=random.choice([True, False]),
                has_garage=random.choice([True, False]),
                has_terrace=random.choice([True, False]),
                has_pool=random.choice([True, False]),
                condition_status=random.choice([
                    "new", "good", "renovation", "needs_renovation"
                ])
            )

            # 🟢 LISTINGS (histórico de precios)
            base_price = random.randint(100000, 500000)

            for j in range(5):  # histórico de 5 precios
                Listing.objects.create(
                    property=prop,
                    price=base_price - j * random.randint(1000, 5000),
                    price_per_m2=base_price / prop.size_m2,
                    published_at=timezone.now() - timedelta(days=30 * j),
                    scraped_at=timezone.now() - timedelta(days=30 * j),
                    is_active=(j == 0)
                )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))