import os
import time
import random
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tools import searchProducts, calculateTotal, checkCompatibility

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a Technical Sales Consultant in Malaysia.

When given a client brief, you must:
1. Identify all product categories needed
2. Search for each product category one by one using searchProducts
3. Pick the best option within the budget for each item
4. Check compatibility of all selected items together
5. Calculate the total cost including shipping and tax
6. Return a final structured quote

Always be systematic. Search each category separately.
Always check compatibility before finalizing.
Always calculate the total at the end."""

TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="searchProducts",
                description="Search online for products matching a requirement. Use this to find real products with prices and URLs.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "query": types.Schema(
                            type="STRING",
                            description="What product to search for"
                        ),
                        "budgetRM": types.Schema(
                            type="NUMBER",
                            description="Max budget in RM for this item"
                        ),
                    },
                    required=["query"]
                )
            ),
            types.FunctionDeclaration(
                name="calculateTotal",
                description="Calculate the total cost including shipping and tax for a list of items.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "items": types.Schema(
                            type="ARRAY",
                            description="List of items to calculate total for",
                            items=types.Schema(
                                type="OBJECT",
                                properties={
                                    "name": types.Schema(type="STRING"),
                                    "priceRM": types.Schema(type="NUMBER"),
                                    "url": types.Schema(type="STRING"),
                                },
                                required=["name", "priceRM"]
                            )
                        ),
                        "location": types.Schema(
                            type="STRING",
                            description="Delivery location in Malaysia e.g. Kuala Lumpur"
                        ),
                    },
                    required=["items"]
                )
            ),
            types.FunctionDeclaration(
                name="checkCompatibility",
                description="Verify that selected items are compatible with each other and the user's requirements.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "items": types.Schema(
                            type="ARRAY",
                            description="List of selected items to check",
                            items=types.Schema(
                                type="OBJECT",
                                properties={
                                    "name": types.Schema(type="STRING"),
                                    "specs": types.Schema(type="STRING"),
                                },
                                required=["name"]
                            )
                        ),
                        "requirements": types.Schema(
                            type="STRING",
                            description="The user's original requirements to check against"
                        ),
                    },
                    required=["items", "requirements"]
                )
            )
        ]
    )
]

def runTool(name: str, args: dict):
    """Route tool calls to the correct function."""
    toolMap = {
        "searchProducts": searchProducts,
        "calculateTotal": calculateTotal,
        "checkCompatibility": checkCompatibility,
    }
    tool = toolMap.get(name)
    if not tool:
        return f"Unknown tool: {name}"
    return tool(**args)

def callGeminiWithRetry(client, model, contents, config="", maxRetries=5):
    """Calls Gemini API with automatic retry on 503 errors or 429 errors."""
    for attempt in range(maxRetries):
        try:
            if config == "":
                return client.models.generate_content(
                    model=model,
                    contents=contents
                )
            else:
                return client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
            )

        except Exception as e:
            errorStr = str(e)
            isRateLimit = "503" in errorStr or "UNAVAILABLE" in errorStr or "429" in errorStr or "quota" in errorStr.lower()

            if isRateLimit and attempt < maxRetries - 1:
                waitTime = (2 ** attempt) + random.uniform(0, 1)
                print(
                    f"API busy (attempt {attempt + 1}/{maxRetries}). Retrying in {waitTime:.1f}s...")
                time.sleep(waitTime)
            else:
                raise

    raise Exception("Max retries exceeded. Gemini API is unavailable.")

def runAgent(brief: str) -> str:
    print(f"\n🤖 Agent starting...\nBrief: {brief}\n")

    # Build the initial conversation
    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=f"Client brief: {brief}")]
        )
    ]

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS,
        temperature=0.2
    )

    while True:
        time.sleep(1)

        response = callGeminiWithRetry(
            client=client,
            model="gemini-3.1-flash-lite",
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        contents.append(candidate.content)

        toolCalls = [
            part for part in candidate.content.parts
            if part.function_call is not None
        ]

        if toolCalls:
            toolResults = []
            for part in toolCalls:
                tool = part.function_call
                print(f"  🔧 Calling: {tool.name}({dict(tool.args)})")

                toolRunResult = runTool(tool.name, dict(tool.args))
                print(f"  ✅ Result preview: {str(toolRunResult)[:120]}...")

                toolResults.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=tool.name,
                            response={"result": str(toolRunResult)}
                        )
                    )
                )

            contents.append(
                types.Content(role="user", parts=toolResults)
            )

        else:
            finalText = ""
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    finalText += part.text

            return finalText


if __name__ == "__main__":
    brief = "I need a minimalist home office setup for a 10x10ft room in Kuala Lumpur, budget RM3,000"
    result = runAgent(brief)

    print("\n" + "=" * 60)
    print("📋 FINAL QUOTE:")
    print("=" * 60)
    print(result)