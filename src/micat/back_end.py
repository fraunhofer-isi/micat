# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import io
import json
import logging
import os
import traceback
from decimal import Decimal
from urllib.parse import parse_qs

import pandas as pd
import xlsxwriter
from flask_compress import Compress
from flask_cors import CORS

from micat.calculation import calculation
from micat.description import descriptions as descriptions_
from micat.input.database import Database
from micat.template import (
    measure_specific_parameters_template,
    parameters_template,
    savings_template,
)


class BackEnd:
    # pylint: disable=too-many-arguments, too-many-instance-attributes
    def __init__(
        self,
        injected_serve,
        injected_flask,
        _front_end_port,
        debug_mode=False,
        database_path="./data/public.sqlite",
        confidential_database_path="./data/confidential.sqlite",
    ):
        self._serve = injected_serve
        self._flask = injected_flask
        self._debug_mode = debug_mode
        self._cache = {}
        self._database = Database(database_path)
        self._confidential_database = Database(confidential_database_path)
        self._static_path = "../../static"
        self._app = self.create_application()
        # allowed_origins = [
        #    "http://127.0.0.1:" + str(front_end_port),
        #    "https://micat.bitlabstudio.com",
        #    "https://frontend.micat-project.eu",
        # ]
        CORS(self._app, resources={r"/*": {"origins": "*"}})  # allowed_origins}})

    def start(self, host="127.0.0.1", application_port=8000):
        # if you adapt the port, also consider port forwarding setting in .htaccess
        # file of this project / on web server
        print("Starting flask application at ", host, ":", application_port)
        if self._debug_mode:
            self._app.run(host=host, port=application_port, debug=True)
        else:
            self._serve(self._app, host=host, port=application_port)

    # pylint: disable=too-many-locals
    # pylint: disable=unused-variable
    # pylint: disable=invalid-name
    def create_application(self):
        app = self._flask.Flask(
            __name__,
            static_folder=self._static_path,
            template_folder=self._static_path,
        )

        # Reraise exceptions for easier bug finding, also see
        # https://flask.palletsprojects.com/en/2.0.x/config/#PROPAGATE_EXCEPTIONS
        app.config["PROPAGATE_EXCEPTIONS"] = True

        # For CORS settings / cross-origin access, see function _create_response_from_string

        @app.before_request
        def handle_preflight_options_request():
            # handles preflight OPTIONS requests for "unsafe" requests.
            # Also see
            # https://javascript.info/fetch-crossorigin
            # https://github.com/corydolphin/flask-cors/issues/292#issuecomment-883929183
            if self._flask.request.method.lower() == "options":
                response = self._create_response_from_string("")
                return response
            else:
                return None

        # API routes for id tables

        @app.route("/id_region")
        def id_region():
            table = self._get_table("id_region", self._flask.request)
            return table

        @app.route("/id_subsector")
        def id_subsector():
            return self._get_table("id_subsector", self._flask.request)

        @app.route("/id_action_type")
        def id_action_type():
            return self._get_table("id_action_type", self._flask.request)

        @app.route("/id_final_energy_carrier")
        def id_final_energy_carrier():
            return self._get_table("id_final_energy_carrier", self._flask.request)

        @app.route("/id_indicator_group")
        def id_indicator_group():
            return self._get_table("id_indicator_group", self._flask.request)

        @app.route("/id_indicator")
        def id_indicator():
            return self._get_table("id_indicator", self._flask.request)

        @app.route("/reference_energy_consumption")
        def reference_energy_consumption():
            return self._get_table(
                "fraunhofer_reference_final_energy_consumption",
                self._flask.request,
            )

        # API route for mapping table

        @app.route("/mapping__subsector__action_type")
        def mapping__subsector__action_type():
            return self._get_table(
                "mapping__subsector__action_type", self._flask.request
            )

        # API routes for calculations and templates

        @app.route("/single_description")
        def single_description():
            # Example query:
            # https://micatool-dev.eu/description?key=foo
            request = self._flask.request
            json_or_string_result = descriptions_.description_by_key(request)
            json_string = self._flask.json.dumps(json_or_string_result)
            return self._create_response_from_string(json_string)

        @app.route("/descriptions")
        def descriptions():
            # Example query:
            # https://micatool-dev.eu/descriptions
            json_result = descriptions_.descriptions_as_json()
            json_string = self._flask.json.dumps(json_result)
            return self._create_response_from_string(json_string)

        @app.route("/indicator_data", methods=["POST"])
        def indicator_data():
            # Example query:
            # URL: https://micatool-dev.eu/indicator_data?id_region=2
            # Content-Type: application/json
            # Example content:
            # {
            #   "measures":[
            #     {
            #       "id":1,
            #       "savings":{
            #         "2020":10,
            #         "2025":20,
            #         "2030":30,
            #         "details":{
            #           "parameters":[],
            #           "finalParameters":[],
            #           "constants":[]
            #         },
            #         "id_measure":1,
            #         "id_subsector":1,
            #         "id_action_type":8
            #        },
            #        "parameters":{}
            #      }
            #   ],
            #   "parameters": {}
            # }
            request = self._flask.request
            json_object = calculation.calculate_indicator_data(
                request, self._database, self._confidential_database
            )
            # Create dummy response while developing
            # json_object = _dummy_indicator_data()
            json_string = self._flask.json.dumps(json_object)
            response = self._create_response_from_string(json_string)
            return response

        @app.route("/parameters")
        def parameters():
            # Returns the global parameter template as Excel file.
            # Example query:
            # https://micatool-dev.eu/parameters?id_region=0&file_name=parameters.xlsx
            request = self._flask.request
            parameter_bytes = parameters_template.parameters_template(
                request, self._database
            )
            return self.create_excel_file_response(parameter_bytes, request)

        @app.route("/json_parameters")
        def json_parameters():
            # Returns the global parameter template as json
            # Example query:
            # https://micatool-dev.eu/json_parameters?id_region=0&orient=index
            # allowed_orients = ['split', 'records', 'index', 'columns', 'values', 'table'], also see
            # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html
            # also see
            request = self._flask.request
            parameter_bytes = parameters_template.parameters_template(
                request,
                self._database,
                self._confidential_database,
            )
            return self.create_json_parameters_response(parameter_bytes, request)

        @app.route("/json_measure", methods=["POST"])
        def json_measure():
            # Returns the measure specific parameter template as json; also includes the passed savings.
            # Example query:
            # https://micatool-dev.eu/json_measure?id_region=0&orient=index
            # allowed_orients = ['split', 'records', 'index', 'columns', 'values', 'table'], also see
            # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html
            # Content-Type: application/json
            # Example Content: see measure route

            request = self._flask.request
            return measure_specific_parameters_template.measure_specific_parameters_template(
                request,
                self._database,
                self._confidential_database,
            )

        @app.route("/export-results", methods=["POST"])
        def export_results():
            request = self._flask.request
            data = request.json
            output = io.BytesIO()
            workbook = xlsxwriter.workbook.Workbook(output)

            # ---- Formats ----
            bold = workbook.add_format({"bold": True})
            italic = workbook.add_format({"italic": True, "font_color": "#666666"})
            number_format = workbook.add_format({"num_format": "#,##0.00#######"})
            header_format = workbook.add_format({
                "bold": True, "bg_color": "#0284c7", "font_color": "white", "border": 1,
                "align": "center",
            })
            title_format = workbook.add_format(
                {"bold": True, "font_size": 13, "font_color": "#0c4a6e"}
            )
            subtitle_format = workbook.add_format(
                {"italic": True, "font_color": "#666666"}
            )
            toc_title_format = workbook.add_format(
                {"bold": True, "font_size": 18, "font_color": "#0c4a6e"}
            )
            toc_link_format = workbook.add_format(
                {"font_color": "#0284c7", "underline": True, "font_size": 12}
            )
            toc_section_format = workbook.add_format(
                {"bold": True, "font_size": 12, "bg_color": "#e0f2fe"}
            )
            negative_format = workbook.add_format(
                {"bg_color": "#dcfce7", "font_color": "#166534"}
            )
            positive_format = workbook.add_format(
                {"bg_color": "#fee2e2", "font_color": "#991b1b"}
            )

            workbook.set_properties({
                "title": "MICAT Results Export",
                "subject": "Multiple Impacts Calculation Tool - Results",
                "author": "Fraunhofer ISI",
                "company": "Fraunhofer ISI",
                "comments": "Generated by the MICATool - https://app.micatool.eu",
            })

            # ---- Overview / table of contents (filled in at the end, once all
            # other sheets exist) ----
            toc = workbook.add_worksheet("Overview")
            toc.set_tab_color("#0284c7")
            toc.hide_gridlines(2)
            toc.set_column(0, 0, 45)
            toc.set_column(1, 3, 30)
            toc.merge_range("A1:D1", "MICAT Results Export", toc_title_format)

            region_where_clause = {"id": str(data["region"])}
            region = self._database.table("id_region", region_where_clause)
            region_label = region["label"].values[0]
            program_names = ", ".join(p["name"] for p in data["programs"])
            years_label = (
                f"{min(data['years'])}-{max(data['years'])}" if data["years"] else ""
            )
            toc.write(
                "A2",
                f"{program_names}  ·  Region: {region_label}  ·  Years: {years_label}",
                subtitle_format,
            )
            toc.merge_range("A4:D4", "Jump to a sheet", toc_section_format)
            toc_row = 5
            toc_entries = []

            # ---- Inputs ----
            worksheet = workbook.add_worksheet("Inputs")
            worksheet.set_tab_color("#64748b")
            worksheet.hide_gridlines(2)
            worksheet.set_column(0, 0, 24)
            worksheet.set_column(1, 10, 16)
            toc_entries.append(
                ("Inputs", "Programme configuration and energy savings entered")
            )
            row_idx = 0
            for program in data["programs"]:
                worksheet.write(row_idx, 0, "Program", bold)
                worksheet.write(row_idx, 1, program["name"], bold)
                row_idx += 1
                worksheet.write(row_idx, 0, "Unit")
                worksheet.write(row_idx, 1, program["unitName"], bold)
                row_idx += 1
                worksheet.write(row_idx, 0, "Region")
                worksheet.write(row_idx, 1, region_label, bold)
                row_idx += 1
                worksheet.write(row_idx, 0, "Subsector")
                worksheet.write(
                    row_idx, 1, program.get("subsectorName", program["subsector"]), bold
                )
                row_idx += 2
                for improvement in program["improvements"]:
                    worksheet.write(
                        row_idx, 0, improvement.get("name", improvement["id"]), italic
                    )
                    row_idx += 1
                    col_idx = 0
                    for key, value in improvement["values"].items():
                        worksheet.write(row_idx, col_idx, key, bold)
                        worksheet.write(row_idx + 1, col_idx, value, number_format)
                        col_idx += 1
                    row_idx += 2
                row_idx += 5

            # ---- Outputs: quantification (split by subcategory) and
            # monetisation, each indicator with its own table + chart ----
            for program in data["results"]:
                aggregation_measurements = []
                title_appendix = (
                    f" ({program['name']})" if len(data["results"]) > 1 else ""
                )
                for key, category in data["categories"].items():
                    if key not in ["quantification", "monetization"]:
                        continue
                    subcategories = category.get("subcategories") or [None]
                    for subcategory in subcategories:
                        measurements_in_sheet = [
                            m
                            for m in category["measurements"]
                            if subcategory is None or m.get("subcategory") == subcategory
                        ]
                        if not measurements_in_sheet:
                            continue
                        sheet_base_name = (
                            f"{subcategory}{title_appendix}"
                            if subcategory
                            else f"{category['title']}{title_appendix}"
                        )
                        sheet_name = sheet_base_name[:31]
                        worksheet = workbook.add_worksheet(sheet_name)
                        worksheet.set_tab_color(
                            "#16a34a" if key == "quantification" else "#f97316"
                        )
                        worksheet.hide_gridlines(2)
                        worksheet.set_column(0, 0, 42)
                        worksheet.freeze_panes(1, 1)
                        toc_entries.append((
                            sheet_name,
                            f"{subcategory or category['title']} indicators{title_appendix}",
                        ))

                        row_idx = 0
                        for measurement in measurements_in_sheet:
                            try:
                                result = program["data"][measurement["identifier"]]
                            except KeyError:
                                continue
                            if (
                                key == "monetization"
                                or measurement["identifier"]
                                == "impactOnGrossDomesticProduct"
                            ):
                                aggregation_measurements.append(measurement)
                            if row_idx > 0:
                                row_idx += 1
                            title = measurement["title"]
                            worksheet.write(row_idx, 0, title, title_format)
                            row_idx += 1
                            worksheet.write(row_idx, 0, measurement["yAxis"], italic)
                            row_idx += 1
                            for year_idx, year in enumerate(result["yearColumnNames"]):
                                worksheet.write(row_idx, year_idx + 1, year, header_format)
                            year_header_row = row_idx
                            row_idx += 1
                            col_idx = 0
                            num_years = len(result["yearColumnNames"])
                            total = [0 for _ in result["yearColumnNames"]]
                            data_start_row = row_idx
                            for row in result["rows"]:
                                for idx, entry in enumerate(row):
                                    try:
                                        column_name = result["idColumnNames"][idx]
                                    except IndexError:
                                        if col_idx == 0:
                                            col_idx += 1
                                        worksheet.write(
                                            row_idx, col_idx, entry, number_format
                                        )
                                        total[col_idx - 1] += entry
                                    else:
                                        if column_name == "id_measure":
                                            continue
                                        worksheet.write(
                                            row_idx, col_idx, entry, number_format
                                        )
                                    col_idx += 1
                                row_idx += 1
                                col_idx = 0
                            num_data_rows = len(result["rows"])
                            if num_data_rows > 1:
                                worksheet.write(row_idx, 0, "Total", bold)
                                for idx, entry in enumerate(total):
                                    worksheet.write(
                                        row_idx, idx + 1, entry, number_format
                                    )
                                row_idx += 1

                            if num_years > 0 and num_data_rows > 0:
                                chart_options = {"type": "column"}
                                if num_data_rows > 1:
                                    chart_options["subtype"] = "stacked"
                                chart = workbook.add_chart(chart_options)
                                for r in range(
                                    data_start_row, data_start_row + num_data_rows
                                ):
                                    series = {
                                        "categories": [
                                            sheet_name,
                                            year_header_row,
                                            1,
                                            year_header_row,
                                            num_years,
                                        ],
                                        "values": [sheet_name, r, 1, r, num_years],
                                    }
                                    if num_data_rows > 1:
                                        series["name"] = [sheet_name, r, 0]
                                    else:
                                        series["name"] = title
                                    chart.add_series(series)
                                chart.set_title(
                                    {"name": title, "name_font": {"size": 11}}
                                )
                                chart.set_x_axis({"name": "Year"})
                                chart.set_y_axis({"name": measurement["yAxis"]})
                                chart.set_size({"width": 480, "height": 260})
                                chart.set_legend(
                                    {"position": "bottom"}
                                    if num_data_rows > 1
                                    else {"none": True}
                                )
                                worksheet.insert_chart(row_idx, 0, chart)
                                row_idx += 15

                # ---- Aggregation ----
                aggregation_title = f"Aggregation{title_appendix}"[:31]
                worksheet = workbook.add_worksheet(aggregation_title)
                worksheet.set_tab_color("#f97316")
                worksheet.hide_gridlines(2)
                worksheet.set_column(0, 0, 42)
                worksheet.freeze_panes(1, 1)
                toc_entries.append((
                    aggregation_title,
                    f"Combined view of monetised indicators{title_appendix}",
                ))
                col_idx = 1
                worksheet.write(0, 0, "Indicator", header_format)
                for year in data["years"]:
                    worksheet.write(0, col_idx, year, header_format)
                    col_idx += 1
                row_idx = 1
                for measurement in aggregation_measurements:
                    worksheet.write(row_idx, 0, measurement["title"], bold)
                    result = program["data"][measurement["identifier"]]
                    col_idx = 0
                    for row in result["rows"]:
                        for idx, entry in enumerate(row):
                            try:
                                column_name = result["idColumnNames"][idx]
                            except IndexError:
                                if col_idx == 0:
                                    col_idx += 1
                                worksheet.write(row_idx, col_idx, entry, number_format)
                            else:
                                if column_name == "id_measure":
                                    continue
                                worksheet.write(row_idx, col_idx, entry, number_format)
                            col_idx += 1
                        row_idx += 1
                        col_idx = 0

                num_measurements = len(aggregation_measurements)
                last_col = len(data["years"])
                if num_measurements > 0 and last_col > 0:
                    agg_chart = workbook.add_chart(
                        {"type": "column", "subtype": "stacked"}
                    )
                    for i in range(num_measurements):
                        series_row = i + 1
                        agg_chart.add_series({
                            "name": [aggregation_title, series_row, 0],
                            "categories": [aggregation_title, 0, 1, 0, last_col],
                            "values": [
                                aggregation_title, series_row, 1, series_row, last_col,
                            ],
                        })
                    agg_chart.set_title({"name": aggregation_title})
                    agg_chart.set_x_axis({"name": "Year"})
                    agg_chart.set_y_axis({"name": "Value in EUR"})
                    agg_chart.set_size({"width": 760, "height": 420})
                    agg_chart.set_legend({"position": "bottom"})
                    worksheet.insert_chart(row_idx + 3, 0, agg_chart)

            # ---- CBA ----
            cba_units = {
                "weightedAnnuity": "M-EUR",
                "netPresentValue": "M-EUR",
                "LCOE": "EUR/MWh",
                "LCOCO2": "EUR/tCO2",
                "CBR": "ratio",
                "BCR": "ratio",
            }
            for program in data["cbaData"]:
                cba_title = (
                    f"CBA ({program['name']})" if len(data["results"]) > 1 else "CBA"
                )[:31]
                worksheet = workbook.add_worksheet(cba_title)
                worksheet.set_tab_color("#0284c7")
                worksheet.hide_gridlines(2)
                worksheet.set_column(0, 0, 32)
                worksheet.set_column(1, 1, 22)
                worksheet.set_column(2, 2, 12)
                toc_entries.append((
                    cba_title,
                    "Cost-benefit analysis results"
                    + (f" ({program['name']})" if len(data["results"]) > 1 else ""),
                ))
                row_idx = 0
                worksheet.write(row_idx, 0, "Cost-benefit analysis", title_format)
                row_idx += 2

                list_results = {}
                dict_results = {}
                weighted_annuity_row = None
                for key, result in program.items():
                    if key in ["parameters", "years"]:
                        continue
                    if isinstance(result, list):
                        list_results[key] = result
                        continue
                    if isinstance(result, dict):
                        dict_results[key] = result
                        continue
                    worksheet.write(row_idx, 0, key, bold)
                    worksheet.write(row_idx, 1, result, number_format)
                    worksheet.write(row_idx, 2, cba_units.get(key, "EUR"), italic)
                    if key == "weightedAnnuity":
                        weighted_annuity_row = row_idx
                    row_idx += 1

                if weighted_annuity_row is not None:
                    cell_ref = f"B{weighted_annuity_row + 1}"
                    worksheet.conditional_format(cell_ref, {
                        "type": "cell", "criteria": "<", "value": 0,
                        "format": negative_format,
                    })
                    worksheet.conditional_format(cell_ref, {
                        "type": "cell", "criteria": ">=", "value": 0,
                        "format": positive_format,
                    })

                # Per-year results (e.g. CBR by year)
                if list_results:
                    row_idx += 1
                    worksheet.write(row_idx, 0, "Per-year results", bold)
                    row_idx += 1
                    col_idx = 1
                    for year in program["years"]:
                        worksheet.write(row_idx, col_idx, year, header_format)
                        col_idx += 1
                    for key, result in list_results.items():
                        row_idx += 1
                        worksheet.write(row_idx, 0, key, bold)
                        col_idx = 1
                        for value in result:
                            worksheet.write(row_idx, col_idx, value, number_format)
                            col_idx += 1

                # Indicator annuities: annualised over the measure's lifetime,
                # NOT tied to specific years - kept in a separate section so it
                # is not mistaken for the per-year table above.
                if dict_results:
                    row_idx += 2
                    worksheet.write(
                        row_idx, 0,
                        "Indicator annuities (annualised over the measure's "
                        "lifetime - not per year)",
                        bold,
                    )
                    row_idx += 1
                    for key, result in dict_results.items():
                        worksheet.write(row_idx, 0, key, bold)
                        worksheet.write(row_idx, 2, "EUR", italic)
                        row_idx += 1
                        for sub_key, sub_value in result.items():
                            worksheet.write(row_idx, 0, sub_key)
                            worksheet.write(row_idx, 1, sub_value, number_format)
                            row_idx += 1

                row_idx += 2
                worksheet.write(row_idx, 0, "Parameters", bold)
                row_idx += 1
                for key, value in program["parameters"].items():
                    worksheet.write(row_idx, 0, key, bold)
                    worksheet.write(row_idx, 1, value)
                    row_idx += 1

            # ---- Fill in the Overview jump links now that all sheets exist ----
            for name, description in toc_entries:
                toc.write_url(
                    toc_row, 0, f"internal:'{name}'!A1", toc_link_format,
                    string=f"-> {name}",
                )
                toc.write(toc_row, 1, description, subtitle_format)
                toc_row += 1
            toc_row += 2
            toc.write(
                toc_row, 0,
                "This project has received funding from the European Union's Horizon 2020",
                subtitle_format,
            )
            toc_row += 1
            toc.write(
                toc_row, 0,
                "research and innovation programme. Learn more at micatool.eu",
                subtitle_format,
            )

            workbook.close()
            response = self._flask.make_response(output.getvalue())
            response.headers["Content-Disposition"] = (
                "attachment; filename=MICAT_results.xlsx"
            )
            response.headers["Content-type"] = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            return response

        @app.route("/export-input", methods=["POST"])
        def export_input():
            request = self._flask.request
            data = request.json
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=[
                    "time_frame",
                    "region",
                    "unit",
                    "municipality",
                    "inhabitants",
                    "years",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "time_frame": "ex_ante" if data["future"] else "ex_post",
                    "region": data["region"],
                    "unit": data["unit"],
                    "municipality": data["municipality"],
                    "inhabitants": data["inhabitants"],
                    "years": ",".join(str(y) for y in data["years"]),
                }
            )
            response = self._flask.make_response(output.getvalue())
            response.headers["Content-Disposition"] = (
                "attachment; filename=MICAT_inputs.csv"
            )
            response.headers["Content-type"] = "text/csv"
            return response

        # Deprecated API routes

        @app.route("/savings", methods=["POST"])
        def savings():
            # Example query:
            # https://micatool-dev.eu/savings?id_region=0&
            # &file_name=micat_energy_savings.xlsx'
            # Content-Type: application/json
            # Example Content: [
            #   ["Subsector", "Improvement", 2020, 2025, 2030],
            #   ["Average agriculture", "Cross-cutting technologies", 5000, 4000, 3000],
            #   ["Average agriculture", "Cross-cutting technologies", 10000, 9000, 8000]
            # ]
            request = self._flask.request
            savings_bytes = savings_template.savings_template(request, self._database)
            return self.create_excel_file_response(savings_bytes, request)

        @app.route("/odyssee")
        def get_odyssee_data():
            request = self._flask.request
            ODYSSEE_CATEGORIES = {
                2: "savrescum",  # Household
                3: "savindcum",  # Industry
                4: "savtercum",  # Services
                5: "savtracum",  # Transport
            }
            category = ODYSSEE_CATEGORIES.get(int(request.args.get("category", 2)))
            region = request.args.get("region", "European Unoion")
            start = int(request.args.get("start", "2000"))
            end = int(request.args.get("end", "2022"))
            df = pd.read_csv(
                os.path.join(os.getcwd(), "data/enerdata_odyssee_240911_170909.csv")
            )
            df = df.loc[(df["Item Code"] == category) & (df["Zone Name"] == region)]
            df.sort_values("Year", inplace=True)
            data = {}
            previous_value = 0
            # Deaggregate to get the yearly values
            for year, value in df[["Year", "Value"]].values.tolist():
                data[year] = float(
                    (Decimal(value) - previous_value) * Decimal(1000)
                )  # Convert from mtoe to ktoe
                previous_value = Decimal(value)
            # Filter years
            filtered_data = {
                k: v for k, v in data.items() if int(k) >= start and int(k) <= end
            }
            # Aggregate again
            data = {}
            previous_value = 0
            for year, value in filtered_data.items():
                data[year] = value + previous_value
                previous_value = value + previous_value
            return data

        @app.route("/<path:path>")
        def catch_all(path):
            response = BackEnd._catch_all(path, self._app, self._flask)
            return response

        # There is no guaranty, that this method handles all exceptions.
        # For example, it won't handle HTMLException and there might be
        # further uncaught exceptions. Therefore, the
        # front end still needs to check for html response texts
        # that might occur instead of json and handle it.
        # The purpose of this method is only to provide additional
        # information about the exception.
        @app.errorhandler(Exception)
        def handle_exception(exception):
            response = self._handle_exception(exception)
            return response

        Compress(app)

        # add error handling function as property for easier testing
        app._handle_exception = handle_exception  # pylint: disable=protected-access

        return app

    @staticmethod
    def _parse_request(http_request):
        query_string = http_request.query_string
        query_parameters = dict(parse_qs(query_string.decode()))
        where_clause = {k: v[0] for k, v in query_parameters.items()}
        return where_clause

    @staticmethod
    def _catch_all(path, app, flask):
        if "index.html" in path:
            path = "index.html"

        directory_path = os.path.abspath(app.static_folder)  # Path react build
        absolute_path = os.path.join(directory_path, path)
        if path != "" and os.path.exists(absolute_path):
            # This is used for files existing in 'static' folder (if 'static' is the directory_path)
            return flask.send_from_directory(os.path.join(directory_path), path)
        else:
            # Redirect to out/index.html (if 'out' is the directory_path)
            return flask.send_from_directory(os.path.join(directory_path), "index.html")

    @staticmethod
    def create_json_parameters_response(parameter_bytes, request):
        orient = request.args.get("orient", "records")
        allowed_orients = ["split", "records", "index", "columns", "values", "table"]
        # for the meaning of orients also see
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html
        if orient not in allowed_orients:
            orient = "records"
        df_dict = pd.read_excel(parameter_bytes, sheet_name=None)
        for sheet_name in df_dict:
            df_dict[sheet_name] = json.loads(df_dict[sheet_name].to_json(orient=orient))
        return json.dumps(df_dict, indent=2)

    @staticmethod
    def _exception_to_json(exception):
        class_name = exception.__class__.__qualname__
        stack_trace = traceback.format_exc()
        error = {
            "type": class_name,
            "stackTrace": stack_trace,
        }

        args = exception.args
        if len(args) > 0:
            index = 0
            for arg in args:
                key = "arg" + str(index)
                error[key] = str(arg)
                index += 1
        if hasattr(exception, "name"):
            error["name"] = exception.name
        if hasattr(exception, "description"):
            error["description"] = exception.description
        if hasattr(exception, "code"):
            error["code"] = exception.code

        json_object = {"error": error}
        return json_object

    @staticmethod
    def _log_json_exception(exception_as_json):
        error = exception_as_json["error"]
        logging.error("## Exception occurred while handling request ##")
        logging.error(error["type"])
        logging.error(error["stackTrace"])

    def _get_table(self, table_name, http_request):
        key = table_name + str(http_request.query_string)
        if key in self._cache:
            json_string = self._cache[key]
        else:
            self._empty_cache_if_is_full()
            json_string = self._get_table_directly(table_name, http_request)
            self._cache[key] = json_string

        response = self._create_response_from_string(json_string)
        return response

    def _get_table_directly(self, table_name, http_request):
        where_clause = self._parse_request(http_request)
        query = "SELECT * FROM `" + table_name + "`"
        return self._database.json_string(query, where_clause)

    def _empty_cache_if_is_full(self):
        if len(self._cache.keys()) > 100:
            self._cache = {}

    def _handle_exception(self, exception):
        exception_as_json = self._exception_to_json(exception)
        self._log_json_exception(exception_as_json)

        json_string = self._flask.json.dumps(exception_as_json)
        response = self._create_response_from_string(json_string)
        return response

    def _create_response_from_string(self, json_string):
        response = self._flask.Response(json_string)
        response.content_type = "application/json"
        # Add the list of allowed hosts that are allowed to query the API into the "origins" list.
        # Use '*' if you want to allow all hosts during development or to allow
        # accessing the API for all IPs (perhaps a security issue).
        # Use 'http://127.0.0.1:3000' if you want to restrict the access to the server where the application is hosted.
        # We do not need the extra dependency flask_cors.
        # Also see
        # https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/66
        response.headers.set("Access-Control-Allow-Origin", "*")
        response.headers.set("Content-Type", "application/json")
        response.headers.set(
            "Access-Control-Allow-Methods", "PUT, GET, POST, DELETE, OPTIONS"
        )
        response.headers.set(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.set("Access-Control-Expose-Headers", "*")
        return response

    def create_excel_file_response(self, excel_bytes, request, file_name=None):
        if not file_name:
            file_name = request.args["file_name"]
        output = self._flask.make_response(excel_bytes.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=" + file_name
        output.headers["Content-type"] = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        return output
