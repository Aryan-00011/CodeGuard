import ast


def check_security(code):

    vulnerabilities = []

    try:
        tree = ast.parse(code)

    except SyntaxError:

        return vulnerabilities


    # =====================================================
    # SECURITY CHECKS
    # =====================================================

    for node in ast.walk(tree):

        # -------------------------------------------------
        # 1. os.system()
        # -------------------------------------------------

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Attribute):

                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "os"
                    and node.func.attr == "system"
                ):

                    vulnerabilities.append({

                        "type": "Command Injection",

                        "severity": "HIGH",

                        "line": node.lineno,

                        "message":
                            "os.system() can execute operating-system commands. "
                            "Avoid passing untrusted user input."

                    })


        # -------------------------------------------------
        # 2. eval()
        # -------------------------------------------------

        if isinstance(node, ast.Call):

            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "eval"
            ):

                vulnerabilities.append({

                    "type": "Unsafe eval()",

                    "severity": "HIGH",

                    "line": node.lineno,

                    "message":
                        "eval() executes dynamically generated code "
                        "and can allow arbitrary code execution."

                })


        # -------------------------------------------------
        # 3. exec()
        # -------------------------------------------------

        if isinstance(node, ast.Call):

            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "exec"
            ):

                vulnerabilities.append({

                    "type": "Unsafe exec()",

                    "severity": "HIGH",

                    "line": node.lineno,

                    "message":
                        "exec() can execute arbitrary Python code."

                })


        # -------------------------------------------------
        # 4. Hardcoded password / secret
        # -------------------------------------------------

        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name):

                    variable_name = target.id.lower()

                    if any(
                        word in variable_name
                        for word in [
                            "password",
                            "passwd",
                            "secret",
                            "api_key",
                            "apikey"
                        ]
                    ):

                        vulnerabilities.append({

                            "type": "Hardcoded Secret",

                            "severity": "HIGH",

                            "line": node.lineno,

                            "message":
                                "Sensitive credentials should not be "
                                "hardcoded in source code."

                        })


        # -------------------------------------------------
        # 5. pickle.loads()
        # -------------------------------------------------

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Attribute):

                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "pickle"
                    and node.func.attr == "loads"
                ):

                    vulnerabilities.append({

                        "type": "Unsafe Deserialization",

                        "severity": "HIGH",

                        "line": node.lineno,

                        "message":
                            "pickle.loads() can execute malicious code "
                            "when loading untrusted data."

                    })


    return vulnerabilities