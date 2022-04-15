# First function is given as f(x) = x^4 + 7x^3 - 11x^2 + 5 = 0 with the initial points x0 = -1, x1 = 0
# acceptable maximum error is given as |xr_n - xr_n-1| = 10^-5

def f(x):
    return pow(x, 4) + 7 * pow(x, 3) - 11 * pow(x, 2) + 5

xl = -2
xu = 0
maxError = pow(10, -5)
n = 0   # Step number

# First estimation - used to calculate error
xr_current = xu - (f(xu) / ((f(xl) - f(xu)) / (xl - xu)))

# Table header
print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format("n", "xl", "xu", "xr", "|xr_n - xr_n-1|", "f(xr_n)"))

# Iteration begins
while True:
    n += 1


    if f(xr_current) * f(xl) < 0:
        xu = xr_current
    elif f(xr_current) * f(xl) > 0:
        xl = xr_current

    # Regula Falsi root estimation - same as the first estimation
    xr_next = xu - (f(xu) / ((f(xl) - f(xu)) / (xl - xu)))

    # Table content
    print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format(n, xl, xu, xr_next, abs(xr_next - xr_current), f(xr_next)))

    # Checking the termination conditions
    if f(xr_next) == 0 or abs(xr_next - xr_current) <= maxError:
        print(f"\nThe root is {xr_next}")
        break

    # If there is no termination needed, rearrange x_n-1 for next step
    xr_current = xr_next