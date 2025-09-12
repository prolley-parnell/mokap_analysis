#!/bin/bash
parent_folder="$(pwd)"
video_folder=/Users/persie/Movies/Mokap_Video/mokap
video_list=$1
destination_folder=/Users/persie/Movies/Mokap_Video/mokap
#This is the typical file organisation video -> date -> date and time -> session

echo "Starting trawl"
#Find each session
cat ${video_list} | while read video_name || [[ -n $video_name ]];
do
  frame_folder="$video_folder"/"$video_name"
  name=$(echo "$video_name" | cut -d "/" -f 2)
  echo $name
  if [ -f "$destination_folder"/"$name".tar.bz2 ]; then
    echo "${destination_folder}/${name}.tar.bz2 already exists"
  else
    echo "There is no existing ${destination_folder}/${name}.tar.bz2"
    # If the file is an mp4 then process it
    if [ ! -f "$video_folder"/"$video_name".mp4 ] ; then
      echo "$video_folder/$video_name.mp4 could not be found"
    else
      echo "Found $video_folder/$video_name.mp4"
      frame_folder="$video_folder"/"$video_name"
      # If there is not a directory with the same name as the video
      if [ ! -d "$frame_folder" ]; then
        echo "No Frame File for $frame_folder"
        mkdir "$video_folder"/"$video_name"
         < /dev/null ffmpeg -i "$video_folder"/"$video_name".mp4 -q:v 2 -start_number 0 "${frame_folder}"/'%05d.jpg'
      else
        echo "Frame file exists at $frame_folder"
      fi

    fi
  fi
done