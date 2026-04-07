"""
Jarvis-2 - Unificated Streaming Web Server
Fornisce Chat UI in tempo reale e backend con SSE streaming (Server-Sent Events).
"""
import os
import sys
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, Response, jsonify, render_template
from flask_cors import CORS
import config
from core.brain import stream_ai
from core.memory import rebuild_agent_memory, get_vectorstore, get_relevant_context

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
CORS(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

vectors = {
    "linda": get_vectorstore(config.CHROMA_LINDA_DIR),
    "arus": get_vectorstore(config.CHROMA_JARVIS_DIR)
}

@app.route('/')
def home():
    # Home di default, reindirizza a Linda
    return "<script>window.location.href='/linda';</script>"

@app.route('/<persona>')
def ui_chat(persona):
    persona = persona.lower()
    if persona not in ["linda", "arus"]:
        return "Persona non trovata", 404
        
    bot_name = "Linda AI" if persona == "linda" else "Arus Web"
    mode = config.OFFLINE_MODEL if persona == "linda" else config.ONLINE_MODEL
        
    return render_template(
        'chat.html', 
        bot_name=bot_name, 
        bot_id=persona,
        mode=mode
    )

@app.route('/api/chat/<persona>', methods=['POST'])
def chat(persona):
    persona = persona.lower()
    if persona not in ["linda", "arus"]:
        return jsonify({"error": "Persona non trovata"}), 404

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Nessun messaggio fornito'}), 400
        
    user_message = data['message']
    vectorstore = vectors.get(persona)
    
    context = ""
    if vectorstore:
        top_k = config.LINDA_RAG_TOP_K if persona == "linda" else config.JARVIS_RAG_TOP_K
        context = get_relevant_context(user_input=user_message, vectorstore=vectorstore, top_k=top_k)

    def generate():
        try:
            yield f"event: meta\ndata: {json.dumps({'context_used': bool(context)})}\n\n"
            
            for chunk in stream_ai(persona, user_message, context):
                safe_chunk = json.dumps({'chunk': chunk})
                yield f"data: {safe_chunk}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            
        yield "event: end\ndata: {}\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/learn/<persona>', methods=['POST'])
def learn(persona):
    persona = persona.lower()
    if persona == "arus":
        return jsonify({'error': 'La memoria di Arus esegue sync dal core Jarvis.'}), 403
        
    if persona not in ["linda"]:
        return jsonify({"error": "Azione non consentita"}), 404

    try:
        vectors[persona] = rebuild_agent_memory(persona)
        return jsonify({'message': f'Memoria RAG ricostruita con successo ({persona.capitalize()})!'})
    except Exception as e:
        return jsonify({'error': f'Impossibile ricostruire la memoria: {str(e)}'}), 500


if __name__ == '__main__':
    print(f"\n🚀 Avvio Server Unificato Jarvis-2")
    print(f"👉 PRIVATA: http://localhost:5000/linda")
    print(f"👉 PUBBLICA: http://localhost:5000/arus")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
