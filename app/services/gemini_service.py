import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="hackathon-470421", location="us-east1")
model = GenerativeModel("gemini-2.5-flash")

def generate_answer(ocr_text, labels, user_context):
    prompt = f"""
You are a financial assistant.

Here is some OCR text from a user-uploaded image:
"{ocr_text}"

These are the detected image labels:
{labels}

This is the user's financial context:
- Name: {user_context.get("name")}
- Age: {user_context.get("age")}
- Salary: {user_context.get("salary")}
- Budget: {user_context.get("budget")}
- Debt: {user_context.get("debt")}
- Goals: {user_context.get("goals")}
- Expenses: {user_context.get("expenses", "Not specified")}

Using all this, answer the user's question or provide insight.
"""
    response = model.generate_content(prompt)
    return response.text