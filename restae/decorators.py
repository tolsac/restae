"""
Decorators
"""


def action(methods=None, detail=None, url_path=None, param_name=None):
    """
    Mark a Handler method as a routable action.
    Set the `detail` boolean to determine if this action should apply to
    instance/detail requests or collection/list requests.
    """
    methods = ['get'] if (methods is None) else methods
    methods = [method.lower() for method in methods]

    assert detail is not None, (
        "@action() missing required argument: 'detail'"
    )
    if param_name is not None:
        assert detail is not True, (
            "@action() cannot have a 'param_name' when 'detail' is set to False"
        )

    def decorator(func):
        func.is_dynamic_action = True
        func.methods = methods
        func.detail = detail
        func.url_path = url_path if url_path else func.__name__
        func.mapping = {
            _method: func.url_path
            for _method in func.methods
        }

        return func
    return decorator
