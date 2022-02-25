import collections
import operator
import re
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse


app = FastAPI()
HISTORY_SPAN = 3
OPERATIONS = {
    "-": operator.sub,
    "+": operator.add,
    "/": operator.truediv,
    "*": operator.mul,
    }
context = "Test calculator"
storage = collections.deque([], HISTORY_SPAN)


def make_num(string):
    try:
        return int(string)
    except ValueError:
        return float(string)


def calc_recursive(expression):
    if len(expression) == 1:
        return expression
    else:
        operation = OPERATIONS.get(expression[1], None)
        result = [operation(expression[0], expression[2])]
        result.extend(expression[3:])
        return calc_recursive(result)


@app.get("/")
async def user_handle():
    return {context}


@app.get("/calc/")
async def calc(input: str):
    expression = re.findall(r'[0-9\.]+|[^0-9\.]+', input)
    expression = [i.strip(' ') for i in expression]

    if expression[0] == "+":
        expression = expression[1:]
    elif expression[0] == "-":
        expression[1] = make_num(expression[1]) * -1
        expression = expression[1:]

    for i in range(0, len(expression), 2):
        try:
            expression[i] = make_num(expression[i])
        except ValueError:
            failed_response = {"request": input, "response": "", "status": "fail"}
            storage.append(failed_response)
            raise HTTPException(status_code=400, detail="Invalid expression")

    try:
        result = round(calc_recursive(expression)[0], 3)
        response = {"request": input, "response": result, "status": "success"}
        storage.append(response)
        return response
    except Exception as e:
        response = {"request": input, "response": "", "status": "fail"}
        storage.append(response)
        return response


@app.get("/history/")
async def history(limit: Optional[int] = None, status: Optional[str] = None):
    if limit is None:
        size = len(storage)
    else:
        if limit >= 1 and limit <= HISTORY_SPAN:
            size = min(limit, len(storage))
        else:
            raise HTTPException(status_code=400, detail="Invalid limit")

    if status is None:
        response = [i for i in storage]
    elif status in ("success", "fail"):
        response = [i for i in storage if i["status"] == status]
    else:
        raise HTTPException(status_code=400, detail="Invalid status")

    return response[:size]
