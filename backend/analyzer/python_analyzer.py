import ast


# =========================================================
# COMPLEXITY ANALYZER
# =========================================================

def calculate_complexity(tree):

    max_loop_depth = 0

    recursive_functions = set()


    # -----------------------------------------------------
    # Find maximum nested loop depth
    # -----------------------------------------------------

    def check_node(node, depth):

        nonlocal max_loop_depth

        if isinstance(node, (ast.For, ast.While)):

            depth += 1

            max_loop_depth = max(
                max_loop_depth,
                depth
            )

        for child in ast.iter_child_nodes(node):

            check_node(child, depth)


    check_node(tree, 0)


    # -----------------------------------------------------
    # Detect recursion
    # -----------------------------------------------------

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            function_name = node.name

            for child in ast.walk(node):

                if isinstance(child, ast.Call):

                    if (
                        isinstance(child.func, ast.Name)
                        and child.func.id == function_name
                    ):

                        recursive_functions.add(
                            function_name
                        )


    # -----------------------------------------------------
    # Time Complexity
    # -----------------------------------------------------

    if len(recursive_functions) > 0:

        time_complexity = "Recursive"

        complexity_reason = (
            "Recursive function detected. "
            "Exact complexity depends on the recurrence."
        )


    elif max_loop_depth == 0:

        time_complexity = "O(1)"

        complexity_reason = (
            "No loops or recursion detected."
        )


    elif max_loop_depth == 1:

        time_complexity = "O(n)"

        complexity_reason = (
            "Single loop detected."
        )


    elif max_loop_depth == 2:

        time_complexity = "O(n²)"

        complexity_reason = (
            "Two nested loops detected."
        )


    elif max_loop_depth == 3:

        time_complexity = "O(n³)"

        complexity_reason = (
            "Three nested loops detected."
        )


    else:

        time_complexity = f"O(n^{max_loop_depth})"

        complexity_reason = (
            f"{max_loop_depth} levels of nested loops detected."
        )


    # -----------------------------------------------------
    # Space Complexity
    # -----------------------------------------------------

    space_complexity = "O(1)"

    space_reason = (
        "No obvious growing data structure detected."
    )


    for node in ast.walk(tree):

        # list allocation
        if isinstance(node, ast.List):

            space_complexity = "O(n)"

            space_reason = (
                "List allocation detected."
            )


        # dictionary allocation
        elif isinstance(node, ast.Dict):

            space_complexity = "O(n)"

            space_reason = (
                "Dictionary allocation detected."
            )


        # list(), dict(), set()
        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                if node.func.id in [
                    "list",
                    "dict",
                    "set"
                ]:

                    space_complexity = "O(n)"

                    space_reason = (
                        "Growing data structure detected."
                    )


    return {

        "time": time_complexity,

        "space": space_complexity,

        "reason": complexity_reason,

        "space_reason": space_reason

    }


# =========================================================
# PYTHON CODE ANALYZER
# =========================================================

