

class TestCase :
    def __init__(self, arg_value : str, expected_result : bool) :
        self.arg_value = arg_value
        self.expected_result = expected_result

# func это функция, которую требуется протестировать.
# Имя функции передаётся в качестве аргумента.
def run_tests( func, test_cases ) :
    print( f"\n{'Username Value':<20}{'Expected':<13}{'Actual':<10}\n")

    passed_cases_count = 0
    for case in test_cases :
        arg_value = case.arg_value

        expected_result = case.expected_result
        actual_result = func( arg_value )

        if expected_result == actual_result :
            test_result = "passed"

            passed_cases_count += 1
        else :
            test_result = "failed"

        print(f" {arg_value:<20}{expected_result!s:<13}{actual_result!s:<10}{test_result}")

    all_cases_count = len(test_cases)
    if all_cases_count == passed_cases_count:
        status = "PASSED"
    else:
        status = "FAILED"

    print( f"\n{all_cases_count} total, {passed_cases_count} passed" )

    print( f"Status : {status}" )