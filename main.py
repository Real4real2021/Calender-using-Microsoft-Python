from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
import json
import openai 
from openai import OpenAI
import re 
import traceback


app = Flask(__name__)
app.secret_key = "no3250239u_093852ongw"

template = """
Conduct a comprehensive analysis of the speadsheet data the user has provided, focusing on production planning, supply chain management, resource management, market analysis, financial performance, risk management, compliance and regulations, and sustainability within the context of manufacturing:

     **Key Requirements:**

    * **Accuracy:** Provide accurate and reliable data from reputable sources.
    * **Up-to-dateness:** Ensure that all information is current and reflects the latest market conditions.
    * **Objectivity:** Present unbiased and objective analysis.
    * **Clarity:** Communicate complex information in a clear and concise manner.
    * **Data Visualization:** Utilize charts, graphs, and other visual aids to present data effectively.
    * **Source Citation:** When providing data, cite the source of the information.
    * **Data driven:** All conclusions must be supported by data.
    * **No Hallucinations:** When unsure of an answer, state that you do not know, and do not invent information.

    **When presented with a specific query, please follow these steps:**

    1.  **Clarify:** Ask clarifying questions to ensure you understand the specific requirements of the request.
    2.  **Gather:** Collect relevant data from reliable sources.
    3.  **Analyze:** Analyze the data and identify key insights.
    4.  **Summarize:** Summarize the findings in a clear and concise report.
    5.  **Present:** Present the information in a user-friendly format, including charts and graphs where appropriate.
    6.  **Cite:** Cite all sources of information.

    By adhering to these guidelines, you will provide valuable market intelligence that supports informed decision-making.

     User Input: "{user_input}"

    Provide actionable advice for improving manufacturing business operations. Provide your analysis as a JSON object. Do not include any markdown formatting. The JSON should be valid and directly parseable by a JSON parser. The structure should be:

Here is the conversation history: {context}

Question: {question}

Answer:
"""

client = OpenAI()
openai.api_key = os.environ.get('OPENAI_API_KEY')

#Configure SQL Alchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
@app.route('/')
def home():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = username
        return redirect(url_for('industry'))
    else:
      return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("index.html", error="Username already exists")
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect(url_for('industry'))
    
@app.route('/dashboard')
def dashboard():
    if "username" in session:
        return render_template('dashboard.html')
    return redirect(url_for('home'))

@app.route('/industry')
def industry():
     return render_template('industry.html')

@app.route('/agriculture')
def agriculture():
    return render_template('agriculture.html')

@app.route('/education')
def education():
    return render_template('education.html')

@app.route('/finance')
def finance():
    return render_template('finance.html')

@app.route('/healthcare')
def healthcare():
    return render_template('manufacturing.html')

@app.route('/manufacturing')
def manufacturing():
    return render_template('manufacturing.html')

@app.route('/retail')
def retail():
    return render_template('retail.html')

@app.route('/mining_energy')
def mining_energy():
    return render_template('mining_energy.html')

@app.route('/technology')
def technology():
    return render_template('technology.html')

@app.route('/transportation')
def transportation():
    return render_template('transportation.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/chat', methods=['POST'])
