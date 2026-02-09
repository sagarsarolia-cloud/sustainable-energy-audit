# Sustainable Energy Auditor: Towards Net Zero 🌍💡

## Inspiration 💡
The idea was born from a simple frustration: **Electricity bills are rising, and the planet is warming**, but most people don't know *where* to start saving. Professional energy audits are expensive, time-consuming, and intrusive. 

I asked myself: *Why can't I just take a picture of my room and have an AI tell me what's wrong?*
Inspired by climate tech and the rapid advancements in multimodal AI, I set out to build a tool that democratizes energy efficiency—making it accessible to anyone with a smartphone.

## What it does 🚀
**Sustainable Energy Auditor** is an intelligent web application that uses Computer Vision to analyze your living spaces. 
1.  **Upload:** You upload a photo of a room.
2.  **Analyze:** The AI (powered by Gemini/Azure OpenAI) scans for appliances, lighting types, and thermal leaks (like single-pane windows).
3.  **Calculate:** It deterministically calculates potential savings based on wattage deltas and local weather context (e.g., cooling loads in Jaipur).
4.  **Visualize:** It generates a thermal heatmap overlay to visually pinpoint "hot spots" of energy waste.

## How we built it 🛠️
The project is a full-stack application built with:
*   **Frontend:** React + Vite + TailwindCSS for a responsive, modern UI.
*   **Backend:** FastAPI (Python) for high-performance async processing.
*   **AI Engine:** We integrated **Azure OpenAI (GPT-4o)** and **Google Gemini Vision** for object detection and reasoning.
*   **Computer Vision:** **OpenCV** was used to generate the thermal heatmap overlays based on bounding box data.
*   **Weather API:** Integration with OpenWeatherMap to provide location-specific context for cooling/heating load calculations.

## Challenges we ran into 🚧
1.  **Hallucinations vs. Physics:** Initially, the LLM would "guess" savings numbers, which were inconsistent. To fix this, we implemented a **Deterministic Calculation Engine**. The AI now identifies the *device* (e.g., "60W Incandescent Bulb"), but we use Python to calculate the savings using physics-based formulas:
    $$ \text{Savings} = (\text{Watts}_{old} - \text{Watts}_{new}) \times \text{Hours} \times \frac{30}{1000} \times \text{Tariff} $$
    
2.  **Granular Detection:** The model initially grouped all lights into one box. We had to refine the prompting strategy to enforce "granular detection," ensuring every single downlight and table lamp was identified as a unique opportunity.

3.  **Aspect Ratio Hell:** Displaying the generated heatmap perfectly over the original image across different device sizes was a CSS challenge. We solved it by enforcing strict aspect-ratio containers and using `object-fit: contain` logic.

## Accomplishments that I'm proud of 🏆
*   **The Heatmap Visualization:** Seeing the red "thermal" zones overlay perfectly on the real image was a "magic moment."
*   **Real-World Accuracy:** The system correctly identified that a "Decorative Chandelier" creates a completely different energy footprint than a "LED Strip," something generic calculators miss.
*   **Speed:** Optimizing the backend to cache image hashes (SHA256), making repeated analyses instant.

## What I learned 📚
*   **Prompt Engineering is Engineering:** Getting structured JSON out of an LLM requires rigorous constraints and robust error handling.
*   **Hybrid AI Patterns:** The best results come from combining GenAI's reasoning with traditional code's deterministic math.
*   **CV Pipelines:** Learned how to manipulate image byte streams in Python for real-time processing without saving to disk unnecessarily.

## What's next for Sustainable Energy Auditor 🔮
*   **AR Integration:** A live mobile app mode where you just point your camera around the room.
*   **Marketplace:** One-click purchasing of the recommended LED bulbs or efficient fans directly from the dashboard.
*   **Solar Potential:** Estimating rooftop solar potential based on exterior photos.
