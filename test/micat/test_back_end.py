# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import json
import logging
import os
from io import BytesIO

import flask
import pytest
from mock import MagicMock as OriginalMagicMock
from werkzeug.exceptions import HTTPException

from micat import back_end
from micat.back_end import BackEnd
from micat.calculation import calculation
from micat.description import descriptions
from micat.template import (
    measure_specific_parameters_template,
    parameters_template,
    savings_template,
)
from micat.test_utils.isi_mock import MagicMock, patch, patch_by_string

APP_REQUEST_CONTEXT = None

MOCKED_SERVE_ARGS = None


def mocked_serve(app_to_serve, host, port):
    global MOCKED_SERVE_ARGS  # pylint: disable=global-statement
    MOCKED_SERVE_ARGS = {
        "app": app_to_serve,
        "host": host,
        "port": port,
    }


def get_mocked_response():
    mocked_response = OriginalMagicMock()
    mocked_response.headers = {}
    return mocked_response


class HttpRequestMock:
    def __init__(self):
        self.query_string = "queryStringMock"


def assert_unique_data_query(back_end_instance, client):
    response = client.get("/unique_data", query_string={"query_parameter": "value"})
    assert response.status_code == 200
    # noinspection PyProtectedMember
    args = back_end_instance._get_unique_data.mock_calls[0].args
    request = args[0]
    assert request.query_string == b"query_parameter=value"


def assert_table_query(back_end_instance, client, identifier, internal_identifier=None):
    response = client.get("/" + identifier, query_string={"query_parameter": "value"})
    assert response.status_code == 200
    # noinspection PyProtectedMember
    args = back_end_instance._get_table.mock_calls[0].args
    passed_identifier = args[0]
    if not internal_identifier:
        internal_identifier = identifier
    assert passed_identifier == internal_identifier


@pytest.fixture(name="injected_flask")
def fixture_injected_flask():
    return flask  # we use actual flask to be able to run queries


@pytest.fixture(name="sut")
def fixture_sut(injected_flask):
    sut = BackEnd(mocked_serve, injected_flask, False, "../../front_end", "../../import_confidential/public.sqlite")
    sut._get_table = MagicMock(return_value="result")
    return sut


@pytest.fixture(name="unaltered_sut")
def fixture_unaltered_sut(injected_flask):
    sut = BackEnd(mocked_serve, injected_flask, False, "../../front_end", "../../import_confidential/public.sqlite")
    return sut


@pytest.fixture(name="app")
def fixture_app(sut):
    app = sut.create_application()
    return app


@pytest.fixture(name="client")
def fixture_client(app):
    with app.app_context():
        with app.test_request_context():
            app.config["TESTING"] = True
            return app.test_client()


