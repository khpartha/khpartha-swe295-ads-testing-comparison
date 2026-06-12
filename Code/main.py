import logging
from datetime import datetime
import os
import re
import json
import yaml
import openpyxl
from legend.core.algorithm import Fuzzer
from legend.core.extractor import Extractor
from legend.core.converter import Converter
from legend.core.chromosome import Chromosome

start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_file_path = f'data/logs/{start_time}.log'
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
                    datefmt='%Y-%m-%d %A %H:%M:%S',
                    filename=log_file_path,
                    filemode='w')
logger = logging.getLogger(__name__)

with open("configs/config.yaml") as f:
    config = yaml.safe_load(f)

workbook = openpyxl.load_workbook('data/accident_reports/final_straight_cases.xlsx')
sheet = workbook.active
data_rows = sheet.iter_rows(min_row=2, max_row=19, values_only=True)

extractor = Extractor()
converter = Converter()

concerete_testcase_str = """def testcase(self):
    vehicle1 = NPC(lane_id=2, offset=0.131228103185137, initial_speed=38.531054805837044)
    vehicle2 = NPC(lane_id=3, offset=11.793838237315796, initial_speed=28.176327565703392)
    ego = NPC(lane_id=1, offset=30.0, initial_speed=45.54335320560515)
    vehicle1.changeLane(trigger_sequence=1, target_lane=3, target_speed=12.200676954270545)
    vehicle1.decelerate(trigger_sequence=2, target_speed=10.052463178108173)
    vehicle1.decelerate(trigger_sequence=3, target_speed=0.6957226121292823)
    vehicle2.changeLane(trigger_sequence=2, target_lane=1, target_speed=29.44636536456697)
    vehicle2.decelerate(trigger_sequence=3, target_speed=0.33210673749139596)"""

testcase = converter.parse_testcase_string(concerete_testcase_str)
chrom = Chromosome(concrete_testcase=testcase)
fuzzer = Fuzzer(config=config)
fuzzer.sim.set_road("straight_road")
fuzzer.eval(chrom)

os.makedirs("data/results", exist_ok=True)

for row in data_rows:
    report = row[1]
    case_id = row[0]
    logger.info("========New accident report======== \n id: %s", case_id)

    extracted_scenario = None
    try:
        extracted_scenario = extractor.extract(report)
    except Exception as e:
        logger.error(e)
    if extracted_scenario is None:
        continue

    logical_testcase, flag = converter.convert(extracted_scenario)
    if logical_testcase is None:
        continue
    count = 0
    while flag is False and count <= 2:
        logical_testcase, flag = converter.convert(extracted_scenario)
        count += 1
        if logical_testcase is None:
            break

    if logical_testcase is None:
        continue

    if re.search(r'\bcurve\w*\b', report, re.IGNORECASE):
        road_str = "curve_road"
    else:
        road_str = "straight_road"

    num, cs_list = fuzzer.loop(logical_testcase, road_str)

    record_path = "data/results/" + str(case_id) + '.json'
    data = {}
    data["accident_report"] = report
    data["functional_scenario"] = extracted_scenario
    data["logical_scenario"] = str(logical_testcase) if logical_testcase else "N/A"
    data["collision_num"] = num
    data["critical_scenarios"] = cs_list
    with open(record_path, 'w') as f:
        json.dump(data, f, indent=4)
    logger.info("=== Saved results for report: %s ===", case_id)
