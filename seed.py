"""Seed the database with common houseplant species and care tips."""

from app import create_app, db
from app.models import Species

COMMON_SPECIES = [
    {
        "name": "Pothos",
        "watering_interval_days": 7,
        "sunlight": "Low to bright indirect light",
        "soil_type": "Well-draining potting mix",
        "common_issues": "Yellow leaves (overwatering), brown tips (underwatering), leggy growth (low light)",
        "care_tips": "Very forgiving and great for beginners. Trim vines to encourage bushier growth. Can grow in water indefinitely.",
    },
    {
        "name": "Snake Plant",
        "watering_interval_days": 14,
        "sunlight": "Low to bright indirect light",
        "soil_type": "Sandy, well-draining cactus/succulent mix",
        "common_issues": "Root rot (overwatering), mushy leaves, scarring from cold drafts",
        "care_tips": "Extremely drought-tolerant. Let soil dry completely between waterings. One of the best air-purifying plants.",
    },
    {
        "name": "Monstera",
        "watering_interval_days": 7,
        "sunlight": "Bright indirect light",
        "soil_type": "Peat-based, well-draining mix with perlite",
        "common_issues": "Yellow leaves (overwatering), brown edges (low humidity), no fenestrations (insufficient light)",
        "care_tips": "Provide a moss pole for climbing. Wipe leaves to remove dust. Increase humidity for larger leaves with more splits.",
    },
    {
        "name": "Fiddle Leaf Fig",
        "watering_interval_days": 10,
        "sunlight": "Bright indirect light, some direct morning sun",
        "soil_type": "Well-draining, nutrient-rich potting mix",
        "common_issues": "Brown spots (inconsistent watering), leaf drop (drafts or moving), root rot",
        "care_tips": "Keep in one spot — they dislike being moved. Water when top 2 inches of soil are dry. Rotate monthly for even growth.",
    },
    {
        "name": "Spider Plant",
        "watering_interval_days": 7,
        "sunlight": "Bright indirect light",
        "soil_type": "General-purpose potting mix",
        "common_issues": "Brown tips (fluoride in water or low humidity), pale leaves (too much sun)",
        "care_tips": "Use distilled or rainwater to avoid brown tips. Produces baby 'spiderettes' you can propagate. Great hanging plant.",
    },
    {
        "name": "Peace Lily",
        "watering_interval_days": 5,
        "sunlight": "Low to medium indirect light",
        "soil_type": "Peat-based mix that retains some moisture",
        "common_issues": "Drooping (underwatering — recovers quickly), brown tips (low humidity or chemicals in water)",
        "care_tips": "Will dramatically droop when thirsty but bounces back fast. Blooms more with brighter light. Toxic to pets.",
    },
    {
        "name": "Succulent",
        "watering_interval_days": 14,
        "sunlight": "Bright direct to indirect light (4-6 hours)",
        "soil_type": "Gritty cactus/succulent mix with sand and perlite",
        "common_issues": "Etiolation/stretching (not enough light), mushy leaves (overwatering), mealy bugs",
        "care_tips": "Soak and dry method — water thoroughly, then let soil dry completely. More light = more compact, colorful growth.",
    },
    {
        "name": "Cactus",
        "watering_interval_days": 21,
        "sunlight": "Full direct sunlight (6+ hours)",
        "soil_type": "Very fast-draining cactus mix with extra sand/gravel",
        "common_issues": "Root rot (overwatering), etiolation (insufficient light), scarring from sunburn if moved suddenly",
        "care_tips": "Water even less in winter (once a month). Acclimate gradually to direct sun. Use terracotta pots for faster drying.",
    },
    {
        "name": "Fern",
        "watering_interval_days": 3,
        "sunlight": "Low to medium indirect light (no direct sun)",
        "soil_type": "Rich, moisture-retaining peat-based mix",
        "common_issues": "Crispy fronds (low humidity), yellowing (too much light), dropping leaves (underwatering)",
        "care_tips": "Loves humidity — mist regularly or place near a humidifier. Keep soil consistently moist but not soggy. Great for bathrooms.",
    },
    {
        "name": "Rubber Plant",
        "watering_interval_days": 10,
        "sunlight": "Medium to bright indirect light",
        "soil_type": "Well-draining general potting mix with perlite",
        "common_issues": "Dropping leaves (overwatering or cold drafts), leggy growth (low light), dust buildup on leaves",
        "care_tips": "Wipe large leaves with a damp cloth monthly. Prune to desired shape — will branch from cut points. Likes to dry out between waterings.",
    },
]

app = create_app()

with app.app_context():
    for data in COMMON_SPECIES:
        existing = Species.query.filter_by(name=data["name"]).first()
        if existing:
            existing.sunlight = data["sunlight"]
            existing.soil_type = data["soil_type"]
            existing.common_issues = data["common_issues"]
            existing.care_tips = data["care_tips"]
        else:
            db.session.add(Species(**data))
    db.session.commit()
    print(f"Seeded/updated {len(COMMON_SPECIES)} species with care tips.")