def analyze_python_code(code):

    result = {

        "syntax": {

            "valid": True,

            "error": None

        },

        "bugs": [],

        "complexity": {

            "time": "O(1)",

            "space": "O(1)",

            "reason": "",

            "space_reason": ""

        },

        "suggestions": []

    }


    # =====================================================
    # SYNTAX CHECK
    # =====================================================

    try:

        tree = ast.parse(code)

    except SyntaxError as error:

        result["syntax"] = {

            "valid": False,

            "error": {

                "message": error.msg,

                "line": error.lineno,

                "column": error.offset

            }

        }

        return result


    # =====================================================
    # DEFINED VARIABLES
    # =====================================================

    defined_variables = set()


    built_in_names = {

        "print",
        "len",
        "range",
        "str",
        "int",
        "float",
        "list",
        "dict",
        "set",
        "tuple",
        "bool",
        "input",
        "sum",
        "max",
        "min",
        "abs",
        "enumerate",
        "zip",
        "open",

        # Security-related names
        "eval",
        "exec",
        "os",
        "pickle"

    }


    # =====================================================
    # COLLECT DEFINITIONS
    # =====================================================

    for node in ast.walk(tree):

        # -------------------------------------------------
        # Normal assignment
        # -------------------------------------------------

        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name):

                    defined_variables.add(
                        target.id
                    )

                elif isinstance(target, (ast.Tuple, ast.List)):

                    for element in target.elts:

                        if isinstance(
                            element,
                            ast.Name
                        ):

                            defined_variables.add(
                                element.id
                            )


        # -------------------------------------------------
        # Annotated assignment
        # -------------------------------------------------

        elif isinstance(node, ast.AnnAssign):

            if isinstance(
                node.target,
                ast.Name
            ):

                defined_variables.add(
                    node.target.id
                )


        # -------------------------------------------------
        # Augmented assignment
        # -------------------------------------------------

        elif isinstance(node, ast.AugAssign):

            if isinstance(
                node.target,
                ast.Name
            ):

                defined_variables.add(
                    node.target.id
                )


        # -------------------------------------------------
        # For loop variable
        # -------------------------------------------------

        elif isinstance(node, ast.For):

            if isinstance(
                node.target,
                ast.Name
            ):

                defined_variables.add(
                    node.target.id
                )

            elif isinstance(
                node.target,
                (ast.Tuple, ast.List)
            ):

                for element in node.target.elts:

                    if isinstance(
                        element,
                        ast.Name
                    ):

                        defined_variables.add(
                            element.id
                        )


        # -------------------------------------------------
        # Function definition
        # -------------------------------------------------

        elif isinstance(node, ast.FunctionDef):

            defined_variables.add(
                node.name
            )

            for argument in node.args.args:

                defined_variables.add(
                    argument.arg
                )


        # -------------------------------------------------
        # Async function
        # -------------------------------------------------

        elif isinstance(node, ast.AsyncFunctionDef):

            defined_variables.add(
                node.name
            )

            for argument in node.args.args:

                defined_variables.add(
                    argument.arg
                )


        # -------------------------------------------------
        # Import
        # -------------------------------------------------

        elif isinstance(node, ast.Import):

            for alias in node.names:

                if alias.asname:

                    defined_variables.add(
                        alias.asname
                    )

                else:

                    defined_variables.add(
                        alias.name.split(".")[0]
                    )


        # -------------------------------------------------
        # From import
        # -------------------------------------------------

        elif isinstance(node, ast.ImportFrom):

            for alias in node.names:

                if alias.asname:

                    defined_variables.add(
                        alias.asname
                    )

                else:

                    defined_variables.add(
                        alias.name
                    )


    # =====================================================
    # FIND UNDEFINED VARIABLES
    # =====================================================

    for node in ast.walk(tree):

        if isinstance(node, ast.Name):

            if isinstance(node.ctx, ast.Load):

                variable = node.id


                if (
                    variable not in defined_variables
                    and variable not in built_in_names
                ):

                    already_exists = False


                    for bug in result["bugs"]:

                        if (
                            bug["variable"] == variable
                            and bug["line"] == node.lineno
                        ):

                            already_exists = True


                    if not already_exists:

                        result["bugs"].append({

                            "type":
                                "Possible Undefined Variable",

                            "variable":
                                variable,

                            "line":
                                node.lineno,

                            "message":
                                f"'{variable}' is used before being defined."

                        })


    # =====================================================
    # COMPLEXITY
    # =====================================================

    result["complexity"] = calculate_complexity(
        tree
    )


    # =====================================================
    # SUGGESTIONS
    # =====================================================

    if len(result["bugs"]) == 0:

        result["suggestions"].append(
            "No obvious undefined-variable issues detected."
        )


    if result["complexity"]["time"] in [
        "O(n²)",
        "O(n³)"
    ]:

        result["suggestions"].append(
            "Nested loops detected. Look for ways to reduce unnecessary iterations."
        )


    if result["complexity"]["time"].startswith("O(n^"):

        result["suggestions"].append(
            "High loop nesting detected. Consider optimizing the algorithm."
        )


    return result