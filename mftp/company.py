import os
import json
import logging
from env import ROLL_NUMBER
from datetime import datetime
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as bs
from endpoints import TPSTUDENT_URL, COMPANIES_URL


COMPANIES_FILE = f"{os.path.dirname(__file__)}/companies.json"


def filter(companies, filter):
    print('[FILTERING COMPANY UPDATES]', flush=True)

    filter_func = currently_open
    if filter.upper() == "OPEN":
        filter_func = currently_open
    elif filter.upper() == "OPEN_N":
        filter_func = open_not_applied # important
    elif filter.upper() == "APPLIED":
        filter_func = applied
    elif filter.upper() == "APPLIED_Y":
        filter_func = applied_available # important
    elif filter.upper() == "APPLIED_N":
        filter_func = applied_not_available # important

    filtered = []
    for company in companies:
        if filter_func(company):
            filtered.append(company)
            logging.info(
                f" {company['Name']} | {company['Role']} | {company['CTC']} | {company['End_Date']} | {company['Interview_Date']}"
            )

    return filtered


def fetch(session, headers, ssoToken):
    print('[FETCHING COMPANY UPDATES]', flush=True)

    session.post(
        TPSTUDENT_URL,
        data=dict(ssoToken=ssoToken, menu_id=11, module_id=26),
        headers=headers,
    )
    r = session.get(COMPANIES_URL, headers=headers)

    soup = bs(r.text, features="xml")
    xml_string = soup.prettify()
    xml_encoded = xml_string.encode("utf-8")
    root = ET.fromstring(xml_encoded)

    fetched_companies = []
    for row in root.findall("row"):
        # Safely get cell[4] for jd_args
        cell_4 = row.find("cell[4]")
        if cell_4 is None or cell_4.text is None:
            continue  # Skip this row if critical data is missing
        
        jd_args = cell_4.text.split("'")[5].split('"')
        jnf_id, com_id, year = jd_args[1], jd_args[3], jd_args[5]

        # Links
        company_details = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/TPComView.jsp?yop={year}&com_id={com_id}&user_type=SU"
        company_additional_details = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/AdmFilePDF.htm?type=COM&year={year}&com_id={com_id}"
        ppt = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/AdmFilePDF.htm?type=PPT&year={year}&com_id={com_id}"
        jd = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/TPJNFView.jsp?jnf_id={jnf_id}&com_id={com_id}&yop={year}&user_type=SU&rollno={ROLL_NUMBER}"
        apply_link_cv = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/TPJNFViewAction.jsp?jnf_id={jnf_id}&com_id={com_id}&year={year}&rollno={ROLL_NUMBER}&mode=ApplyCV"
        additional_jd = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/JnfMoreDet.jsp?mode=jnfMoreDet&rollno={ROLL_NUMBER}&year={year}&com_id={com_id}&jnf_id={jnf_id}"
        form_additional_details = f"https://erp.iitkgp.ac.in/TrainingPlacementSSO/AdmFilePDF.htm?type=JNF&year={year}&jnf_id={jnf_id}&com_id={com_id}"

        # Get text values safely for ALL critical fields
        cell_1 = row.find("cell[1]")
        cell_4_role = row.find("cell[4]")
        cell_9 = row.find("cell[9]")
        cell_10 = row.find("cell[10]")  
        cell_11 = row.find("cell[11]")
        cell_12 = row.find("cell[12]")
        
        # Safe text extraction with None checks
        def safe_text(cell):
            return cell.text if cell is not None and cell.text is not None else ""
        
        # Extract name safely
        name_text = safe_text(cell_1)
        if ">" in name_text and "<" in name_text:
            try:
                name = name_text.split(">")[1].split("<")[0].strip()
            except (IndexError, AttributeError):
                name = name_text.strip() if name_text else "Unknown"
        else:
            name = name_text.strip() if name_text else "Unknown"
        
        # Extract role safely
        role_text = safe_text(cell_4_role)
        if "'" in role_text:
            try:
                role_parts = role_text.split("'")
                if len(role_parts) > 1:
                    role = role_parts[1].strip()
                else:
                    role = "Unknown"
            except (IndexError, AttributeError):
                role = "Unknown"
        else:
            role = "Unknown"
        
        # Extract other fields safely
        app_status_text = safe_text(cell_9)
        start_date_text = safe_text(cell_10)
        end_date_text = safe_text(cell_11)
        interview_date_text = safe_text(cell_12)

        company_info = {
            "Name": name,
            "Company_Details": company_details,
            "Company_Additional_Details": company_additional_details,
            "PPT": ppt,
            "Role": role,
            "Job_Description": jd,
            "Apply_Link_CV": apply_link_cv,
            "Additional_Job_Description": additional_jd,
            "CTC": get_ctc_with_currency(session, headers, additional_jd),
            "Form_Additional_Details": form_additional_details,
            "Application_Status": app_status_text.strip() if app_status_text and app_status_text.strip() else "N",
            "Start_Date": start_date_text.strip() if start_date_text and start_date_text.strip() else "",
            "End_Date": end_date_text.strip() if end_date_text and end_date_text.strip() else "",
            "Interview_Date": interview_date_text.strip() if interview_date_text and interview_date_text.strip() else None,
        }
        
        fetched_companies.append(company_info)
    
    stored_companies = get_list()
    new_companies, modified_companies = get_new_and_modified_companies(fetched_companies, stored_companies)

    store_list(fetched_companies)

    return fetched_companies, new_companies, modified_companies


