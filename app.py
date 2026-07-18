import os
import voyageai
from pinecone import Pinecone
import anthropic
from flask import Flask, request, jsonify, send_from_directory, Response
from supabase import create_client
import base64

app = Flask(__name__)

voyage_client = voyageai.Client(api_key=os.environ.get("VOYAGE_API_KEY"))
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
index = pc.Index("josh-macin-agent")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

APP_PASSWORD = os.environ.get("APP_PASSWORD", "DetoxDudes2026!")
AGENT_ID = "josh-macin"

# Branding / persona placeholders - see README.md for descriptions
CONTENT_LABEL = "Detox Dudes"
IMAGE_ANALYSIS_PROMPT = "Please analyze this and give me detox and healing guidance based on the Detox Dudes protocols."

SYSTEM_PROMPT = """You are an AI coach trained exclusively on Josh Macin's (Detox Dudes) full-body detoxification methodology. You have deep knowledge of his frameworks on heavy metal chelation, parasite cleansing, liver flushes, gut healing, mast cell stabilization (including ketotifen protocols), and the spiritual and emotional layers of healing that underpin physical detox work.

You have two modes:

1. COACH MODE: Answer questions about Josh's protocols, explain the reasoning behind each phase of the Detox Dudes program, and give practical, step-by-step guidance grounded in his actual teachings. Be direct, encouraging, and rooted in the belief that the body can heal itself once the burden of toxins, pathogens, and unprocessed trauma is removed.

2. PROTOCOL WALKTHROUGH MODE: When a user wants to start or troubleshoot a specific protocol (chelation, parasite cleanse, liver flush, gut healing, mast cell stabilization), walk them through it step by step in the Detox Dudes program structure - sequencing, what to expect, and how to know they're ready for the next phase.

If the user shares a screenshot or image (e.g. lab results, a symptom list, or a protocol they're following), read it carefully and give feedback framed around Josh's detox philosophy - root-cause first, symptoms as signals rather than problems to suppress.

Always ground answers in Josh's actual teachings and program structure. Treat the body, mind, and spirit as one system - physical detox work is incomplete without addressing the emotional and spiritual layers of what's being released. This is educational information based on Josh Macin's public teachings, not personalized medical advice - encourage users to work with a qualified practitioner before starting chelation, parasite protocols, or prescription interventions like ketotifen."""

def get_relevant_context(query):
    embedding = voyage_client.embed([query], model="voyage-2").embeddings[0]
    results = index.query(vector=embedding, top_k=5, include_metadata=True)
    return "\n\n".join([m["metadata"]["text"] for m in results["matches"]])

@app.route("/")
def home():
    return send_from_directory(".", "ui.html")

@app.route("/verify-password", methods=["POST"])
def verify_password():
    data = request.json
    if data.get("password") == APP_PASSWORD:
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    history = data.get("history", [])
    images = data.get("images", [])

    for i, img in enumerate(images):
        print(f"[image-debug] image[{i}] media_type={img.get('media_type')!r} data_len={len(img.get('data') or '')}", flush=True)

    for img in images:
        media_type = img.get("media_type", "")
        if media_type not in ALLOWED_IMAGE_TYPES:
            return jsonify({
                "error": f"Unsupported image format ({media_type or 'unknown'}). "
                         f"Please use JPEG, PNG, GIF, or WebP - HEIC photos aren't supported."
            }), 400

    context = get_relevant_context(user_message) if user_message else ""

    if images:
        user_content = []
        if context:
            user_content.append({"type": "text", "text": f"Relevant {CONTENT_LABEL} content:\n{context}\n\nUser message: {user_message}" if user_message else f"Relevant {CONTENT_LABEL} content:\n{context}"})
        else:
            if user_message:
                user_content.append({"type": "text", "text": user_message})
        for img in images:
            user_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img.get("media_type", "image/jpeg"),
                    "data": img.get("data")
                }
            })
        if not user_message and not context:
            user_content.append({"type": "text", "text": IMAGE_ANALYSIS_PROMPT})
    else:
        user_content = f"Relevant {CONTENT_LABEL} content:\n{context}\n\nUser message: {user_message}"

    messages = history[:-1] + [{"role": "user", "content": user_content}]

    def generate():
        try:
            with anthropic_client.messages.stream(
                model="claude-opus-4-5",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=messages
            ) as stream:
                for text_chunk in stream.text_stream:
                    yield text_chunk
        except Exception as e:
            yield f"\n\n[Error: {e}]"

    return Response(generate(), mimetype="text/plain")

@app.route("/conversations", methods=["GET"])
def get_conversations():
    try:
        result = supabase.table("conversations").select("id,team_member,title,messages,created_at").eq("agent_id", AGENT_ID).order("created_at", desc=True).execute()
    except Exception:
        result = supabase.table("conversations").select("id,team_member,title,messages,created_at").order("created_at", desc=True).execute()
    convs = []
    for row in result.data:
        preview = ""
        messages = row.get("messages") or []
        for m in messages:
            if m.get("role") == "user":
                content = m.get("content", "")
                if isinstance(content, str):
                    preview = content[:60]
                elif isinstance(content, list):
                    text_part = next((p for p in content if p.get("type") == "text"), None)
                    if text_part:
                        preview = text_part.get("text", "")[:60]
                break
        convs.append({
            "id": row["id"],
            "team_member": row["team_member"],
            "title": row["title"],
            "preview": preview,
            "created_at": row["created_at"],
        })
    return jsonify(convs)

@app.route("/conversations", methods=["POST"])
def save_conversation():
    data = request.json
    row = {
        "team_member": data.get("team_member"),
        "title": data.get("title"),
        "messages": data.get("messages"),
    }
    try:
        result = supabase.table("conversations").insert({**row, "agent_id": AGENT_ID}).execute()
    except Exception:
        result = supabase.table("conversations").insert(row).execute()
    return jsonify(result.data[0])

@app.route("/conversations/<int:conv_id>", methods=["GET"])
def get_conversation(conv_id):
    result = supabase.table("conversations").select("*").eq("id", conv_id).execute()
    if result.data:
        return jsonify(result.data[0])
    return jsonify({"error": "Not found"}), 404

@app.route("/conversations/<int:conv_id>", methods=["PATCH"])
def rename_conversation(conv_id):
    data = request.json
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Title required"}), 400
    supabase.table("conversations").update({"title": title}).eq("id", conv_id).execute()
    return jsonify({"success": True})

@app.route("/conversations/<int:conv_id>", methods=["DELETE"])
def delete_conversation(conv_id):
    supabase.table("conversations").delete().eq("id", conv_id).execute()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
