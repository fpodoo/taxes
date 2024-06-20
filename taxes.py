import sys, re, itertools

# parse arguments
try:
    prices = [float(x) for x in sys.argv[1].split(',')]
    perline = not bool(int(sys.argv[2]))
    taxes = []
    taxes_dict = {}
    for tax in sys.argv[3:]:
        g = re.match(r'([0-9.]+)([%€/])([i]?)([<>]*)[abc]?', tax)
        taxes.append([g[0], float(g[1]), g[2], g[3], g[4]])
        taxes_dict[g[0]] = (float(g[1]), g[2], g[3], g[4])
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

# return reversed list of tax included only, merging consecutive %
def tax_include_get(taxes):
    taxes = [x for x in taxes if x[3]]
    groupkey = lambda t: (t[2] == '%' and '<' not in t[4]) or t
    for key, taxes in itertools.groupby(reversed(taxes), groupkey):
        taxes = list(taxes)
        yield (len(taxes) == 1 and taxes[0][0] or None, sum([t[1] for t in taxes]), *taxes[0][2:])

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
        if taxi[0] is not None:                          # None = Aggregated: will be recomputed from base excluded
            tot_taxes[taxi[0]] = x

    # compute all taxes from the base excluding taxes
    base_tax = base
    for taxe in taxes:
        if tot_taxes[taxe[0]] is not None:
            continue # already computed by tax included
        tax_amount = tax_compute(base_tax, taxe)
        tot_taxes[taxe[0]] = tax_amount

        # add in base if affect subsequent taxes
        if '>' in taxe[4]:
            base_tax += round(tax_amount, 2)

    # round per line if necessary
    if perline:
        for key, val in tot_taxes.items():
            tot_taxes[key] = round(val, 2)

    # adjust for one cent in base, for taxes included
    tot_tax_incl = sum([x for key, x in tot_taxes.items() if taxes_dict[key][2]])
    base = price - tot_tax_incl

    tot_tax = sum([x for x in tot_taxes.values()])
    lines.append([price, round(base, 2), tot_tax, round(base+tot_tax,2)])
    result['subtotal'] += base
    for key, val in tot_taxes.items():
        result['tax'][key] += val
    result['total'] += tot_tax + base

print('%-7s     %7s  %7s  %7s' % ('Price', 'HTVA', 'Taxes', 'TVAC'))
for line in lines:
    print('%7.2f    \033[1m %7.2f \033[0m %7.2f  %7.2f' % tuple(line))
print('%-10s  %7.2f' % ('Subtotal', result['subtotal']))
for key, val in result['tax'].items():
    print('%-10s        \033[1m   %7.2f \033[0m' % (key, val))
print('%-10s            \033[1m        %7.2f \033[0m' % ('Total', result['total']))
print()


