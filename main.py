from flask import Flask, render_template, request, jsonify, session
import os
import json
import openai 
from openai import OpenAI
import re 

app = Flask(__name__)
app.secret_key = "no3250239u_093852ongw"

template = """
You are a helpful AI assistant, skilled at providing business product insight based on user input.

Here is the conversation history: {context}

Question: {question}

Answer:
"""

client = OpenAI()
openai.api_key = os.environ.get('OPENAI_API_KEY')

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

    Provide actionable advice for improving business operations. Provide your analysis as a JSON object.  Do not include any markdown formatting.  The JSON should be valid and directly parseable by a JSON parser.  The structure should be:

    {
  "product_information": {
    "product_id": "string (unique identifier)",
    "product_name": "string",
    "product_category": "string",
    "product_description": "string (optional)",
    "launch_date": "string (YYYY-MM-DD)",
    "target_market": "string (description of the target audience)",
    "product_lifecycle_stage": "string (e.g., 'Introduction', 'Growth', 'Maturity', 'Decline')",
    "product_line": "string (if part of a larger product line, optional)"
  },
  "analysis_period": {
    "start_date": "string (YYYY-MM-DD)",
    "end_date": "string (YYYY-MM-DD)"
  },
  "analysis_summary": {
    "overall_health": "string (e.g., 'Excellent', 'Good', 'Fair', 'Poor', 'Critical')",
    "health_score": "number (optional, e.g., 0-100, derived from various metrics)",
    "key_findings": [
      {
        "finding": "string",
        "severity": "string (e.g., 'High', 'Medium', 'Low')",
        "supporting_data": [
          {
            "metric": "string",
            "value": "number or string",
            "trend": "string (e.g., 'Increasing', 'Decreasing', 'Stable')"
          }
        ]
      }
    ],
    "executive_summary": "string (a concise overview of the analysis for quick understanding)"
  },
  "cost_profit_analysis": {
    "costs": {
      "fixed_costs": {
        "total_fixed_costs": "number",
        "components": [
          {
            "name": "string (e.g., 'Rent', 'Salaries', 'Marketing')",
            "amount": "number"
          }
        ]
      },
      "variable_costs": {
        "total_variable_costs": "number",
        "components": [
          {
            "name": "string (e.g., 'Materials', 'Labor', 'Shipping')",
            "amount": "number",
            "per_unit": "boolean (true if this cost is expressed per unit)"
          }
        ]
      },
      "other_costs": [
        {
          "name": "string (e.g. 'Returns', 'Depreciation')",
          "amount": "number"
        }
      ]
    },
    "total_cost_per_unit": "number",
    "variable_cost_per_unit": "number",
    "pricing": {
      "selling_price_per_unit": "number",
      "discount_percentage": "number (if applicable)",
      "average_selling_price_per_unit": "number (after discounts)"
    },
    "profit_per_unit": "number",
    "contribution_margin": "number",
    "contribution_margin_ratio": "number (percentage)",
    "cost_breakdown_analysis": {
      "material_cost_percentage": "number",
      "labor_cost_percentage": "number",
      "overhead_cost_percentage": "number",
      "other_cost_percentage": "number"
    },
    "recommendations": {
      "area": "string (e.g., 'Cost Reduction', 'Pricing Optimization')",
      "advice": "string",
      "impact": "string (e.g., 'Increase profit margin by X%')",
      "priority": "string (e.g., 'High', 'Medium', 'Low')",
      "feasibility": "string (e.g., 'Easy', 'Medium', 'Difficult')",
      "implementation_timeline": "string (e.g., 'Short-term', 'Mid-term', 'Long-term')"
    }
  },
  "revenue_break_even_analysis": {
    "total_revenue": "number",
    "total_units_sold": "number",
    "total_profit": "number",
    "profit_margin": "number (percentage)",
    "break_even_point_units": "number",
    "break_even_point_revenue": "number",
    "margin_of_safety": {
      "units": "number (units sold above break-even)",
      "revenue": "number (revenue above break-even)",
      "percentage": "number"
    },
    "sensitivity_analysis": {
      "scenarios": [
        {
          "scenario_name": "string (e.g., '10% Price Increase', '5% Cost Decrease')",
          "changes": [
            {
              "variable": "string (e.g., 'Selling Price', 'Variable Cost', 'Fixed Cost')",
              "percentage_change": "number"
            }
          ],
          "new_break_even_point_units": "number",
          "new_break_even_point_revenue": "number",
          "new_profit_margin": "number"
        }
      ]
    },
    "recommendations": {
      "area": "string (e.g., 'Revenue Growth', 'Break-Even Optimization')",
      "advice": "string",
      "impact": "string (e.g., 'Reduce break-even point by Y units')",
      "priority": "string (e.g., 'High', 'Medium', 'Low')",
      "feasibility": "string (e.g., 'Easy', 'Medium', 'Difficult')",
      "implementation_timeline": "string (e.g., 'Short-term', 'Mid-term', 'Long-term')"
    }
  },
  "market_analysis": {
    "market_size": "number (total market value or units)",
    "market_growth_rate": "number (percentage)",
    "market_share": "number (percentage of the market held by the product)",
    "market_trends": [
      {
        "trend": "string",
        "impact_on_product": "string (e.g., 'Positive', 'Negative', 'Neutral')",
        "opportunity_or_threat": "string (e.g., 'Opportunity', 'Threat')"
      }
    ],
    "competitor_analysis": {
      "competitor_name": "string",
      "market_share": "number (percentage)",
      "strengths": [
        "list of strengths as strings"
      ],
      "weaknesses": [
        "list of weaknesses as strings"
      ],
      "product_comparison": {
        "features": [
          {
            "feature_name": "string",
            "our_product": "string (description or rating)",
            "competitor_product": "string (description or rating)"
          }
        ],
        "pricing": {
          "our_price": "number",
          "competitor_price": "number"
        },
        "differentiation": "string (how our product differentiates itself)"
      },
      "customer_segmentation": [
        {
          "segment_name": "string",
          "segment_size": "number or percentage",
          "segment_needs": [
            "list of needs as strings"
          ],
          "segment_profitability": "number",
          "segment_growth_potential": "number"
        }
      ],
      "swot_analysis": {
        "strengths": [
          "list of internal strengths as strings"
        ],
        "weaknesses": [
          "list of internal weaknesses as strings"
        ],
        "opportunities": [
          "list of external opportunities as strings"
        ],
        "threats": [
          "list of external threats as strings"
        ]
      }
    }
  },
  "customer_analysis": {
    "customer_satisfaction": {
      "csat_score": "number (e.g., out of 5 or 10)",
      "nps_score": "number (Net Promoter Score)",
      "customer_feedback": [
        {
  
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
