import os
import PyPDF2
import docx2txt
import re
import fitz  # PyMuPDF
from docx import Document

def get_pdf_text(file_path):
    # Get the file extension
    file_extension = os.path.splitext(file_path)[1]
    # Extract text from the document
    if file_extension == ".pdf":
        pdf_reader = PyPDF2.PdfReader(file_path)
        # Iterate over all the pages in the PDF
        page_text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text += page.extract_text()
    elif file_extension == ".docx":
        page_text = docx2txt.process(file_path)
    else:
        # Handle other file formats here
        page_text = ""
    return page_text

def get_highlighted_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    highlighted_text = []
    for page in doc:
        for annot in page.annots():
            if annot.type == fitz.PDF_ANNOT_HIGHLIGHT:
                highlight_info = annot.info
                quad_points = annot.vertices
                for quad in quad_points:
                    quad = [fitz.Quad(p) for p in quad_points]
                    highlight_text = ""
                    for q in quad:
                        highlight_text += page.get_text("text", q.rect)
                    highlighted_text.append(highlight_text.strip())
    return highlighted_text

def get_underlined_text_from_docx(file_path):
    doc = Document(file_path)
    underlined_text = []
    for para in doc.paragraphs:
        for run in para.runs:
            if run.underline:
                underlined_text.append(run.text)
    return underlined_text

def get_msq_from_text(file_path):
    try:
        page_text = get_pdf_text(file_path)
        page_lines = page_text.split('\n')
        # Extract Question if start with questions word, or start with number
        question_pattern = re.compile(r'^\d+\. (.+)|^\d+\- (.+)|(What|Why|How|When|Where|Who|Which)\s', re.IGNORECASE)
        option_pattern = re.compile(r'^\s*[A-Da-d][\-\.\)] .+', re.IGNORECASE)
        answer_pattern = re.compile(r'(?:Answer: [A-Da-d]|ANSWER: [A-Da-d]|ans: [A-Da-d])|Answer [A-Da-d]', re.IGNORECASE)

        questions = []
        current = ""

        if file_path.endswith(".pdf"):
            highlighted_text = get_highlighted_text_from_pdf(file_path)
        elif file_path.endswith(".docx"):
            highlighted_text = get_underlined_text_from_docx(file_path)
        else:
            highlighted_text = []

        question = None
        for i, line in enumerate(page_lines, 0):
            line = line.strip()
            try:
                if re.match(question_pattern, line):
                    if question:  # Append the previous question
                        questions.append(question)
                    question = {
                        "question": line,
                        "options": [],
                        "answer": "",
                        "explanation": "No Explanation",
                        "long_question": [],
                        "images": []
                    }
                    current = "question"

                elif re.match(option_pattern, line):
                    if question:
                        question["options"].append(line)
                    current = "options"

                elif re.match(answer_pattern, line):
                    if question:
                        k = {"a": 0, "b": 1, "c": 2, "d": 3, "A": 0, "B": 1, "C": 2, "D": 3}
                        question["answer"] = k[re.findall(answer_pattern, line)[0][-1]]
                    current = "answer"

                elif line in highlighted_text:
                    if question:
                        # If the line is highlighted, mark it as the answer
                        question["answer"] = line

                else:
                    if current == "question" and question:
                        question["question"] += " " + line
                    elif current == "options" and question and question["options"]:
                        question["options"][-1] += " " + line

            except Exception as e:
                print(e)

        if question:
            questions.append(question)

    except Exception as e:
        print(e)

    return questions

