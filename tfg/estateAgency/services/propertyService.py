from django.db.models import Prefetch
from estateAgency.models import Property, Listing
from estateAgency.dto.propertyDTO import PropertyDTO

PROPERTY_IMAGE_COUNTS = {
    "flat": 75,
    "studio": 75,
    "penthouse": 75,
    "duplex": 75,
    "house": 20,
    "unknown": 20,
}

PROPERTY_IMAGE_PREFIXES = {
    "flat": "flat",
    "studio": "flat",
    "penthouse": "flat",
    "duplex": "flat",
    "house": "house",
    "unknown": "unknown",
}

def _image_prefix(property_type):
    return PROPERTY_IMAGE_PREFIXES.get(property_type or "unknown", "unknown")

def _image_count(property_type):
    return PROPERTY_IMAGE_COUNTS.get(property_type or "unknown", PROPERTY_IMAGE_COUNTS["unknown"])

def get_property_image_path(property_id, property_type=None):
    prefix = _image_prefix(property_type)
    image_number = ((property_id or 1) - 1) % _image_count(property_type) + 1
    return f"estateAgency/img/{prefix}-{image_number:02d}.jpg"

def get_property_list_image_path(position, property_type=None):
    prefix = _image_prefix(property_type)
    image_number = (position % _image_count(property_type)) + 1
    return f"estateAgency/img/{prefix}-{image_number:02d}.jpg"

def get_properties_by_location(city=None, province=None):
    
    queryset = Property.objects.select_related("location").prefetch_related(
        Prefetch(
            "listings",
            queryset=Listing.objects.order_by("-scraped_at"),
            to_attr="prefetched_listings"
        )
    )

    if city:
        queryset = queryset.filter(location__city__iexact=city)

    if province:
        queryset = queryset.filter(location__province__iexact=province)

    dtos = []

    image_positions = {}

    for p in queryset:
        image_key = _image_prefix(p.property_type)
        image_position = image_positions.get(image_key, 0)
        image_positions[image_key] = image_position + 1
        latest_listing = p.prefetched_listings[0] if p.prefetched_listings else None

        dto = PropertyDTO(
            id=p.id,
            title=p.title,
            price=float(latest_listing.price) if latest_listing else None,
            city=p.location.city if p.location else None,
            province=p.location.province if p.location else None,
            rooms=p.rooms,
            size_m2=float(p.size_m2) if p.size_m2 else None,
            price_per_m2=float(latest_listing.price_per_m2) if latest_listing and latest_listing.price_per_m2 else None,
            image_path=get_property_list_image_path(image_position, p.property_type)
        )

        dtos.append(dto)

    return dtos

def get_properties_by_operation(flag, city= None):

    queryset = Property.objects.select_related("location").prefetch_related(
        Prefetch(
            "listings",
            queryset=Listing.objects.order_by("-scraped_at"),
            to_attr="prefetched_listings"
        )
    )

    if flag == "sale":
        queryset = queryset.filter(operation_type="sale")

    elif flag == "rent_short":
        queryset = queryset.filter(operation_type="rent", rental_type="short")

    elif flag == "rent_long":
        queryset = queryset.filter(operation_type="rent", rental_type="long")
        
    if city:
        queryset = queryset.filter(location__city__iexact=city)

    dtos = []

    image_positions = {}

    for p in queryset:
        image_key = _image_prefix(p.property_type)
        image_position = image_positions.get(image_key, 0)
        image_positions[image_key] = image_position + 1
        latest_listing = p.prefetched_listings[0] if p.prefetched_listings else None

        dtos.append(PropertyDTO(
            id=p.id,
            title=p.title,
            price=float(latest_listing.price) if latest_listing else None,
            city=p.location.city if p.location else None,
            province=p.location.province if p.location else None,
            rooms=p.rooms,
            size_m2=float(p.size_m2) if p.size_m2 else None,
            price_per_m2=float(latest_listing.price_per_m2) if latest_listing and latest_listing.price_per_m2 else None,
            image_path=get_property_list_image_path(image_position, p.property_type)
        ))

    return dtos
