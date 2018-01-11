#!/bin/sh
echo "Please enter FTP [IP](ex: 140.112.107.150): "
read HOST
echo "Please enter FTP [USER NAME](ex: weal222c): "
read USER
echo "Please enter FTP [PASSWORD]: "
read PASSWD

cd src/display/
echo 'remove old files...'
rm graph/*.html

echo 'start generating files...'
python main.py


echo 'Please enter Compressed [File NAME](ex: graph.zip): '
read FILE
echo ''
echo 'zip & compress files...'
echo ''

zip -r $FILE graph

echo ''
echo 'transfer file to ftp(local/'$FILE')...'
echo ''

ftp -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
cd local
binary
put $FILE
quit
END_SCRIPT
rm $FILE

echo ''
echo 'done.'
echo ''

exit 0