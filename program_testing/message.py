program_testing_execution = {
    0: ['In a waiting queue ({[0] + 1})', 0],
    1: ['Compiling', 1],
    2: ['Running on test {[0] + 1}', 2]
}

program_testing_verdict = {
    0: ['All correct', 3],
    1: ['Compile error', 5],
    2: ['Runtime error on test {[0] + 1}', 4],
    3: ['Time limit error on test {[0] + 1}', 4],
    4: ['Memory limit error on test {[0] + 1}', 4],
    5: ['Wrong answer on test {[0] + 1}', 6],
    9: ['Server error', 5]
}

colors = ['text-secondary', 'text-dark', 'text-secondary',
          'text-success', 'text-danger', 'text-primary', 'text-danger']


def get_message_solution(solution):
    state = solution.state
    if state is None:
        return state
    if state < 10:
        message = program_testing_execution[state]
        arg = solution.state_arg
    else:
        message = program_testing_verdict[state - 10]
        arg = solution.failed_test
    message = message.copy()
    message[1] = colors[message[1]]
    if arg is not None:
        message[0] = message[0].replace('[0]', str(arg))
        message[0] = eval(f'f"""{message[0]}"""')
    return tuple(message)
