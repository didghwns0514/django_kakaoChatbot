
#echo "Change current directory"
#cd compose-spring

echo "Pull newest image to local Container"
docker pull korshika/stockmanager-back-django:latest

echo "Remove daningling images"
docker rmi -f $(docker images -f "dangling=true" -q) || true

echo "Stop container if exists"
docker stop StockManager-Django-Server && docker rm StockManager-Django-Server
docker stop StockManager-Django-Server1 && docker rm StockManager-Django-Server1
docker stop StockManager-Django-Server2 && docker rm StockManager-Django-Server2
echo "Run the newest image"
cd ..
echo "Current PWD : $PWD"
echo "Current files ls : "
ls

# BackUp and data gen
docker run  --name StockManager-Django-Server1 -d -p 5550:5552  \
  -e PYTHONUNBUFFERED=1  \
  -e DJANGO_SECRET='django-insecure-dgbp!q_yauu-j)udgh*wa(ml-epuw#_&8hh=afgs_ocy_)#vtl'  \
  -e DB_USERNAME='root' \
  -e DB_PASSWORD='d@12YinYang' \
  -e DEBUG=0 \
  -e IS_MAIN_SERVER=0 \
  --network shareNetwork_stockmanager \
  --ip=172.22.0.6 \
  korshika/stockmanager-back-django:latest
#-v StockManager:/usr/src/app/staticfiles \
# -> static files served from Main server

# Main and no data gen
docker run  --name StockManager-Django-Server2 -d -p 5551:5552  \
  -e PYTHONUNBUFFERED=1  \
  -e DJANGO_SECRET='django-insecure-dgbp!q_yauu-j)udgh*wa(ml-epuw#_&8hh=afgs_ocy_)#vtl'  \
  -e DB_USERNAME='root' \
  -e DB_PASSWORD='d@12YinYang' \
  -e DEBUG=0 \
  -e IS_MAIN_SERVER=1 \
  -v StockManager:/usr/src/app/staticfiles \
  --network shareNetwork_stockmanager \
  --ip=172.22.0.7 \
  korshika/stockmanager-back-django:latest

# ip : Shared network 설정이후, ip 고정으로 할당
#  -> Ngnix에서 볼 수 있도록 하기 위함
#-v StockManager:/django_home \

echo ""
echo "---------------------"
echo "Check Running Dockers"
docker ps -a