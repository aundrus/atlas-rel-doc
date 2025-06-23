function rsync_loop () {
    arg=$1
    quant=1
    LIMIT=10
    a=1
    while [ "$a" -le $LIMIT ]
    do
        echo "ardo_webpage: info: running iteration ${a} for rsync ${arg}" $(date)
        ((a++))
        echo ${arg}; r_code=$?
        if [ "${r_code}" -eq 0 ]; then
            echo "ardo_webpage: info: successful iteration ${a} for rsync ${arg}" $(date)
            break
        fi
        echo "ardo_webpage: warning: rsync error code (${arg})" $(date)
        echo "ardo_webpage: info: sleeping $((a-1))"
        sleep $quant
        if [ "$a" -gt "$LIMIT" ]; then
            echo "ardo_webpage: persistent error ${r_code} for rsync ${arg}" $(date)
            break
        fi
    done
    return ${r_code}
}

ARDOC_PROJECT_RELNAME="ARDOC_PROJECT_RELNAME"
copy_origin="copy_origin"
copy_target="copy_target"
rsync_params="--delete -uvrlpt --include=\"/*${ARDOC_PROJECT_RELNAME}/***\" --exclude=\"*\" $copy_origin/ $copy_target"
rsync_loop "${rsync_params}"
echo $?
