all: beincl india round

beincl:
	python3 taxes.py 21.53 2 1 21%i

india:
	python3 taxes.py 118.04 1 1 9%i 9%ib

perline:
	python3 taxes.py 0.01 5 0 21%

global:
	python3 taxes.py 0.01 5 1 21%
