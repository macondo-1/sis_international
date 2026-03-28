from modules.project_class.main import Project
from modules.csv_tools.main import get_project_info_from_filename, fix_columns_to_match_db, read_file_pandas, fix_data_before_insert_to_db
from modules.utilities.main import get_information_from_blast_master_excel
from modules.database.database import connect_to_db, insert_new_recruits, get_update_records, insert_update_recruits, insert_new_csv_to_db, bulk_update_records, prepare_update_records, update_validation_status, add_new_million_verifier_job, get_processing_jobs, update_mv_job_status, save_records_to_project, get_project_recruits, get_ss_ready_records, insert_new_blasting_quotas, get_today_blast_quota, update_project_recruits_last_sent, save_newly_added_records_to_project, get_project_limit, prepare_csv_for_database_input, insert_new_mailmerging_quotas, create_column_mapper_and_prepare_for_db_input, get_project_name_with_project_number, insert_into_table_surveys, insert_into_table_surveys_bulk, insert_into_table_survey_collectors_bulk, insert_into_table_survey_responses_daily_bulk
from modules.super_send.super_send import SuperSend
from modules.million_verifier_api.million_verifier_api import MillionVerifier
from modules.smtp_bot.smtp_bot import SMTP
import pprint
from pathlib import Path
import os
import pandas as pd
import modules.constants.main as const
import csv
import json
import sys
from datetime import datetime
import traceback
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


# const.TEMP_DIR = Path("files/temp")
# const.MV_TEMP_DIR = Path("modules/million_verifier_api/temp")

LOCK_FILE_PATH = const.TEMP_DIR / 'check_jobs.lock'

def save_new_ru_files_to_db():
    path_ = Path('/Users/albertoruizcajiga/Library/CloudStorage/GoogleDrive-beautifulday874@gmail.com/My Drive/Information_Technology/ramped_up_database')
    paths = path_.glob('*.csv')
    processed_files_path = const.TEMP_DB_DIR.joinpath('processed_files.txt')
    failed_files_path = const.TEMP_DB_DIR.joinpath('failed_files.txt')

    with open(processed_files_path, 'r') as file:
        lines = file.readlines()
    lines = [x.strip() for x in lines]

    with open(failed_files_path, 'r') as file:
        bad_lines = file.readlines()
    bad_lines = [x.strip() for x in bad_lines]

    lines.extend(bad_lines)
    to_process_paths = [str(x) for x in paths if str(x) not in lines]

    for file_path in to_process_paths:

        try:

            with open(processed_files_path, 'r') as file:
                lines = file.readlines()
            lines = [x.strip() for x in lines]

            file_path = Path(file_path)
            source, status, project_id = 'ramped_up','cold',' '
            insert_new_csv_to_db(file_path, source, status, project_id)

            lines.append(str(file_path))

            with open(processed_files_path, 'w') as file:
                content = '\n'.join(lines)
                file.write(content)

        except Exception as e:
            print('error:', e)
            print('saving file name to failed files text file...')
            with open(failed_files_path, 'r') as file:
                bad_lines = file.readlines()
            bad_lines = [x.strip() for x in bad_lines]
            bad_lines.append(str(file_path))
            with open(failed_files_path, 'w') as file:
                content = '\n'.join(bad_lines)
                file.write(content)
            print('saved succesfully!')

