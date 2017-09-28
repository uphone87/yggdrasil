#!/bin/bash

export PSI_DEBUG="INFO"
export PSI_NAMESPACE="helloPar"

yaml= 

# ----------------Your Commands------------------- #
case $1 in
    "" | -a | --all )
	echo "Running Python, Matlab, C integration"
	yaml='helloPar_all.yml'
	;;
    -p | --python )
	echo "Running Python"
	yaml='helloPar_python.yml'
	;;
    -m | --matlab )
	echo "Running Matlab"
	yaml='helloPar_matlab.yml'
	;;
    -c | --gcc )
	echo "Running C"
	yaml='helloPar_c.yml'
	;;
    --cpp | --g++)
	echo "Running C++"
	yaml='helloPar_cpp.yml'
	;;
    * )
	echo "Running ", $1
	yaml=$1
	;;
esac

cisrun $yaml

cat /tmp/output_helloPar.txt
