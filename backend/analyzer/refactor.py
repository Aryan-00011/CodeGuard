import ast


# =========================================================
# FIND BODY OF A NODE
# =========================================================

def find_parent_body(tree, target_node):

    for parent in ast.walk(tree):

        if hasattr(parent, "body"):

            body = parent.body

            for index, statement in enumerate(body):

                if statement is target_node:

                    return body, index

    return None, None


# =========================================================
# CREATE REFACTORED CODE
# =========================================================

def generate_refactored_code(code, tree):

    refactored_tree = ast.parse(code)

    changed = False


    # =====================================================
    # 1. range(len(numbers)) + append(numbers[i] ...)
    # =====================================================

    for body_parent in ast.walk(refactored_tree):

        if not hasattr(body_parent, "body"):

            continue

        body = body_parent.body

        index = 0

        while index < len(body) - 1:

            first = body[index]
            second = body[index + 1]


            # -------------------------------------------------
            # result = []
            # -------------------------------------------------

            if (
                isinstance(first, ast.Assign)
                and len(first.targets) == 1
                and isinstance(first.targets[0], ast.Name)
                and isinstance(first.value, ast.List)
                and len(first.value.elts) == 0
                and isinstance(second, ast.For)
            ):

                result_name = first.targets[0].id


                # -------------------------------------------------
                # for i in range(len(numbers)):
                # -------------------------------------------------

                if (
                    isinstance(second.target, ast.Name)
                    and isinstance(second.iter, ast.Call)
                    and isinstance(second.iter.func, ast.Name)
                    and second.iter.func.id == "range"
                    and len(second.iter.args) == 1
                ):

                    range_argument = second.iter.args[0]


                    if (
                        isinstance(range_argument, ast.Call)
                        and isinstance(range_argument.func, ast.Name)
                        and range_argument.func.id == "len"
                        and len(range_argument.args) == 1
                        and isinstance(range_argument.args[0], ast.Name)
                    ):

                        loop_variable = second.target.id
                        list_name = range_argument.args[0].id


                        # -------------------------------------------------
                        # Check loop contains result.append(...)
                        # -------------------------------------------------

                        if len(second.body) == 1:

                            loop_statement = second.body[0]


                            if isinstance(
                                loop_statement,
                                ast.Expr
                            ):

                                append_call = loop_statement.value


                                if (
                                    isinstance(append_call, ast.Call)
                                    and isinstance(
                                        append_call.func,
                                        ast.Attribute
                                    )
                                    and append_call.func.attr == "append"
                                    and isinstance(
                                        append_call.func.value,
                                        ast.Name
                                    )
                                    and append_call.func.value.id
                                    == result_name
                                    and len(append_call.args) == 1
                                ):

                                    expression = append_call.args[0]


                                    # -------------------------------------------------
                                    # Replace numbers[i] with item
                                    # -------------------------------------------------

                                    class ReplaceIndex(ast.NodeTransformer):

                                        def visit_Subscript(self, node):

                                            if (
                                                isinstance(
                                                    node.value,
                                                    ast.Name
                                                )
                                                and node.value.id
                                                == list_name
                                            ):

                                                if (
                                                    isinstance(
                                                        node.slice,
                                                        ast.Name
                                                    )
                                                    and node.slice.id
                                                    == loop_variable
                                                ):

                                                    return ast.Name(
                                                        id="item",
                                                        ctx=ast.Load()
                                                    )

                                            return self.generic_visit(node)


                                    new_expression = ReplaceIndex().visit(
                                        ast.fix_missing_locations(
                                            expression
                                        )
                                    )


                                    # -------------------------------------------------
                                    # Create list comprehension
                                    # -------------------------------------------------

                                    comprehension = ast.ListComp(

                                        elt=new_expression,

                                        generators=[
                                            ast.comprehension(
                                                target=ast.Name(
                                                    id="item",
                                                    ctx=ast.Store()
                                                ),

                                                iter=ast.Name(
                                                    id=list_name,
                                                    ctx=ast.Load()
                                                ),

                                                ifs=[],

                                                is_async=0
                                            )
                                        ]
                                    )


                                    new_assignment = ast.Assign(

                                        targets=[
                                            ast.Name(
                                                id=result_name,
                                                ctx=ast.Store()
                                            )
                                        ],

                                        value=comprehension
                                    )


                                    ast.copy_location(
                                        new_assignment,
                                        first
                                    )


                                    body[index:index + 2] = [
                                        new_assignment
                                    ]


                                    changed = True

                                    index += 1

                                    continue


            index += 1


    # =====================================================
    # RETURN RESULT
    # =====================================================

    if changed:

        ast.fix_missing_locations(
            refactored_tree
        )

        try:

            return ast.unparse(
                refactored_tree
            )

        except Exception:

            return code


    return code


