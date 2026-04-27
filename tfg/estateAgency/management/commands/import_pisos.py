from django.core.management.base import BaseCommand
from estateAgency.models import Source, Location, Property, Listing, ScrapingLog
from estateAgency.services.scraping.pisos_scraper import PisosScraper


class Command(BaseCommand):
    help = "Importa viviendas reales desde una URL publica de pisos.com"

    def add_arguments(self, parser):
        parser.add_argument("--url", required=True)
        parser.add_argument("--city", required=True)
        parser.add_argument(
            "--operation",
            choices=["sale", "rent"],
            default="sale"
        )
        parser.add_argument(
            "--rental-type",
            choices=["short", "long"],
            default=None
        )
        parser.add_argument("--limit", type=int, default=10)

    def handle(self, *args, **options):
        source, _ = Source.objects.get_or_create(
            name="pisos.com",
            defaults={"base_url": "https://www.pisos.com"}
        )

        location, _ = Location.objects.get_or_create(
            country="Spain",
            city=options["city"],
            province=options["city"],
        )

        scraper = PisosScraper(delay=2)

        try:
            scraped_properties = scraper.scrape(
                search_url=options["url"],
                city=options["city"],
                limit=options["limit"],
            )

            imported = 0

            for item in scraped_properties:
                if not item.price:
                    continue

                prop, created = Property.objects.get_or_create(
                    external_id=item.url,
                    source=source,
                    defaults={
                        "location": location,
                        "url": item.url,
                        "title": item.title,
                        "description": "Vivienda importada desde pisos.com",
                        "property_type": "flat",
                        "operation_type": options["operation"],
                        "rental_type": options["rental_type"],
                        "rooms": item.rooms,
                        "size_m2": item.size_m2,
                    }
                )

                Listing.objects.create(
                    property=prop,
                    price=item.price,
                    price_per_m2=(
                        item.price / item.size_m2
                        if item.size_m2
                        else None
                    ),
                    is_active=True,
                )

                imported += 1

            ScrapingLog.objects.create(
                source=source,
                status="success",
                message=f"Importadas {imported} viviendas desde pisos.com"
            )

            self.stdout.write(
                self.style.SUCCESS(f"Importadas {imported} viviendas")
            )

        except Exception as error:
            ScrapingLog.objects.create(
                source=source,
                status="error",
                message=str(error)
            )
            raise error
