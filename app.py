from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from sympy import preview
from io import BytesIO
import base64
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

SYSTEM_PROMPT = "You are a LaTeX generation model. The user will give you the name or description of a formula. If you know it you provide the LaTeX code that visualizes it. Nothing more. No text or explanation. Under no circumstances EVER provide anything but LaTeX code. No clarification. No context. Nothing. Make sure the formulas are properly enclosed using dollar signs."
# Prompt for story generation
SYSTEM_PROMPT_STORY = "You are a creative story generation model. The user will provide a story prompt, and you will generate a creative and engaging story based on that prompt."

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/latex", methods=["GET", "POST"])
def latex():
    latex_code = None
    latex_image = None

    if request.method == "POST":
        formula_description = request.form.get("formula_description")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": formula_description},
            ])
        latex_code = response.choices[0].message.content.strip()

        buffer = BytesIO()
        preview(latex_code, viewer="BytesIO", outputbuffer=buffer, euler=False, dvioptions=['-D', "300"])
        latex_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template("latex.html", latex_code=latex_code, latex_image=latex_image)

@app.route("/story_generator", methods=["GET", "POST"])
def story_gen():
    story_text = None

    if request.method == "POST":
        story_description = request.form.get("story_description")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_STORY},
                {"role": "user", "content": story_description},
            ])
        story_text = response.choices[0].message.content.strip()

    return render_template("story.html", story_text=story_text)

if __name__ == "__main__":
    app.run(debug=True)