# =========================================================
# PYTHON REFACTORING ENGINE
# =========================================================

def refactor_python_code(code):

    suggestions = []


    # =====================================================
    # PARSE CODE
    # =====================================================

    try:

        tree = ast.parse(code)

    except SyntaxError:

        return {

            "success": False,

            "suggestions": [],

            "refactored_code": code,

            "message":
                "Cannot refactor code because syntax is invalid."

        }


    # =====================================================
    # 1. range(len(list)) LOOP
    # =====================================================

    for node in ast.walk(tree):

        if isinstance(node, ast.For):

            loop = node.iter


            if isinstance(loop, ast.Call):

                if (
                    isinstance(loop.func, ast.Name)
                    and loop.func.id == "range"
                    and len(loop.args) == 1
                ):

                    argument = loop.args[0]


                    if isinstance(argument, ast.Call):

                        if (
                            isinstance(argument.func, ast.Name)
                            and argument.func.id == "len"
                            and len(argument.args) == 1
                        ):

                            if isinstance(
                                argument.args[0],
                                ast.Name
                            ):

                                list_name = argument.args[0].id


                                suggestions.append({

                                    "type":
                                        "Unnecessary Index Loop",

                                    "line":
                                        node.lineno,

                                    "message":
                                        f"Loop uses range(len({list_name})). "
                                        "Direct iteration may be simpler.",

                                    "suggestion":
                                        f"for item in {list_name}:"

                                })


    # =====================================================
    # 2. EMPTY LIST + APPEND LOOP
    # =====================================================

    for node in ast.walk(tree):

        if isinstance(node, ast.Assign):

            if len(node.targets) != 1:

                continue


            target = node.targets[0]


            if not isinstance(
                target,
                ast.Name
            ):

                continue


            if not isinstance(
                node.value,
                ast.List
            ):

                continue


            if len(node.value.elts) != 0:

                continue


            variable_name = target.id


            parent_body, current_index = find_parent_body(
                tree,
                node
            )


            if parent_body is None:

                continue


            if current_index + 1 >= len(parent_body):

                continue


            next_statement = parent_body[
                current_index + 1
            ]


            if isinstance(
                next_statement,
                ast.For
            ):

                for loop_statement in next_statement.body:

                    if isinstance(
                        loop_statement,
                        ast.Expr
                    ):

                        call = loop_statement.value


                        if isinstance(
                            call,
                            ast.Call
                        ):

                            if isinstance(
                                call.func,
                                ast.Attribute
                            ):

                                if (
                                    isinstance(
                                        call.func.value,
                                        ast.Name
                                    )
                                    and
                                    call.func.value.id
                                    == variable_name
                                    and
                                    call.func.attr
                                    == "append"
                                ):

                                    suggestions.append({

                                        "type":
                                            "List Comprehension",

                                        "line":
                                            node.lineno,

                                        "message":
                                            f"{variable_name} is created "
                                            "and populated using a loop.",

                                        "suggestion":
                                            "Consider using a list "
                                            "comprehension."

                                    })


    # =====================================================
    # 3. PRINT DEBUGGING
    # =====================================================

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ):

                suggestions.append({

                    "type":
                        "Debug Print",

                    "line":
                        node.lineno,

                    "message":
                        "print() statements may be debugging code.",

                    "suggestion":
                        "Remove unnecessary print() statements "
                        "before production."

                })


    # =====================================================
    # 4. NESTED IF
    # =====================================================

    for node in ast.walk(tree):

        if isinstance(node, ast.If):

            if len(node.body) == 1:

                first_statement = node.body[0]


                if isinstance(
                    first_statement,
                    ast.If
                ):

                    suggestions.append({

                        "type":
                            "Nested If",

                        "line":
                            node.lineno,

                        "message":
                            "Nested if statements detected.",

                        "suggestion":
                            "Consider combining conditions "
                            "using logical operators."

                    })


    # =====================================================
    # GENERATE ACTUAL REFACTORED CODE
    # =====================================================

    refactored_code = generate_refactored_code(
        code,
        tree
    )


    # =====================================================
    # NO SUGGESTIONS
    # =====================================================

    if len(suggestions) == 0:

        suggestions.append({

            "type":
                "Clean Code",

            "line":
                None,

            "message":
                "No obvious refactoring opportunities detected.",

            "suggestion":
                "Code structure looks reasonable."

        })


    # =====================================================
    # RETURN
    # =====================================================

    return {

        "success": True,

        "suggestions":
            suggestions,

        "refactored_code":
            refactored_code

    }