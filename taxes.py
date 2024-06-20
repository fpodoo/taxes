import sys, re, functools

# parse arguments
try:
    price = float(sys.argv[1])
    lines = int(sys.argv[2])
    perline = not bool(int(sys.argv[3]))
    taxes = []
    for tax in sys.argv[4:]:
        g = re.match(r'([0-9.]+)([%€/])([i]?)([>]?[abc]?)', tax)
        taxes.append((g[0], float(g[1]), g[2], g[3], g[4]))
    assert all(taxes)
except:
    print('''Usage: taxes.py 100.0 3 1 21% 5€
    - 100.0: the price
    - 3: number of lines in the SO (all lines have same value)
    - 1: 1 = round globally, 0 = round per line
    - taxes: 21%i
        . % (percent)
        . € (fixed)
        . / (divided)
        . i tax included in price
        . > affect subsequent taxes
        . [abc] optional suffix to differenciate same taxes
    ''')
    raise


# Compute taxes for one line, price included in taxes
def tax_compute_include(base, tax):
    if tax[2] == '€':
        tax = tax[1]
    elif tax[2] == '%':
        tax = base - base / (1+tax[1] / 100.0)
    elif tax[2] == '/':
        tax = base * tax[1] / 100.0
    return tax, base - tax, base

# Compute taxes for one line, price excluded
def tax_compute(base, tax):
    if tax[2] == '€':
        tax = tax[1]
    elif tax[2] == '%':
        tax = base * tax[1] / 100.0
    elif tax[2] == '/':
        tax = base / (1 - tax[1] / 100) - base
    return tax, base, base + tax

# return reversed list of tax included only, merging consecutive % or /
def tax_include_get(taxes):
    old = old_value = None
    for t in reversed(taxes):
        if not t[3]: continue  # exclude taxes that are not included
        if old and t[2] != old:
            yield (None, old_value, old, False)
        old = t[2]
        old_value = (old_value or 0.0) + t[1]
    if old:
        yield (None, old_value, old, False)


result = {
    'subtotal': 0.0,
    'total': 0.0,
    'tax': dict.fromkeys(map(lambda x: x[0], taxes), 0.0)
}

print('%10s  %7s     %7s  %7s  %7s' % ('', 'Price', 'HTVA', 'Taxes', 'TVAC'))
for i in range(lines):
    base = price
    tot_taxes = dict.fromkeys(map(lambda x: x[0], taxes), 0.0)

    # deduce base from price included
    for taxi in list(tax_include_get(taxes)):
        base = tax_compute_include(base, taxi)[1]

    # compute all taxes from the base excluding taxes
    base = round(base, 2)
    for taxe in taxes:
        r = tax_compute(base, taxe)
        tot_taxes[taxe[0]] += r[0]

        # add in base if affect subsequent taxes
        if taxe[4]:
            base += round(r[0], 2)

    # round per line if necessary
    if perline:
        base = round(base, 2)
        for key, val in tot_taxes.items():
            tot_taxes[key] = round(tot_taxes[key], 2)

    # adjust for one cent in base, if all taxes are included
    tot_tax = functools.reduce(lambda x, y: round(x,2)+y, tot_taxes.values(), 0.0)
    if all(map(lambda x: x[3], taxes)):
        base = price - tot_tax

    print('%-10s  %7.2f     %7.2f  %7.2f  %7.2f' % ('Line '+str(i), price, base, tot_tax, base+tot_tax))
    result['subtotal'] += base
    for key, val in tot_taxes.items():
        result['tax'][key] += val
    result['total'] += tot_tax + base


print()
print('          %-12s  %7.2f' % ('Subtotal', result['subtotal']))
for key, val in result['tax'].items():
    print('          %-12s           %7.2f' % (key, val))
print('          %-12s                    %7.2f' % ('Total', result['total']))
print()


