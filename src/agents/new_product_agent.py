import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools
from agno.tools.yfinance import YFinanceTools
from agno.team import Team

# Handle both direct execution and module import
try:
    from .tools.Deepsearch import Deepsearch
except ImportError:
    # If running directly, add the current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    from tools.Deepsearch import Deepsearch

# Load .env file environment variables
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please ensure it is available.")
if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY environment variable not set. Please ensure it is available.")

# Create Deepsearch tool
class DeepsearchTool:
    def __init__(self):
        self.searcher = Deepsearch()
    
    def search_market_trends(self, query: str) -> str:
        """Search for market trends and industry information using Perplexity API."""
        result = self.searcher.search(query)
        if result["success"]:
            return result["content"]
        else:
            return f"Search failed: {result['error']}"

# Initialize shared components
deepsearch_tool = DeepsearchTool()

# Deepsearch Agent - Deep Market Research Specialist
deepsearch_agent = Agent(
    name="Deep Market Research Specialist",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=openai_api_key,
    ),
    tools=[],  # We'll add the deepsearch functionality via functions
    description="""You are a deep market research specialist with access to advanced AI-powered 
    search capabilities through Perplexity API. You conduct comprehensive market intelligence 
    gathering and provide detailed, structured market analysis for product development decisions.""",
    instructions=[
        "You are responsible for extracting business context from user queries and conducting comprehensive deep market research",
        "When a user describes their business and product idea in natural language, extract the key information:",
        "- Business type/context (e.g., 'coffee shop', 'bakery', 'restaurant')",
        "- Product idea they want to develop (e.g., 'vegan protein brownie', 'functional smoothie')",
        "- Location/target market (e.g., 'Dublin', 'New York', or assume 'globally' if not specified)",
        "",
        "Then use this extracted information to perform comprehensive market research using advanced AI search",
        "Structure your research using the comprehensive product development template",
        "Focus on providing detailed, actionable market intelligence that other team members can build upon",
        "",
        "Always provide detailed, data-driven insights with specific examples and recent market developments",
        "Structure your findings in a clear, comprehensive format that supports the full product development process",
    ],
    markdown=True,
    show_tool_calls=True,
)

# Update the deepsearch agent to handle natural language extraction
def extract_and_search(user_query: str) -> str:
    """Extract business context from user query and perform comprehensive market research."""
    
    # The deepsearch agent will extract the business info, product idea, and location from the user query
    # and then format it into the structured research template
    extraction_prompt = f"""
    Please extract the following information from this user query: "{user_query}"
    
    Extract:
    - Business type/context (e.g., "coffee shop", "bakery", "restaurant")
    - Product idea (e.g., "vegan protein brownie", "functional smoothie")
    - Location/market (e.g., "Dublin", "New York", or "globally" if not specified)
    
    Then perform comprehensive market research using this structured template:
    
    # Product Development and Marketing Plan Request

    Based on the user query, I understand they are the owner of a **[extracted business type]** in **[extracted location]** and want to develop a new **[extracted product idea]**. 

    Please provide a detailed product development and marketing plan, including:

    ## Product Research
    - Current trends relevant to this product (in the specified location and globally)
    - Background on how these trends influence the product concept
    - Steps to develop the product (from idea to launch)
    - Competitive landscape analysis - who are the key players and what are they offering
    - Market size and growth projections for this product category
    - Consumer demographics and target audience insights
    - Regulatory considerations and food safety requirements

    ## Marketing Research
    - Suggestions for sourcing suppliers
    - A detailed costing spreadsheet (ingredients, packaging, labor, etc.) for small, medium, and large-scale production
    - Pricing analysis, including competitor pricing
    - A marketing plan and examples of marketing content
    - Distribution channels and retail partnerships
    - Seasonal trends and demand patterns

    ## Costing Spreadsheet Format Example

    | Component           | Supplier        | Package Size | Unit Cost      | Cost per unit |
    |---------------------|-----------------|--------------|----------------|---------------|
    | Ingredient 1        | Supplier A      | 1kg          | €X.XX/kg       | €X.XX         |
    | Ingredient 2        | Supplier B      | 500g         | €X.XX/kg       | €X.XX         |
    | ...                 | ...             | ...          | ...            | ...           |
    | Packaging           | Supplier C      | Per unit     | €X.XX          | €X.XX         |
    | Labor               | Local rate      | €X.XX/hour   | €X.XX/hour     | €X.XX         |
    | **Total Cost**      |                 |              |                | **€X.XX**     |
    | Suggested Retail    |                 |              |                | **€X.XX**     |
    | **Gross Margin**    |                 |              |                | **XX.X%**     |

    Please provide detailed, data-driven insights with specific examples and recent market developments for:
    
    1. **Product research** (trends, concept, development steps, competitive analysis)
    2. **Marketing research** (suppliers, costing spreadsheet for different scales, pricing/competitor analysis)
    3. **Marketing plan** with content ideas and distribution strategies
    4. **Financial analysis** including costing spreadsheet in the format above
    5. **Innovation opportunities** and white space in the market
    6. **Supply chain trends** and sourcing opportunities
    """
    
    return deepsearch_tool.search_market_trends(extraction_prompt)

