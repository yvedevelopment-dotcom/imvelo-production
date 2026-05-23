from openai import OpenAI
from geopy.geocoders import Nominatim
from django.conf import settings

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_region_from_coordinates(lat, lon):
    try:
        geolocator = Nominatim(user_agent="tree-ai-monitor")
        location = geolocator.reverse((lat, lon), language='en')
        return location.address if location else "Unknown region"
    except Exception:
        return "Unknown region"

def get_tree_ai_insights(tree_summary: str) -> str:
    system_prompt = (
            "You are Tree Analyzer AI... "
    "When previous analysis is provided, use it as a baseline: update findings, "
    "track trends, and ensure the report remains coherent over time."
        "You are Tree Analyzer AI, an expert in tree conservation, forestry health, and "
        "climate-adaptive land management. Use the planting region, environmental conditions, "
        "plot size (in hectares), and historical monitoring records to provide smart, scalable "
        "interventions and predictions."
    )

    user_prompt = f"""
{tree_summary}

Generate a detailed, size-aware professional tree monitoring report with the following insights (it should be relevant):
1. 🌱 Estimated Growth Stage or Expected Maturity Date
2. 📈 Current survival rate, Probability of Survival in the Next 12 Months
3. 🚨 Predict Interventions (e.g., watering, fertilizer, pest control) - adjusted to plot scale
4. ✅ Recommended Applicable Conservation Actions
5. ⚠️ Early Threat Detection Based on Past Records
6. 🌍 Regional Vulnerability Assessment (based on location)
7. 📐 Advice Relevant to the Plot Size (hectares), such as planting density, management load, and resource planning
8. next section on: a)Environmental Context, Soil Type & Health (if recorded), Nearby Tree Competition, Rainfall Patterns (if available from sensors or region), Climate Stress Notes (e.g., drought periods)
9. 🟩 Conclusion & Next Action Plan (make it very detailed):

"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error generating AI insights: {e}"
