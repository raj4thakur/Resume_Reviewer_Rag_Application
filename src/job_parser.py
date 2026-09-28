#job_parser.py
def extract_job_keywords(job_description):
    lines = job_description.split("\n")
    keywords = [line.strip() for line in lines if "-" in line or "•" in line]
    return keywords
