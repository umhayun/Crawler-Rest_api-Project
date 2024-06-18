import sys, os
from scrapy.cmdline import execute

try:
    crawler_name = sys.argv[1]
    job_id = sys.argv[2]
    sub_id = sys.argv[3]
    os.chdir(f'/app/Crawler/{crawler_name}Crawler/{crawler_name}Crawler')
    execute(['scrapy', 'crawl', f'{crawler_name}Spider','-a',f'job_id={job_id}','-a' ,f'sub_id={sub_id}'])

except Exception as e:
    print(e)