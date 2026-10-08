
    export PYTHONHOME=""
    export PATH=""
    export PYTHONPATH=""

    # >>> conda initialize >>>
    # !! Please replace the following paths with your own !!

    __conda_setup="$('/scratch/anaconda/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
    if [ $? -eq 0 ]; then
        eval "$__conda_setup"
    else
        if [ -f "/scratch/anaconda/anaconda3/etc/profile.d/conda.sh" ]; then
            . "/scratch/anaconda/anaconda3/etc/profile.d/conda.sh"
        else
            export PATH="/scratch/anaconda/anaconda3/bin:$PATH"
        fi
    fi
    unset __conda_setup
    echo $PATH

    # <<< conda initialize <<<

    conda activate tf
    cd haruspex
    source/hpx_unet_190116.py -n network/hpx_190116 -d map-predict /scratch/haruspex/emd_3488.map -o /scratch/haruspex/testout/emd_3488.map