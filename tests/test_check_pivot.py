import pytest
from copy import deepcopy
from utils import Identity, Mutation, try_exercise, compose, Deletion, Addition

# Fixtures
@pytest.fixture()
def pivot_tables():
    return [
        [
            {
                "source": {
                    "startRowIndex": 0,
                    "endRowIndex": 613,
                    "startColumnIndex": 0,
                    "endColumnIndex": 5,
                },
                "rows": [{"showTotals": True, "sortOrder": "ASCENDING"}],
                "columns": [
                    {
                        "sourceColumnOffset": 2,
                        "showTotals": True,
                        "sortOrder": "ASCENDING",
                    }
                ],
                "values": [
                    {
                        "sourceColumnOffset": 4,
                        "summarizeFunction": "SUM",
                        "calculatedDisplayType": "PERCENT_OF_ROW_TOTAL",
                    }
                ],
                "criteria": {
                    "0": {
                        "visibleValues": [
                            "01-Jan",
                            "02-Feb",
                            "03-Mar",
                            "04-Apr",
                            "05-May",
                            "06-Jun",
                            "07-Jul",
                            "08-Aug",
                            "09-Sep",
                            "10-Oct",
                        ]
                    }
                },
            }
        ]
    ]


@pytest.fixture()
def pivot_tables_two_values():
    return [
        [
            {
                "source": {
                    "startRowIndex": 0,
                    "endRowIndex": 613,
                    "startColumnIndex": 0,
                    "endColumnIndex": 5,
                },
                "rows": [],
                "values": [
                    {"sourceColumnOffset": 3, "summarizeFunction": "MAX"},
                    {"sourceColumnOffset": 4, "summarizeFunction": "MAX"},
                ],
                "criteria": {
                    "0": {
                        "visibleValues": [
                            "01-Jan",
                            "02-Feb",
                            "03-Mar",
                            "04-Apr",
                            "05-May",
                            "06-Jun",
                            "07-Jul",
                            "08-Aug",
                            "09-Sep",
                            "10-Oct",
                        ]
                    }
                },
            }
        ]
    ]


@pytest.fixture()
def solution_data(pivot_tables):
    return {
        "values": [[1, 1, 1], [1, 52, 8]],
        "formulas": [["=0+1", 1, 1], ["=1+0", "=52", 8]],
        "pivotTables": pivot_tables,
    }


@pytest.fixture()
def solution_data_two_values(pivot_tables_two_values):
    return {
        "values": [[1, 1, 1], [1, 52, 8]],
        "formulas": [["=0+1", 1, 1], ["=1+0", "=52", 8]],
        "pivotTables": pivot_tables_two_values,
    }


