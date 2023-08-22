import traceback


def debug_subprocess_pytest(result):
    try:
        print(result.output)
    except UnicodeEncodeError:
        print(result.output.encode("utf-8"))
    if result.exception is not None:
        traceback.print_tb(result.exception.__traceback__)
        print(result.exception)
    assert result.exit_code == 0
