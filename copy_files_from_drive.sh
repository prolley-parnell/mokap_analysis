video_list=$1
folder_name=$2

drive_mount="/media/persie/Storage/AntVideos"
video_dest="/home/persie/Code/sleap/infer/input/"

mkdir -p "${video_dest}/${folder_name}"

cat ${video_list} | while read video_name || [[ -n $video_name ]];
do
  date=$(echo "$video_name" | cut -d "-" -f 1)
  date_time=$(echo "$video_name" | cut -d "/" -f 1)
  name=$(echo "$video_name" | cut -d "/" -f 2)

  if [ ! -f "${video_dest}/${folder_name}/${date_time}/${name}.mp4" ]; then
    #cp "${drive_mount}/${date}/${date_time}/${name}.mp4" "${video_dest}/${date_time}"
    if [ -f "${drive_mount}/${date}/${date_time}/${name}.mp4" ]; then
      echo "Copying ${name}.mp4 to local folder"
      cp "${drive_mount}/${date}/${date_time}/${name}.mp4" "${video_dest}/${folder_name}/"
    else
      echo "I would if I could find it here: ${drive_mount}/${date}/${date_time}/${name}.mp4"
      cam_without_dt=$(echo "$name" | cut -d "_" -f 2)
      fruit_without_dt=$(echo "$name" | cut -d "_" -f 3)
      sess_without_dt=$(echo "$name" | cut -d "_" -f 4)
      name_without_dt="${cam_without_dt}_${fruit_without_dt}_${sess_without_dt}"
      if [ -f "${drive_mount}/${date}/${date_time}/${name_without_dt}.mp4" ]; then
        echo "i did find ${drive_mount}/${date}/${date_time}/${name_without_dt}.mp4"
        cp "${drive_mount}/${date}/${date_time}/${name_without_dt}.mp4" "${video_dest}/${folder_name}/${name}.mp4"
      fi
    fi
  fi
done

