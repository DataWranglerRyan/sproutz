"""Seed the database with common houseplant species and care tips."""

from app import create_app, db
from app.models import Species, SpeciesIssue

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
        "name": "Canna Lily",
        "watering_interval_days": 2,
        "sunlight": "Full direct sunlight (6+ hours)",
        "soil_type": "Rich, moist, well-draining soil with organic matter",
        "common_issues": "Rust fungus (orange spots on leaves), caterpillars (leaf rollers), rhizome rot in waterlogged soil",
        "care_tips": "Heavy feeders — fertilize monthly during growing season. Cut spent flower stalks to encourage more blooms. Dig up rhizomes before frost in cold climates and store over winter.",
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

SPECIES_ISSUES = {
    "Pothos": [
        ("Yellow leaves", "Reduce watering frequency — let the top inch of soil dry out between waterings"),
        ("Brown leaf tips", "Increase watering slightly or raise humidity with a pebble tray"),
        ("Leggy, sparse growth", "Move to a brighter spot with more indirect light; trim long vines to encourage fullness"),
    ],
    "Snake Plant": [
        ("Mushy/soft leaves", "Stop watering immediately. Remove affected leaves and let soil dry completely. Repot if root rot is extensive"),
        ("Leaves falling over", "Usually overwatering — reduce frequency. Ensure pot isn't too large for the root system"),
        ("Brown/scarred patches", "Move away from cold drafts or windows. Avoid temperatures below 50°F"),
    ],
    "Monstera": [
        ("Yellow leaves", "Cut back on watering. Check for root rot and repot in fresh soil if needed"),
        ("Brown crispy edges", "Increase humidity — mist daily, use a humidifier, or place on a pebble tray"),
        ("No leaf fenestrations", "Provide more bright indirect light. Young plants need maturity + light to develop splits"),
        ("Drooping leaves", "Usually needs water. Soak thoroughly and it should perk up within hours"),
    ],
    "Fiddle Leaf Fig": [
        ("Brown spots on leaves", "Establish a consistent watering schedule. Check for root rot if spots are dark and spreading"),
        ("Dropping leaves", "Avoid moving the plant. Keep away from drafts and heating/AC vents"),
        ("Red/brown spots near veins", "Likely root rot — reduce watering, ensure drainage, repot in dry soil if severe"),
    ],
    "Spider Plant": [
        ("Brown leaf tips", "Switch to distilled or rainwater — spider plants are sensitive to fluoride and chlorine"),
        ("Pale/faded leaves", "Move to a spot with less direct sunlight; they prefer bright indirect light"),
        ("No babies/spiderettes", "Needs to be slightly root-bound and get enough light. Avoid repotting too frequently"),
    ],
    "Peace Lily": [
        ("Dramatic drooping", "Water thoroughly — peace lilies droop when thirsty but recover quickly within an hour"),
        ("Brown leaf tips", "Use filtered water and increase humidity. Trim brown tips with scissors"),
        ("No flowers", "Move to brighter indirect light. They need sufficient light energy to produce blooms"),
    ],
    "Succulent": [
        ("Stretched/elongated growth", "Needs much more light. Move to the brightest window or add a grow light"),
        ("Mushy translucent leaves", "Overwatered — remove affected leaves, let soil dry, reduce watering dramatically"),
        ("White cottony spots (mealybugs)", "Dab with rubbing alcohol using a cotton swab. Isolate plant and treat weekly until clear"),
    ],
    "Cactus": [
        ("Soft/mushy base", "Root rot from overwatering. Cut away rot, let callus for days, repot in dry soil"),
        ("Leaning/stretching toward light", "Rotate regularly and provide more direct sunlight hours"),
        ("White/brown scaly patches", "Likely sunburn from sudden direct sun exposure. Acclimate gradually over 1-2 weeks"),
    ],
    "Fern": [
        ("Crispy/brown fronds", "Humidity too low — mist daily, use a humidifier, or move to bathroom"),
        ("Yellowing fronds", "Too much direct light — move to a shadier spot with filtered light"),
        ("Dropping leaves", "Soil is too dry — keep consistently moist (not soggy). Never let it fully dry out"),
    ],
    "Rubber Plant": [
        ("Dropping lower leaves", "Overwatering or cold drafts. Let top 2 inches dry between waterings and move from drafty areas"),
        ("Leggy with few leaves", "Needs more light. Prune the top to encourage branching"),
        ("Dusty/dull leaves", "Wipe with a damp cloth monthly. Dust blocks light absorption and slows growth"),
    ],
    "Canna Lily": [
        ("Orange spots on leaves (rust)", "Remove affected leaves immediately. Improve air circulation and avoid overhead watering"),
        ("Rolled/chewed leaves (caterpillars)", "Inspect and hand-pick leaf roller caterpillars. Use Bt (Bacillus thuringiensis) spray for infestations"),
        ("Mushy rhizomes", "Improve drainage. Dig up, cut away rotted sections, let dry, and replant in better-draining soil"),
    ],
}

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

    # Seed issues/solutions
    for species_name, issues in SPECIES_ISSUES.items():
        species = Species.query.filter_by(name=species_name).first()
        if species:
            # Clear existing issues to avoid duplicates on re-seed
            SpeciesIssue.query.filter_by(species_id=species.id).delete()
            for issue, solution in issues:
                db.session.add(SpeciesIssue(species_id=species.id, issue=issue, solution=solution))
    db.session.commit()
    print(f"Seeded/updated {len(COMMON_SPECIES)} species with care tips and issue/solution pairs.")
