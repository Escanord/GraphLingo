from PyPDF2 import PdfReader
from knowledge_graph_builder import course_builder


def readPDF(path):
    reader = PdfReader(path)
    return reader.pages


def sanitize(lines):
    sanitized_lines = []
    flag = True
    for i, line in enumerate(lines):
        if i > 0 and len(lines[i - 1]) <= 1 and len(sanitized_lines) > 0:
            line = sanitized_lines.pop() + line
        if 'Course Outcomes to Program Outcomes Mapping' in line:
            flag = False
        if 'Course Topic' in line:
            flag = True
        if flag:
            sanitized_lines.append(line)

    return sanitized_lines


def get_text(path):
    pages = readPDF(path)[1:]

    # sanitized_lines = sanitize(pages[34].extract_text().split('\n'))
    # builder = course_builder(sanitized_lines)
    # builder.retrieve_entities()
    # sanitized_lines = sanitize(pages[35].extract_text().split('\n'))
    # builder.update_data(sanitized_lines)
    # builder.retrieve_entities()
    # builder.inject_course_info()

    # for i in range(int(len(pages) / 2)):
    #     sanitized_lines = sanitize(pages[i * 2].extract_text().split('\n'))
    #     builder = course_builder(sanitized_lines)
    #     builder.retrieve_entities()
    #     sanitized_lines = sanitize(pages[i * 2 + 1].extract_text().split('\n'))
    #     builder.update_data(sanitized_lines)
    #     builder.retrieve_entities()
    #     builder.inject_course_info()


get_text('/Applications/CWRU/Spring2023/CSDS 396/VACAS/syllabi.pdf')