def chat():
    global context
    user_input = request.json['message']

    # --- Information Extraction ---
    extraction_prompt = """
    Conduct a business analysis on the spreasheet data the user has provided, focusing on cost and profit, revenue, break-even analysis, and the interconnectedness of these metrics:

     **Key Requirements:**

    * **Accuracy:** Provide accurate and reliable data from reputable sources.
    * **Up-to-dateness:** Ensure that all information is current and reflects the latest market conditions.
    * **Objectivity:** Present unbiased and objective analysis.
    * **Clarity:** Communicate complex information in a clear and concise manner.
    * **Data Visualization:** Utilize charts, graphs, and other visual aids to present data effectively.
    * **Source Citation:** When providing data, cite the source of the information.
    * **Data driven:** All conclusions must be supported by data.
    * **No Hallucinations:** When unsure of an answer, state that you do not know, and do not invent information.

    **When presented with a specific query, please follow these steps:**

    1.  **Clarify:** Ask clarifying questions to ensure you understand the specific requirements of the request.
    2.  **Gather:** Collect relevant data from reliable sources.
    3.  **Analyze:** Analyze the data and identify key insights.
    4.  **Summarize:** Summarize the findings in a clear and concise report.
    5.  **Present:** Present the information in a user-friendly format, including charts and graphs where appropriate.
    6.  **Cite:** Cite all sources of information.

    By adhering to these guidelines, you will provide valuable market intelligence that supports informed decision-making.
    
    User Input: "{user_input}"

    Provide actionable advice for improving business operations. Provide your analysis as a JSON object.  Do not include any markdown formatting.  The JSON should be valid and directly parseable by a JSON parser.  The structure should be:

    
      {{
        "product_information": {{
          "product_id": "string (unique identifier)",
          "product_name": "string",
          "product_category": "string",
          "product_description": "string (optional)",
          "launch_date": "string (YYYY-MM-DD)",
          "target_market": "string (description of the target audience)",
          "product_lifecycle_stage": "string (e.g., 'Introduction', 'Growth', 'Maturity', 'Decline')",
          "product_line": "string (if part of a larger product line, optional)",
          "swot_analysis": {{
              "strengths": [
                "list of product internal strengths as strings"
              ],
              "weaknesses": [
                "list of product internal weaknesses as strings"
              ],
              "opportunities": [
                "list of product external opportunities as strings"
              ],
              "threats": [
                "list of product external threats as strings"
              ]
        }},
        "analysis_period": {{
          "start_date": "string (YYYY-MM-DD)",
          "end_date": "string (YYYY-MM-DD)"
        }},
        "analysis_summary": {{
          "overall_health": "string (e.g., 'Excellent', 'Good', 'Fair', 'Poor', 'Critical')",
          "health_score": "number (optional, e.g., 0-100, derived from various metrics)",
          "key_findings": [
            {{
              "finding": "string",
              "severity": "string (e.g., 'High', 'Medium', 'Low')",
              "supporting_data": [
                {{
                  "metric": "string",
                  "value": "number or string",
                  "trend": "string (e.g., 'Increasing', 'Decreasing', 'Stable')"
                }}
              ]
            }}
          ],
          "executive_summary": "string (a concise overview of the analysis for quick understanding)"
        }},
        "cost_profit_analysis": {{
          "costs": {{
            "fixed_costs": {{
              "total_fixed_costs": "number",
              "components": [
                {{
                  "name": "string (e.g., 'Rent', 'Salaries', 'Marketing')",
                  "amount": "number"
                }}
              ]
            }},
            "variable_costs": {{
              "total_variable_costs": "number",
              "components": [
                {{
                  "name": "string (e.g., 'Materials', 'Labor', 'Shipping')",
                  "amount": "number",
                  "per_unit": "boolean (true if this cost is expressed per unit)"
                }}
              ]
            }},
            "other_costs": [
              {{
                "name": "string (e.g. 'Returns', 'Depreciation')",
                "amount": "number"
              }}
            ]
          }},
          "total_cost_per_unit": "number",
          "variable_cost_per_unit": "number",
          "pricing": {{
            "selling_price_per_unit": "number",
            "discount_percentage": "number (if applicable)",
            "average_selling_price_per_unit": "number (after discounts)"
          }},
          "profit_per_unit": "number",
          "contribution_margin": "number",
          "contribution_margin_ratio": "number (percentage)",
          "cost_breakdown_analysis": {{
            "material_cost_percentage": "number",
            "labor_cost_percentage": "number",
            "overhead_cost_percentage": "number",
            "other_cost_percentage": "number"
          }},
          "recommendations": {{
            "area": "string (e.g., 'Cost Reduction', 'Pricing Optimization')",
            "advice": "string" (A detailed, well thought out, specific, actionable, and achievable recommendation for improving the cost structure of the product),
            "impact": "string (e.g., 'Increase profit margin by X%')",
            "priority": "string (e.g., 'High', 'Medium', 'Low')",
            "feasibility": "string (e.g., 'Easy', 'Medium', 'Difficult')",
            "implementation_timeline": "string (e.g., 'Short-term', 'Mid-term', 'Long-term')"
          }},
          {{
            "area": "string (e.g., 'Cost Reduction', 'Pricing Optimization')",
            "advice": "string" (A detailed, well thought out, specific, actionable, and achievable recommendation for improving the cost structure of the product),
            "impact": "string (e.g., 'Increase profit margin by X%')",
            "priority": "string (e.g., 'High', 'Medium', 'Low')",
            "feasibility": "string (e.g., 'Easy', 'Medium', 'Difficult')",
            "implementation_timeline": "string (e.g., 'Short-term', 'Mid-term', 'Long-term')"
          }},
          {{
            "area": "string (e.g., 'Cost Reduction', 'Pricing Optimization')",
            "advice": "string" (A detailed, well thought out, specific, actionable, and achievable recommendation for improving the cost structure of the product),
            "impact": "string (e.g., 'Increase profit margin by X%')",
            "priority": "string (e.g., 'High', 'Medium', 'Low')",
            "feasibility": "string (e.g., 'Easy', 'Medium', 'Difficult')",
            "implementation_timeline": "string (e.g., 'Short-term', 'Mid-term', 'Long-term')"
          }}
        }},
        "revenue_break_even_analysis": {{
          "total_revenue": "number",
          "total_units_sold": "number",
          "total_profit": "number",
          "profit_margin": "number (percentage)",
          "break_even_point_units": "number",
          "break_even_point_revenue": "number",
          "margin_of_safety": {{
            "units": "number (units sold above break-even)",
            "revenue": "number (revenue above break-even)",
            "percentage": "number"
          }},
          "sensitivity_analysis": {{
            "scenarios": [
              {{
                "scenario_name": "string (e.g., '10% Price Increase', '5% Cost Decrease')",
                "changes": [
                  {{
                    "variable": "string (e.g., 'Selling Price', 'Variable Cost', 'Fixed Cost')",
                    "percentage_change": "number"
                  }}
                ],
                "new_break_even_point_units": "number",
                "new_break_even_point_revenue": "number",
                "new_profit_margin": "number"
              }}
            ]
          }},
          "recommendations": {{
            "area": "string (e.g., 'Revenue Growth', 'Break-Even Optimization')",
            "advice": "string"(A detailed, well thought out, specific, actionable, and achievable recommendation for improving the revenue structure of the product),
            "impact": "string (e.g., 'Reduce break-even point by Y units')",
            "priority": "string (e.g., 'High', 'Medium', 'Low')",
            "feasibility": "string (e.g., 'Easy', 'Medium', 'Difficult')",
            "implementation_timeline": "string (e.g., 'Short-term', 'Mid-term', 'Long-term')"
          }},
          {{
            "area": "string (e.g., 'Revenue Growth', 'Break-Even Optimization')",
            "advice": "string"(A detailed, well thought out, specific, actionable, and achievable recommendation for improving the revenue structure of the product),
            "impact": "string (e.g., 'Reduce break-even point by Y units')",
            "priority": "string (e.g., 'High', 'Medium', 'Low')",
            "feasibility": "string (e.g., 'Easy', 'Medium', 'Difficult')",
            "implementation_timeline": "string (e.g., 'Short-term', 'Mid-term', 'Long-term')"
          }},
          {{
            "area": "string (e.g., 'Revenue Growth', 'Break-Even Optimization')",
            "advice": "string"(A detailed, well thought out, specific, actionable, and achievable recommendation for improving the revenue structure of the product),
            "impact": "string (e.g., 'Reduce break-even point by Y units')",
            "priority": "string (e.g., 'High', 'Medium', 'Low')",
            "feasibility": "string (e.g., 'Easy', 'Medium', 'Difficult')",
            "implementation_timeline": "string (e.g., 'Short-term', 'Mid-term', 'Long-term')"
          }},
          
        }},
        "market_analysis": {{
          "market_size": "number (total market value or units)",
          "market_growth_rate": "number (percentage)",
          "market_share": "number (percentage of the market held by the product)",
          "market_trends": [
            {{
              "trend": "string",
              "impact_on_product": "string (e.g., 'Positive', 'Negative', 'Neutral')",
              "opportunity_or_threat": "string (e.g., 'Opportunity', 'Threat')"
            }},
            {{
              "trend": "string",
              "impact_on_product": "string (e.g., 'Positive', 'Negative', 'Neutral')",
              "opportunity_or_threat": "string (e.g., 'Opportunity', 'Threat')"
            }},
            {{
              "trend": "string",
              "impact_on_product": "string (e.g., 'Positive', 'Negative', 'Neutral')",
              "opportunity_or_threat": "string (e.g., 'Opportunity', 'Threat')"
            }},
            {{
              "trend": "string",
              "impact_on_product": "string (e.g., 'Positive', 'Negative', 'Neutral')",
              "opportunity_or_threat": "string (e.g., 'Opportunity', 'Threat')"
            }}
          ],
          "market_segments": 
            {{
              "segment_A(Name of segment)": "number (total market value or units)",
              "segment_B(Name of segment)": "number (total market value or units)",
              "segment_C(Name of segment)": "number (total market value or units)",
              "segment_D(Name of segment)": "number (total market value or units)",
              "segment_E(Name of segment)": "number (total market value or units)",
              "segment_F(Name of segment)": "number (total market value or units)",
              "segment_G(Name of segment)": "number (total market value or units)",
            }},
            "historical_growth": {{
              "2019": "number (percentage)",
              "2020": "number (percentage)",
              "2021": "number (percentage)",
              "2022": "number (percentage)",
              "2023": "number (percentage)",
              "2024": "number (percentage)",
              "2025 5000000": "number (percentage)",
            }},
          "competitor_analysis": {{
            "competitor_name": "string",
            "market_share": "number (percentage)",
            "strengths": [
              "list of strengths as strings"
            ],
            "weaknesses": [
              "list of weaknesses as strings"
            ],
            "product_comparison": {{
              "features": [
                {{
                  "feature_name": "string",
                  "our_product": "string (description or rating)",
                  "competitor_product": "string (description or rating)"
                }}
              ],
              "pricing": {{
                "our_price": "number",
                "competitor_price": "number"
              }},
              "differentiation": "string (how our product differentiates itself)"
            }},
            "customer_segmentation": [
              {{
                "segment_name": "string",
                "segment_size": "number or percentage",
                "segment_needs": [
                  "list of needs as strings"
                ],
                "segment_profitability": "number",
                "segment_growth_potential": "number"
              }}
            ],
            "swot_analysis": {{
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
            }}
          }}
        }},
        "customer_analysis": {{
          "customer_satisfaction": {{
            "csat_score": "number (e.g., out of 5 or 10)",
            "nps_score": "number (Net Promoter Score)",
            "customer_feedback": [
              {{
                "feedback_type": "string (e.g., 'Review', 'Survey', 'Support Ticket')",
                "sentiment": "string (e.g., 'Positive', 'Negative', 'Neutral')",
                "summary": "string",
                "date": "string (YYYY-MM-DD)"
              }}
            ]
          }},
          "customer_acquisition_cost": "number (CAC)",
          "customer_lifetime_value": "number (CLTV)",
          "churn_rate": "number (percentage of customers lost)",
          "customer_retention_rate": "number (percentage of customers retained)",
          "customer_engagement": {{
            "active_users": "number",
            "usage_frequency": "string (e.g., 'Daily', 'Weekly', 'Monthly')",
            "average_session_duration": "number (e.g., in minutes)",
            "key_features_used": [
              {{
                "feature_name": "string",
                "usage_rate": "number (percentage)"
              }}
            ]
            }},
          "customer_demographics": {{
            "age_distribution": [
              {{
                "age_range": "string",
                "percentage": "number"
              }}
            ],
            "gender_distribution": [
              {{
                "gender": "string",
                "percentage": "number"
              }}
            ],
            "location_distribution": [
              {{
                "location": "string (e.g., city, region, country)",
                "percentage": "number"
              }}
            ],
            "other_demographics": [
              {{
                "characteristic": "string",
                "value": "string or number"
              }}
            ]
          }}
        }},
        "sales_performance": {{
          "total_sales_revenue": "number",
          "sales_growth_rate": "number (percentage)",
          "sales_by_channel": [
            {{
              "channel_name": "string (e.g., 'Online', 'Retail', 'Distributors')",
              "revenue": "number",
              "percentage_of_total_sales": "number"
            }}
          ],
          "sales_by_region": [
            {{
              "region_name": "string",
              "revenue": "number",
              "percentage_of_total_sales": "number"
            }}
          ],
          "average_order_value": "number (AOV)",
          "sales_conversion_rate": "number (percentage of leads converted to sales)",
          "sales_cycle_length": "number (average time to close a sale)",
          "top_performing_products": [
            {{
              "product_name": "string",
              "revenue": "number",
              "units_sold": "number"
            }}
          ],
          "sales_forecast": {{
            "methodology": "string (e.g., 'Linear Regression', 'Moving Average')",
            "forecast_period": {{
              "start_date": "string (YYYY-MM-DD)",
              "end_date": "string (YYYY-MM-DD)"
            }},
            "projected_revenue": "number",
            "projected_units_sold": "number",
            "confidence_level": "number (percentage)"
          }}
        }},
        "marketing_performance": {{
          "marketing_roi": "number (Return on Investment)",
          "total_marketing_spend": "number",
          "marketing_spend_by_channel": [
            {{
              "channel_name": "string (e.g., 'Social Media', 'PPC', 'Email')",
              "spend": "number",
              "impressions": "number",
              "clicks": "number",
              "conversions": "number",
              "cpa": "number (Cost Per Acquisition)"
            }}
          ],
          "website_analytics": {{
            "website_traffic": "number (unique visitors)",
            "bounce_rate": "number (percentage)",
            "average_time_on_page": "number (in minutes)",
            "conversion_rate": "number (percentage of visitors who complete a desired action)",
            "top_performing_pages": [
              {{
                "page_url": "string",
                "visits": "number",
                "conversion_rate": "number"
              }}
            ]
          }},
          "social_media_engagement": {{
            "total_followers": "number",
            "engagement_rate": "number (percentage)",
            "reach": "number",
            "top_performing_posts": [
              {{
                "post_id": "string",
                "engagement": "number",
                "reach": "number"
              }}
            ]
          }},
          "email_marketing_performance": {{
            "open_rate": "number (percentage)",
            "click_through_rate": "number (percentage)",
            "conversion_rate": "number (percentage)",
            "unsubscribe_rate": "number (percentage)"
          }},
          "lead_generation": {{
            "total_leads": "number",
            "lead_sources": [
              {{
                "source_name": "string",
                "leads_generated": "number"
              }}
            ],
            "lead_conversion_rate": "number (percentage)",
            "cost_per_lead": "number"
          }}
        }},
        "product_development": {{
          "new_features_released": "number",
          "development_costs": "number",
          "time_to_market": "number (average time for new features/products)",
          "innovation_rate": "string (e.g., 'High', 'Medium', 'Low')",
          "product_roadmap": {{
            "upcoming_features": [
              {{
                "feature_name": "string",
                "description": "string",
                "expected_release_date": "string (YYYY-MM-DD)",
                "development_status": "string (e.g., 'In Progress', 'Planned', 'Delayed')",
                "business_impact": "string"
              }}
            ],
            "long_term_vision": "string"
          }}
        }},
        "operational_efficiency": {{
          "inventory_turnover_rate": "number",
          "order_fulfillment_time": "number (average time)",
          "return_rate": "number (percentage of products returned)",
          "defect_rate": "number (percentage of defective products)",
          "supply_chain_costs": "number",
          "production_capacity_utilization": "number (percentage)",
          "process_improvement_initiatives": [
            {{
              "initiative_name": "string",
              "description": "string",
              "status": "string (e.g., 'Completed', 'In Progress', 'Planned')",
              "impact": "string (e.g., 'Cost savings of X', 'Efficiency improvement of Y%')"
            }}
          ]
        }},
        "interconnectedness": {{
          "notes": "string summarizing the interconnectedness of the metrics",
          "dependency_mapping": [
            {{
              "metric_1": "string",
              "metric_2": "string",
              "relationship": "string (e.g., 'Positive Correlation', 'Negative Correlation', 'Causal')",
              "strength": "string (e.g., 'Strong', 'Moderate', 'Weak')"
            }}
          ],
          "scenario_planning": [
            {{
              "scenario_name": "string",
              "trigger_events": "string (e.g. 'Competitor releases a new product', 'Economic downturn')",
              "potential_impacts": "string",
              "contingency_plans": "string"
            }}
          ]
        }},
        "risk_assessment": {{
          "identified_risks": [
            {{
              "risk_name": "string",
              "severity": "string (e.g.,'Critical', 'High', 'Medium', 'Low')",
              "description": "string",
              "probability": "string (e.g., 'High', 'Medium', 'Low')",
              "impact": "string (e.g., 'High', 'Medium', 'Low')",
              "mitigation_strategy": "string",
              "risk_owner": "string (person or team responsible)"
            }}
          ],
          [
            {{
              "risk_name": "string",
              "severity": "string (e.g.,'Critical', 'High', 'Medium', 'Low')",
              "description": "string",
              "probability": "string (e.g., 'High', 'Medium', 'Low')",
              "impact": "string (e.g., 'High', 'Medium', 'Low')",
              "mitigation_strategy": "string",
              "risk_owner": "string (person or team responsible)"
            }}
          ],
          [
            {{
              "risk_name": "string",
              "severity": "string (e.g.,'Critical', 'High', 'Medium', 'Low')",
              "description": "string",
              "probability": "string (e.g., 'High', 'Medium', 'Low')",
              "impact": "string (e.g., 'High', 'Medium', 'Low')",
              "mitigation_strategy": "string",
              "risk_owner": "string (person or team responsible)"
            }}
          ],
          "risk_mitigation_effectiveness": {{
            "overall_effectiveness": "string (e.g., 'Effective', 'Partially Effective', 'Ineffective')",
            "mitigation_success_rate": "number (percentage)",
            "areas_for_improvement": [
              "list of areas as strings"
            ]
          }}
        }}
      }}
  
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": "You are a financial analyst.  Respond to the user's prompt by providing a detailed business analysis in the format of a JSON object.  Do not include any additional text or formatting.  The JSON must be valid."},
                {"role": "user", 
                 "content": extraction_prompt.format(user_input=user_input)
                 }
            ],
            temperature=0.7, 
            # max_tokens=1000      
        )

        if response.choices and response.choices[0].message:
          generated_text = response.choices[0].message.content

          generated_text = generated_text.replace('\n', '') # Remove newlines
          generated_text = generated_text.strip('`').strip() 
          generated_text = generated_text.replace('```json','').strip()
          generated_text = re.sub(r"^\s*|\s*$", "", generated_text) 
          generated_text = re.sub(r"[^\x20-\x7E]+", "", generated_text)
          generated_text = generated_text.replace('\\"', '"') # replace escaped quotes with quotes
          generated_text = re.sub(r"(?<!\\)\\(?![\"'])", "", generated_text)
          generated_text = re.sub(r'^[^\{]*', '', generated_text)
          generated_text = re.sub(r'[^}]*$', '', generated_text)
        else:
          raise ValueError("Unexpected response format from OpenAI API.")

        try:
            print(repr(response.choices[0].message.content))
            extraction_result = json.loads(generated_text)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON returned from OpenAI: {e}, Raw response: {generated_text}"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {e}"})

    session["dashboard_params"] = extraction_result
    return jsonify({"message": extraction_result})

@app.route('/agricultureChat', methods=['POST'])
def agriChat():
    global context
    user_input = request.json['message']

    # --- Information Extraction ---
    extraction_prompt = """

   You are a financial analyst with expertise in the agricultural industry. You will receive data from a user-provided spreadsheet. 

  User Input: "{user_input}"

  Perform a detailed analysis of the agricultural data in the spreadsheet, focusing on the following sections using data from the User Input:

  1. Financial Performance:
    - Calculate total revenue, profit margin, and return on investment.
    - Identify the most profitable revenue streams based on the spreadsheets.
    - Provide actionable recommendations to optimize the financial performance of the business, ensuring all recommendations are specific, achievable, and data-driven.

  2. Resource Management:
    - Summarize all data associated with water usage, fertilizer consumption, and feed consumption.
    - Provide strategies for improved resource efficiency, highlighting where these can be implemented, the positive impacts that will follow, the difficulty to implement, and the timeframe.

  3. Risk Management:
    - Analyze identified weather risks and supply chain risks.
    - Present mitigation strategies for each risk, ensuring all strategies are specific and achievable

  Structure your response as a valid JSON object with the following format:

  `{{
        "agricultural_analysis": {{
            "product_information": {{
                "farm_id": "string (unique identifier, e.g., farm_id-crop_type-year)",
                "farm_name": "string (e.g., 'Organic Corn', 'Angus Beef')",
                "farm_category": "string (e.g., 'Crops', 'Livestock')",
                "farm_description": "string (optional, e.g., 'Description of farming practices')",
                "planting_date": "string (YYYY-MM-DD, for crops)",
                "birth_date": "string (YYYY-MM-DD, for livestock)",
                "harvest_date": "string (YYYY-MM-DD, for crops)",
                "slaughter_date": "string (YYYY-MM-DD, for livestock)",
                "target_market": "string (description of the target audience, e.g., 'Local consumers', 'Export market')",
                "agricultural_cycle_stage": "string (e.g., 'Planting', 'Growth', 'Harvest', 'Breeding', 'Fattening')",
                "geographic_location": "string (e.g., 'Latitude, Longitude' or 'Region')",
                "farm_size": "number (in acres or hectares)",
                "farm_establishment_date": "string (YYYY-MM-DD)",
                "soil_type": "string",
                "climate_zone": "string",
                "irrigation_source": "string"
            }},
            "swot_analysis": {{
                "strengths": ["list of strengths as strings"],
                "weaknesses": ["list of weaknesses as strings"],
                "opportunities": ["list of opportunities as strings"],
                "threats": ["list of threats as strings"]
            }},
            "analysis_period": {{
                "start_date": "string (YYYY-MM-DD)",
                "end_date": "string (YYYY-MM-DD)"
            }},
            "crop_management": {{
                "crop_type": "string",
                "planting_practices": "string (e.g., 'No-till', 'Conventional')",
                "irrigation_methods": "string (e.g., 'Drip', 'Sprinkler')",
                "fertilization_practices": "string (e.g., 'Organic', 'Synthetic', 'Variable Rate')",
                "pest_control_methods": "string (e.g., 'Integrated Pest Management', 'Chemical')",
                "pest_incidence": "number (e.g., 0-100)",
                "harvesting_methods": "string (e.g., 'Combine', 'Manual')",
                "yield_per_acre": "number (bushels/acre or tons/hectare)",
                "crop_health_index": "number (e.g., 0-10)",
                "soil_health_assessment": {{
                    "organic_matter_percentage": "number",
                    "nutrient_levels": "string (e.g., 'N: High, P: Medium, K: Low')",
                    "pH_level": "number",
                    "compaction_level": "string"
                    "moisture_level": "number (percentage)"
                }},
                "input_costs_per_acre": {{
                    "seed_cost": "number",
                    "fertilizer_cost": "number",
                    "pesticide_cost": "number",
                    "irrigation_cost": "number",
                    "labor_cost": "number"
                }},
                "crop_rotation_plan": "string",
                "precision_agriculture_usage": "string (e.g., 'GPS guidance', 'Variable rate application')",
                "recommendations": ["list of recommendations as strings"]
            }},
            "livestock_management": {{
                "livestock_breed": "string",
                "reproduction_rate": "number (e.g., '1-2 offspring per year')",
                "feed_costs': 'number (e.g., 'Feed per animal')",
                "feeding_practices": "string (e.g., 'Pasture-raised', 'Feedlot')",
                "breeding_practices": "string (e.g., 'Artificial insemination', 'Natural mating')",
                "animal_health_management": {{
                    "health_status": "string",
                    "vaccination_records": "string",
                    "disease_incidence_rate": "number (percentage)",
                    "parasite_control": "string"
                    "weight_gain": "number (kg/day)",
                }},
                "veterinary_care": {{
                    "frequency": "string",
                    "cost_per_animal": "number"
                }},
                "production_metrics": {{
                    "milk_yield_per_cow": "number (liters/day)",
                    "average_daily_gain": "number (kg/day)",
                    "feed_conversion_ratio": "number",
                    "mortality_rate": "number (percentage)"
                }},
                "animal_welfare_practices": "string (e.g., 'Space allowance', 'Handling procedures')",
                "pasture_management": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "resource_management": {{
                "land_use": {{
                    "crop_acreage": "number",
                    "pasture_acreage": "number",
                    "fallow_acreage": "number",
                    "grazing_land_utilization": "number (percentage of animals per hectare)"
                }},
                "water_usage": {{
                    "total_water_consumption": "number (liters/year)",
                    "water_source": "string",
                    "water_efficiency_metrics": "number (e.g., liters/kg of product)"
                }},
                "energy_consumption": {{
                    "fuel_consumption": "number (liters/year)",
                    "electricity_consumption": "number (kWh/year)",
                    "renewable_energy_usage": "string"
                }},
                "feed": {{
                  "total_feed_consumption": "number (liters/year)",
                  "feed_inventory": "string"(tons),
                  "feed_source": "string",
                  "feed_efficiency_metrics": "number (e.g., liters/kg of product)"
                }}
                "fertilizer_usage":{{
                  "total_fertilizer_consumption": "number (liters/year)",
                  "fertilizer_inventory": "string"(tons),
                  "fertilizer_source": "string",
                  "fertilizer_efficiency_metrics": "number (e.g., liters/kg of product)"
                }}
                "waste_management": {{
                    "manure_management": "string",
                    "crop_residue_management": "string",
                    "recycling_practices": "string",
                    "disposal_costs": "number (e.g., $100/ton)"
                }},
                "equipment_utilization": {{
                    "equipment_inventory": "string",
                    "equipment_maintenance_records": "string",
                    "equipment_utilization_rate": "number (percentage)"
                }},
                "input_sourcing": {{
                    "supplier_relationships": "string",
                    "input_traceability": "string",
                    "local_sourcing_percentage": "number"
                }},
                "resource_efficiency_metrics": {{
                    "resource_use_intensity": "number",
                    "input_output_ratio": "number"
                    "overall_rating": "number" (rating out of 5)
                }},
                "recommendations": ["list of recommendations as strings"],
                "total_resource_availability": "number (units)"
            }},
            "market_analysis": {{
                "market_size": "number (total market value or units)",
                "market_trends": ["list of market trends as strings"],
                "competitor_analysis": {{
                    "competitor_name": "string",
                    "market_share": "number (percentage)",
                    "strengths": ["list of strengths as strings"],
                    "weaknesses": ["list of weaknesses as strings"],
                    "pricing_strategy": "string"
                }},
                "customer_analysis": {{
                    "customer_segments": ["list of customer segments as strings"],
                    "pricing_strategies": "string",
                    "distribution_channels": "string",
                    "customer_feedback": "string"
                }},
                "market_price_volatility": "string",
                "forward_contracting": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "financial_performance": {{
                "production_costs": {{
                    "total_production_costs": "number",
                    "cost_breakdown": "string (e.g., 'Labor: 30%, Inputs: 40%, Overhead: 30%')"
                }},
                "operating_expenses": {{
                    "total_operating_expenses": "number",
                    "expense_breakdown": "string"
                }},
                "revenue": {{
                    "total_revenue": "number",
                    "revenue_streams": "string (e.g., 'Direct sales', 'Wholesale', 'Government subsidies')"
                }},
                "profit_margin": "number (percentage)",
                "return_on_investment": "number (percentage)",
                "cash_flow_analysis": {{
                    "cash_flow_statement": "string",
                    "working_capital": "number",
                    "debt_to_equity_ratio": "number"
                }},
                "break_even_point_units": "number",
                "financial_ratios": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "risk_management": {{
                "weather_risks": {{
                    "drought_risk": "string",
                    "flood_risk": "string",
                    "frost_risk": "string"
                }},
                "disease_risks": {{
                    "crop_disease_risk": "string",
                    "livestock_disease_risk": "string"
                }},
                "market_risks": {{
                    "price_volatility": "string",
                    "input_cost_fluctuations": "string"
                }},
                "regulatory_risks": {{
                    "environmental_compliance_risk": "string",
                    "food_safety_risk": "string",
                    "labor_law_risk": "string"
                }},
                "supply_chain_risks":{{
                    "transportation_and_logistics_risk": "string",
                    "distribution_channel_risk": "string",
                    "supplier_relationships_risk": "string",
                    "input_traceability_risk": "string",
                    "local_sourcing_risk": "string",
                    "supplier_security_risk": "string",
                    "supplier_quality_risk": "string",
                    "supplier_trust_risk": "string"
                }},
                "mitigation_strategies": ["list of mitigation strategies as strings"],
                "insurance_coverage": {{
                    "crop_insurance": "string",
                    "livestock_insurance": "string",
                    "liability_insurance": "string"
                }},
                "risk_assessment_matrix": "string (e.g., 'Risk: Severity, Probability, Impact')",
                "contingency_plans": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "compliance_and_regulations": {{
                "environmental_regulations": {{
                    "water_usage_permits": "string",
                    "emission_standards": "string",
                    "waste_disposal_compliance": "string"
                }},
                "food_safety_regulations": {{
                    "traceability_systems": "string",
                    "hygiene_standards": "string",
                    "product_labeling": "string"
                }},
                "labor_regulations": {{
                    "minimum_wage_compliance": "string",
                    "worker_safety_standards": "string",
                    "labor_contracts": "string"
                }},
                "certification_status": {{
                    "organic_certification": "string",
                    "GAP_certification": "string",
                    "animal_welfare_certification": "string"
                }},
                "compliance_audits": {{
                    "audit_frequency": "string",
                    "audit_findings": "string",
                    "corrective_actions": "string"
                }},
                "regulatory_changes_monitoring": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "sustainability": {{
                "environmental_impact": {{
                    "soil_carbon_sequestration": "number (tons/acre)",
                    "biodiversity_impact": "string",
                    "biodiversity_index": "number (e.g., 0-100)",
                    "water_footprint": "number (liters/kg)",
                    "greenhouse_gas_emissions": "number (tons CO2e)"
                }},
                "social_impact": {{
                    "community_engagement": "string",
                    "fair_labor_practices": "string",
                    "local_economic_contribution": "string"
                }},
                "economic_impact": {{
                    "long_term_viability": "string",
                    "resource_efficiency": "string",
                    "resilience_to_climate_change": "string"
                }},
                "sustainable_practices": {{
                    "cover_cropping": "string",
                    "rotational_grazing": "string",
                    "renewable_energy_usage": "string",
                    "reduced_tillage": "string"
                }},
                "carbon_footprint": {{
                    "scope_1_emissions": "number",
                    "scope_2_emissions": "number",
                    "scope_3_emissions": "number",
                    "carbon_offsetting_practices": "string"
                }},
                "sustainability_reporting": "string (e.g. 'GRI standards', 'Internal reporting')",
                "recommendations": ["list of recommendations as strings"]
            }},
            "overall_summary": {{
                "key_findings": ["list of key findings as strings"],
                "recommendations": ["list of overall recommendations as strings"],
                "performance_indicators": {{
                    "economic_indicators": ["list of economic performance indicators"],
                    "environmental_indicators": ["list of environmental performance indicators"],
                    "social_indicators": ["list of social performance indicators"]
                }},
                "strategic_recommendations": ["list of strategic recommendations"],
                "technology_integration_opportunities": ["list of technology integration opportunities"]
            }}
        }}
    }}`

  
    **Key Requirements:**

    * **Accuracy:** Provide accurate and reliable data from reputable sources.
    * **Up-to-dateness:** Ensure that all information is current and reflects the latest market conditions.
    * **Objectivity:** Present unbiased and objective analysis.
    * **Clarity:** Communicate complex information in a clear and concise manner.
    * **Data Visualization:** Utilize charts, graphs, and other visual aids to present data effectively.
    * **Source Citation:** When providing data, cite the source of the information.
    * **Data driven:** All conclusions must be supported by data.
    * **No Hallucinations:** When unsure of an answer, state that you do not know, and do not invent information.

    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": "You are a financial analyst.  Respond to the user's prompt by providing a detailed business analysis in the format of a JSON object.  Do not include any additional text or formatting.  The JSON must be valid."},
                {"role": "user", 
                 "content": extraction_prompt.format(user_input=user_input)
                }
            ],
            temperature=0.7, 
            # max_tokens=1000      
        )

        if response.choices and response.choices[0].message:
          generated_text = response.choices[0].message.content
          print(generated_text)

          generated_text = generated_text.replace('\n', '') # Remove newlines
          generated_text = generated_text.strip('`').strip() 
          generated_text = generated_text.replace('```json','').strip()
          generated_text = re.sub(r"^\s*|\s*$", "", generated_text) 
          generated_text = re.sub(r"[^\x20-\x7E]+", "", generated_text)
          generated_text = generated_text.replace('\\"', '"') # replace escaped quotes with quotes
          generated_text = re.sub(r"(?<!\\)\\(?![\"'])", "", generated_text)
          generated_text = re.sub(r'^[^\{]*', '', generated_text)
          generated_text = re.sub(r'[^}]*$', '', generated_text)
        else:
          raise ValueError("Unexpected response format from OpenAI API.")

        try:
            # print(repr(response.choices[0].message.content))
            extraction_result = json.loads(generated_text)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON returned from OpenAI: {e}, Raw response: {generated_text}"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {e}"})

    session["dashboard_params"] = extraction_result
    return jsonify({"message": extraction_result})

