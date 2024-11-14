#!/bin/bash
parent_folder="$(pwd)"
video_folder=/home/persie/Videos/mokap
video_list=$1
destination_folder=/home/persie/Code/input
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
        echo "Make video into frames? [Y/N]: "
        read response < /dev/tty
        if [ "$response" = "y" ] ; then
          mkdir "$video_folder"/"$video_name"
          ffmpeg -i "$video_folder"/"$video_name".mp4 -q:v 2 -start_number 0 "${frame_folder}"/'%05d.jpg'
        else
          exit
        fi
      fi
    fi
    if [ -d "$frame_folder" ]; then
      echo "Frame File Exists at ${frame_folder}"
      if [ ! -f "$frame_folder"/"$name".csv ]; then
        echo "Annotate Frames for $name? [Y/N]: "
        read response < /dev/tty
        if [ "$response" = "y" ] ; then
          python3 annotate_video.py --video_dir "$frame_folder" --video_name "$name"
        else
          exit
        fi
      else
        echo "Annotations Exist Already for ${name}"
      fi
      echo "Compressing frames and annotations to '${destination_folder}/${name}.tar.bz2'"
      cd "$frame_folder" && cd ..
      # Zip up the folder
      tar --no-xattrs --exclude="._*" -cjf "$name".tar.bz2 "$name"
      mv "$name".tar.bz2 "$destination_folder"
      cd "$parent_folder"
    else
      echo "No Frame Folder Exists at ${frame_folder}, and no mp4 exists at ${video_folder}/${video_name}.mp4 "
    fi
  fi
done