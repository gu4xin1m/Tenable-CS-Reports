import os
import pandas as pd
from tenable.io import TenableIO
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm


load_dotenv()

now =  datetime.now().strftime("%Y%m%d-%H%M%S")
filename = f"Tenable_CS-{now}.xlsx"

TENABLE_ACCESS_KEY = os.getenv('TENABLE_ACCESS_KEY')
TENABLE_SECRET_KEY = os.getenv('TENABLE_SECRET_KEY')


tio = TenableIO(TENABLE_ACCESS_KEY,TENABLE_SECRET_KEY)

def get_report():
    print("Generating the report...")
    report = []
    resp = tio.cs.images.list(return_json=True, limit=100000)
    for item in tqdm(resp['items']):
        image = item['name']
        repo = item['repo_name']
        tag = item['tag']
        tioReport = tio.cs.reports.report(repo,image,tag)
        imageFindings = convert(tioReport,repo)
        report += imageFindings
    return report



def convert(tio_report,repository):
    image_findings = []
    for line in tio_report['findings']:
                finding = line['nvd_finding']
        
                #Fixing report structure here !!!
                #Get Values from parent node
                finding['image_name'] = tio_report['image_name']
                finding['repository'] = repository
                finding['docker_image_id'] = tio_report['docker_image_id']
                finding['tag'] = tio_report['tag']
                finding['created_at'] = tio_report['created_at']
                finding['updated_at'] = tio_report['updated_at']
                finding['platform'] = tio_report['platform']
                finding['packages'] = line['packages']
                finding.pop("packages", None)
                image_findings.append(finding)
    return image_findings


report = get_report()


print("writing to xls file...")
df = pd.DataFrame.from_dict(report)

#Removing Brackets from 'cpe' and 'references' columns 
# df['references'] = df.references.apply(lambda x: ', '.join([str(i) for i in x]))
# df['cpe'] = df.cpe.apply(lambda x: ', '.join([str(i) for i in x]))
# writer = pd.ExcelWriter(filename,engine='xlsxwriter',engine_kwargs={'options': {'strings_to_urls': False}})
# df.to_excel(writer,index=False,)


df.to_excel(filename, engine='xlsxwriter',index=False,)

