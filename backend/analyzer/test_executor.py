import ast
import subprocess
import sys
import tempfile
import os


# =========================================================
# EXECUTE PYTHON TEST CASES
# =========================================================

def execute_python_tests(code):

    results = []

    # =====================================================
    # CHECK SYNTAX
    # =====================================================

    try:

        tree = ast.parse(code)

    except SyntaxError:

        return {
            "success": False,
            "results": [],
            "passed": 0,
            "failed": 0,
            "total": 0,
            "message": "Cannot execute tests because syntax is invalid."
        }


    # =====================================================
    # FIND FIRST FUNCTION
    # =====================================================

    function = None

    for node in tree.body:

        if isinstance(node, ast.FunctionDef):

            function = node
            break


    if function is None:

        return {
            "success": True,
            "results": [],
            "passed": 0,
            "failed": 0,
            "total": 0,
            "message": "No Python function found."
        }


    function_name = function.name

    parameters = []

    for argument in function.args.args:

        parameters.append(argument.arg)


    # =====================================================
    # GENERATE INPUTS
    # =====================================================

    test_inputs = []


    if len(parameters) == 1:

        test_inputs = [

            {
                "type": "Normal Case",
                "values": [5]
            },

            {
                "type": "Zero Case",
                "values": [0]
            },

            {
                "type": "Negative Case",
                "values": [-5]
            },

            {
                "type": "Large Value",
                "values": [100000]
            }

        ]


    elif len(parameters) == 2:

        test_inputs = [

            {
                "type": "Normal Case",
                "values": [10, 5]
            },

            {
                "type": "Zero Case",
                "values": [0, 0]
            },

            {
                "type": "Negative Case",
                "values": [-10, -5]
            },

            {
                "type": "Equal Values",
                "values": [5, 5]
            }

        ]


    else:

        values = []

        for parameter in parameters:

            values.append(5)


        test_inputs = [

            {
                "type": "Normal Case",
                "values": values
            }

        ]


    # =====================================================
    # RUN EACH TEST
    # =====================================================

    for index, test in enumerate(test_inputs):

        values = test["values"]

        arguments = []

        for value in values:

            arguments.append(repr(value))


        arguments_string = ", ".join(arguments)


        # =================================================
        # CREATE TEST RUNNER
        # =================================================

        runner_code = f"""
import json

{code}

try:

    result = {function_name}({arguments_string})

    print(json.dumps({{
        "success": True,
        "result": result
    }}))

except Exception as error:

    print(json.dumps({{
        "success": False,
        "error": str(error)
    }}))
"""


        temp_file = None


        try:

            # =============================================
            # CREATE TEMP FILE
            # =============================================

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8"
            ) as file:

                file.write(runner_code)

                temp_file = file.name


            # =============================================
            # EXECUTE WITH TIME LIMIT
            # =============================================

            process = subprocess.run(

                [
                    sys.executable,
                    temp_file
                ],

                capture_output=True,

                text=True,

                timeout=3

            )


            output = process.stdout.strip()


            # =============================================
            # CHECK RESULT
            # =============================================

            if process.returncode != 0:

                results.append({

                    "test_case":
                        index + 1,

                    "type":
                        test["type"],

                    "status":
                        "FAIL",

                    "input":
                        values,

                    "output":
                        None,

                    "error":
                        process.stderr.strip()
                        or "Program execution failed."

                })

                continue


            try:

                data = __import__(
                    "json"
                ).loads(output)

            except Exception:

                data = None


            if data and data.get("success"):

                results.append({

                    "test_case":
                        index + 1,

                    "type":
                        test["type"],

                    "status":
                        "PASS",

                    "input":
                        values,

                    "output":
                        data.get("result"),

                    "error":
                        None

                })

            else:

                results.append({

                    "test_case":
                        index + 1,

                    "type":
                        test["type"],

                    "status":
                        "FAIL",

                    "input":
                        values,

                    "output":
                        None,

                    "error":
                        data.get("error")
                        if data
                        else "Unknown execution error."

                })


        except subprocess.TimeoutExpired:

            results.append({

                "test_case":
                    index + 1,

                "type":
                    test["type"],

                "status":
                    "FAIL",

                "input":
                    values,

                "output":
                    None,

                "error":
                    "Execution timed out."

            })


        except Exception as error:

            results.append({

                "test_case":
                    index + 1,

                "type":
                    test["type"],

                "status":
                    "FAIL",

                "input":
                    values,

                "output":
                    None,

                "error":
                    str(error)

            })


        finally:

            if temp_file and os.path.exists(temp_file):

                try:

                    os.remove(temp_file)

                except Exception:

                    pass


    # =====================================================
    # COUNT RESULTS
    # =====================================================

    passed = 0
    failed = 0


    for result in results:

        if result["status"] == "PASS":

            passed += 1

        else:

            failed += 1


    # =====================================================
    # RETURN
    # =====================================================

    return {

        "success": True,

        "results": results,

        "passed": passed,

        "failed": failed,

        "total": len(results),

        "message":
            f"{passed}/{len(results)} test cases passed."

    }