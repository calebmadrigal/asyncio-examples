# For time comparison with tail_recursion_with_asyncio.py
#
# Results: 
#  * This (iterative): 1.3s
#  * Tail-recursive with asyncio: 2.6s (about 2x longer)

def factorial(n):
    acc = 1
    for i in range(1, n+1):
        acc *= i
    return acc

print("Result: {}".format(factorial(50000)))