class TestPublicApi:
    def test_construction(self, sut):
        # noinspection PyProtectedMember
        assert sut._cache == {}

    def test_start(self, sut):
        sut._debug_mode = False
        sut._serve = MagicMock()
        sut.start()
        assert sut._serve.called is True

    def test_start_debug(self, sut):
        sut._debug_mode = True
        mocked_app = MagicMock()
        mocked_app.run = MagicMock()
        sut._app = mocked_app
        sut.start()
        assert mocked_app.run.called is True

    class TestCreateApplication:
        def test_config(self, app):
            assert app.config["PROPAGATE_EXCEPTIONS"] is True

        def test_handle_preflight_options_request(self, sut, client):  # pylint: disable=unused-argument
            response = client.options(
                "/id_mode",
                query_string={
                    "query_parameter": "value",
                },
            )
            assert response.status_code == 200

        def test_id_mode(self, sut, client):
            assert_table_query(sut, client, "id_mode")

        def test_id_region(self, sut, client):
            assert_table_query(sut, client, "id_region")

        def test_id_subsector(self, sut, client):
            assert_table_query(sut, client, "id_subsector")

        def test_id_indicator(self, sut, client):
            assert_table_query(sut, client, "id_indicator")

        def test_id_indicator_group(self, sut, client):
            assert_table_query(sut, client, "id_indicator_group")

        def test_id_action_type(self, sut, client):
            assert_table_query(sut, client, "id_action_type")

        def test_id_final_energy_carrier(self, sut, client):
            assert_table_query(sut, client, "id_final_energy_carrier")

        def test_mapping__subsector__action_type(self, sut, client):
            assert_table_query(sut, client, "mapping__subsector__action_type")

        @patch(descriptions.description_by_key)
        def test_single_description(self, sut, client):
            sut._flask = MagicMock()
            sut._flask.json = MagicMock()
            sut._flask.json.dumps = MagicMock()
            sut._create_response_from_string = MagicMock(return_value="mocked_response")
            response = client.get("/single_description")
            assert response.text == "mocked_response"

        @patch(descriptions.descriptions_as_json)
        def test_descriptions(self, sut, client):
            sut._flask = MagicMock()
            sut._flask.json = MagicMock()
            sut._flask.json.dumps = MagicMock()
            sut._create_response_from_string = MagicMock(return_value="mocked_response")
            response = client.get("/descriptions")
            assert response.text == "mocked_response"

        class TestIndicatorData:
            @patch(calculation.calculate_indicator_data, "mocked_indicator_data")
            def test_without_error(self, client):
                response = client.post("/indicator_data")
                assert response.text == '"mocked_indicator_data"'

            # noinspection PyMethodParameters
            def mocked_calculate_indicator_data(  # pylint: disable=no-self-argument
                request,
                database,
                confidential_database,
            ):
                raise AttributeError("mocked_error")

        class TestParameter:
            @patch(
                parameters_template.parameters_template,
                "mocked_parameters_bytes",
            )
            @patch(back_end.BackEnd.create_excel_file_response, "mocked_excel_file")
            def test_parameter(self, client):
                response = client.get("/parameters")
                assert response.text == "mocked_excel_file"

        class TestJsonParameters:
            @patch(
                parameters_template.parameters_template,
                "mocked_parameters_bytes",
            )
            @patch(back_end.BackEnd.create_json_parameters_response, "mocked_json")
            def test_json_parameters(self, client):
                response = client.get("json_parameters")
                assert response.text == "mocked_json"

        class TestSavings:
            @patch(
                savings_template.savings_template,
                "mocked_savings_bytes",
            )
            @patch(
                back_end.BackEnd.create_excel_file_response,
                "mocked_excel_file",
            )
            def test_savings(self, client):
                response = client.post("/savings")
                assert response.text == "mocked_excel_file"

        @patch(
            measure_specific_parameters_template.measure_specific_parameters_template,
            "mocked_measure_specific_parameters_bytes",
        )
        def test_json_measure(self, client):
            response = client.post("json_measure")
            assert response.text == "mocked_measure_specific_parameters_bytes"

        @patch(
            back_end.BackEnd._catch_all,
            "mocked_catch_all_response_text",
        )
        def test_non_existing_url(self, client):
            response = client.get("/non_exiting_url")
            assert response.text == "mocked_catch_all_response_text"

        class TestCreateJsonParametersResponse:
            class MockedRequest:
                args = {"orient": "records"}

            class MockedDataFrame:
                # pylint: disable=unused-argument
                @staticmethod
                def to_json(orient):
                    return "mocked_json"

            mocked_sheet_to_df_map = {
                "mocked_sheet_1": MockedDataFrame,
                "mocked_sheet_2": MockedDataFrame,
            }

            @patch(json.dumps, "mocked_json")
            @patch_by_string("pandas.read_excel", mocked_sheet_to_df_map)
            @patch_by_string("pandas.DataFrame.to_json", "mocked_json")
            @patch_by_string("json.loads", MockedDataFrame)
            @patch(json.dumps, "mocked_json")
            def test_create_json_parameters_response(self, sut):
                result = sut.create_json_parameters_response("mocked_parameter_bytes", self.MockedRequest)
                assert result == "mocked_json"
                self.MockedRequest.args["orient"] = "wrong_orient"
                result = sut.create_json_parameters_response("mocked_parameter_bytes", self.MockedRequest)
                assert result == "mocked_json"

        @patch(back_end.BackEnd._handle_exception, "mocked_exception_response")
        def test_handle_exception(self, app):
            response = app._handle_exception("mocked_exception")
            assert response == "mocked_exception_response"

        class TestCatchAll:
            @patch(os.path.exists, True)
            def test_path_exists(self, client):
                response = client.get("/id_region")
                assert response.data == b"result"


