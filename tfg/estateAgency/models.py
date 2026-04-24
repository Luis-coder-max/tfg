from django.db import models

class Source(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    country = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    neighborhood = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    def __str__(self):
        return f"{self.city} ({self.province})"

class Property(models.Model):

    PROPERTY_TYPE_CHOICES = [
        ('flat', 'Flat'),
        ('house', 'House'),
        ('studio', 'Studio'),
        ('penthouse', 'Penthouse'),
        ('duplex', 'Duplex'),
        ('land', 'Land'),
        ('other', 'Other'),
    ]

    OPERATION_TYPE_CHOICES = [
        ('sale', 'Sale'),
        ('rent', 'Rent'),
    ]

    external_id = models.CharField(max_length=100)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    url = models.URLField(unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPE_CHOICES)

    rooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.IntegerField(null=True, blank=True)
    size_m2 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    floor = models.CharField(max_length=50, blank=True, null=True)
    energy_rating = models.CharField(max_length=10, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('external_id', 'source')
        indexes = [
            models.Index(fields=['property_type']),
            models.Index(fields=['operation_type']),
        ]

    def __str__(self):
        return self.title

class Listing(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="listings")

    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_per_m2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    published_at = models.DateTimeField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['scraped_at']),
        ]

    def __str__(self):
        return f"{self.property.title} - {self.price}€"

class PropertyFeature(models.Model):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name="features")

    has_elevator = models.BooleanField(null=True, blank=True)
    has_garage = models.BooleanField(null=True, blank=True)
    has_terrace = models.BooleanField(null=True, blank=True)
    has_pool = models.BooleanField(null=True, blank=True)

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('renovation', 'Renovation'),
        ('needs_renovation', 'Needs Renovation'),
    ]

    condition_status = models.CharField(max_length=20, choices=CONDITION_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"Features of {self.property.title}"

class Prediction(models.Model):
    property = models.ForeignKey(Property, null=True, blank=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)

    predicted_price = models.DecimalField(max_digits=12, decimal_places=2)
    model_name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction {self.predicted_price}€"

class AreaStats(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="stats")

    avg_price = models.DecimalField(max_digits=12, decimal_places=2)
    avg_price_m2 = models.DecimalField(max_digits=12, decimal_places=2)
    num_properties = models.IntegerField()

    date = models.DateField()

    class Meta:
        unique_together = ('location', 'date')

    def __str__(self):
        return f"Stats {self.location.city} - {self.date}"

class ScrapingLog(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'),
    ]

    source = models.ForeignKey(Source, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.status} - {self.created_at}"