# Update the deepsearch agent with the new function
deepsearch_agent.functions = [extract_and_search]

# Product Research Agent
product_research_agent = Agent(
    name="Product Research Specialist",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=openai_api_key,
    ),
    tools=[TavilyTools()],
    description="""You are a product research specialist with expertise in market analysis, 
    consumer trends, and product development. You analyze market opportunities and provide 
    data-driven insights for new product development.""",
    instructions=[
        "Research current market trends for the specified product category",
        "Analyze consumer behavior and preferences in the target market",
        "Identify market gaps and opportunities",
        "Provide competitive landscape analysis",
        "Suggest product features and positioning based on market research",
        "Use search tools to gather the latest market data and trends",
        "Present findings in a structured, actionable format",
    ],
    markdown=True,
    show_tool_calls=True,
)

# Marketing Strategy Agent
marketing_strategy_agent = Agent(
    name="Marketing Strategy Expert",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=openai_api_key,
    ),
    tools=[TavilyTools()],
    description="""You are a marketing strategy expert specializing in brand positioning, 
    customer acquisition, and marketing campaigns. You create comprehensive marketing 
    plans for new product launches.""",
    instructions=[
        "Develop comprehensive marketing strategies for new products",
        "Create customer personas and target audience profiles",
        "Design marketing campaigns across multiple channels",
        "Suggest marketing content ideas and messaging strategies",
        "Analyze competitor marketing approaches",
        "Recommend marketing budget allocation and timeline",
        "Focus on practical, implementable marketing tactics",
    ],
    markdown=True,
    show_tool_calls=True,
)

# Financial Analysis Agent
financial_analysis_agent = Agent(
    name="Financial Analysis Expert",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=openai_api_key,
    ),
    tools=[TavilyTools()],
    description="""You are a financial analysis expert specializing in cost analysis, 
    pricing strategies, and profitability assessment for new products. You create 
    detailed financial models and costing analyses.""",
    instructions=[
        "Create detailed cost analysis and pricing models",
        "Research supplier options and material costs",
        "Develop costing spreadsheets for different production scales",
        "Analyze competitor pricing and market positioning",
        "Calculate profit margins and break-even points",
        "Suggest pricing strategies and revenue projections",
        "Present financial data in clear tables and formats",
        "Include labor, packaging, ingredient, and overhead costs",
    ],
    markdown=True,
    show_tool_calls=True,
)

