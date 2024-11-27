video_list=$1

video_src="/home/persie/Videos/mokap"
video_dest="/home/persie/Code/sleap/data/input"

cat ${video_list} | while read video_name || [[ -n $video_name ]];
do
  date=$(echo "$video_name" | cut -d "-" -f 1)
  date_time=$(echo "$video_name" | cut -d "/" -f 1)
  name=$(echo "$video_name" | cut -d "/" -f 2)

  if [ ! -f "${video_dest}/${date_time}/${name}.mp4" ]; then
    if [ -f "${video_src}/${date}/${date_time}/${name}.mp4" ]; then
      echo "Copying ${name}.mp4 to local folder"
      mkdir -p "${video_dest}/${date_time}"
      cp "${video_src}/${date}/${date_time}/${name}.mp4" "${video_dest}/"
    elif [ -f "${video_src}/${date_time}/${name}.mp4" ]; then
      echo "Copying ${name}.mp4 to local folder"
      mkdir -p "${video_dest}/${date_time}"
      cp "${video_src}/${date_time}/${name}.mp4" "${video_dest}/"
    else
      echo "I would if I could find it here: ${video_src}/${date}/${date_time}/${name}.mp4"
      cam_without_dt=$(echo "$name" | cut -d "_" -f 2)
      fruit_without_dt=$(echo "$name" | cut -d "_" -f 3)
      sess_without_dt=$(echo "$name" | cut -d "_" -f 4)
      name_without_dt="${cam_without_dt}_${fruit_without_dt}_${sess_without_dt}"
      if [ -f "${video_src}/${date}/${date_time}/${name_without_dt}.mp4" ]; then
        echo "i did find ${video_src}/${date}/${date_time}/${name_without_dt}.mp4"
        mkdir -p "${video_dest}/${date_time}"
        cp "${video_src}/${date}/${date_time}/${name_without_dt}.mp4" "${video_dest}/${date_time}/${name}.mp4"
      fi
    fi
  fi
done

