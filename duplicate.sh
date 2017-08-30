#!/bin/bash

# --------------------------------------------
# author     clement.robert@oca.eu
# project    github.com/neutrinoceros/fargotb
# started    10/2016
# --------------------------------------------
# This program copies a base simulation with all its file-tree 
# except the output files
#
# Arguments 
#    0) $base   : simulation to be copied
#    1) $target : path for the copy
#
# Options
#    r|R) restart mode, preserves the files requiered for a restart.
#    m|M) move (mv) mode : base is moved to target while auto-refering
#                          files are still being updated

# DEFINITIONS *********************************************************

restartfrom=0
MVMODE=false
USAGE="usage\n-----\n\t\$0:base\n \t\$1:target"

AUTOEXCLUDE=(
    --exclude="*output/*"  # output files
    --exclude="*out/*"     # output files
    --exclude="*.dat"      # data files
    --exclude="*~"         # temp files
    --exclude="\#*\#"      # emacs autosave files
    --exclude="*tmp*"      # temp files
    --exclude="*src*"      # source files
    --exclude="*build*"    # build files
    --exclude="*.pdf"      # images
    --exclude="*.jpg"      # images
    --exclude="*.png"      # images
    --exclude="*.plt"      # gnuplot temporary files
    --exclude="*.std*"     # .stdout and .stderr generated by mpi
    --exclude="*.md*"      # documentation files
     )

RESTART_AUTOINCLUDE=(
    --include="planet*.dat"
    --include="orbit*.dat"
    --include="tqwk*.dat"
    --include="acc*.dat"
    --include="used_rad.dat"
    --include="dims.dat"    
    )


# PARSING *************************************************************
# options ---------------------------------------------------------
while getopts r:R:s:S:mMhH option
do
    case $option in
        r|R|s|S ) restartfrom=$2 ;
            shift $((OPTIND-1))
            ;;
        m|M ) MVMODE=true
            shift $((OPTIND-1))
            ;;
        h|H ) echo -e $USAGE ; exit 0;
            ;;
        *) echo "error : invalid argument"; echo -e $USAGE; exit 1
            ;;
    esac
done

if [[ $# != 2 ]] ; then
    echo "error : invalid number of arguments" ; exit 1
fi


# $base definition ------------------------------------------------
target=$(readlink -e $2)
if [ $? == 0 ] ; then
    echo "error : \$target must not be an existing directory" ; exit 1
else
    target=$(readlink -f $2)
fi

# $target definition ----------------------------------------------
base=$(readlink -e $1)
if [ $? == 1 ] ; then
    echo "error : \$base must be an  existing directory" ; exit 1
else
    if [[ $base == *"gpfs"* ]] ; then
        base=/$(  echo $base   | cut --complement -d / -f 1,2) 
        target=/$(echo $target | cut --complement -d / -f 1,2) 
    fi
    if [[ $base != *"$USER"* ]] ; then
        echo "error : you can only use this script on directories you own"
        exit 1
    fi
fi


# SYNCHRONIZATION *****************************************************

if [[ $MVMODE == true ]] ; then
    read -p  \
        "*) This is mv-mode of duplicate. Proceed (y/[n])?    " choice

    case "$choice" in
        y|Y|yes|YES ) mv $base $target
            ;;
        *) echo "I'm sorry Dave. I'm afraid I can't do that"
            ;;
    esac

else
    # main synchronisation
    rsync -av "${AUTOEXCLUDE[@]}" $base/ $target 

    if [[ $restartfrom > 0 ]] ; then
        # optional, addtional synchro including specified restart files
        RESTART_FILES=(--include="*$restartfrom.dat")
        rsync -av \
            "${RESTART_AUTOINCLUDE[@]}" \
            "${RESTART_FILES[@]}" \
            --exclude="*" \
            $base/out*/ $target/out/ 2>/dev/null
    fi
fi

if [[ $? != 0 ]] ; then
    echo "error : something went wrong while syncing." ; exit 1
fi

# AUTO-EDITING of files mentioning their own location *****************

sed -i "s?$base?$target?g" $target/jobs/*oar >> /dev/null 2>&1
sed -i "s?$base?$target?g" $target/*oar      >> /dev/null 2>&1
sed -i "s?$base?$target?g" $target/in*/*par  >> /dev/null 2>&1
sed -i "s?$base?$target?g" $target/*par      >> /dev/null 2>&1


# INTERACTIVE DOCUMENTATION *******************************************

if [[ $MVMODE != true ]] ; then
    OLD_OARTAG=$(eval "grep --no-filename '#OAR -n' $base/jobs/*.oar | head --lines 1")
    echo 
    read -p "*) enter new OAR tag        " NEW_OARTAG
    sed -i "s?$OLD_OARTAG?#OAR -n $NEW_OARTAG?g" $target/jobs/*oar >> /dev/null 2>&1


    docfile=$target/Infos.md
    echo
    read -p "*) enter docstring          " DocString


    echo ''                             >  $docfile
    echo "# file : $docfile"            >> $docfile
    echo "----------------------------------------------------------------" \
        >> $docfile
    echo "simtag           $NEW_OARTAG" >> $docfile
    echo "copied from      $base"       >> $docfile
    echo "docstring        $DocString"  >> $docfile
    echo -e "\n"                        >> $docfile
fi

# SECURITY ************************************************************
# we force the user to change persmissions before they can 
# run the simulation in case there is still something wrong

chmod -x $target/*exe >> /dev/null 2>&1
echo
echo " Warning ------------------------------------------------------"
echo "   *.exe files are being removed of their -x persmission."
echo "   please check that everything went well before using chmod +x"
echo " ------------------------------------------------------ Warning" 
echo
