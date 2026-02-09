import os
import json
import base64
from openai import AzureOpenAI
from weather_service import get_current_weather

client = None

def init_azure():
    global client
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    
    if not api_key or not endpoint:
        print("Warning: AZURE_OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT not found.")
        return False
        
    try:
        client = AzureOpenAI(
            api_key=api_key,  
            api_version="2024-02-15-preview",
            azure_endpoint=endpoint
        )
        print("Azure OpenAI initialized successfully.")
        return True
    except Exception as e:
        print(f"Failed to initialize Azure OpenAI: {e}")
        return False

async def analyze_image_with_azure(image_bytes):
    global client
    if not client:
        if not init_azure():
            return {
                "summary": "Azure OpenAI not configured. Check API Key.",
                "detections": [],
                "overall_score": 0,
                "estimated_monthly_savings_potential_kwh": 0
            }

    deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    
    # Encode image to base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    weather_context = get_current_weather()

    prompt = f"""
    You are an expert energy auditor using computer vision. Analyze this image for energy efficiency.
    Context: Location is India (Jaipur). Current Weather: {weather_context}.
    
    GOAL: Identify EVERY energy-consuming device, lighting fixture, window, and thermal leak source.
    
    CRITICAL INSTRUCTION FOR BOUNDING BOXES:
    - Be extremely granular. Do NOT group multiple items into one box.
    - If there are two lamps, create TWO separate entries with separate bounding boxes.
    - If there is a side table lamp, detect it specifically.
    - Detect: ACs, Ceiling Fans, Lights (Table lamps, floor lamps, ceiling LEDs), Windows, Curtains, Appliances.
    
    For each item, infer the "Current Wattage" (based on typical old models) and "Efficient Wattage" (modern standard).
    Also estimate "Daily Usage Hours" based on the room type (e.g., Living room lights = 6h, AC = 8h).

    Return the result strictly as a JSON object with the following structure:
    {{
        "summary": "Impactful summary of findings...",
        "energy_score": 65,  # 0-100, where 100 is perfectly efficient
        "weather_context": "{weather_context}",
        "opportunities": [
            {{
                "title": "Inefficient Table Lamp Detected",
                "description": "Old incandescent bulb detected.",
                "fix_action": "Replace with 9W LED",
                "current_watts": 60,
                "efficient_watts": 9,
                "hours_per_day": 5,
                "box_2d": [ymin, xmin, ymax, xmax]
            }}
        ],
        "trees_planted_equivalent": 1.5
    }}
    DO NOT use markdown code blocks. Just return the JSON string.
    """

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                },
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_completion_tokens=2000
        )
        
        content = response.choices[0].message.content
        # Clean up code blocks
        content = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)
        
        # --- DETERMINISTIC CALCULATION ENGINE ---
        # Formula: (Delta_Watts * Hours * 30days / 1000) * Tariff
        TARIFF_INR = 10.0 # Average upper tier tariff
        
        total_savings = 0
        
        for item in result.get("opportunities", []):
            try:
                w_old = item.get("current_watts", 0)
                w_new = item.get("efficient_watts", 0)
                hours = item.get("hours_per_day", 0)
                
                # Calculate Monthly kWh Saved
                kwh_saved_monthly = (w_old - w_new) * hours * 30 / 1000
                
                # Calculate Savings in INR
                savings_inr = int(kwh_saved_monthly * TARIFF_INR)
                
                # Ensure non-negative
                if savings_inr < 10: savings_inr = 10 # Minimum nominal savings
                
                # Inject back into item
                item["savings_monthly_inr"] = savings_inr
                total_savings += savings_inr
            except:
                item["savings_monthly_inr"] = 0
                
        result["total_monthly_savings_inr"] = total_savings
        
        # Recalculate trees
        # 1 Tree ~ 20kg CO2/year. 1 kWh ~ 0.82 kg CO2.
        # Annual CO2 saved (kg) = (Total INR / Tariff) * 12 * 0.82
        # Trees = Annual CO2 / 20
        total_kwh_annual = (total_savings / TARIFF_INR) * 12
        co2_saved_kg = total_kwh_annual * 0.82
        result["trees_planted_equivalent"] = round(co2_saved_kg / 20, 1)

        return result

    except Exception as e:
        print(f"Azure OpenAI Error: {e}")
        return {
            "summary": f"Error calling Azure OpenAI: {str(e)}",
            "detections": [],
            "overall_score": 0,
            "estimated_monthly_savings_potential_kwh": 0
        }