class TestPrivateApi:
    class TestCatchAll:
        @patch_by_string("os.path.exists", False)
        def test_including_index(self, unaltered_sut):
            app_mock = MagicMock()
            flask_mock = MagicMock()
            flask_mock.send_from_directory = MagicMock(return_value="mocked_result")

            path = "/foo/baa/index.html"
            # noinspection PyProtectedMember
            response = unaltered_sut._catch_all(path, app_mock, flask_mock)
            assert response == "mocked_result"

        @patch_by_string("os.path.exists", True)
        def test_existing_path(self, unaltered_sut):
            app_mock = MagicMock()
            flask_mock = MagicMock()
            flask_mock.send_from_directory = MagicMock(return_value="mocked_result")

            path = "/foo/baa/index.html"
            # noinspection PyProtectedMember
            response = unaltered_sut._catch_all(path, app_mock, flask_mock)
            assert response == "mocked_result"

    class TestGetTable:
        @patch(back_end.BackEnd._create_response_from_string, "mocked_response")
        def test_is_in_cache(self, unaltered_sut):
            table_name = "tableNameMock"
            http_request = HttpRequestMock()
            unaltered_sut._cache["tableNameMockqueryStringMock"] = "mocked_query_result"
            response = unaltered_sut._get_table(table_name, http_request)
            assert response == "mocked_response"

        @patch(back_end.BackEnd._empty_cache_if_is_full, MagicMock())
        @patch(back_end.BackEnd._get_table_directly, "mocked_json_string")
        @patch(back_end.BackEnd._create_response_from_string, "mocked_response")
        def test_is_not_in_cache(self, unaltered_sut):
            table_name = "tableNameMock"
            http_request = HttpRequestMock()
            unaltered_sut._cache = {}
            response = unaltered_sut._get_table(table_name, http_request)
            assert response == "mocked_response"

    @patch(back_end.BackEnd._parse_request, "where_clause_mock")
    def test_get_table_directly(self, unaltered_sut):
        table_name = "foo"
        http_request = "http_request_mock"

        class DatabaseMock:
            def __init__(self):
                self.passed_query = None
                self.where_clause = None

            def json_string(self, query, where_clause):
                self.passed_query = query
                self.where_clause = where_clause
                return "mocked_query_result"

        mocked_database = DatabaseMock()
        unaltered_sut._database = mocked_database

        # noinspection PyProtectedMember
        response = unaltered_sut._get_table_directly(table_name, http_request)
        assert response == "mocked_query_result"

    class TestEmptyCacheIfIsFull:
        def test_cache_is_full(self, sut):
            cache = {}
            for index in range(0, 110):
                cache["key" + str(index)] = "foo"
            sut._cache = cache
            sut._empty_cache_if_is_full()

            assert len(sut._cache.keys()) == 0

        def test_cache_is_not_full(self, sut):
            sut._cache["key"] = "foo"
            sut._empty_cache_if_is_full()
            assert sut._cache["key"] == "foo"

    def test_parse_request(self, sut):
        class AnotherHttpRequestMock:
            query_string = b'data_set="geo"&query_parameter="value"'

        http_request_mock = AnotherHttpRequestMock()
        where_clause = sut._parse_request(http_request_mock)
        assert where_clause["data_set"] == '"geo"'
        assert where_clause["query_parameter"] == '"value"'

    @patch(back_end.BackEnd._exception_to_json, "mocked_json_exception")
    @patch(back_end.BackEnd._log_json_exception)
    @patch(back_end.BackEnd._create_response_from_string, "mocked_response")
    def test_handle_exception(self, unaltered_sut):
        mocked_exception = HTTPException("my exception")
        response = unaltered_sut._handle_exception(mocked_exception)
        assert response == "mocked_response"

    class TestExceptionToJson:
        def test_with_http_exception(self, unaltered_sut):
            exception = HTTPException("my exception")
            json_result = unaltered_sut._exception_to_json(exception)
            error = json_result["error"]
            assert error["type"] == "HTTPException"
            assert error["description"] == "my exception"

        def test_with_attribute_error(self, unaltered_sut):
            exception = AttributeError("my error")
            json_result = unaltered_sut._exception_to_json(exception)
            error = json_result["error"]
            assert error["type"] == "AttributeError"
            assert error["arg0"] == "my error"

    def test_log_json_exception(self, unaltered_sut):
        exception_as_json = {
            "error": {
                "type": "mocked_type",
                "stackTrace": "mocked_stack_trace",
            },
        }
        with patch(logging.error) as mocked_logging_error:
            unaltered_sut._log_json_exception(exception_as_json)
            assert mocked_logging_error.has_been_called()

    def test_create_response_from_string(self, unaltered_sut):
        response = unaltered_sut._create_response_from_string("mocked_json_string")
        assert response.content_type == "application/json"
        assert response.data == b"mocked_json_string"

    def test_create_excel_file_response(self, unaltered_sut):
        mocked_request = OriginalMagicMock()
        mocked_request.args = {
            "file_name": "mocked_file_name.xlsx",
        }
        unaltered_sut._flask = MagicMock()
        unaltered_sut._flask.make_response = OriginalMagicMock(return_value=get_mocked_response())
        response = unaltered_sut.create_excel_file_response(BytesIO(), mocked_request)
        assert "mocked_file_name" in response.headers["Content-Disposition"]
