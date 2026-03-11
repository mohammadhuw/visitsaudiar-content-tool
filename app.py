from flask import Flask, render_template, request, Response, stream_with_context
from openai import OpenAI
import json

app = Flask(__name__)
client = OpenAI()

SYSTEM_PROMPT = """You are a professional social media content writer for @visitsaudiar,
the official tourism account of Saudi Arabia on X (Twitter).

Your job is to write engaging, inspiring, and authentic content that showcases
Saudi Arabia's beauty, culture, heritage, and modern attractions.

Content guidelines:
- Write in an enthusiastic, welcoming, and inspiring tone
- Highlight Saudi Arabia's unique experiences: desert adventures, historical sites,
  coastal beauty, modern cities, culture, food, and hospitality
- Use relevant hashtags like #VisitSaudi #SaudiArabia #Saudi #ExploreKSA
- Each post should be under 280 characters (unless writing a thread)
- Make content shareable and visually descriptive
- Appeal to international and regional tourists
- Blend tradition with modernity in your messaging
- Use emojis appropriately to enhance engagement

When given a brief, generate the requested number of posts.
Format each post clearly numbered (1., 2., etc.) and ready to copy-paste.
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    brief = data.get("brief", "")
    num_posts = data.get("num_posts", 3)
    post_type = data.get("post_type", "single")

    user_message = f"""Brief: {brief}

Number of posts to generate: {num_posts}
Post type: {post_type}

Please generate {num_posts} {post_type} post(s) based on this brief for the @visitsaudiar X account."""

    def stream():
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2048,
            stream=True,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        for chunk in response:
            text = chunk.choices[0].delta.content
            if text:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(stream()), mimetype="text/event-stream")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)