# Competitor Analysis Agent
competitor_analysis_agent = Agent(
    name="Competitor Analysis Specialist",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=openai_api_key,
    ),
    tools=[TavilyTools()],
    description="""You are a competitive intelligence specialist with expertise in 
    comprehensive competitor analysis, market positioning, and competitive strategy. 
    You provide detailed competitive landscape assessments and strategic recommendations.""",
    instructions=[
        "Conduct comprehensive competitor research and analysis",
        "Identify direct and indirect competitors in the market",
        "Analyze competitor products, pricing, and positioning strategies",
        "Evaluate competitor strengths, weaknesses, opportunities, and threats (SWOT)",
        "Research competitor marketing strategies and customer reviews",
        "Assess competitor market share and growth trajectories",
        "Identify competitive gaps and opportunities for differentiation",
        "Provide actionable competitive intelligence for strategic positioning",
        "Use structured frameworks for competitor comparison and analysis",
        "Present findings in clear, actionable formats with strategic recommendations",
    ],
    markdown=True,
    show_tool_calls=True,
)

# Team coordinator - Updated to handle natural language queries
new_product_development_team = Team(
    name="New Product Development Team",
    description="""A specialized AI team for comprehensive new product development and marketing planning. 
    We help business owners research, develop, and launch new products with detailed market research, 
    competitive analysis, marketing strategies, and financial projections.""",
    members=[
        deepsearch_agent,
        product_research_agent,
        marketing_strategy_agent, 
        financial_analysis_agent,
        competitor_analysis_agent,
    ],
    model=OpenAIChat(
        id="o3-mini",
        api_key=openai_api_key,
    ),
    instructions=[
        "Welcome! I understand you want to develop a new product for your business.",
        "Our team will provide comprehensive product development guidance through 5 specialized areas:",
        "",
        "🔍 **Deep Market Research Specialist**: Extract business context from your query and conduct comprehensive market research using advanced AI search",
        "📊 **Product Research Specialist**: Analyze market trends, consumer insights, and development strategies",
        "🏆 **Competitor Analysis Specialist**: Provide detailed competitive intelligence and positioning recommendations", 
        "📈 **Marketing Strategy Expert**: Develop complete marketing plans, campaigns, and customer acquisition strategies",
        "💰 **Financial Analysis Expert**: Create detailed cost analysis, pricing models, and financial projections with comprehensive costing spreadsheets",
        "",
        "**How to interact with us:**",
        "Simply describe your business and product idea naturally, for example:",
        "- 'I am a coffee shop owner in Dublin, I want to create a vegan protein brownie'",
        "- 'I run a bakery in New York and want to launch functional smoothies'",
        "- 'I own a restaurant and want to develop a new plant-based burger'",
        "",
        "Our team will automatically extract the relevant information and provide:",
        "✅ Comprehensive market research and trends analysis",
        "✅ Detailed competitive landscape assessment",
        "✅ Complete marketing strategy and campaign ideas",
        "✅ Financial analysis with detailed costing spreadsheets",
        "✅ Step-by-step product development roadmap",
        "",
        "Each specialist contributes their expertise while building upon the research foundation.",
        "We coordinate our findings to provide a complete, actionable product development plan.",
    ],
    show_tool_calls=True,
    markdown=True,
)

# Example usage function
def analyze_new_product(user_query: str) -> str:
    """
    Analyze a new product idea using natural language query.
    
    Args:
        user_query (str): Natural language description of business and product idea
                         Example: "I am a coffee shop owner in Dublin, I want to create a vegan protein brownie"
    
    Returns:
        str: Comprehensive analysis report
    """
    
    print("🔍 Analyzing new product with AI agent team...")
    
    # Use the team to analyze the product directly with natural language
    return new_product_development_team.print_response(user_query, stream=True)

# Example usage
if __name__ == "__main__":
    # Example 1: Natural language query
    print("=== Example 1: Natural Language Query ===")
    analyze_new_product("I am a coffee shop owner in Dublin, I want to create a vegan protein brownie")
    
    print("\n" + "="*80 + "\n")
    
    # Example 2: Another natural language query
    print("=== Example 2: Another Natural Language Query ===")
    analyze_new_product("I run a bakery in New York and want to launch functional smoothies")
    
    print("\n" + "="*80 + "\n")
    
