import math

# Function is given as f(x) = x^(1/3) + lnx = 0
# Initial interval is given as [xl, xu] = [0.25, 2]
# Acceptable maximum error is given as |xu - xr| = 10^-6

xl = 0.25
xu = 2
maxError = pow(10, -6)
n = 0   # Step number

def f(x):
    return pow(x, 1/3) + math.log(x)

# Table header
print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format("n", "xl", "xu", "xr", "|xu - xr|", "f(xr)"))

# Iteration begins
while True:
    n += 1

    # Bisection root estimation
    xr = (xl + xu) / 2

    # Table content
    print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format(n, xl, xu, xr, abs(xu - xr), f(xr)))

    # Checking the termination conditions
    if f(xr) == 0 or abs(xu - xr) <= maxError:
        print(f"\nThe root is {xr}")
        break

    # If there is no termination needed, the interval is rearranged
    else:
        if f(xr) * f(xl) > 0:
            xl = xr

        elif f(xr) * f(xl) < 0:
            xu = xr
