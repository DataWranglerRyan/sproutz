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
        "fertilizer_type": "Balanced liquid fertilizer (10-10-10 or 20-20-20)",
        "fertilizer_schedule": "Once a month during spring and summer",
        "fertilizer_notes": "Dilute to half strength. No fertilizer needed in fall/winter. Over-fertilizing causes brown leaf edges.",
    },
    {
        "name": "Snake Plant",
        "watering_interval_days": 14,
        "sunlight": "Low to bright indirect light",
        "soil_type": "Sandy, well-draining cactus/succulent mix",
        "common_issues": "Root rot (overwatering), mushy leaves, scarring from cold drafts",
        "care_tips": "Extremely drought-tolerant. Let soil dry completely between waterings. One of the best air-purifying plants.",
        "fertilizer_type": "Balanced houseplant fertilizer (10-10-10)",
        "fertilizer_schedule": "Once in spring and once in summer",
        "fertilizer_notes": "Very light feeder — less is more. Dilute to half strength. Skip fertilizer entirely in fall/winter.",
    },
    {
        "name": "Monstera",
        "watering_interval_days": 7,
        "sunlight": "Bright indirect light",
        "soil_type": "Peat-based, well-draining mix with perlite",
        "common_issues": "Yellow leaves (overwatering), brown edges (low humidity), no fenestrations (insufficient light)",
        "care_tips": "Provide a moss pole for climbing. Wipe leaves to remove dust. Increase humidity for larger leaves with more splits.",
        "fertilizer_type": "Balanced liquid fertilizer (20-20-20) or fertilizer higher in nitrogen",
        "fertilizer_schedule": "Every 2-4 weeks during spring and summer",
        "fertilizer_notes": "Supports large leaf growth. Reduce to monthly in fall, stop in winter. Flush soil every few months to prevent salt buildup.",
    },
    {
        "name": "Fiddle Leaf Fig",
        "watering_interval_days": 10,
        "sunlight": "Bright indirect light, some direct morning sun",
        "soil_type": "Well-draining, nutrient-rich potting mix",
        "common_issues": "Brown spots (inconsistent watering), leaf drop (drafts or moving), root rot",
        "care_tips": "Keep in one spot — they dislike being moved. Water when top 2 inches of soil are dry. Rotate monthly for even growth.",
        "fertilizer_type": "Liquid fertilizer with 3-1-2 NPK ratio (e.g., 9-3-6)",
        "fertilizer_schedule": "Every 4 weeks during growing season (spring/summer)",
        "fertilizer_notes": "High nitrogen supports leaf growth. Don't fertilize new plants for 1 month after repotting. Stop in winter.",
    },
    {
        "name": "Spider Plant",
        "watering_interval_days": 7,
        "sunlight": "Bright indirect light",
        "soil_type": "General-purpose potting mix",
        "common_issues": "Brown tips (fluoride in water or low humidity), pale leaves (too much sun)",
        "care_tips": "Use distilled or rainwater to avoid brown tips. Produces baby 'spiderettes' you can propagate. Great hanging plant.",
        "fertilizer_type": "Balanced liquid fertilizer (10-10-10 or 20-20-20)",
        "fertilizer_schedule": "Every 2 weeks during spring and summer",
        "fertilizer_notes": "Sensitive to fluoride and boron in some fertilizers — use organic if possible. Reduce to monthly in fall, skip winter.",
    },
    {
        "name": "Peace Lily",
        "watering_interval_days": 5,
        "sunlight": "Low to medium indirect light",
        "soil_type": "Peat-based mix that retains some moisture",
        "common_issues": "Drooping (underwatering — recovers quickly), brown tips (low humidity or chemicals in water)",
        "care_tips": "Will dramatically droop when thirsty but bounces back fast. Blooms more with brighter light. Toxic to pets.",
        "fertilizer_type": "Balanced liquid fertilizer (20-20-20)",
        "fertilizer_schedule": "Every 6-8 weeks during spring and summer",
        "fertilizer_notes": "Light feeder. Too much fertilizer causes brown leaf tips and prevents blooming. Dilute to quarter strength.",
    },
    {
        "name": "Succulent",
        "watering_interval_days": 14,
        "sunlight": "Bright direct to indirect light (4-6 hours)",
        "soil_type": "Gritty cactus/succulent mix with sand and perlite",
        "common_issues": "Etiolation/stretching (not enough light), mushy leaves (overwatering), mealy bugs",
        "care_tips": "Soak and dry method — water thoroughly, then let soil dry completely. More light = more compact, colorful growth.",
        "fertilizer_type": "Cactus/succulent fertilizer or diluted balanced fertilizer",
        "fertilizer_schedule": "Once a month during spring and summer only",
        "fertilizer_notes": "Dilute to quarter strength. Never fertilize dormant plants in winter. Too much causes leggy, weak growth.",
    },
    {
        "name": "Cactus",
        "watering_interval_days": 21,
        "sunlight": "Full direct sunlight (6+ hours)",
        "soil_type": "Very fast-draining cactus mix with extra sand/gravel",
        "common_issues": "Root rot (overwatering), etiolation (insufficient light), scarring from sunburn if moved suddenly",
        "care_tips": "Water even less in winter (once a month). Acclimate gradually to direct sun. Use terracotta pots for faster drying.",
        "fertilizer_type": "Low-nitrogen cactus fertilizer (2-7-7 or 1-2-2 ratio)",
        "fertilizer_schedule": "2-3 times total during spring/summer growing season",
        "fertilizer_notes": "Very light feeder. High nitrogen causes soft, vulnerable growth. Stop entirely in fall/winter dormancy.",
    },
    {
        "name": "Fern",
        "watering_interval_days": 3,
        "sunlight": "Low to medium indirect light (no direct sun)",
        "soil_type": "Rich, moisture-retaining peat-based mix",
        "common_issues": "Crispy fronds (low humidity), yellowing (too much light), dropping leaves (underwatering)",
        "care_tips": "Loves humidity — mist regularly or place near a humidifier. Keep soil consistently moist but not soggy. Great for bathrooms.",
        "fertilizer_type": "Balanced liquid fertilizer (20-20-20) or fish emulsion",
        "fertilizer_schedule": "Every 2-4 weeks during spring and summer",
        "fertilizer_notes": "Dilute to half strength — ferns have sensitive roots. Organic options like fish emulsion work great. Reduce in winter.",
    },
    {
        "name": "Perennial Hibiscus",
        "watering_interval_days": 2,
        "sunlight": "Full direct sunlight (6-8 hours)",
        "soil_type": "Rich, moist, well-draining soil amended with compost",
        "common_issues": "Yellow leaves (overwatering or nutrient deficiency), bud drop (stress or inconsistent watering), aphids and whiteflies",
        "care_tips": "Thrives in heat and moisture. Mulch heavily to retain soil moisture. Cut back to ground in late fall — new growth emerges in late spring. Be patient, as it's one of the last perennials to emerge.",
        "fertilizer_type": "High-potassium fertilizer (10-4-12 or bloom booster)",
        "fertilizer_schedule": "Every 2 weeks during growing season (late spring through early fall)",
        "fertilizer_notes": "Heavy feeder that needs consistent nutrition for large blooms. Potassium promotes flowering. Slow-release granules in spring plus liquid feedings work well. Stop after first frost.",
    },
    {
        "name": "Canna Lily",
        "watering_interval_days": 2,
        "sunlight": "Full direct sunlight (6+ hours)",
        "soil_type": "Rich, moist, well-draining soil with organic matter",
        "common_issues": "Rust fungus (orange spots on leaves), caterpillars (leaf rollers), rhizome rot in waterlogged soil",
        "care_tips": "Heavy feeders — fertilize monthly during growing season. Cut spent flower stalks to encourage more blooms. Dig up rhizomes before frost in cold climates and store over winter.",
        "fertilizer_type": "High-phosphorus fertilizer (5-10-5) or bloom booster",
        "fertilizer_schedule": "Monthly during growing season (spring through fall)",
        "fertilizer_notes": "Heavy feeder that rewards generous fertilizing. Use slow-release granules at planting, then liquid monthly. Phosphorus encourages blooms.",
    },
    {
        "name": "Rubber Plant",
        "watering_interval_days": 10,
        "sunlight": "Medium to bright indirect light",
        "soil_type": "Well-draining general potting mix with perlite",
        "common_issues": "Dropping leaves (overwatering or cold drafts), leggy growth (low light), dust buildup on leaves",
        "care_tips": "Wipe large leaves with a damp cloth monthly. Prune to desired shape — will branch from cut points. Likes to dry out between waterings.",
        "fertilizer_type": "Balanced liquid fertilizer (10-10-10 or 20-20-20)",
        "fertilizer_schedule": "Every 2-4 weeks during spring and summer",
        "fertilizer_notes": "Moderate feeder. Dilute to half strength. Yellow lower leaves can indicate need for fertilizer. Stop in winter.",
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
    "Perennial Hibiscus": [
        ("Yellow leaves", "Check for overwatering or iron deficiency. Amend soil with iron sulfate if pH is too high"),
        ("Bud drop before opening", "Keep watering consistent — stress from drought or overwatering causes buds to abort. Avoid moving the plant"),
        ("Aphids/whiteflies on new growth", "Spray with insecticidal soap or neem oil. Blast with water hose to dislodge. Treat weekly until clear"),
        ("No new growth in spring", "Be patient — perennial hibiscus emerges very late (May-June). Don't dig up assuming it's dead"),
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
            existing.fertilizer_type = data.get("fertilizer_type", "")
            existing.fertilizer_schedule = data.get("fertilizer_schedule", "")
            existing.fertilizer_notes = data.get("fertilizer_notes", "")
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
