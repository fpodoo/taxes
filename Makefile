all: beincl ecotax india perline global quebec

beincl:
	python3 taxes.py 21.53 2 1 21%i

ecotax:
	python3 taxes.py 121 1 0 5€ 21%i

india:
	python3 taxes.py 118.04 1 0 9%i 9%ib

perline:
	python3 taxes.py 0.01 5 0 21%

global:
	python3 taxes.py 0.01 5 1 21%

quebec:
	python3 taxes.py 100 1 1 5%\> 10%

quebecincl:
	python3 taxes.py 115.50 1 1 5%i\> 10%i\>
