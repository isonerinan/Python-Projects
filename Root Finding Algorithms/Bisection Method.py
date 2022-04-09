import math

# First function given as f(x) = x^(1/3) + lnx = 0
# initial interval is given as [xl, xu] = [0.25, 2]
# acceptable maximum error is given as |xu - xr| = 10^-6

def f(x):
    return pow(x, 1/3) + math.log(x)

xl = 0.25
xu = 2
maxError = pow(10, -6)
n = 0

print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format("n", "xl", "xu", "xr", "|xu - xr|", "f(xr)"))

while True:
    n += 1
    xr = (xl + xu) / 2

    print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format(n, xl, xu, xr, abs(xu - xr), f(xr)))

    if f(xr) == 0 or abs(xu - xr) <= maxError:
        print(f"\nThe root is {xr}")
        break

    else:
        if f(xr) * f(xl) > 0:
            xl = xr

        elif f(xr) * f(xl) < 0:
            xu = xr
