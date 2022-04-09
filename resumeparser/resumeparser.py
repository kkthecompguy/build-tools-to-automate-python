import spacy
import pdfminer
import re
import os
import pandas as pd 
import pdf2txt



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(BASE_DIR, 'resumeparser'), exist_ok=True)
os.makedirs(os.path.join(f"{BASE_DIR}/resumeparser", 'output'), exist_ok=True)
os.makedirs(os.path.join(f"{BASE_DIR}/resumeparser", 'resumes'), exist_ok=True)
os.makedirs(os.path.join(f"{BASE_DIR}/resumeparser/output", 'csv'), exist_ok=True)
os.makedirs(os.path.join(f"{BASE_DIR}/resumeparser/output", 'txt'), exist_ok=True)


skills_input = input('Please enter the required skills  ')
skills_required = skills_input.replace(' ', '|').replace(',', '|')

assert skills_required is not None


def convert_pdf(f):
    print(f)
    output_filename = os.path.splitext(f)[0] + '.txt'
    print(output_filename)
    abs_path = f"{BASE_DIR}/output/txt/"
    output_filepath = os.path.join(abs_path, output_filename)
    pdf2txt.main(args=[f, '--outfile', output_filepath])
    print(output_filepath + " saved successfully!!!")
    return open(output_filepath).read()


nlp = spacy.load("en_core_web_sm")

result_dict = {'name': [], 'phone': [], 'email': [], 'skills': []}
names = []
phones = []
emails = []
skills = []

re_compiled_skills = f"python|java|sql|hadoop|tableau|{skills_required}"
print(re_compiled_skills)

def parse_content(text):
    skillset = re.compile(re_compiled_skills)
    phone_num = re.compile('(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    doc = nlp(text)
    name = [entity.text for entity in doc.ents if entity.label_ is 'PERSON']
    print(name)
    email = [word for word in doc if word.like_email == True]
    print(email)
    phone = str(re.findall(phone_num,text.lower()))
    skills_list = re.findall(skillset,text.lower())
    unique_skills_list = str(set(skills_list))
    names.append(name)
    emails.append(email)
    phones.append(phone)
    skills.append(unique_skills_list)
    print("Extraction completed successfully!!!")

resume_file_path = f"{BASE_DIR}/resumeparser/resumes"

for file in os.listdir(resume_file_path):
    if file.endswith('.pdf'):
        print('Reading.....' + file)
        txt = convert_pdf(os.path.join(resume_file_path,file))
        parse_content(txt)


result_dict['name'] = names
result_dict['phone'] = phones
result_dict['email'] = emails
result_dict['skills'] = skills
print(result_dict)



result_df = pd.DataFrame(result_dict)
result_df

output_csv_file = os.path.join(f"{BASE_DIR}/resumeparser/output/csv", "parsed_resumes.csv")

result_df.to_csv(output_csv_file)