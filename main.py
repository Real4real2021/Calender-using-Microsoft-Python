from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
import json
import openai 
from openai import OpenAI
import re 
from authlib.integrations.flask_client import OAuth
from keys import *

app = Flask(__name__)
app.secret_key = os.environ.get('secret_key')

template = """
You are a helpful AI assistant, skilled at providing business product insight based on user input.

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

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_uri='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope':'openid profile email'}
)

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
        return redirect(url_for('dashboard'))
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
        return redirect(url_for('dashboard'))
    
@app.route('/dashboard')
def dashboard():
    if "username" in session:
        return render_template('dashboard.html')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/login/google')
def login_google():
    try:
        redirect_uri = url_for('authorize_google', _external=True)
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        app.logger.error(f"Error during login:{str(e)}")
        return "Error occured during login", 500
    
@app.route("/authorize/google")
def authorize_google():
    token = google.authorize_access_token()
    userinfo_endpoint = google.server_metadata['userinfo_endpoint']
    resp = google.get(userinfo_endpoint)
    user_info = resp.json()
    username = user_info['email']

    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()

    session['username'] = username
    session['oauth_token'] = token

    return redirect(url_for('dashboard'))

@app.route('/chat', methods=['POST'])
def chat():
    global context
    user_input = request.json['message']

    # --- Information Extraction ---
    extraction_prompt = """
    Conduct a business analysis of the following user input, focusing on cost and profit, revenue, break-even analysis, and the interconnectedness of these metrics:
    
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
          "product_line": "string (if part of a larger product line, optional)"
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
            "advice": "string",
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
            "advice": "string",
            "impact": "string (e.g., 'Reduce break-even point by Y units')",
            "priority": "string (e.g., 'High', 'Medium', 'Low')",
            "feasibility": "string (e.g., 'Easy', 'Medium', 'Difficult')",
            "implementation_timeline": "string (e.g., 'Short-term', 'Mid-term', 'Long-term')"
          }}
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
            }}
          ],
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
              "description": "string",
              "probability": "string (e.g., 'High', 'Medium', 'Low')",
              "impact": "string (e.g., 'High', 'Medium', 'Low')",
              "mitigation_strategy": "string",
              "risk_owner": "string (person or team responsible)"
            }}
          ],
          "risk_mitigation_effectiveness": {{
            "overall_effectiveness": "string (e.g., 'Effective', 'Partially Effective', 'Ineffective')",
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
                 "content": extraction_prompt
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
        return jsonify({"error": f"An error occurred: {e}"})

    session["dashboard_params"] = extraction_result
    return jsonify({"message": extraction_result})
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0',port=5000)
