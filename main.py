from flask import Flask, render_template, request, jsonify, session
import os
import json
import openai 
from openai import OpenAI
from dotenv import load_dotenv
import re 

app = Flask(__name__)
app.secret_key = "no3250239u_093852ongw"

template = """
You are a helpful AI assistant, skilled at providing business product insight based on user input.

Here is the conversation history: {context}

Question: {question}

Answer:
"""
# load_dotenv()
client = OpenAI()
# openai.api_key = os.environ.get('OPENAI_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global context
    user_input = request.json['message']

    # --- Information Extraction ---
    extraction_prompt = f"""
    Conduct a business analysis of the following user input, focusing on cost and profit, revenue, break-even analysis, and the interconnectedness of these metrics:
    
    User Input: "{user_input}"

    Provide actionable advice for improving business operations.Provide your analysis as a JSON object.  Do not include any markdown formatting.  The JSON should be valid and directly parseable by a JSON parser.  The structure should be:

    {{
      "analysis_summary": {{
        "overall_health": "string (e.g., 'Good', 'Fair', 'Poor')",
        "key_findings": ["list of key findings as strings"]
      }},
      "cost_profit_analysis": {{
        "total_cost_per_unit": number,
        "profit_per_unit": number,
        "variable_cost_per_unit": number,
        "contribution_margin": number,
        "recommendations": [{{"area": "string", "advice": "string", "impact": "string"}}]
      }},
      "revenue_break_even_analysis": {{
        "total_revenue": number,
        "total_profit": number,
        "profit_margin": number,
        "break_even_point_units": number,
        "fixed_costs": number,
        "recommendations": [{{"area": "string", "advice": "string", "impact": "string"}}]
      }},
      "interconnectedness": {{
        "notes": "string summarizing the interconnectedness of the metrics"
      }}
    }}
  
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": "You are a financial analyst.  Respond to the user's prompt by providing a detailed business analysis in the format of a JSON object.  Do not include any additional text or formatting.  The JSON must be valid."},
                {"role": "user", 
                 "content": extraction_prompt
                 }
            ],
            temperature=0.7, 
            max_tokens=500      
        )

        if response.choices and response.choices[0].message:
          generated_text = response.choices[0].message.content

          generated_text = generated_text.strip('`').strip() 
          generated_text = generated_text.replace('```json','').strip()
          generated_text = re.sub(r"^\s*|\s*$", "", generated_text) 
          generated_text = re.sub(r"[^\x20-\x7E]+", "", generated_text)
        else:
          raise ValueError("Unexpected response format from OpenAI API.")

        try:
            print(repr(response.choices[0].message.content))
            extraction_result = json.loads(generated_text)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON returned from OpenAI: {e}, Raw response: {generated_text}"})

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"})

    session["dashboard_params"] = extraction_result
    return jsonify({"message": extraction_result})

@app.route('/index')
def dashboard():
    dashboard_params = session.get("dashboard_params", {})
    return render_template('index.html', **dashboard_params)

    result = chain.invoke({"context": context, "question": user_input})
    context += f"\nUser: {user_input}\nAI: {result}"
    return jsonify({'response': result})
    
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5000)
