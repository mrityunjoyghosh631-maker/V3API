import os
import json
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Initialize OpenAI client with DeepSeek base URL
client = OpenAI(
    api_key=os.getenv("sk-d2892b522fee4d618b457bd4adb42d65"),
    base_url="https://api.deepseek.com/v1"
)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "ANIRBAN V4 API is running!"})

@app.route("/chat", methods=["POST"])
def chat():
    """
    Chat endpoint that accepts JSON:
    {
        "messages": [{"role": "user", "content": "Hello!"}],
        "model": "deepseek/deepseek-v4-flash",  # optional
        "stream": false,                         # optional
        "thinking": false                        # optional - enable thinking mode
    }
    """
    data = request.get_json()
    
    if not data or "messages" not in data:
        return jsonify({"error": "Missing 'messages' field"}), 400
    
    # Default model - can be overridden
    model = data.get("model", "deepseek/deepseek-v4-flash")
    stream = data.get("stream", False)
    
    # For thinking mode, use deepseek-reasoner or deepseek-v4-flash with thinking
    # Legacy names are deprecated after July 24, 2026[reference:3]
    if data.get("thinking", False) and model == "deepseek/deepseek-v4-flash":
        # Use the thinking mode of v4-flash
        model = "deepseek/deepseek-v4-flash"  # thinking mode is controlled by extra_body
    
    try:
        # Prepare the API call
        params = {
            "model": model,
            "messages": data["messages"],
            "stream": stream
        }
        
        # Add thinking mode if requested
        if data.get("thinking", False):
            params["extra_body"] = {"thinking": {"type": "enabled"}}
        
        # Make the API call
        response = client.chat.completions.create(**params)
        
        if stream:
            # For streaming, we'd need to handle SSE differently
            # This is a simplified non-streaming example
            return jsonify({"error": "Streaming not implemented in this example"}), 501
        
        return jsonify({
            "response": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/models", methods=["GET"])
def list_models():
    """List available DeepSeek V4 models"""
    return jsonify({
        "models": [
            {"id": "deepseek/deepseek-v4-pro", "description": "DeepSeek V4 Pro - 49B active params"},
            {"id": "deepseek/deepseek-v4-flash", "description": "DeepSeek V4 Flash - 13B active params"}
        ],
        "note": "Legacy models deepseek-chat and deepseek-reasoner are deprecated after July 24, 2026[reference:4]"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)