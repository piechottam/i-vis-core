"""
API specific methods.
"""
from typing import Any, MutableMapping

import hgvs.parser
from flask import Blueprint, jsonify, request, Response
from flask_login.utils import login_required
from hgvs.enums import ValidationLevel
from sqlalchemy import desc

from ..utils import _AUTOCOMPLETE, _DATATABLE

bp = Blueprint("api", __name__, url_prefix="/api")


# TODO api description
# add swagger description here


# TODO-report
@login_required
@bp.route("/autocomplete/<string:model_name>/<string:column>", methods=["GET", "POST"])
def autocomplete(model_name: str, column: str) -> Response:
    response: MutableMapping[str, Any] = {"found": ()}
    query = request.args.get("q")
    if query is None or len(query) < 3:
        return jsonify(response)

    model_name = model_name.title()
    model_meta = _AUTOCOMPLETE.get(model_name)
    if model_meta is None:
        return jsonify(response)
    cols = model_meta["cols"]
    if column not in cols or model_meta["cols"]():
        return jsonify(response)
    model = model_meta["model"]

    attr = getattr(model, column)
    results = model.query.filter(attr.contains(query))
    response["found"] = tuple(getattr(result, column) for result in results)
    return jsonify(response)


# TODO-report
@login_required
@bp.route("/datatable/<string:query_name>", methods=["GET", "POST"])
def datatable(query_name: str) -> Response:
    query_meta = _DATATABLE.get(query_name)
    if query_meta is None:
        return jsonify({"error": "Unknown query."}), 405
    if not query_meta["callback"]():
        return jsonify({"error": "Permission denied."}), 403

    model = query_meta["model"]
    query = model.query
    total = query.count()
    schema = query_meta["schema"]

    values = request.json
    if values and "columns" in values:
        cols = values["columns"]

        if "order" in values:
            orders = values["order"]
            attrs = []
            for order in orders:
                col_index = order["column"]
                col = cols[col_index]
                if not col["orderable"]:
                    continue

                data = col["data"]
                attr = getattr(model, data)
                if order.get("dir", "asc") == "desc":
                    attr = desc(attr)
                attrs.append(attr)
            if attrs:
                query = query.order_by(*attrs)

        if "start" in values and "length" in values:
            start = values.get("start", 0)
            length = values.get("length", 100)
            query = query.limit(length).offset(start)

    query_desc = query_meta["query_desc"]()
    formatters = {
        col_desc["db"]["data"]: col_desc["db"]["formatter"]
        for col_desc in query_desc
        if "db" in col_desc and "formatter" in col_desc["db"]
    }
    result = query.all()
    data = schema.dump(result, many=True)
    if formatters:
        for row in data:
            for col, formatter in formatters.items():
                row[col] = formatter(row)

    filtered = total

    draw = 0
    if values:
        draw = int(values.get("draw", 0))

    return jsonify(
        {
            "draw": draw + 1,
            "data": data,
            "recordsTotal": total,
            "recordsFiltered": filtered,
        }
    )


# TODO move to api
hgvs_parser = hgvs.parser.Parser()

# TODO move to api
@bp.route("/validate-variants", methods=["GET", "POST"])
def validate_variants() -> Response:
    data = request.get_json()
    if data is None:
        return jsonify({"error": "No variants in request"}), 403

    validated_vars = []
    for var_id, var in enumerate(data.get("variants")):
        parsed = hgvs_parser.parse_hgvs_variant(var)
        validation = tuple(
            obj for obj in parsed.validate() if not isinstance(obj, ValidationLevel)
        )

        validated_var = {
            "id": var_id,
            "var": var,
            "type": parsed.type,
            "validation_info": validation,
            "valid": len(validation) == 0,
        }
        validated_vars.append(validated_var)

    response = {
        "draw": data.get("draw", 0) + 1,
        "validated_variants": validated_vars,
        "recordsTotal": len(validated_vars),
    }

    return jsonify(response)
