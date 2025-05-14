from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

user_sessions = {}

@app.route('/post', methods=['POST'])
def respond():
    request_data = request.json
    logging.info(f"Запрос от Алисы: {request_data}")

    reply = {
        "session": request_data["session"],
        "version": request_data["version"],
        "response": {
            "end_session": False
        }
    }

    build_reply(request_data, reply)

    logging.info(f"Ответ для Алисы: {reply}")
    return jsonify(reply)

def build_reply(request_data, reply):
    user_id = request_data["session"]["user_id"]

    if request_data["session"]["new"]:
        user_sessions[user_id] = {
            "options": ["Не хочу.", "Не буду.", "Отстань!"]
        }
        reply["response"]["text"] = "Привет! Купи слона!"
        reply["response"]["buttons"] = suggest_options(user_id)
        return

    user_input = request_data["request"]["original_utterance"].lower()
    if user_input in ["ладно", "куплю", "покупаю", "хорошо"]:
        reply["response"]["text"] = "Слона можно найти на Яндекс.Маркете!"
        reply["response"]["end_session"] = True
        return

    reply["response"]["text"] = f"Все говорят '{user_input}', а ты купи слона!"
    reply["response"]["buttons"] = suggest_options(user_id)

def suggest_options(user_id):
    session = user_sessions[user_id]
    suggestions = [{"title": opt, "hide": True} for opt in session["options"][:2]]
    session["options"] = session["options"][1:]
    user_sessions[user_id] = session

    if len(suggestions) < 2:
        suggestions.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggestions

if __name__ == "__main__":
    app.run()