@app.route('/manufacturingChat', methods=['POST'])
def manufacturingChat():
    global context
    user_input = request.json['message']

        # --- Information Extraction ---
    extraction_prompt = """
    You are a financial analyst with expertise in the agricultural industry. You will receive data from a user-provided spreadsheet. 
  
    User Input: "{user_input}"
    
    Conduct a comprehensive analysis of the speadsheet data the user has provided, focusing on production planning, supply chain management, resource management, market analysis, financial performance, risk management, compliance and regulations, and sustainability within the context of manufacturing:

    **Key Requirements:**

    * **Accuracy:** Provide accurate and reliable data from reputable sources.
    * **Up-to-dateness:** Ensure that all information is current and reflects the latest market conditions.
    * **Objectivity:** Present unbiased and objective analysis.
    * **Clarity:** Communicate complex information in a clear and concise manner.
    * **Data Visualization:** Utilize charts, graphs, and other visual aids to present data effectively.
    * **Source Citation:** When providing data, cite the source of the information.
    * **Data driven:** All conclusions must be supported by data.
    * **No Hallucinations:** When unsure of an answer, state that you do not know, and do not invent information.

    Provide actionable advice for improving agricultural business operations. Provide your analysis as a JSON object. The structure should be:

    `{{
        "manufacturing_analysis": {{
            "product_information": {{
                "product_sku": "string (unique identifier, e.g., product_sku-product_type-year)",
                "factory_id": "string (unique identifier, e.g., factory_id-product_type-year)",
                "production_output": "number (total number of units produced)",
                "factory_name": "string (e.g., 'Acme Manufacturing', 'Global Tech')",
                "factory_category": "string (e.g., 'Automotive', 'Electronics', 'Food Processing')",
                "factory_description": "string (optional, e.g., 'Description of manufacturing processes')",
                "product_name": "string (e.g., 'Model X Car', 'XYZ Smartphone')",
                "product_quality_index": "number (e.g., '4.5' for 'Excellent')",
                "product_type": "string (e.g., 'Automobile', 'Electronics', 'Textiles')",
                "manufacturing_start_date": "string (YYYY-MM-DD)",
                "manufacturing_end_date": "string (YYYY-MM-DD)",
                "target_market": "string (description of the target audience, e.g., 'High-end consumers', 'Industrial clients')",
                "manufacturing_cycle_stage": "string (e.g., 'Design', 'Prototyping', 'Production', 'Distribution')",
                "geographic_location": "string (e.g., 'Latitude, Longitude' or 'Region')",
                "factory_size": "number (in square meters or acres)",
                "factory_establishment_date": "string (YYYY-MM-DD)",
                "production_line_setup": "string (e.g., 'Assembly line', 'Batch processing')",
                "automation_level": "string (e.g., 'Fully automated', 'Semi-automated', 'Manual')",
                "raw_material_sources": "string"
            }},
            "swot_analysis": {{
                "strengths": ["list of strengths as strings"],
                "weaknesses": ["list of weaknesses as strings"],
                "opportunities": ["list of opportunities as strings"],
                "threats": ["list of threats as strings"]
            }},
            "analysis_period": {{
                "start_date": "string (YYYY-MM-DD)",
                "end_date": "string (YYYY-MM-DD)"
            }},
            "production_planning": {{
                "production_capacity": "number (units per month or year)",
                "capacity_utilization_rate": "number (percentage)",
                "machine_utilization_rate": "number (percentage)",
                "inventory_levels": {{
                    "raw_materials": "number (units)",
                    "work_in_progress": "number (units)",
                    "finished_goods": "number (units)",
                    "turnover_rate": "number (percentage)"
                    "stockout_rate": "number (percentage)"
                    "parts_inventory": "number (units)"
                }},
                "demand_forecasting_accuracy": "number (percentage)",
                "production_scheduling_methods": "string (e.g., 'Just-in-Time', 'MRP')",
                "lead_time": "number (days)",
                "setup_time": "number (hours)",
                "machine_uptime": "number (percentage)",
                "downtime_causes": "string",
                "total_downtime": "number (hours)",
                "throughput": "number (units/hour)",
                "bottleneck_analysis": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "supply_chain_management": {{
                "supplier_network": "string",
                "supplier_performance": {{
                    "supplier_name": "string",
                    "on_time_delivery_rate": "number (percentage)",
                    "quality_rating": "number (e.g., 0-10)",
                    "pricing_competitiveness": "string"
                }},
                "logistics_and_transportation": {{
                    "transportation_modes": "string (e.g., 'Truck', 'Rail', 'Air')",
                    "carrying_costs": "number",
                    "transportation_costs": "number",
                    "delivery_time": "number (days)"
                }},
                "inventory_management_practices": "string (e.g., 'FIFO', 'LIFO')",
                "warehousing_practices": "string",
                "supply_chain_visibility": "string",
                "supply_chain_risk_assessment": "string",
                "supplier_relationships": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "resource_management": {{
                "raw_material_usage": {{
                    "total_consumption": "number (units)",
                    "material_sourcing": "string",
                    "material_waste": "number (percentage)",
                    "material_costs": "number",
                    "material_availability": "string"
                }},
                "energy_consumption": {{
                    "total_energy_consumption": "number (kWh/year)",
                    "energy_sources": "string",
                    "energy_efficiency_measures": "string",
                    "energy_costs": "number"
                }},
                "water_usage": {{
                    "total_water_consumption": "number (liters/year)",
                    "water_sources": "string",
                    "water_treatment_practices": "string",
                    "water_costs": "number"
                }},
                "waste_management": {{
                    "waste_generation": "number (tons/year)",
                    "waste_disposal_methods": "string",
                    "recycling_rate": "number (percentage)",
                    "waste_disposal_costs": "number"
                }},
                "equipment_maintenance": {{
                    "maintenance_schedule": "string",
                    "schedule_adherence": "number (percentage)",
                    "maintenance_costs": "number",
                    "equipment_failure_rate": "number (percentage)"
                    "downtime_due_to_maintenance": "number (hours)" 
                    "mean_time_to_repair" : "number (hours)"
                }},
                "labor_management": {{
                    "labor_costs": "number",
                    "labor_productivity": "number (units/hour)",
                    "employee_turnover_rate": "number (percentage)",
                    "employee_training": "string"
                }},
                "resource_efficiency_metrics": {{
                    "resource_use_intensity": "number",
                    "input_output_ratio": "number",
                    "overall_rating": "number"
                }},
                "recommendations": ["list of recommendations as strings"]
            }},
            "market_analysis": {{
                "market_size": "number (total market value or units)",
                "market_trends": ["list of market trends as strings"],
                "competitor_analysis": {{
                    "competitor_name": "string",
                    "market_share": "number (percentage)",
                    "strengths": ["list of strengths as strings"],
                    "weaknesses": ["list of weaknesses as strings"],
                    "pricing_strategy": "string"
                }},
                "customer_analysis": {{
                    "customer_segments": ["list of customer segments as strings"],
                    "pricing_strategies": "string",
                    "distribution_channels": "string",
                    "customer_feedback": "string"
                }},
                "market_price_volatility": "string",
                "demand_elasticity": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "financial_performance": {{
                "production_costs": {{
                    "total_production_costs": "number",
                    "cost_breakdown": "string (e.g., 'Labor: 30%, Materials: 40%, Overhead: 30%')"
                }},
                "operating_expenses": {{
                    "total_operating_expenses": "number",
                    "expense_breakdown": "string"
                }},
                "revenue": {{
                    "total_revenue": "number",
                    "revenue_streams": "string (e.g., 'Direct sales', 'Wholesale', 'Government contracts')"
                }},
                "profit_margin": "number (percentage)",
                "return_on_investment": "number (percentage)",
                "cash_flow_analysis": {{
                    "cash_flow_statement": "string",
                    "working_capital": "number",
                    "debt_to_equity_ratio": "number"
                }},
                "break_even_point_units": "number",
                "cost_of_goods_sold": "number",
                "marketing_spend": "number",
                "gross_profit": "number",
                "net_profit": "number",
                "return_on_assests": "number",
                "financial_ratios": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "risk_management": {{
                "operational_risks": {{
                    "equipment_failure_risk": "string",
                    "supply_chain_disruption_risk": "string",
                    "quality_control_risk": "string"
                }},
                "market_risks": {{
                    "demand_fluctuation_risk": "string",
                    "pricing_pressure_risk": "string",
                    "competition_risk": "string"
                }},
                "financial_risks": {{
                    "currency_exchange_rate_risk": "string",
                    "interest_rate_risk": "string",
                    "credit_risk": "string"
                }},
                "regulatory_risks": {{
                    "environmental_compliance_risk": "string",
                    "product_safety_risk": "string",
                    "labor_law_risk": "string"
                }},
                 "supply_chain_risks": {{
                    "transportation_and_logistics_risk": "string",
                    "distribution_channel_risk": "string",
                    "supplier_relationships_risk": "string",
                    "input_traceability_risk": "string",
                    "local_sourcing_risk": "string",
                    "supplier_security_risk": "string",
                    "supplier_quality_risk": "string",
                    "supplier_trust_risk": "string"
                }},
                "mitigation_strategies": ["list of mitigation strategies as strings"],
                "insurance_coverage": {{
                    "property_insurance": "string",
                    "liability_insurance": "string",
                    "business_interruption_insurance": "string"
                }},
                "risk_assessment_matrix": "string (e.g., 'Risk: Severity, Probability, Impact')",
                "contingency_plans": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "compliance_and_regulations": {{
                "environmental_regulations": {{
                    "emission_standards": "string",
                    "waste_disposal_compliance": "string",
                    "hazardous_materials_handling": "string"
                }},
                "product_safety_regulations": {{
                    "product_testing": "string",
                    "labeling_requirements": "string",
                    "recall_procedures": "string"
                }},
                "labor_regulations": {{
                    "minimum_wage_compliance": "string",
                    "worker_safety_standards": "string",
                    "labor_contracts": "string"
                }},
                "certification_status": {{
                    "ISO_certification": "string",
                    "quality_management_certification": "string",
                    "environmental_management_certification": "string"
                }},
                "compliance_audits": {{
                    "audit_frequency": "string",
                    "audit_findings": "string",
                    "corrective_actions": "string"
                }},
                "regulatory_changes_monitoring": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "sustainability": {{
                "environmental_impact": {{
                    "carbon_footprint": "number (tons CO2e)",
                    "water_footprint": "number (liters/unit)",
                    "waste_generation": "number (tons/year)",
                    "resource_depletion": "string"
                }},
                "social_impact": {{
                    "community_engagement": "string",
                    "fair_labor_practices": "string",
                    "employee_wellbeing": "string"
                }},
                "economic_impact": {{
                    "long_term_viability": "string",
                    "job_creation": "string",
                    "local_economic_contribution": "string"
                }},
                "sustainable_practices": {{
                    "energy_efficiency_improvements": "string",
                    "energy_consumption": "string",
                    "waste_reduction_strategies": "string",
                    "renewable_energy_usage": "string",
                    "sustainable_sourcing": "string"
                }},
                 "carbon_footprint": {{
                    "scope_1_emissions": "number",
                    "scope_2_emissions": "number",
                    "scope_3_emissions": "number",
                    "carbon_offsetting_practices": "string"
                }},
                "sustainability_reporting": "string (e.g. 'GRI standards', 'Internal reporting')",
                "recommendations": ["list of recommendations as strings"]
            }},
            "quality_control":{{
                "defect_rate": "number",
                "first_pass_yield": "number",
                "scrap_rate": "number",
                "rework_rate": "number",
                "customer_complaints": "string",
                "customer_returns": "number",
                "inspection_methods": "string",
                "cost_of_quality": "number",
                "quality_control_metrics": "number",
                "quality_assurance_programs": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "automation_and_technology":{{
                "automation_level": "string (e.g., 'Fully automated', 'Semi-automated', 'Manual')",
                "technology_used": "string",
                "integration_of_AI": "string",
                "machine_learning_applications": "string",
                "internet_of_things_applications": "string",
                "robotics": "string",
                "predictive_maintenance": "string",
                "recommendations": ["list of recommendations as strings"]
            }},
            "overall_summary": {{
                "key_findings": ["list of key findings as strings"],
                "recommendations": ["list of overall recommendations as strings"],
                "performance_indicators": {{
                    "economic_indicators": ["list of economic performance indicators"],
                    "environmental_indicators": ["list of environmental performance indicators",
                    "social_indicators": ["list of social performance indicators"
                }},
                "strategic_recommendations": ["list of strategic recommendations"],
                "technology_integration_opportunities": ["list of technology integration opportunities"]
            }}
        }}
    }}`

    """
  
    try:
        print("Extraction Prompt:\n", extraction_prompt)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": "You are a financial analyst.  Respond to the user's prompt by providing a detailed business analysis in the format of a JSON object.  Do not include any additional text or formatting.  The JSON must be valid."},
                {"role": "user", 
                 "content": extraction_prompt.format(user_input=user_input)
                }
            ],
            temperature=0.7, 
            # max_tokens=1000      
        )

        if response.choices and response.choices[0].message:
          generated_text = response.choices[0].message.content

          generated_text = generated_text.replace('\n', '') # Remove newlines
          generated_text = generated_text.strip('`').strip() 
          generated_text = generated_text.replace('```json','').strip()
          generated_text = re.sub(r"^\s*|\s*$", "", generated_text) 
          generated_text = re.sub(r"[^\x20-\x7E]+", "", generated_text)
          generated_text = generated_text.replace('\\"', '"') # replace escaped quotes with quotes
          generated_text = re.sub(r"(?<!\\)\\(?![\"'])", "", generated_text)
          generated_text = re.sub(r'^[^\{]*', '', generated_text)
          generated_text = re.sub(r'[^}]*$', '', generated_text)
        else:
          raise ValueError("Unexpected response format from OpenAI API.")

        try:
            # print(repr(response.choices[0].message.content))
            extraction_result = json.loads(generated_text)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON returned from OpenAI: {e}, Raw response: {generated_text}"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {e}"})

    session["dashboard_params"] = extraction_result
    return jsonify({"message": extraction_result})
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0',port=5000)
