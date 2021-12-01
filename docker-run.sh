
#echo "Change current directory"
#cd compose-spring

echo "Pull newest image to local Container"
docker pull korshika/stockmanager-back-django:latest

echo "Remove daningling images"
docker rmi -f $(docker images -f "dangling=true" -q) || true

echo "Stop container if exists"
docker stop StockManager-Django-Server && docker rm StockManager-Django-Server

echo "Run the newest image"
cd ..
echo "Current PWD : $PWD"
echo "Current files ls : "
ls

docker run  --name StockManager-Django-Server -d -p 5552:8080  \
  -e DJANGO_SECRET="django-insecure-dgbp!q_yauu-j)udgh*wa(ml-epuw#_&8hh=afgs_ocy_)#vtl"  \
  -e DB_USERNAME="root" \
  -e DB_PASSWORD="d@12YinYang" \
  korshika/stockmanager-back-django:latest


echo ""
echo "---------------------"
echo "Check Running Dockers"
docker ps -a