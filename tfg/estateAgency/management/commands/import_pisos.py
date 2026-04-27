import unicodedata

from django.core.management.base import BaseCommand
from estateAgency.models import Source, Location, Property, Listing, ScrapingLog
from estateAgency.services.scraping.pisos_scraper import PisosScraper


def slugify_for_pisos(value):
    """
    Convierte nombres tipo:
    'Madrid Capital' -> 'madrid_capital'
    'A Coruña' -> 'a_coruna'
    """
    value = value.lower().strip()
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.replace(" ", "_")
    value = value.replace("-", "_")
    return value


def build_pisos_url(location, operation):
    """
    Genera la URL de pisos.com según la localización.
    De momento prioriza ciudad.
    """

    city_slug = slugify_for_pisos(location.city)

    if operation == "sale":
        return f"https://www.pisos.com/venta/pisos-{city_slug}/"

    if operation == "rent":
        return f"https://www.pisos.com/alquiler/pisos-{city_slug}/"

    raise ValueError(f"Operación no válida: {operation}")


class Command(BaseCommand):
    help = "Importa viviendas reales desde pisos.com para todas las localizaciones de la base de datos"

    def add_arguments(self, parser):
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

        parser.add_argument(
            "--city",
            required=False,
            help="Opcional. Scrapea solo una ciudad concreta"
        )

    def handle(self, *args, **options):
        source, _ = Source.objects.get_or_create(
            name="pisos.com",
            defaults={"base_url": "https://www.pisos.com"}
        )

        scraper = PisosScraper(delay=2)

        locations = (
            Location.objects
            .filter(country__iexact="Spain")
            .exclude(city__isnull=True)
            .exclude(city="")
        )

        if options.get("city"):
            locations = locations.filter(city__iexact=options["city"])

        total_imported = 0
        total_locations = locations.count()

        self.stdout.write(
            self.style.WARNING(
                f"Iniciando scraping de pisos.com para {total_locations} localizaciones"
            )
        )

        for location in locations:
            url = build_pisos_url(
                location=location,
                operation=options["operation"]
            )

            self.stdout.write(
                f"Scrapeando {location.city} -> {url}"
            )

            try:
                scraped_properties = scraper.scrape(
                    search_url=url,
                    city=location.city,
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

                total_imported += imported

                ScrapingLog.objects.create(
                    source=source,
                    status="success",
                    message=(
                        f"Importadas {imported} viviendas desde pisos.com "
                        f"para {location.city}"
                    )
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"{location.city}: importadas {imported} viviendas"
                    )
                )

            except Exception as error:
                ScrapingLog.objects.create(
                    source=source,
                    status="error",
                    message=f"Error en {location.city}: {str(error)}"
                )

                self.stdout.write(
                    self.style.ERROR(
                        f"Error scrapeando {location.city}: {error}"
                    )
                )

                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Scraping terminado. Total importadas: {total_imported}"
            )
        )