import sys, re, functools

# parse arguments
try:
    prices = [float(x) for x in sys.argv[1].split(',')]
    perline = not bool(int(sys.argv[2]))
    taxes = []
    for tax in sys.argv[3:]:
        g = re.match(r'([0-9.]+)([%€/])([i]?)([<>]*)[abc]?', tax)
        taxes.append([g[0], float(g[1]), g[2], g[3], g[4]])
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
        . < affect previous taxes (price included)
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
    return tax

# Compute taxes for one line, price excluded
def tax_compute(base, tax):
    if tax[2] == '€':
        tax = tax[1]
    elif tax[2] == '%':
        tax = base * tax[1] / 100.0
    elif tax[2] == '/':
        tax = base / (1 - tax[1] / 100) - base
    return tax

# return reversed list of tax included only, merging consecutive % or /
def tax_include_get(taxes):
    old = None
    percent = 0.0
    for t in reversed(taxes):
        if not t[3] or t[2] in ('/', '€') or ('<' in t[4]):   # flush continuous taxes
            if old is not None:
                yield (None, percent, old[2], old[3], old[4])
                old = None
                percent = 0.0
        if not t[3]: continue
        if t[2] in ('/', '€'):
            yield t
        else:
            old = old or t
            percent += t[1]
    if old is not None:
        yield (None, percent, old[2], old[3], old[4])

result = {
    'subtotal': 0.0,
    'total': 0.0,
    'tax': dict.fromkeys(map(lambda x: x[0], taxes), 0.0)
}

lines = []
for price in prices:
    base = price
    tot_taxes = dict.fromkeys(map(lambda x: x[0], taxes), None)

    # deduce base from price included
    base_tax = base
    for taxi in list(tax_include_get(taxes)):
        x = round(tax_compute_include(base_tax, taxi),2)
        base -= x
        if '<' in taxi[4]: base_tax -= x
        if taxi[0] is not None:
            tot_taxes[taxi[0]] = x

    # compute all taxes from the base excluding taxes
    base_tax = base
    for taxe in taxes:
        tax_amount = tax_compute(base_tax, taxe)
        if tot_taxes[taxe[0]] is None:
            tot_taxes[taxe[0]] = tax_amount

        # add in base if affect subsequent taxes
        if '>' in taxe[4]:
            base_tax += round(tax_amount, 2)

    # round per line if necessary
    if perline:
        for key, val in tot_taxes.items():
            tot_taxes[key] = round(tot_taxes[key], 2)

    # adjust for one cent in base, if all taxes are included
    tot_tax = functools.reduce(lambda x, y: round(x,2)+y, tot_taxes.values(), 0.0)
    if all(map(lambda x: x[3], taxes)):
        base = price - tot_tax

    lines.append([price, round(base, 2), tot_tax, round(base+tot_tax,2)])
    result['subtotal'] += base
    for key, val in tot_taxes.items():
        result['tax'][key] += val
    result['total'] += tot_tax + base

# Adjust first line if total does not match (because of tax included)
lines[0][2] += result['subtotal'] - sum(map(lambda x: x[2], lines))

print('%-7s     %7s  %7s  %7s' % ('Price', 'HTVA', 'Taxes', 'TVAC'))
for line in lines:
    print('%7.2f    \033[1m %7.2f \033[0m %7.2f  %7.2f' % tuple(line))
print('%-10s  %7.2f' % ('Subtotal', result['subtotal']))
for key, val in result['tax'].items():
    print('%-10s        \033[1m   %7.2f \033[0m' % (key, val))
print('%-10s            \033[1m        %7.2f \033[0m' % ('Total', result['total']))
print()


