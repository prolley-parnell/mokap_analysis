video_list=$1

drive_mount="/media/persie/Storage/Segmentation"
annotation_dest="/home/persie/Code/segment/data/input"

folder_name=$2

mkdir -p "${annotation_dest}/${folder_name}"

cat ${video_list} | while read video_name || [[ -n $video_name ]];
do
#  frame_folder="$video_folder"/"$video_name"
  date=$(echo "$video_name" | cut -d "-" -f 1)
  date_time=$(echo "$video_name" | cut -d "/" -f 1)
  name=$(echo "$video_name" | cut -d "/" -f 2)
#  echo $name
#  echo $date_time
#  echo $date

  if [ ! -f "${annotation_dest}/${folder_name}/${name}.tar.bz2" ]; then
    if [ -f "${drive_mount}/${name}.tar.bz2" ]; then
      echo "Copying ${name}.tar.bz2 to local folder"
      cp "${drive_mount}/${name}.tar.bz2" "${annotation_dest}/${folder_name}/"
    else
      echo "I would if I could find it here: ${drive_mount}/${name}.tar.bz2"
    fi
  fi
done