def query_to_csv(query_str: str, out_path: str):
    conn, cursor = connect_to_db()
    print('connected succesfully')
    cursor.execute(query_str)
    print('query executed succesfully')
    with open(out_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(d[0] for d in cursor.description)
        writer.writerows(cursor.fetchall())
    conn.close()

def query_project_needs(sql_file_path: str, limit: int):
    with open(sql_file_path, 'r') as file:
        query = file.read()
    query = query.format(limit=limit)
    conn, cursor = connect_to_db()
    print('connected succesfully')
    cursor.execute(query)
    print('query executed succesfully')

    data = cursor.fetchall()
    conn.close()
    return data

def prepare_fetched_data_to_supersend(data: list[tuple]) -> list[dict]:
    ss_data = []

    for x in data:
        recruit_dict = {}
        recruit_dict['first_name'] = x[0]
        recruit_dict['email'] = x[1]
        ss_data.append(recruit_dict)
    
    return ss_data

def acquire_lock():
    if os.path.exists(LOCK_FILE_PATH):
        sys.exit()
    open(LOCK_FILE_PATH, "w").close()

def release_lock():
    if os.path.exists(LOCK_FILE_PATH):
        os.remove(LOCK_FILE_PATH)

def download_and_process_all_available_lists_on_mv():
    jobs = get_processing_jobs()
    if not jobs:
        print('nothing to process')
        return

    for (job_id,) in jobs:
        try:
            mv_handler = MillionVerifier()
            file_info_dict = mv_handler.file_info(job_id)
            print(file_info_dict)
            status = file_info_dict['status']
            print(status)

            if status == 'finished':
                mv_report = mv_handler.download_report(job_id)
                validated_file_name = const.MV_TEMP_DIR / 'validated_{}.csv'.format(job_id)
                mv_handler.save_csv_file(mv_report, validated_file_name)
                print('updating validation status... ', job_id)
                update_validation_status(validated_file_name)
                print('update done')
                os.remove(validated_file_name)
                update_mv_job_status(job_id, 'completed')

        except Exception as e:
            print(f"Error processing MillionVerifier job {job_id}: {e}")
            print('traceback:')
            traceback.print_exc()


def print_report():

    # -----------------------------
    # Load CSV
    # -----------------------------

    df = pd.read_csv('/Users/albertoruizcajiga/Downloads/email_report.csv')

    df["date"] = pd.to_datetime(df["date"])

    # -----------------------------
    # Chart 1
    # Emails Sent Per Day
    # -----------------------------

    daily = df.groupby("date")["sent_count"].sum().reset_index()

    fig = px.line(
        daily,
        x="date",
        y="sent_count",
        title="Emails Sent Per Day"
    )

    fig.write_image("chart_1_emails_per_day.png")

    daily["cumulative"] = daily["sent_count"].cumsum()

    fig = px.line(
        daily,
        x="date",
        y="cumulative",
        title="Cumulative Emails Sent"
    )

    fig.write_image("chart_6_cumulative_outreach.png")

    # -----------------------------
    # Chart 2
    # Emails Sent by Strategy Over Time
    # -----------------------------

    strategy_daily = df.groupby(["date", "strategy"])["sent_count"].sum().reset_index()

    fig = px.line(
        strategy_daily,
        x="date",
        y="sent_count",
        color="strategy",
        title="Emails Sent by Strategy Over Time"
    )

    fig.write_image("chart_2_strategy_over_time.png")

    # -----------------------------
    # Chart 3
    # Emails Sent by Project Over Time
    # -----------------------------

    project_daily = df.groupby(["date", "project_name"])["sent_count"].sum().reset_index()

    fig = px.line(
        project_daily,
        x="date",
        y="sent_count",
        color="project_name",
        title="Emails Sent by Project Over Time"
    )

    fig.write_image("chart_3_project_over_time.png")

    # -----------------------------
    # Chart 4
    # Strategy Distribution
    # -----------------------------

    strategy_totals = df.groupby("strategy")["sent_count"].sum().reset_index()

    fig = px.bar(
        strategy_totals,
        x="strategy",
        y="sent_count",
        title="Total Emails Sent by Strategy"
    )

    fig.write_image("chart_4_strategy_distribution.png")

    # -----------------------------
    # Chart 5
    # Project x Strategy Heatmap
    # -----------------------------

    pivot = df.pivot_table(
        values="sent_count",
        index="project_name",
        columns="strategy",
        aggfunc="sum",
        fill_value=0
    )

    plt.figure(figsize=(10,6))
    plt.imshow(pivot, aspect="auto")

    plt.xticks(range(len(pivot.columns)), pivot.columns)
    plt.yticks(range(len(pivot.index)), pivot.index)

    plt.colorbar(label="Emails Sent")

    plt.title("Project vs Strategy Outreach")
    plt.tight_layout()

    plt.savefig("chart_5_project_strategy_heatmap.png")

    print("Charts generated successfully")


def generate_report(
    start_date,
    end_date,
    csv_file="email_report.csv",
    project_name=None,
    strategy=None,
    output_dir="report_output",
):
    """
    Generate outreach charts from a CSV export.

    Expected CSV columns:
        project_name, sent_count, date, strategy

    Args:
        start_date (str): inclusive start date, e.g. '2026-03-01'
        end_date (str): inclusive end date, e.g. '2026-03-10'
        csv_file (str): path to CSV file
        project_name (str | list[str] | None): optional project filter
        strategy (str | list[str] | None): optional strategy filter
        output_dir (str): folder where charts will be saved
    """

    # -----------------------------
    # Load data
    # -----------------------------
    df = pd.read_csv(csv_file)

    required_cols = {"project_name", "sent_count", "date", "strategy"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["sent_count"] = pd.to_numeric(df["sent_count"], errors="coerce").fillna(0)

    df = df.dropna(subset=["date"])
    df["project_name"] = df["project_name"].astype(str).fillna("Unknown")
    df["strategy"] = df["strategy"].astype(str).fillna("Unknown")

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # -----------------------------
    # Filter by date
    # -----------------------------
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    # -----------------------------
    # Optional project filter
    # -----------------------------
    if project_name is not None:
        if isinstance(project_name, str):
            project_name = [project_name]
        df = df[df["project_name"].isin(project_name)]

    # -----------------------------
    # Optional strategy filter
    # -----------------------------
    if strategy is not None:
        if isinstance(strategy, str):
            strategy = [strategy]
        df = df[df["strategy"].isin(strategy)]

    if df.empty:
        print("No data found for the selected filters.")
        return

    # -----------------------------
    # Create output folder
    # -----------------------------
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Safe label for filenames/titles
    project_label = (
        ", ".join(project_name) if isinstance(project_name, list) else project_name
    ) or "All Projects"
    strategy_label = (
        ", ".join(strategy) if isinstance(strategy, list) else strategy
    ) or "All Strategies"

    subtitle = (
        f"{start_date.date()} to {end_date.date()} | "
        f"Project: {project_label} | Strategy: {strategy_label}"
    )

    # -----------------------------
    # Chart 1
    # Emails Sent Per Day
    # -----------------------------

    daily = df.groupby("date")["sent_count"].sum().reset_index()

    fig = px.line(
        daily,
        x="date",
        y="sent_count",
        markers=True,
        text="sent_count",
        title=f"Emails Sent Per Day ({start_date.date()} → {end_date.date()})"
    )

    fig.update_traces(
        texttemplate="%{text:,}",   # adds comma separators
        textposition="top center"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Emails Sent"
    )

    fig.update_yaxes(tickformat=",")

    fig.write_image(out / "chart_1_emails_per_day.png")

    # -----------------------------
    # Chart 2
    # Emails Sent by Strategy Over Time
    # -----------------------------

    strategy_daily = df.groupby(["date", "strategy"], as_index=False)["sent_count"].sum()

    fig = px.line(
        strategy_daily,
        x="date",
        y="sent_count",
        color="strategy",
        markers=True,
        text="sent_count",
        title="Emails Sent by Strategy Over Time"
    )

    fig.update_traces(
        texttemplate="%{text:,}",   # <-- adds comma separators
        textposition="top center"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Emails Sent",
        legend_title="Strategy"
    )

    fig.write_image(out / "chart_2_strategy_over_time.png")

    # -----------------------------
    # Chart 3: Emails Sent by Project Over Time
    # -----------------------------
    project_daily = df.groupby(["date", "project_name"], as_index=False)["sent_count"].sum()

    fig = px.line(
        project_daily,
        x="date",
        y="sent_count",
        color="project_name",
        title=f"Emails Sent by Project Over Time<br><sup>{subtitle}</sup>",
        markers=True,
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Emails Sent", legend_title="Project")
    fig.write_image(out / "chart_3_project_over_time.png")

    # -----------------------------
    # Chart 4: Total Emails Sent by Strategy
    # -----------------------------
    strategy_totals = (
        df.groupby("strategy", as_index=False)["sent_count"]
        .sum()
        .sort_values("sent_count", ascending=False)
    )

    fig = px.bar(
        strategy_totals,
        x="strategy",
        y="sent_count",
        title=f"Total Emails Sent by Strategy<br><sup>{subtitle}</sup>",
    )
    fig.update_layout(xaxis_title="Strategy", yaxis_title="Emails Sent")
    fig.write_image(out / "chart_4_strategy_distribution.png")

    # -----------------------------
    # Chart 5: Total Emails Sent by Project
    # -----------------------------
    project_totals = (
        df.groupby("project_name", as_index=False)["sent_count"]
        .sum()
        .sort_values("sent_count", ascending=True)
    )

    max_val = project_totals["sent_count"].max()

    fig = px.bar(
        project_totals,
        x="sent_count",
        y="project_name",
        orientation="h",
        text="sent_count",
        title=f"Total Emails Sent by Project<br><sup>{subtitle}</sup>",
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Emails Sent",
        yaxis_title="Project"
    )

    # extend axis so labels have space
    fig.update_xaxes(range=[0, max_val * 1.15], tickformat=",")

    fig.write_image(out / "chart_5_project_distribution.png")

    # -----------------------------
    # Chart 6: Project x Strategy Heatmap
    # -----------------------------
    pivot = df.pivot_table(
        values="sent_count",
        index="project_name",
        columns="strategy",
        aggfunc="sum",
        fill_value=0,
    )

    plt.figure(figsize=(12, max(5, len(pivot) * 0.45)))
    plt.imshow(pivot, aspect="auto")
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha="right")
    plt.yticks(range(len(pivot.index)), pivot.index)
    plt.colorbar(label="Emails Sent")
    plt.title(f"Project vs Strategy Outreach\n{subtitle}")
    plt.tight_layout()
    plt.savefig(out / "chart_6_project_strategy_heatmap.png", bbox_inches="tight")
    plt.close()

    # -----------------------------
    # Chart 7: Cumulative Emails Sent
    # -----------------------------
    daily = daily.sort_values("date").copy()
    daily["cumulative_sent"] = daily["sent_count"].cumsum()

    fig = px.line(
        daily,
        x="date",
        y="cumulative_sent",
        title=f"Cumulative Emails Sent<br><sup>{subtitle}</sup>",
        markers=True,
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Cumulative Emails Sent")
    fig.write_image(out / "chart_7_cumulative_outreach.png")

    # -----------------------------
    # Save filtered data too
    # -----------------------------
    df.sort_values(["date", "project_name", "strategy"]).to_csv(
        out / "filtered_data.csv", index=False
    )

    print(f"Report generated successfully in: {out.resolve()}")



if __name__ == '__main__':
    # project_id = '2010273'
    # save_records_to_project(project_id)


    # filename = '/Users/albertoruizcajiga/python/survey_monkey_api/files/all_surveys_jsons_csv/all_responses_counts.csv'
    # with open(filename, 'r') as file:
    #     lines = file.readlines()
    # lines = [x.strip() for x in lines]
    # lines = [tuple(x.split(',')) for x in lines]
    # lines = lines[1:]

    # print(lines[0])
    # insert_into_table_survey_responses_daily_bulk(lines)
    # values = []    
    # values.append((survey_id, project_id, survey_name, platform))

    # 

    # generate_report(
    #     start_date="2026-03-10",
    #     end_date="2026-03-11",
    #     csv_file="/Users/albertoruizcajiga/Downloads/email_report.csv",
    #     project_name=None,              # e.g. "HVAC Study" or ["HVAC Study", "AI Study"]
    #     strategy='mailmerge',                  # e.g. "linkedin" or ["linkedin", "email"]
    #     output_dir="/Users/albertoruizcajiga/python/sis_international/modules/reporting",
    # )
    # handler = SMTP()
    # handler.send_emails_smtp()

    # project_id = '1150717'
    # data = get_project_limit(project_id)
    # print(data)
    acquire_lock()
    try:
        file_path = '/Users/albertoruizcajiga/Downloads/blast_needs.csv'
        insert_new_mailmerging_quotas(file_path)
    finally:
        release_lock()
    
    # # CONTINUE THIS
    # blast_needs_file_path = '/Users/albertoruizcajiga/Downloads/blast.csv'
    # sql_file_path = '/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp/base_query.sql'

    # # Gets and fixes blast needs
    # # CHECK: need to save campaign_id to json
    # with open(blast_needs_file_path, 'r') as file:
    #     reader = csv.DictReader(file)
    #     blast_needs = {'blast_needs' : []}
    #     for x in reader:
    #         if x['\ufeffproject_id']:
    #             cleaned_str = x[' q '].strip().replace(',','')
    #             project_needs = {'project_id': x['\ufeffproject_id'],
    #                              'total_records': int(float(cleaned_str)),
    #                              'remaining_records': int(float(cleaned_str))}
    #             blast_needs['blast_needs'].append(project_needs)

    # blast_needs_path = TEMP_DIR / 'blast_needs.json'
    # with open(blast_needs_path, 'w') as file:
    #     json.dump(blast_needs, file)

    # # print(blast_needs)

    
    # for x in blast_needs['blast_needs']:
        # try:
        #     project_id = '1994141'
        #     save_records_to_project(project_id=project_id)
    #         # Gets records and fixes them for supersend
    #         limit = int(x['remaining_records'])
    #         data = query_project_needs(sql_file_path, limit)
    #         # CHECK: if len(data) <= 0 break the loop for this project
    #         data = prepare_fetched_data_to_supersend(data)

            # Uploads contacts to a supersend campaign

            # contacts = {
            #             "contacts": [
            #                 {
            #                 "email": "john@example.com",
            #                 "first_name": "John",
            #                 "last_name": "Doe",
            #                 "company_name": "Acme Corp"
            #                 },
            #                 {
            #                 "email": "jane@example.com",
            #                 "first_name": "Jane",
            #                 "last_name": "Smith"
            #                 }
            #             ],
            #             "TeamId": "1523d91c-eb2c-400a-b97d-37ca8247a0e6",
            #             "CampaignId": "ca97ecda-0d03-4d83-8dd8-d08c1b107091"
            #             }
            # campaign_id = 'ca97ecda-0d03-4d83-8dd8-d08c1b107091'
            # super_send = SuperSend()
            # data = super_send.bulk_create_contacts(contacts=contacts, campaign_id=campaign_id)
            # print(data)
            # if data != None:
            #     update_project_recruits_last_sent('1994141', recruits_ids)
            # else:
            #     print('SS upload unsuccesfull')
    #         if data['success']:
    #             x['remaining_records'] = x['remaining_records'] - len(contacts)
    #             with open(blast_needs_path, 'w') as file:
    #                 json.dump(blast_needs, file)

        # HERE
        # try:
            # project_id = '1994141'
            # save_records_to_project(project_id)
            # DELETE
            # blast_needs_path = TEMP_DIR / 'blast_needs.json'
            # sql_file_path = '/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp/base_query.sql'
            
            # with open(blast_needs_path, 'r') as file:
            #     blast_needs = json.load(file)

            # for x in blast_needs['blast_needs']:
            #     # Gets remaining records for email validation
            #     limit = int(x['remaining_records'])
            #     data = query_project_needs(sql_file_path, limit)
                
            #     to_validate_file_name = const.MV_TEMP_DIR / 'validating_{}.csv'.format(x['project_id'])
            #     with open(to_validate_file_name, 'w') as file:
            #         writer = csv.writer(file)
            #         writer.writerow(['first_name', 'email'])
            #         writer.writerows(data)

        #     # MV upload
            # to_validate_file_name = '/Users/albertoruizcajiga/python/sis_international/modules/million_verifier_api/temp/validating_1150711.csv'

            # million_verifier = MillionVerifier()
            # mv_upload_data = million_verifier.file_upload(to_validate_file_name, '123456')
            # mv_file_id = mv_upload_data['file_id']

        #         mv_file_id = '30257592' # DELETE
        #         file_status = million_verifier.file_info(mv_file_id)
        #         if file_status['status'] == 'finished':
        #             mv_report = million_verifier.download_report(mv_file_id)
        #             validated_file_name = const.MV_TEMP_DIR / 'validated_{}.csv'.format(x['project_id'])
        #             print(validated_file_name)
        #             million_verifier.save_csv_file(mv_report, validated_file_name)
        #             print('updating... ', x['project_id'])
        #             update_validation_status(Path(validated_file_name))
        #             print('update done')

        #         break


        #     # REPEAT # Gets records and fixes them for supersend

        #     # REPEAT # Uploads contacts to a supersend campaign

        #     # REPEAT # Gets remaining records for email validation (while loop until remaining records are zero)

        
        # except Exception as e:
        #     print('SuperSend part error: ', e)




    # # MAKE THIS A DATABASE MODULE
    # # QUERIES THE DATABASE AND SAVES AS CSV
    # sql_file_path = '/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp/test_sql.sql'
    # with open(sql_file_path, 'r') as file:
    #     query = file.read()

    # out_path = '/Users/albertoruizcajiga/Downloads/alex_nyc_mm.csv'
    # query_to_csv(query, out_path)

    # MAKE THIS A DATABASE MODULE
    # ITERATES A DIRECTORY AND STORES ALL VALIDATION CSVS TO DATABASE
    # dir_path = Path('/Users/albertoruizcajiga/Library/CloudStorage/GoogleDrive-beautifulday874@gmail.com/My Drive/Information_Technology/alberto/utilities/to_process/alberto')
    # for x in dir_path.glob('*.csv'):
    #     print('updating... ', x.name)
    #     update_validation_status(x)
    #     print('update done')

        # print('insertion done\n')
        # project_id = '1993742'
        # print('saving for project {}'.format(project_id))
        # save_newly_added_records_to_project(project_id, ids)
        # print('succesfull project save')


    # MAKE THIS A DATABASE MODULE
    # SAVE NEW CSV INTO DATABASE
    # dir_path = Path('/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp/pending_database_input/manual_cleaning_needed')
    # for x in dir_path.glob('*.csv'):
    #     print('preparing... ', x.name)
    #     # ids = insert_new_csv_to_db(x, source="", status='cold', project_id="")
    #     # project_id = '1993742'
    #     project_id = '1546582'
    #     prepare_csv_for_database_input(x, source="client", status='cold', project_id=project_id)