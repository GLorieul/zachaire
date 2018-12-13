
dirOut:=out


.PHONY: all clean

all:
	python3 build.py

clean:
	@printf "Cleaning directories: "
	rm -fr $(dirOut)/* 

