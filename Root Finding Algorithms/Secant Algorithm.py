# Function is given as f(x) = -x^6 + 3x + 7 = 0 with the initial points x0 = -1, x1 = 0
# Acceptable maximum error is given as |x_n+1 - x_n| = 10^-6

def f(x):
    return -pow(x, 6) + 3*x + 7

x0 = -1
x1 = 0
maxError = pow(10, -6)
n = 0   #Step number

# Table header
print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format("n", "x_n-1", "x_n", "x_n+1", "|x_n+1 - x_n|", "f(x_n+1)"))

# Iterations begins
while True:
    n += 1

    # Secant root estimation
    x_next = x1 - (f(x1) / ((f(x1) - f(x0)) / (x1 - x0)))

    # Table content
    print("{:<5} {:<25} {:<25} {:<25} {:<25} {:<25}".format(n, x0, x1, x_next, abs(x_next - x1), f(x_next)))

    # Checking the termination conditions
    if f(x_next) == 0 or abs(x_next - x1) <= maxError:
        print(f"\nThe root is {x_next}")
        break

    # If there is no termination needed, rearrange x_n-1 and x_n for next step
    x0 = x1
    x1 = x_next