
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    if not current_question_id:
        return False, "No question to answer."

    if not answer.strip():
        return False, "Answer cannot be empty."

    question = next((q for q in PYTHON_QUESTION_LIST if q["id"] == current_question_id), None)

    if not question:
        return False, "Invalid question ID."

    if "answers" not in session:
        session["answers"] = {}

    session["answers"][current_question_id] = answer.strip()
    session.save()

    return True, ""


def get_next_question(current_question_id):
    if current_question_id is None:
        return PYTHON_QUESTION_LIST[0]["text"], PYTHON_QUESTION_LIST[0]["id"]

    for index, question in enumerate(PYTHON_QUESTION_LIST):
        if question["id"] == current_question_id:
            if index + 1 < len(PYTHON_QUESTION_LIST):
                next_question = PYTHON_QUESTION_LIST[index + 1]
                return next_question["text"], next_question["id"]
            else:
                return None, -1

    return None, -1

def generate_final_response(session):
    answers = session.get("answers", {})
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_count = 0

    for question in PYTHON_QUESTION_LIST:
        question_id = question["id"]
        correct_answer = question["correct_answer"].strip().lower()
        user_answer = answers.get(question_id, "").strip().lower()

        if user_answer == correct_answer:
            correct_count += 1

    score = (correct_count / total_questions) * 100
    return f"Quiz completed! You got {correct_count} out of {total_questions} correct. Your score: {score:.2f}%."
