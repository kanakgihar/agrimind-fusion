"""Knowledge base for the 15 PlantVillage classes used by this project.

IMPORTANT: this is general crop-protection guidance written for students/farmers to START a conversation
with a local agricultural extension officer (e.g. KVK / state agriculture department). It contains NO pesticide
doses on purpose. Add citations in research/references.md before using it in the report.
"""

KNOWLEDGE_SOURCE = "General crop-protection guidance (not a validated expert system) - confirm with a local agricultural extension officer."

DISCLAIMER = (
    "AgriMind Fusion is a research/educational prototype. The image model only knows 15 PlantVillage classes "
    "(tomato, potato, bell pepper) and was trained on controlled-background photos, so accuracy on field photos "
    "can be much lower. Confidence is a softmax score, not a calibrated probability. Grad-CAM shows where the "
    "model looked, not the biological cause. Weather and satellite values are context and are never used to "
    "change the image prediction. Recommendations are general guidance, not a diagnosis or a guaranteed cure."
)

HEALTHY_NOTE = ("The model found no sign of the 15 trained conditions in this image. This does not rule out "
                "other diseases, pests or nutrient problems.")

KNOWLEDGE = {
    "Pepper__bell___Bacterial_spot": {
        "display_name": "Bell pepper - Bacterial spot", "crop": "Pepper", "category": "bacterial", "urgency": "moderate",
        "summary": "A bacterial leaf disease (Xanthomonas) that causes small water-soaked spots turning brown; it spreads by splashing water and contaminated seed or tools and is favoured by warm, wet weather.",
        "management": ["Remove and destroy badly affected leaves/plants; do not compost them.",
                       "Avoid working in the field when foliage is wet, so bacteria are not spread on hands and tools.",
                       "Ask your local extension office whether copper-based products are approved and suitable locally; they only give partial protection and must be used exactly as the label says."],
        "prevention": ["Use certified disease-free seed or transplants.", "Rotate with non-host crops for a few seasons.", "Use drip irrigation instead of overhead sprinklers; space plants for airflow."],
        "monitoring": ["Check new leaves every 2-3 days, especially after rain.", "Photograph affected plants with date and plot number to track spread."],
    },
    "Pepper__bell___healthy": {
        "display_name": "Bell pepper - Healthy", "crop": "Pepper", "category": "healthy", "urgency": "low",
        "summary": HEALTHY_NOTE,
        "management": ["No disease treatment is suggested by the model result."],
        "prevention": ["Keep good airflow, avoid wetting leaves late in the day, and keep tools clean."],
        "monitoring": ["Keep scouting weekly; re-scan if new spots or curling appear."],
    },
    "Potato___Early_blight": {
        "display_name": "Potato - Early blight", "crop": "Potato", "category": "fungal", "urgency": "moderate",
        "summary": "A fungal disease (Alternaria solani) with dark, ring-patterned spots usually on older leaves first; stressed plants and alternating wet/dry, warm periods favour it.",
        "management": ["Remove heavily infected lower leaves where practical.", "Keep plants well fed and watered to reduce stress.", "Ask your extension officer about locally recommended fungicides and timing; follow the label."],
        "prevention": ["Rotate away from potato/tomato for 2+ seasons.", "Remove crop debris after harvest.", "Use certified seed tubers and resistant/tolerant varieties where available."],
        "monitoring": ["Scout lower leaves weekly; note how fast lesions enlarge.", "Watch the weather: repeated leaf wetness raises the chance of spread."],
    },
    "Potato___healthy": {
        "display_name": "Potato - Healthy", "crop": "Potato", "category": "healthy", "urgency": "low",
        "summary": HEALTHY_NOTE,
        "management": ["No disease treatment is suggested by the model result."],
        "prevention": ["Use certified seed, rotate crops, and avoid long periods of leaf wetness."],
        "monitoring": ["Scout weekly, especially during cool humid weather when late blight can appear."],
    },
    "Potato___Late_blight": {
        "display_name": "Potato - Late blight", "crop": "Potato", "category": "oomycete", "urgency": "high",
        "summary": "Caused by Phytophthora infestans. It can spread very quickly in cool, humid or wet weather, damaging leaves, stems and tubers.",
        "management": ["Act quickly: contact a local extension officer the same day if possible.", "Remove and destroy infected plants and volunteer potatoes; do not leave cull piles near the field.", "Protective fungicide programmes are usually timed before/at first symptoms; ask for the locally approved option and follow the label."],
        "prevention": ["Plant certified disease-free seed tubers.", "Avoid overhead irrigation late in the day.", "Hill up soil well so tubers are covered."],
        "monitoring": ["Check neighbouring plants and fields daily while weather stays cool and humid.", "Inspect harvested tubers for rot before storage."],
    },
    "Tomato_Bacterial_spot": {
        "display_name": "Tomato - Bacterial spot", "crop": "Tomato", "category": "bacterial", "urgency": "moderate",
        "summary": "A bacterial disease (Xanthomonas spp.) producing small dark spots on leaves and fruit; spreads by water splash, tools and infected seed or transplants.",
        "management": ["Remove severely infected leaves/plants and keep them out of the compost.", "Do not handle plants when wet.", "Ask your extension office about approved copper-based or other options; they give limited protection."],
        "prevention": ["Buy certified seed/transplants.", "Rotate crops and clean tools.", "Use drip irrigation and stake plants for airflow."],
        "monitoring": ["Look for new spots after each rain or irrigation.", "Track what proportion of plants show symptoms each week."],
    },
    "Tomato_Early_blight": {
        "display_name": "Tomato - Early blight", "crop": "Tomato", "category": "fungal", "urgency": "moderate",
        "summary": "A fungal disease (Alternaria) with brown target-like rings on older leaves; it can also affect stems and fruit.",
        "management": ["Remove infected lower leaves and dispose of them away from the field.", "Mulch to reduce soil splash onto leaves.", "Ask your extension officer about locally approved fungicides; follow label directions."],
        "prevention": ["Rotate crops; stake and prune for airflow.", "Water at the base of plants.", "Maintain balanced fertilisation to avoid plant stress."],
        "monitoring": ["Scout lower canopy weekly.", "Record whether lesions are spreading upward."],
    },
    "Tomato_healthy": {
        "display_name": "Tomato - Healthy", "crop": "Tomato", "category": "healthy", "urgency": "low",
        "summary": HEALTHY_NOTE,
        "management": ["No disease treatment is suggested by the model result."],
        "prevention": ["Stake plants, water at the base, and clean tools between plants."],
        "monitoring": ["Scout weekly and re-scan if spots, curling or mottling appear."],
    },
    "Tomato_Late_blight": {
        "display_name": "Tomato - Late blight", "crop": "Tomato", "category": "oomycete", "urgency": "high",
        "summary": "Caused by Phytophthora infestans; spreads fast in cool, humid, wet conditions and can destroy plants in a short time.",
        "management": ["Contact a local extension officer promptly.", "Remove and destroy infected plants rather than composting them.", "Ask which protective fungicides are approved locally and how to time them; follow the label."],
        "prevention": ["Avoid overhead irrigation and long leaf wetness.", "Do not plant tomatoes next to infected potato fields.", "Use resistant varieties where available."],
        "monitoring": ["Inspect plants daily during cool humid spells.", "Check nearby potato and tomato plots."],
    },
    "Tomato_Leaf_Mold": {
        "display_name": "Tomato - Leaf mold", "crop": "Tomato", "category": "fungal", "urgency": "moderate",
        "summary": "A fungal disease (Passalora fulva) that shows yellow patches on the upper leaf surface and olive-grey mold underneath; it is favoured by high humidity, common in greenhouses and poorly ventilated plots.",
        "management": ["Improve ventilation and lower humidity (open vents, widen spacing).", "Remove badly affected leaves.", "Ask your extension officer about suitable fungicides if the problem continues."],
        "prevention": ["Avoid wetting leaves; water early in the day.", "Choose resistant varieties.", "Prune lower leaves for airflow."],
        "monitoring": ["Check leaf undersides weekly.", "Track humidity in greenhouses/tunnels."],
    },
    "Tomato_Septoria_leaf_spot": {
        "display_name": "Tomato - Septoria leaf spot", "crop": "Tomato", "category": "fungal", "urgency": "moderate",
        "summary": "A fungal disease (Septoria lycopersici) with many small round spots with grey centres and dark edges, usually starting on lower leaves; spreads by splashing water.",
        "management": ["Remove infected lower leaves.", "Mulch to limit soil splash.", "Ask your extension officer about locally approved fungicides; follow the label."],
        "prevention": ["Rotate crops for a few seasons.", "Water at the base and avoid working with wet foliage.", "Clean up plant debris after the season."],
        "monitoring": ["Scout lower leaves weekly, more often in wet weather."],
    },
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "display_name": "Tomato - Spider mites (two-spotted)", "crop": "Tomato", "category": "pest", "urgency": "moderate",
        "summary": "This is a pest (mite) problem, not a pathogen. Mites cause fine speckling, bronzing and sometimes webbing, and tend to build up in hot, dry, dusty conditions.",
        "management": ["Check leaf undersides with a hand lens to confirm mites.", "A strong spray of water or insecticidal soap on leaf undersides can reduce numbers; follow label instructions.", "Ask your extension officer about suitable miticides and avoid products that kill natural enemies."],
        "prevention": ["Avoid water stress and heavy dust on plants.", "Protect natural predators; remove heavily infested leaves."],
        "monitoring": ["Check undersides of leaves twice a week in hot dry weather."],
    },
    "Tomato__Target_Spot": {
        "display_name": "Tomato - Target spot", "crop": "Tomato", "category": "fungal", "urgency": "moderate",
        "summary": "A fungal disease (Corynespora cassiicola) causing brown spots with concentric rings on leaves, and sometimes stems and fruit; favoured by warm, humid conditions.",
        "management": ["Remove infected leaves and improve airflow.", "Ask your extension officer about suitable fungicides if spread continues; follow the label."],
        "prevention": ["Rotate crops, stake and prune plants, and water at the base."],
        "monitoring": ["Scout weekly and record if spots increase after humid periods."],
    },
    "Tomato__Tomato_mosaic_virus": {
        "display_name": "Tomato - Mosaic virus", "crop": "Tomato", "category": "viral", "urgency": "high",
        "summary": "A virus with mottled light/dark green leaves and distortion. It has no cure and spreads easily on hands, tools and plant sap, and can be carried on seed.",
        "management": ["Remove and destroy infected plants (do not compost).", "Wash hands with soap and disinfect tools after handling suspect plants.", "Handle healthy plants before suspect plants."],
        "prevention": ["Use certified seed and resistant varieties.", "Avoid handling plants after touching tobacco products.", "Clean stakes, trays and tools between seasons."],
        "monitoring": ["Look for mottling and leaf distortion on new growth and nearby plants."],
    },
    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "display_name": "Tomato - Yellow leaf curl virus", "crop": "Tomato", "category": "viral", "urgency": "high",
        "summary": "A virus spread by whiteflies. Typical signs are upward-curling, yellowing leaves and stunted growth. There is no cure once a plant is infected.",
        "management": ["Remove infected plants early to reduce the virus source.", "Control whiteflies; ask your extension officer about locally suitable methods.", "Use yellow sticky traps to monitor whitefly numbers."],
        "prevention": ["Use resistant varieties and insect-proof nets in nurseries.", "Keep weeds down around the plot.", "Inspect transplants before planting."],
        "monitoring": ["Check leaf undersides for whiteflies weekly.", "Check new growth for curling and yellowing."],
    },
}


def get_knowledge(class_name: str) -> dict | None:
    return KNOWLEDGE.get(class_name)


def display_name(class_name: str) -> str:
    k = KNOWLEDGE.get(class_name)
    return k["display_name"] if k else class_name.replace("_", " ").strip()
