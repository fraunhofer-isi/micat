# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
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
            return self._get_table("id_region", self._flask.request)

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

        # API route for mapping table

        @app.route("/mapping__subsector__action_type")
        def mapping__subsector__action_type():
            return self._get_table("mapping__subsector__action_type", self._flask.request)

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
            json_object = calculation.calculate_indicator_data(request, self._database, self._confidential_database)
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
            parameter_bytes = parameters_template.parameters_template(request, self._database)
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
            bold = workbook.add_format({"bold": True})
            italic = workbook.add_format({"italic": True})
            number_format = workbook.add_format({"num_format": "#,##0.00#######"})

            # Inputs
            worksheet = workbook.add_worksheet("Inputs")
            row_idx = 0
            for program in data["programs"]:
                worksheet.write(row_idx, 0, "Program")
                worksheet.write(row_idx, 1, program["name"], bold)
                row_idx += 1
                worksheet.write(row_idx, 0, "Unit")
                worksheet.write(row_idx, 1, program["unitName"], bold)
                row_idx += 1
                worksheet.write(row_idx, 0, "Region")
                where_clause = {"id": str(data["region"])}
                region = self._database.table("id_region", where_clause)
                worksheet.write(row_idx, 1, region["label"].values[0], bold)
                row_idx += 1
                worksheet.write(row_idx, 0, "Subsector")
                worksheet.write(row_idx, 1, program.get("subsectorName", program["subsector"]), bold)
                row_idx += 2
                for improvement in program["improvements"]:
                    worksheet.write(row_idx, 0, improvement.get("name", improvement["id"]), italic)
                    row_idx += 1
                    col_idx = 0
                    for key, value in improvement["values"].items():
                        worksheet.write(row_idx, col_idx, key, bold)
                        worksheet.write(row_idx + 1, col_idx, value, number_format)
                        col_idx += 1
                    row_idx += 2
                row_idx += 5

            # Outputs
            for program in data["results"]:
                aggregation_measurements = []
                title_appendix = f" ({program['name']})" if len(data["results"]) > 1 else ""
                for key, category in data["categories"].items():
                    if key not in ["quantification", "monetization"]:
                        continue
                    worksheet = workbook.add_worksheet(f"{category['title']}{title_appendix}")
                    row_idx = 0
                    for measurement in category["measurements"]:
                        if key == "monetization" or measurement["identifier"] == "impactOnGrossDomesticProduct":
                            aggregation_measurements.append(measurement)
                        if row_idx > 0:
                            row_idx += 1
                        # title
                        title = (
                            f"[{measurement['subcategory']}] {measurement['title']}"
                            if measurement.get("subcategory")
                            else measurement["title"]
                        )
                        worksheet.write(row_idx, 0, title, bold)
                        row_idx += 1
                        # unit
                        worksheet.write(row_idx, 0, measurement["yAxis"], italic)
                        row_idx += 1
                        result = program["data"][measurement["identifier"]]
                        for year_idx, year in enumerate(result["yearColumnNames"]):
                            worksheet.write(row_idx, year_idx + 1, year, bold)
                        row_idx += 1
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
                                    else:
                                        worksheet.write(row_idx, col_idx, entry, number_format)
                                col_idx += 1
                            row_idx += 1
                            col_idx = 0
                        row_idx += 1

                # Aggregation
                worksheet = workbook.add_worksheet(f"Aggregation{title_appendix}")
                col_idx = 1
                for year in data["years"]:
                    worksheet.write(0, col_idx, year, bold)
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
                                else:
                                    worksheet.write(row_idx, col_idx, entry, number_format)
                            col_idx += 1
                        row_idx += 1
                        col_idx = 0

            # CBA
            for program in data["cbaData"]:
                worksheet = workbook.add_worksheet(f"CBA ({program['name']})" if len(data["results"]) > 1 else "CBA")
                row_idx = 0

                # Add unit
                worksheet.write(row_idx, 0, "unit", bold)
                worksheet.write(row_idx, 1, "Euro", italic)
                row_idx += 1

                for key, result in program.items():
                    if key == "parameters":
                        continue
                    worksheet.write(row_idx, 0, key, bold)
                    worksheet.write(row_idx, 1, result, number_format)
                    row_idx += 1

                # Add parameters
                row_idx += 1
                worksheet.write(row_idx, 0, "Parameters", bold)
                row_idx += 1
                for key, value in program["parameters"].items():
                    worksheet.write(row_idx, 0, key, bold)
                    worksheet.write(row_idx, 1, value)
                    row_idx += 1

            # years = cbaData.pop("years")
            # del cbaData["supportingYears"]
            # for key, charts in cbaData.items():
            #     row_idx = 0
            #     worksheet = workbook.add_worksheet(f"CBA - {key}"[:30])
            #     for chart_key, chart in charts.items():
            #         worksheet.write(row_idx, 0, chart_key, bold)
            #         row_idx += 1
            #         col_idx = 1 if key == "marginalCostCurves" else 0
            #         worksheet.write(row_idx, 0, "€", italic)
            #         row_idx += 1
            #         for year in years:
            #             worksheet.write(row_idx, col_idx, year)
            #             col_idx += 1
            #         row_idx += 1
            #         col_idx = 0
            #         for row in chart:
            #             if key == "marginalCostCurves":
            #                 legend = {
            #                     "x": "Totally generated energy savings"
            #                     if chart_key == "marginalEnergySavingsCostCurves"
            #                     else "Totally generated CO2 savings",
            #                     "y": "Totally saved energy savings"
            #                     if chart_key == "marginalEnergySavingsCostCurves"
            #                     else "Totally saved CO2 savings",
            #                 }
            #                 worksheet.write(row_idx, col_idx, legend["x"])
            #                 row_idx += 1
            #                 worksheet.write(row_idx, col_idx, legend["y"])
            #                 row_idx -= 1
            #                 col_idx += 1
            #             for year, value in row["data"].items():
            #                 if key == "marginalCostCurves":
            #                     worksheet.write(row_idx, col_idx, value["x"])
            #                     row_idx += 1
            #                     worksheet.write(row_idx, col_idx, value["y"])
            #                     row_idx -= 1
            #                 else:
            #                     worksheet.write(row_idx, col_idx, value)
            #                 col_idx += 1
            #         row_idx += 2
            workbook.close()
            response = self._flask.make_response(output.getvalue())
            response.headers["Content-Disposition"] = "attachment; filename=MICAT_results.xlsx"
            response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            return response

        @app.route("/export-input", methods=["POST"])
        def export_input():
            request = self._flask.request
            data = request.json
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=["time_frame", "region", "unit", "municipality", "inhabitants", "years"],
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
            response.headers["Content-Disposition"] = "attachment; filename=MICAT_inputs.csv"
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
            df = pd.read_csv(os.path.join(os.getcwd(), "data/enerdata_odyssee_240911_170909.csv"))
            df = df.loc[(df["Item Code"] == category) & (df["Zone Name"] == region)]
            df.sort_values("Year", inplace=True)
            data = {}
            previous_value = 0
            # Deaggregate to get the yearly values
            for year, value in df[["Year", "Value"]].values.tolist():
                data[year] = float((Decimal(value) - previous_value) * Decimal(1000))  # Convert from mtoe to ktoe
                previous_value = Decimal(value)
            # Filter years
            filtered_data = {k: v for k, v in data.items() if int(k) >= start and int(k) <= end}
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
        response.headers.set("Access-Control-Allow-Methods", "PUT, GET, POST, DELETE, OPTIONS")
        response.headers.set("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.set("Access-Control-Expose-Headers", "*")
        return response

    def create_excel_file_response(self, excel_bytes, request, file_name=None):
        if not file_name:
            file_name = request.args["file_name"]
        output = self._flask.make_response(excel_bytes.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=" + file_name
        output.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return output
