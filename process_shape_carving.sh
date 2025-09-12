#!/bin/bash
offline_mokap_path=~/PycharmProjects/offline_mokap/
data_folder=/Users/persie/PhD_Code/3d_ant_data_rle
experiment_list=$1
analysis_dir="$(pwd)"

#Set up params for python script
object_name='seed'
folder="${data_folder}"

#This is the typical file organisation video -> date -> date and time -> session

echo "Starting shape carving trawl, activating uv environment..."
source "${offline_mokap_path}/.venv/bin/activate"
#Find each session
cat ${experiment_list} | while read experiment_name || [[ -n $experiment_name ]];
do

  prefix=$(echo "$experiment_name" | cut -d "/" -f 1)
  session=$(echo "$experiment_name" | cut -d "/" -f 2)
    #If the session doesn't exist, move on
  if [ ! -d "${data_folder}/${prefix}/inputs/segmentation/" ]; then
    echo "${data_folder}/${prefix}/inputs/segmentation/ does not exist"
  else
    if [ -f "${data_folder}/${prefix}/outputs/segmentation/${prefix}_${object_name}_session${session}.toml" ]; then
        echo " ${prefix}_${object_name}_session${session}.toml already exists "
    else
        echo " Processing $prefix on Experiment $session"
        cd $offline_mokap_path

        python3 get_voxel_carved_shape.py $folder "$prefix" "$session" $object_name
        echo "$analysis_dir"
        echo "$(pwd)"
        cd $analysis_dir

     fi
   fi
done