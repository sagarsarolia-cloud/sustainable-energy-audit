import os
import google.generativeai as genai
import json
from weather_service import get_current_weather

# Configure Gemini
# Configure Gemini
model = None

def init_gemini():
    global model
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment variables.")
        return False
    
    try:
        genai.configure(api_key=api_key)
        # Use 'gemini-1.5-pro' or 'gemini-1.5-flash'
        model = genai.GenerativeModel('gemini-3-pro-preview')
        print("Gemini initialized successfully.")
        return True
    except Exception as e:
        print(f"Failed to initialize Gemini: {e}")
        return False

async def analyze_image_with_gemini(image_bytes):
    """
    Analyzes the image using Gemini Vision capabilities.
    Returns a structured dictionary with detected appliances and issues.
    """
    global model
    if not model:
        # Try initializing if not ready (e.g. reload)
        if not init_gemini():
             return {
                "summary": "Gemini not configured. Check API Key.",
                "detections": [],
                "overall_score": 0,
                "estimated_monthly_savings_potential_kwh": 0
            }
    
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
                "box_2d": [ymin, xmin, ymax, xmax]  # scale 0-1000 or absolute
            }}
        ],
        "trees_planted_equivalent": 1.5
    }}
    DO NOT use markdown code blocks. Just return the JSON string.
    """
    
    try:
        from PIL import Image
        import io
        
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}
        
        response = model.generate_content([prompt, image_part])
        
        # Clean up response text if it contains markdown
        text = response.text.replace("```json", "").replace("```", "").strip()
        
        result = json.loads(text)
        
        # --- DETERMINISTIC CALCULATION ENGINE ---
        # Formula: (Delta_Watts * Hours * 30days / 1000) * Tariff
        TARIFF_INR = 10.0 
        
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
                if savings_inr < 10: savings_inr = 10 
                
                # Inject back into item
                item["savings_monthly_inr"] = savings_inr
                total_savings += savings_inr
            except:
                item["savings_monthly_inr"] = 0
                
        result["total_monthly_savings_inr"] = total_savings
        
        # Recalculate trees
        total_kwh_annual = (total_savings / TARIFF_INR) * 12
        co2_saved_kg = total_kwh_annual * 0.82
        result["trees_planted_equivalent"] = round(co2_saved_kg / 20, 1)

        return result
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        # Return fallback mock data if API fails (useful for dev without key)
        return {
            "summary": "Error calling Gemini (Check API Key). Returning mock data.",
            "detections": [
                {"label": "Mock Fridge", "box_2d": [100, 100, 600, 400], "efficiency": "Low", "watts": 200, "estimated_hours": 24, "recommendation": "Check API Key"}
            ],
            "overall_score": 0,
            "estimated_monthly_savings_potential_kwh": 0
        }
