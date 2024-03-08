import re
import html

from .scrapper import Scrapper


def scrape_links(url):
    sc = Scrapper()
    soup = sc.get_responce(url)
    links = {}
    for link in soup.find_all('a'):
      links[link.text] = link.get('href')
  
    return links


def scrape_questions(url):
    sc = Scrapper()
    soup = sc.get_responce(url)
    questions = []
    for questions_p in soup.find_all('div', {'class': 'entry-content'}):
        for question, ans in zip(questions_p.findAll("p")[1:-3],questions_p.find_all('div', {'class': 'collapseomatic_content'})) :
            try:
                q = {"question":"","options":[],"answer":"","explanation":"No Explanation","long_question":[],"images":[]}

                ques = html.unescape(str(question))
                ques = ques.replace(r"<sub>", r"_").replace(r"<sup>", r"^").replace(r"</sup>", " ").replace(r"</sub>", " ")
                ques = ques.split("<br/>")
                ques_list = []
                for i  in range(5):
                  ques_list.extend(ques[i].split("<br>"))
                # Extract Image From Question
                img_list = []
                print(len(ques_list))
                for  i in range(len(ques_list)):
                        link_regex = r'<a href="(.*?)">'
                        match = re.search(link_regex, ques_list[i])
                        if match:
                            img_list.append(match.group(1))
                            ques_list[i] = ques_list[i].split("<a")[0]
                            print("get link")
                        else:
                            img_list.append("")
                # Add Images to dict              
                q["images"] = img_list
                print(img_list)
                # Add Questino to 
                if len(ques_list[0][3:])< 300:
                      q["question"] = ques_list[0][3:]
                else:
                      q["question"] = ques_list[0][3:5]
                      q["long_question"] = [ques_list[0][3:]]
                # Add Options to dict 
                if ques_list[3].strip().startswith('c') :
                    q['options'] = []   
                    for que in ques_list[1:5]:
                        if len(que) < 100:
                            q['options'].append(que)
                        else:
                            q['options'].append(que[:3])                    
                            q['long_question'].append(que) 
                else:
                    q['options'] = [ques_list[1][:100],ques_list[2][:100],"c) None Of above","d) both answers"]
                # Add Correct Answer to dict
                ans = html.unescape(str(ans)).split("<br/>")
                alpha = {"a":0,"b":1,"c":2,"d":3}
                q["answer"] = alpha[ ans[0].strip()[-1]]
                # Add Explanation to the dict
                try:
                    q['explanation'] = modifiStr(f'{ans[1][:-6]}')[:100]
                except: 
                        q['explanation']  = "No explanation"
                questions.append(q)
            except Exception as e :
                print("excption while scrape Sanfoundry",e)
    return questions





def modifiStr (str):

    new_str = str.replace("_", "\_") \
        .replace("*", "\*") \
        .replace("[", "\[") \
        .replace("`", "\`") \
        .replace(".", " ") \
        .replace("(", "\(") \
        .replace(")", "\)") \
        .replace("-", " ") \
        .replace("+", "\+") \
        .replace("=", "\=") \
        .replace("<", "\<") \
        .replace(">", "\>") \
        .replace("!", "\!") 

    return new_str


