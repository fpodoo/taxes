all: beincl ecotax india indiacess perline global quebec quebecincl brazil mexico las0 las1 las2 firstl nofirstl

beincl:
	python3 taxes.py 21.53,21.53 1 21%i

ecotax:
	python3 taxes.py 121 0 5€ 21%i

india:
	python3 taxes.py 118.04 0 9%i 9%ib

perline:
	python3 taxes.py 0.01,0.01,0.01,0.01,0.01 0 21%

global:
	python3 taxes.py 0.01,0.01,0.01,0.01,0.01 1 21%

quebec:
	python3 taxes.py 100 1 5%\<\> 10%\<\>

quebecincl:
	python3 taxes.py 115.50 1 5%i\<\> 10%i\<\>

brazil:
	python3 taxes.py 48.0 1 5/i 3/i 9/i 15/i 0.65/i

indiacess:
	python3 taxes.py 118.04 0 9%i 9%ib 1%

mexico:
	python3 taxes.py 1199.0,1699.0,1999.0,10999.0,11999.0,11999.0,11999.0 1 16%i

las0:
	python3 taxes.py 124.40 0 8%i 0%i

las1:
	python3 taxes.py 2300 0 15% 5.5%i

las2:
	python3 taxes.py 121 1 5€i\> 21%i

firstl:
	python3 taxes.py 0.04 1 23%i 23%ib 23%ic
	python3 taxes.py 0.04,0.04 1 23%i 23%ib 23%ic

nofirstl:
	python3 taxes.py 21.53,21.53,21.53,21.53,21.53,21.53,21.53 1 21%i
