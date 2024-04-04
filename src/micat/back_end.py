# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import logging
import os
import traceback
from urllib.parse import parse_qs

import pandas as pd
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

        @app.route("/id_mode")
        def id_mode():
            return self._get_table("id_mode", self._flask.request)

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
            # URL: https://micatool-dev.eu/indicator_data?id_mode=1&id_region=2
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
            # https://micatool-dev.eu/parameters?id_mode=1&id_region=0&file_name=parameters.xlsx
            request = self._flask.request
            parameter_bytes = parameters_template.parameters_template(request, self._database)
            return self.create_excel_file_response(parameter_bytes, request)

        @app.route("/json_parameters")
        def json_parameters():
            # Returns the global parameter template as json
            # Example query:
            # https://micatool-dev.eu/json_parameters?id_mode=1&id_region=0&orient=index
            # allowed_orients = ['split', 'records', 'index', 'columns', 'values', 'table'], also see
            # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html
            # also see
            request = self._flask.request
            parameter_bytes = parameters_template.parameters_template(request, self._database)
            return self.create_json_parameters_response(parameter_bytes, request)

        @app.route("/measure", methods=["POST"])
        def measure():
            # Returns the measure specific parameter template as Excel file; also includes the passed savings.
            # Example query:
            # https://micatool-dev.eu/measure?id_mode=1&id_region=1
            # Content-Type: application/json
            # Example Content:
            # {
            #       "2000": 0,
            #       "2010": 0,
            #       "2015": 0,
            #       "2020": 10,
            #       "2025": 20,
            #       "2030": 30,
            #       "id": 1,
            #       "row_number": 1,
            #       "active": true,
            #       "subsector": {
            #         "id": 1,
            #         "label": "Average agriculture",
            #         "_description": "Agriculture, forestry & fishing"
            #       },
            #       "action_type": {
            #        "id": 8,
            #        "label": "Cross-cutting technologies",
            #        "_description": "Energy-efficient electric cross-cutting technologies"
            #       },
            #       "details": {},
            #       "unit": {
            #         "name": "kilotonne of oil equivalent",
            #         "symbol": "ktoe",
            #         "factor": 1
            #       }
            #  };
            request = self._flask.request
            measure_bytes = measure_specific_parameters_template.measure_specific_parameters_template(
                request,
                self._database,
                self._confidential_database,
            )
            return self.create_excel_file_response(measure_bytes, request, "filename")

        @app.route("/json_measure", methods=["POST"])
        def json_measure():
            # Returns the measure specific parameter template as json; also includes the passed savings.
            # Example query:
            # https://micatool-dev.eu/json_measure?id_mode=1&id_region=0&orient=index
            # allowed_orients = ['split', 'records', 'index', 'columns', 'values', 'table'], also see
            # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html
            # Content-Type: application/json
            # Example Content: see measure route

            request = self._flask.request
            measure_bytes = measure_specific_parameters_template.measure_specific_parameters_template(
                request,
                self._database,
                self._confidential_database,
            )
            return self.create_json_parameters_response(measure_bytes, request)

        # Deprecated API routes

        @app.route("/savings", methods=["POST"])
        def savings():
            # Example query:
            # https://micatool-dev.eu/savings?id_mode=1&id_region=0&
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
