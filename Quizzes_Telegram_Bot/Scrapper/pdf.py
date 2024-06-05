import os
import PyPDF2
import docx2txt
import re


def get_pdf_text(file_path):
    # Get the file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    # Extract text from the document
    try:
        if file_extension == ".pdf":
            pdf_reader = PyPDF2.PdfReader(file_path)
            page_text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text += page.extract_text()
        elif file_extension == ".docx":
            page_text = docx2txt.process(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        page_text = ""
    return page_text


def get_msq_from_text(file_path):
    try:
        page_text = get_text_from_file(file_path)
        page_lines = page_text.split('\n')

        question_pattern = re.compile(r'^\d+\. (.+)|^\d+\- (.+)|(What|Why|How|When|Where|Who|Which)\s', re.IGNORECASE)
        option_pattern = re.compile(r'^\s*[A-Da-d][\.\)] .+', re.IGNORECASE)
        answer_pattern = re.compile(r'(?:Answer: [A-Da-d]|ANSWER: [A-Da-d]|ans: [A-Da-d])', re.IGNORECASE)

        questions = []
        question = {
            "question": "",
            "options": [],
            "answer": "",
            "explanation": "No Explanation",
            "long_question": [],
            "images": []
        }

        for line in page_lines:
            line = line.strip()
            if re.match(question_pattern, line):
                if question["question"]:
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
                question["options"].append(line)
            elif re.match(answer_pattern, line):
                answer_char = re.findall(answer_pattern, line)[0][-1].upper()
                question["answer"] = "ABCD".index(answer_char)
            else:
                if question["question"]:
                    if len(question["question"]) > 300:
                        question["long_question"].append(question["question"])
                        question["question"] = question["question"][:300]
                    for i, opt in enumerate(question["options"]):
                        if len(opt) > 100:
                            question["long_question"].append(opt)
                            question["options"][i] = opt[:100]
        if question["question"]:
            questions.append(question)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        questions = []

    return questions