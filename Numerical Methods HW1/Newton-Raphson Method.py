import math

# First function given as f(x) = xe^(-x^2 / 4) - 3x + 2 = 0 with the initial point x0 = 0
# Second function is given as g(x) = x^(1/3) + lnx = 0 with the initial point x0 = 1
# acceptable maximum error is given as |x_n+1 - x_n| = 10^-7

def f(x):
    return x * math.exp(-pow(x, 2) / 4) - 3 * x + 2

def f_derived(x):
    return math.exp(-pow(x, 2) / 4) + x * (-2 * x / 4) * math.exp(-pow(x, 2) / 4) - 3

x_current = 0
maxError = pow(10, -7)
n = 0

print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format("n", "x_n", "f(x_n)", "f'(x_n)", "x_n+1", "|x_n+1 - x_n|"))

while True:
    n += 1
    x_next = x_current - (f(x_current) / f_derived(x_current))

    print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format(n, x_current, f(x_current), f_derived(x_current), x_next, abs(x_current - x_next)))

    if f(x_next) == 0 or abs(x_next - x_current) <= maxError:
        print(f"\nThe root is {x_next}")
        break

    x_current = x_next