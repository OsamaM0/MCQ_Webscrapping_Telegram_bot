import os
import fitz  # PyMuPDF
from docx import Document
import re

def get_pdf_text(file_path):
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error in PDF extraction: {e}")
    return text

def get_docx_text(file_path):
    text = ""
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error in DOCX extraction: {e}")
    return text

def get_msq_from_text(file_path):
    questions = []
    text = ""
    if file_path.endswith('.pdf'):
        text = get_pdf_text(file_path)
    elif file_path.endswith('.docx'):
        text = get_docx_text(file_path)

    # Parse text to extract questions
    try:
        lines = text.split('\n')
        question_pattern = r'^\d+\. .+|^\d+\- .+|(What|Why|How|When|Where|Who|Which)\s'
        option_pattern = r'^\s*[A-Da-d][\-\.\)] .+'
        answer_pattern = r'(Answer: [A-Da-d]|ANSWER:[A-Da-d]|ans: [A-Da-d]|Answer [A-Da-d]|ANSWER [A-Da-d]|ans [A-Da-d])'
        explination_pattern = r'(Explanation:[A-Da-d]|Explanation[A-Da-d]|Explanation :[A-Da-d]|Explanation :[A-Da-d]|Explanation: [A-Da-d]|Explanation : [A-Da-d])'
        k = {"a": 0, "b": 1, "c": 2, "d": 3, "A": 0, "B": 1, "C": 2, "D": 3}

        question = None
        for line in lines:
            line = line.strip()

            if line and not line.startswith("Explanation:") and not line.startswith("Hint:"):
                if re.match(question_pattern, line):
                    if question:
                        questions.append(question)
                    question = {
                        "question": line,
                        "options": [],
                        "answer": "",
                        "explanation": "No Explanation",
                        "long_question": [],
                        "images": []
                    }

                elif re.match(option_pattern, line):
                    if question:
                        if re.match(answer_pattern, line):
                            question["answer"] = k[re.findall(answer_pattern, line)[0][-1]]
                        option = re.sub(r'^\s*[A-Da-d][\-\.\)]\s*', '', line)
                        question["options"].append(option)

                elif re.match(answer_pattern, line):
                    if question:
                        question["answer"] = k[re.findall(answer_pattern, line)[0][-1]]

                elif re.match(explination_pattern, line):
                    if question:
                        question["explanation"] = line

                elif question:
                    question["question"] += " " + line

        if question:
            questions.append(question)

    except Exception as e:
        print(f"Error parsing questions: {e}")

    return questions


