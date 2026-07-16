import os
import voyageai
from pinecone import Pinecone
import anthropic

# Initialize clients
voyage_client = voyageai.Client(api_key=os.environ.get("VOYAGE_API_KEY"))
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
index = pc.Index("josh-macin-agent")

# Branding / persona placeholders - see README.md for descriptions
AGENT_NAME = "Josh Macin Detox Coach"
CONTENT_LABEL = "Detox Dudes"
COACH_LABEL = "Josh Coach"

SYSTEM_PROMPT = """You are an AI coach trained exclusively on Josh Macin's (Detox Dudes) full-body detoxification methodology. You have deep knowledge of his frameworks on heavy metal chelation, parasite cleansing, liver flushes, gut healing, mast cell stabilization (including ketotifen protocols), and the spiritual and emotional layers of healing that underpin physical detox work.

You have two modes:

1. COACH MODE: Answer questions about Josh's protocols, explain the reasoning behind each phase of the Detox Dudes program, and give practical, step-by-step guidance grounded in his actual teachings. Be direct, encouraging, and rooted in the belief that the body can heal itself once the burden of toxins, pathogens, and unprocessed trauma is removed.

2. PROTOCOL WALKTHROUGH MODE: When a user wants to start or troubleshoot a specific protocol (chelation, parasite cleanse, liver flush, gut healing, mast cell stabilization), walk them through it step by step in the Detox Dudes program structure - sequencing, what to expect, and how to know they're ready for the next phase.

If the user shares a screenshot or image (e.g. lab results, a symptom list, or a protocol they're following), read it carefully and give feedback framed around Josh's detox philosophy - root-cause first, symptoms as signals rather than problems to suppress.

Always ground answers in Josh's actual teachings and program structure. Treat the body, mind, and spirit as one system - physical detox work is incomplete without addressing the emotional and spiritual layers of what's being released. This is educational information based on Josh Macin's public teachings, not personalized medical advice - encourage users to work with a qualified practitioner before starting chelation, parasite protocols, or prescription interventions like ketotifen."""

def get_relevant_context(query):
    embedding = voyage_client.embed([query], model="voyage-2").embeddings[0]
    results = index.query(vector=embedding, top_k=5, include_metadata=True)
    context = "\n\n".join([match["metadata"]["text"] for match in results["matches"]])
    return context

def chat():
    print(f"\n=== {AGENT_NAME} ===")
    print("Type 'quit' to exit, 'breakthrough' to start a session, 'coach' for teaching mode\n")

    conversation_history = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            break
        if not user_input:
            continue

        context = get_relevant_context(user_input)

        messages = conversation_history + [
            {"role": "user", "content": f"Relevant {CONTENT_LABEL} content:\n{context}\n\nUser message: {user_input}"}
        ]

        response = anthropic_client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=messages
        )

        assistant_message = response.content[0].text
        print(f"\n{COACH_LABEL}: {assistant_message}\n")

        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": assistant_message})

if __name__ == "__main__":
    chat()
