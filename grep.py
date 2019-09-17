import argparse
import sys
import re


def output(line):
    print(line)


def condition(line, params):
    if params.invert:
        if not params.ignore_case:
            return not re.search(params.pattern, line)
        else:
            return not re.search(params.pattern.lower(), line.lower())
    else:
        if not params.ignore_case:
            return re.search(params.pattern, line)
        else:
            return re.search(params.pattern.lower(), line.lower())


def context(params, lines, before, after, counter):
    buffer = []
    flag = 0
    number = 1
    for line in lines:
        line = line.rstrip()
        buffer.append(line)

        if len(buffer) > before + 1:
            del buffer[0]
        if condition(line, params):
            if flag <= 0:
                i = len(buffer) - 1
                for line_print in buffer:
                    count_number_base(params, line_print, counter, number - i)
                    i = i - 1
                buffer.clear()
                flag = after
            else:
                buffer.clear()
                count_number_base(params, line, counter, number)
                flag = after
        elif flag > 0:
            buffer.clear()
            count_number_base(params, line, counter, number)
            flag = flag - 1
        number = number + 1


def count_number_base(params, line, counter, number):
    if params.count:
        counter[0] = counter[0] + 1
    elif params.line_number:
        if condition(line, params):
            output('{}:{}'.format(number, line))
        else:
            output('{}-{}'.format(number, line))
    else:
        output(line)


def grep(lines, params):

    if '?' in params.pattern or '*' in params.pattern:
        params.pattern = params.pattern.replace('?', '.')
        params.pattern = params.pattern.replace('*', '\w*')

    counter = [0]

    if params.context:
        if params.context >= params.before_context:
            params.before_context = params.context
        if params.context >= params.after_context:
            params.after_context = params.context

    if params.after_context != 0 and params.before_context != 0 and params.context != 0:
        context(params, lines, params.before_context, params.after_context, counter)

    elif params.after_context != 0 and params.before_context!=0 :
        context(params, lines, params.before_context, params.after_context, counter)

    elif params.context != 0:
        context(params, lines, params.context, params.context, counter)

    elif params.before_context != 0:
        context(params, lines, params.before_context, 0, counter)

    elif params.after_context != 0:
        context(params, lines, 0, params.after_context, counter)

    else:
        context(params, lines, 0, 0, counter)
        if params.count:
            output(str(counter[0]))


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()