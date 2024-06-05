import os
import PyPDF2
import docx2txt
import re


def get_pdf_text(file_path):
  # get the file extension
  file_extension = os.path.splitext(file_path)[1]
  print(file_extension)
  # extract text from the document
  if file_extension == ".pdf":
    pdf_reader = PyPDF2.PdfReader(file_path)
    # iterate over all the pages in the PDF
    page_text = ""
    for page_num in range(len(pdf_reader.pages)):
      page = pdf_reader.pages[page_num]
      page_text += page.extract_text()
  elif file_extension == ".docx":
    page_text = docx2txt.process(file_path)
  else:
    # handle other file formats here
    page_text = ""
  return page_text


def get_msq_from_text(file_path):
  try:
    page_text = get_pdf_text(file_path)
    page_lines = page_text.split('\n')
    # Extract Question if start with questions word, or start with number
    question_pattern = re.compile(r'^\d+\. (.+)|^\d+\- (.+)|(What|Why|How|When|Where|Who|Which)\s', re.IGNORECASE)
    option_pattern = re.compile(r'^\s*[A-Da-d][\-\.\)] .+', re.IGNORECASE)
    answer_pattern = re.compile(r'(?:Answer: [A-Da-d]|ANSWER: [A-Da-d]|ans: [A-Da-d])', re.IGNORECASE)

    questions = []
    current = ""

    for i, line in enumerate(page_lines, 0):
      line = line.strip()
      try:
        if re.match(question_pattern, line):
          try:
            questions.append(question)
          except:
            pass
          question = {
            "question": "",
            "options": [],
            "answer": "",
            "explanation": "No Explanation",
            "long_question": [],
            "images": []
          }
          # Add Questino to
          question["question"] = line
          current = "question"

        elif re.match(option_pattern, line):
          question["options"].append(line)
          current = "options"

        elif re.match(answer_pattern, line):
          k = {"a": 0, "b": 1, "c": 2, "d": 3, "A": 0, "B": 1, "C": 2, "D": 3}
          question["answer"] = k[re.findall(answer_pattern, line)[0][-1]]
          current = "answer"

          # After Find the Answer time to show if lenght > limit
          if len(question["question"]) > 300:
            question["question"] = question["question"][:3]
            question['long_question'].append(question["question"])
          for i, que in enumerate(question["options"]):
            if len(que) > 100:
              question["options"][i] = que[:3]
              question['long_question'].append(que)

        else:
          try:
            if current == "question":
              question[current] += line
            elif current == "options":
              question[current][-1] += line
          except:
            continue

      except Exception as e:
        print(e)

  except Exception as e:
    print(e)

  return questions