def get_new_and_modified_companies(fetched, stored, unique_key="Job_Description"):
    # Create dictionaries for quick lookup by the unique key
    stored_dict = {entry[unique_key]: entry for entry in stored}
    fetched_dict = {entry[unique_key]: entry for entry in fetched}

    new_entries = []
    updated_entries = []

    for key, fetched_entry in fetched_dict.items():
        if key not in stored_dict:
            # New entry
            new_entries.append(fetched_entry)
            logging.info(
                f" [NEW COMPANY]: {fetched_entry['Name']} | {fetched_entry['Role']} | {fetched_entry['CTC']} | {fetched_entry['End_Date']} | {fetched_entry['Interview_Date']}"
            )
        else:
            # Compare the values of the fetched entry with the stored entry
            stored_entry = stored_dict[key]
            if any(fetched_entry[k] != stored_entry.get(k) for k in fetched_entry):
                updated_entries.append(fetched_entry)
                logging.info(
                    f" [MODIFIED COMPANY]: {fetched_entry['Name']} | {fetched_entry['Role']} | {fetched_entry['CTC']} | {fetched_entry['End_Date']} | {fetched_entry['Interview_Date']}"
                )

    return new_entries, updated_entries


def store_list(companies):
    with open(COMPANIES_FILE, "w") as json_file:
        json.dump(companies, json_file, indent=2)


def get_list():
    try:
        with open(COMPANIES_FILE, "r") as json_file:
            return json.load(json_file)
    except json.JSONDecodeError as _:
        store_list([])
        return []
    except FileNotFoundError:
        store_list([])
        return []


# Downloads pdf content in bytes format
## Not used currently
def parse_link(session, link):
    stream = session.get(link, stream=True)
    attachment = b''
    for chunk in stream.iter_content(4096):
        attachment += chunk
    
    return attachment


def get_ctc_with_currency(session, headers, jd_url):
    try:
        jd_response = session.get(jd_url, headers=headers)
        html_content = jd_response.text.strip()
        soup = bs(html_content, "html.parser")

        rows = soup.find_all("tr")
        if not rows:
            return "N/A"
        
        row = rows[-1]
        columns = row.find_all("td")
        if not columns:
            return "N/A"
        
        column = columns[-1]
        ctc = column.text if column.text else "N/A"
        return ctc
    except Exception as e:
        logging.error(f"Error fetching CTC: {str(e)}")
        return "N/A"


def open_not_applied(company):
    return currently_open(company) and not applied(company)


def applied_not_available(company):
    return applied(company) and compare_deadline_gt(company, "Interview_Date")


def applied_available(company):
    return applied(company) and compare_deadline_lt(company, "Interview_Date")


def applied(company):
    return company["Application_Status"] == "Y"


def currently_open(company):
    return compare_deadline_lt(company, "End_Date")


def compare_deadline_gt(company, deadline_key):
    current_time = datetime.now()
    deadline = parse_date(company, deadline_key)

    return deadline is None or current_time > deadline


def compare_deadline_lt(company, deadline_key):
    current_time = datetime.now()
    deadline = parse_date(company, deadline_key)

    return deadline is None or current_time < deadline


def parse_date(company, date_key):
    date_format = "%d-%m-%Y %H:%M"
    
    date = None
    if company.get(date_key):
        try:
            date = datetime.strptime(company[date_key], date_format)
        except ValueError as e:
            logging.error(f" Failed to parse date for {company['Name']} ~ {str(e)}")
            date = None

    return date

