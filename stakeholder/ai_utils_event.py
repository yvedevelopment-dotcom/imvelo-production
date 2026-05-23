from openai import OpenAI
from django.conf import settings

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_event_ai_insights(event_summary: str) -> str:
    """
    Analyze a full planting event report and generate AI-driven insights
    for each tree monitored within the event, including overall event health.
    """

    system_prompt = (
        "You are Tree Analyzer AI, an expert in reforestation project analysis, "
        "tree survival assessment, and ecological restoration management. "
        "You will be given detailed planting event data containing multiple trees, "
        "monitoring summaries, and environmental details. "
        "Your goal is to provide a concise yet professional AI report with per-tree insights "
        "and an overall planting event evaluation."
    )

    user_prompt = f"""
{event_summary}

Generate a concise and professional AI analysis with the following structure:

1. 🌳 **Per-Tree Insights**
   - For each monitored tree, summarize:
     • Tree Name and Species  
     • Growth Stage or Health Trend  
     • Survival Rate or Change Since Last Monitoring  
     • Key Threats or Environmental Stress  
     • Immediate Actions Recommended (watering, pest control, pruning, etc.)

2. 🌍 **Event-Level Summary**
   - Summarize the collective performance of all trees (average survival rate, dominant threats, general condition)
   - Comment on soil health, rainfall, or other environmental observations (if present)
   - Identify at-risk areas or plots
   - Provide an overall conservation or management recommendation for the next season
5. 📐 Advice Relevant to the Plot Size (hectares), such as planting density, management load, and resource planning

4. ✅ **Final Recommendations**
   - Bullet actionable advice for event organizers to improve success rates next time
   - Include specific operational or environmental follow-ups

Make sure the tone is professional, data-informed, and clear.
Do NOT use markdown formatting; return as plain text paragraphs and bullet points only.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating AI event insights: {e}"
