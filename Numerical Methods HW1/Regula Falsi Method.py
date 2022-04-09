import math

# First function given as f(x) = x^4 + 7x^3 - 11x^2 + 5 = 0 with the initial points x0 = -1, x1 = 0
# Second function is given as g(x) = -x^6 + 3x + 7 = 0 with the initial interval [xl, xu] = [2, 0]
# acceptable maximum error is given as |xr_n - xr_n-1| = 10^-5

def f(x):
    return pow(x, 4) + 7 * pow(x, 3) - 11 * pow(x, 2) + 5

xl = -2
xu = 0
maxError = pow(10, -5)
n = 0

# First estimation
xr_current = xu - (f(xu) / ((f(xl) - f(xu)) / (xl - xu)))

print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format("n", "xl", "xu", "xr", "|xr_n - xr_n-1|", "f(xr_n)"))

while True:
    n += 1

    if f(xr_current) * f(xl) < 0:
        xu = xr_current
    elif f(xr_current) * f(xl) > 0:
        xl = xr_current

    xr_next = xu - (f(xu) / ((f(xl) - f(xu)) / (xl - xu)))

    print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format(n, xl, xu, xr_current, abs(xr_next - xr_current), f(xr_next)))

    if f(xr_next) == 0 or abs(xr_next - xr_current) <= maxError:
        print(f"\nThe root is {xr_next}")
        break

    xr_current = xr_next