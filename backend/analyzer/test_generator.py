import ast


# =========================================================
# PYTHON TEST CASE GENERATOR
# =========================================================

def generate_test_cases(code):

    test_cases = []


    # =====================================================
    # CHECK SYNTAX
    # =====================================================

    try:

        tree = ast.parse(code)

    except SyntaxError:

        return {
            "success": False,
            "test_cases": [],
            "message":
                "Cannot generate test cases because syntax is invalid."
        }


    # =====================================================
    # FIND FUNCTIONS
    # =====================================================

    functions = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            functions.append(node)


    # =====================================================
    # NO FUNCTION FOUND
    # =====================================================

    if len(functions) == 0:

        return {

            "success": True,

            "test_cases": [],

            "message":
                "No Python function found. "
                "Test generation currently works with functions."

        }


    # =====================================================
    # PROCESS EACH FUNCTION
    # =====================================================

    for function in functions:

        function_name = function.name


        # -------------------------------------------------
        # GET PARAMETERS
        # -------------------------------------------------

        parameters = []

        for argument in function.args.args:

            parameters.append(
                argument.arg
            )


        # =================================================
        # BASIC TEST CASE
        # =================================================

        if len(parameters) == 1:

            parameter = parameters[0]


            test_cases.append({

                "type":
                    "Normal Case",

                "description":
                    "Test with a normal positive value.",

                "input":
                    f"{parameter} = 5",

                "expected":
                    "Function should return the correct result."

            })


            # =================================================
            # ZERO
            # =================================================

            test_cases.append({

                "type":
                    "Zero Case",

                "description":
                    "Test with zero.",

                "input":
                    f"{parameter} = 0",

                "expected":
                    "Function should handle zero correctly."

            })


            # =================================================
            # NEGATIVE
            # =================================================

            test_cases.append({

                "type":
                    "Negative Case",

                "description":
                    "Test with a negative value.",

                "input":
                    f"{parameter} = -5",

                "expected":
                    "Function should handle negative values correctly."

            })


            # =================================================
            # LARGE VALUE
            # =================================================

            test_cases.append({

                "type":
                    "Large Value",

                "description":
                    "Test with a larger input value.",

                "input":
                    f"{parameter} = 100000",

                "expected":
                    "Function should return the correct result without errors."

            })


        # =================================================
        # MULTIPLE PARAMETERS
        # =================================================

        elif len(parameters) == 2:

            first_parameter = parameters[0]

            second_parameter = parameters[1]


            # -------------------------------------------------
            # NORMAL
            # -------------------------------------------------

            test_cases.append({

                "type":
                    "Normal Case",

                "description":
                    "Test with normal input values.",

                "input":
                    f"{first_parameter} = 10, "
                    f"{second_parameter} = 5",

                "expected":
                    "Function should return the correct result."

            })


            # -------------------------------------------------
            # ZERO
            # -------------------------------------------------

            test_cases.append({

                "type":
                    "Zero Case",

                "description":
                    "Test with zero values.",

                "input":
                    f"{first_parameter} = 0, "
                    f"{second_parameter} = 0",

                "expected":
                    "Function should handle zero correctly."

            })


            # -------------------------------------------------
            # NEGATIVE
            # -------------------------------------------------

            test_cases.append({

                "type":
                    "Negative Case",

                "description":
                    "Test with negative values.",

                "input":
                    f"{first_parameter} = -10, "
                    f"{second_parameter} = -5",

                "expected":
                    "Function should handle negative values correctly."

            })


            # -------------------------------------------------
            # SAME VALUES
            # -------------------------------------------------

            test_cases.append({

                "type":
                    "Equal Values",

                "description":
                    "Test with equal input values.",

                "input":
                    f"{first_parameter} = 5, "
                    f"{second_parameter} = 5",

                "expected":
                    "Function should correctly handle equal values."

            })


        # =================================================
        # MORE THAN 2 PARAMETERS
        # =================================================

        else:

            input_values = []

            for parameter in parameters:

                input_values.append(
                    f"{parameter} = 5"
                )


            test_cases.append({

                "type":
                    "Normal Case",

                "description":
                    "Test with normal input values.",

                "input":
                    ", ".join(input_values),

                "expected":
                    "Function should return the correct result."

            })


    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {

        "success":
            True,

        "test_cases":
            test_cases,

        "message":
            f"{len(test_cases)} test cases generated."

    }