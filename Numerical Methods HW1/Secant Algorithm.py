# First function given as f(x) = -x^6 + 3x + 7 = 0 with the initial points x0 = -1, x1 = 0
# Second function is given as g(x) = xe^(-x^2 / 4) - 3x + 2 = 0 with the initial points x0 = 0, x1 = 1
# acceptable maximum error is given as |x_n+1 - x_n| = 10^-6

def f(x):
    return -pow(x, 6) + 3*x + 7

x0 = -1
x1 = 0
maxError = pow(10, -6)
n = 0

print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format("n", "x_n-1", "x_n", "x_n+1", "|x_n+1 - x_n|", "f(x_n+1)"))

while True:
    n += 1
    x_next = x1 - (f(x1) / ((f(x1) - f(x0)) / (x1 - x0)))

    print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format(n, x0, x1, x_next, abs(x_next - x1), f(x_next)))

    if f(x_next) == 0 or abs(x_next - x1) <= maxError:
        print(f"\nThe root is {x_next}")
        break

    x0 = x1
    x1 = x_next