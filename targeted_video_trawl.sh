#!/bin/bash
parent_folder="$(pwd)"
video_folder=/Users/persie/Movies/Mokap_Video
video_list=$1
destination_folder=/Users/persie/PhD_Code/cluster/data/input/
#This is the typical file organisation video -> date -> date and time -> session


#Find each session
cat ${video_list} | while read video_name || [[ -n $video_name ]];
do
  # If the file is an mp4 then process it
  if [ ! -f "$video_folder"/"$video_name".mp4 ] ; then
    echo "$video_folder/$video_name.mp4 could not be found"
  else
    echo "Found $video_folder/$video_name.mp4"
    frame_folder="$video_folder"/"$video_name"
    # If there is not a directory with the same name as the video
    if [ ! -d "$frame_folder" ]; then
      echo "No Frame File for $frame_folder"
      echo "Make video into frames? [Y/N]: "
      read response < /dev/tty
      if [ "$response" = "y" ] ; then
        mkdir "$video_folder"/"$video_name"
        ffmpeg -i "$video_folder"/"$video_name".mp4 -q:v 2 -start_number 0 "${frame_folder}"/'%05d.jpg'
      else
        exit
      fi
    fi
    if [ -d "$frame_folder" ]; then
      echo "Frame File Exists"
      name=$(echo "$video_name" | cut -d "/" -f 3)
      echo $name
      if [ ! -f "$frame_folder"/"$name".csv ]; then
        echo "Annotate Frames for $name? [Y/N]: "
        read response < /dev/tty
        if [ "$response" = "y" ] ; then
          python3 annotate_video.py --video_dir "$frame_folder" --video_name "$name"
        else
          exit
        fi
      else
        echo "Annotations Exist Already"
      fi
      if [ ! -f "$destination_folder"/"$video_name".tar ]; then
        cd "$frame_folder" && cd ..
        echo ${name}
        # Zip up the folder
        tar -cf "$name".tar "$name"
        mv "$name".tar "$destination_folder"
        cd "$parent_folder"
      fi
    fi
  fi
done