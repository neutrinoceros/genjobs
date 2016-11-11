#!/bin/bash

# --------------------------
# Author : Clément Robert
# written october 2016
# --------------------------
# This program copies a base simulation with all its file-tree 
# except the output files


# PARSING
#----------------------------------------------------------------------
restartfrom=0

while getopts r:R: option
do
    case $option in
        r|R ) restartfrom=$2 ;
            shift $((OPTIND-1))
            ;;
        *) exit 1;;
    esac
done
            
# gets the absolute path even from relative input
base="/"$(readlink -e $1 | cut --complement -d '/' -f 1,2)
# removes a "/" ending char if provided
target=$(pwd)/$(basename $2)


# SYNCHRONIZATION
#----------------------------------------------------------------------

FLAGS=(
    --exclude="*output/*"  # output files
    --exclude="*.std*"     # .stdout and .stderr generated by mpi
    --exclude="*~"         # temp files
    --exclude="\#*\#"      # emacs autosave files
    )


echo base is $base
echo target is $target
#rsync -av "${FLAGS[@]}" $base/ $target    
if [[  $restartfrom > 0 ]]
then
    echo RESTART FROM : $restartfrom
    #rsync --dry-run -av $base/output/*$restartfrom.dat $target/output
    #rsync --dry-run -av $base/output/*$restartfrom.dat test
    rsync --dry-run -av $base/output/*$restartfrom.dat test
fi


# AUTO-EDITION of files mentioning their own location
#----------------------------------------------------------------------
# /!\ This part may still be subject to bug corrections

#sed -i "s!$base!$target!g" $target/jobs/*oar
#sed -i "s!$base!$target!g" $target/input*/*par


# SECURITY
#----------------------------------------------------------------------
# we force the user to change persmissions before they can 
# run the simulation in case there is still something wrong

#chmod -x $target/*exe 
