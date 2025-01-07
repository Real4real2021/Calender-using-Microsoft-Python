from flask import Flask, render_template, request, jsonify, session
from google.generativeai import GeminiLLM
from langchain_core.prompts import ChatPromptTemplate
import json

app = Flask(__name__)
app.secret_key = "no3250239u_093852ongw"

template = """
You are a helpful AI assistant, skilled at extracting specific information 
related to product management methodologies from user input.

Here is the conversation history: {context}

Question: {question}

Answer:
"""
#use a different model here, running ollama locally is becoming and issue. Preferably use a model that is hosted on the cloud
model = GeminiLLM("gemini-1.5-pro-exp-0827")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

context = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global context
    user_input = request.json['message']

    # --- Information Extraction ---
    extraction_prompt = f"""
    Carefully analyze the user's provided epic: "{user_input}"

    Based on the content and characteristics of the epic, extract the following information and determine the 3 most suitable product management methodologies. 

    **Information to Extract:**
    * **Complexity:** How complex is the epic "{user_input}"? (e.g., simple, moderate, highly complex)
    * **Uncertainty:** Is there a high degree of uncertainty regarding requirements or technology for the epic "{user_input}"? 
    * **Customer Collaboration:** Is frequent customer feedback and iteration crucial for the epic "{user_input}"?
    * **Time to Market:** Is there a strong emphasis on getting a minimum viable product (MVP) to market quickly for the epic "{user_input}"?
    * **Team Size and Structure:** Is the team working on the epic "{user_input}" large, distributed, or self-organizing?
    * **Project Timeline:** Is the project timeline for the epic "{user_input}" flexible or fixed?
    * **Focus on Quality:** Is there a strong emphasis on defect reduction and process improvement for the epic "{user_input}"?
    * **Focus on Efficiency:** Is there a strong need to eliminate waste and optimize workflows for the epic "{user_input}"?


    **Methodologies to Consider:**
    * **Total Quality Management (TQM):** Focuses on continuous improvement, customer satisfaction, and employee involvement to achieve high quality.
    * **Six Sigma:** A data-driven approach to reduce defects and variations in processes, aiming for near-perfection.
    * **Design Thinking:** Emphasizes user-centered design, prototyping, and testing to develop innovative solutions.
    * **Lean Product Development:** Applies lean principles to product development, focusing on reducing waste and delivering value quickly.
    * **Lean Startup:** Focuses on building and iterating on MVPs quickly, validating assumptions, and adapting to customer feedback.
    * **Kanban:** A visual workflow management system that emphasizes continuous flow and limiting work in progress.
    * **Scrum:** An iterative and incremental framework for managing complex projects, promoting collaboration and self-organization.

    **Return your analysis in a JSON format similar to this example (but tailor the content to the specific epic):**

    {{
        "epic_assessment": {{
            "complexity": "Assess the complexity of '{user_input}' (e.g., simple, moderate, highly complex)", 
            "uncertainty": "Assess the level of uncertainty in '{user_input}' (e.g., low, medium, high)",
            "customer_collaboration": "Determine if frequent customer feedback is crucial for '{user_input}' (e.g., yes, no, somewhat)",
            "time_to_market": "Determine the importance of a fast time-to-market for '{user_input}' (e.g., critical, important, not a priority)",
            "team_size_and_structure": "Describe the likely team size and structure for '{user_input}' (e.g., small, co-located, large, distributed)",
            "project_timeline": "Assess the flexibility of the project timeline for '{user_input}' (e.g., flexible, fixed)",
            "focus_on_quality": "Determine the importance of quality for '{user_input}' (e.g., high, medium, low)",
            "focus_on_efficiency": "Determine the importance of efficiency for '{user_input}' (e.g., high, medium, low)" 
        }},
        "recommended_methodologies": [
            {{
                "methodology": "Choose a methodology from the list above that best fits '{user_input}'", 
                "reasoning": "Explain why this methodology is a good fit for '{user_input}'" 
            }},
            {{
                "methodology": "Choose another suitable methodology",
                "reasoning": "Explain why this methodology is also a good fit"
            }},
            {{
                "methodology": "Choose a third suitable methodology",
                "reasoning": "Explain why this methodology is a good fit" 
            }}
        ] 
    }}
    """
    extraction_result_json = chain.invoke({"context": context, "question": extraction_prompt})

    try:
        extraction_result = json.loads(extraction_result_json) 
        # Access the extracted information (e.g., extraction_result["sprints"]["definition"])
    except json.JSONDecodeError as e:
        return jsonify({"error": "Could not extract information from input."})

    session["dashboard_params"]=extraction_result

    return jsonify({"message": extraction_result})

@app.route('/index')
def dashboard():
    dashboard_params = session.get("dashboard_params", {})
    return render_template('index.html', **dashboard_params)

    result = chain.invoke({"context": context, "question": user_input})
    context += f"\nUser: {user_input}\nAI: {result}"
    return jsonify({'response': result})
    
if __name__ == "__main__":
    app.run(debug=True)