# Tests
@pytest.mark.parametrize(
    "trans, sct_range, correct, message_contains",
    [
        (Identity(), "A1", True, None),
        (
            Mutation(["pivotTables", 0, 0, "source", "startRowIndex"], 1),
            "A1",
            False,
            ["`1` mistake", "source data"],
        ),
        (
            Mutation(["pivotTables", 0, 0, "source", "endRowIndex"], 1),
            "A1",
            False,
            ["`1` mistake", "source data"],
        ),
        (
            Mutation(["pivotTables", 0, 0, "source", "startColumnIndex"], 1),
            "A1",
            False,
            ["`1` mistake", "source data"],
        ),
        (
            Mutation(["pivotTables", 0, 0, "source", "endColumnIndex"], 1),
            "A1",
            False,
            ["`1` mistake", "source data"],
        ),
        (
            Mutation(["pivotTables", 0, 0, "source", "startRowIndex"], 1),
            "B1",
            True,
            None,
        ),
        (
            Mutation(["pivotTables", 0, 0, "rows", 0, "sortOrder"], "DESCENDING"),
            "A1",
            False,
            ["`1` mistake", "sorting order"],
        ),
        (
            Deletion(["pivotTables", 0, 0, "rows"]),
            "A1",
            False,
            ["`1` mistake", "define", "any rows"],
        ),
        (
            Deletion(["pivotTables", 0, 0, "columns"]),
            "A1",
            False,
            ["`1` mistake", "define", "any columns"],
        ),
        (
            Deletion(["pivotTables", 0, 0, "criteria"]),
            "A1",
            False,
            ["`1` mistake", "define", "any filter"],
        ),
        (
            Mutation(
                ["pivotTables", 0, 0, "columns", 0, "valueBucket"],
                {"buckets": [{"stringValue": "01-Jan"}]},
            ),
            "A1",
            False,
            ["`1` mistake", "sort", "correct value"],
        ),
        (
            Mutation(["pivotTables", 0, 0, "columns", 0, "sourceColumnOffset"], 1),
            "A1",
            False,
            ["`1` mistake", "column", "use the correct field"],
        ),
        (
            Mutation(
                ["pivotTables", 0, 0, "values", 0, "summarizeFunction"], "AVERAGE"
            ),
            "A1",
            False,
            [
                "`1` mistake",
                "summarize function",
                "1st value",
                "Expected `SUM`",
                "got `AVERAGE`",
            ],
        ),
        (
            Mutation(["pivotTables", 0, 0, "columns", 0, "name"], "test"),
            "A1",
            False,
            ["`1` mistake", "Don't give", "1st column", "a name"],
        ),
        (
            Deletion(["pivotTables", 0, 0, "columns", 0, "showTotals"]),
            "A1",
            False,
            ["`1` mistake", "show the totals"],
        ),
        (
            Deletion(["pivotTables", 0, 0, "values", 0, "calculatedDisplayType"]),
            "A1",
            False,
            ["`1` mistake", "% of row", "the default"],
        ),
        (
            Addition(
                ["pivotTables", 0, 0, "rows"],
                {"showTotals": True, "sortOrder": "ASCENDING"},
            ),
            "A1",
            False,
            ["`1` mistake", "too many rows", "remove the 2nd row"],
        ),
    ],
)
def test_check_pivots(solution_data, trans, sct_range, correct, message_contains):
    user_data = trans(deepcopy(solution_data))
    sct = [{"range": sct_range, "sct": ["check_pivot"]}]
    result = try_exercise(solution_data, user_data, sct)

    assert result.get("success") == correct
    if message_contains is not None:
        assert result.get("message") is not None
        message = result.get("message")
        if isinstance(message_contains, list):
            assert all([x in message for x in message_contains])
        else:
            assert message_contains in message


@pytest.mark.parametrize(
    "trans, sct_range, correct, message_contains",
    [
        (Identity(), "A1", True, None),
        (
            Deletion(["pivotTables", 0, 0, "values", 1]),
            "A1",
            False,
            ["`1` mistake", "defined enough"],
        ),
        (
            Addition(
                ["pivotTables", 0, 0, "rows"],
                {"showTotals": True, "sortOrder": "ASCENDING"},
            ),
            "A1",
            False,
            ["`1` mistake", "too many rows"],
        ),
        (
            Mutation(
                ["pivotTables", 0, 0, "columns"],
                [{"showTotals": True, "sortOrder": "ASCENDING"}],
            ),
            "A1",
            False,
            ["`1` mistake", "don't have to define any columns"],
        ),
    ],
)
def test_check_pivots_two_values(
    solution_data_two_values, trans, sct_range, correct, message_contains
):
    user_data = trans(deepcopy(solution_data_two_values))
    sct = [{"range": sct_range, "sct": ["check_pivot"]}]
    result = try_exercise(solution_data_two_values, user_data, sct)

    assert result.get("success") == correct
    if message_contains is not None:
        assert result.get("message") is not None
        message = result.get("message")
        if isinstance(message_contains, list):
            assert all([x in message for x in message_contains])
        else:
            assert message_contains in message