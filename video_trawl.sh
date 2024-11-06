#!/bin/bash

video_folder=/Users/persie/Movies/Mokap_Video
#This is the typical file organisation video -> date -> date and time -> session
#Find the date folders
for date_folder in "$video_folder"/*
do
  #Find the Experiment Folders
  for time_folder in "$date_folder"/*
  do
    #Find each session
    for video_file in $(ls -p "$time_folder")
    do
      ext=$(echo "$video_file" | cut -d "." -f 2)
      name=$(echo "$video_file" | cut -d "." -f 1)

      # If the file is an mp4 then process it
      if [ "$ext" = "mp4" ] ; then
        frame_folder="$time_folder"/"$name"
        # If there is not a directory with the same name as the video
        if [ ! -d "$frame_folder" ]; then
          echo "No Frame File for $frame_folder"
          echo "Make video into frames? [Y/N]: "
          read response
          if [ "$response" = "y" ] ; then
            mkdir "$time_folder"/"$name"
            ffmpeg -i "$time_folder"/"$video_file" -q:v 2 -start_number 0 "$time_folder"/"$name"/'%05d.jpg'
          else
            exit
          fi
        fi
        if [ -d "$frame_folder" ]; then
          echo "Frame File Exists"
          if [ ! -f "$frame_folder"/"$name".csv ]; then
            echo "Annotate Frames for $name? [Y/N]: "
            read response
            if [ "$response" = "y" ] ; then
              python3 annotate_video.py --video_dir "$frame_folder" --video_name "$name"
            else
              exit
            fi
          else
            echo "Annotations Exist Already"
          fi
          if [ ! -f "$time_folder"/"$name".tar ]; then
            cd "$time_folder"
            # Zip up the folder
            tar -cf "$name".tar "$name"
            cd -
          fi
        fi
      fi
    done
  done
done