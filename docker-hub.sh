DOCKER_REPOSITORY_NAME=$1
#ID=DOCKER_HUB_ID
#PW=DOCKER_HUB_PW
ID=$2
PW=$3

# Change Directory
#cd compose-spring

echo "PWD now : $PWD"

#docker image의 첫 tag를 확인 후, 다음 버전의 image를 생성
#만약 처음 생성되는 이름이라면 0.01 이름으로 생성해준다.

TAG=$(docker images | awk -v DOCKER_REPOSITORY_NAME=$DOCKER_REPOSITORY_NAME '{if ($1 == DOCKER_REPOSITORY_NAME) print $2;}') || true
echo "Tag file is :"
echo $TAG

# 만약 [0-9]\.[0-9]{1,2} 으로 버전이 관리된 기존의 이미지 일 경우
if [[ $TAG =~ [0-9]\.[0-9]{1,2} ]]; then
    NEW_TAG_VER=$(echo $TAG 0.01 | awk '{print $1+$2}')
    echo "현재 버전은 $TAG 입니다."
    echo "새로운 버전은 $NEW_TAG_VER 입니다"

# 그 외 새롭게 만들거나, lastest or lts 등 tag 일 때
else
    # echo "새롭게 만들어진 이미지 입니다."
    NEW_TAG_VER=0.01
    echo "이전 버전이 없으므로 새롭게 생성된 버전은 $NEW_TAG_VER 입니다"
fi

echo "---current configuration---"
echo "TAG : $TAG"
echo "DOCKER_REPOSITORY_NAME : $DOCKER_REPOSITORY_NAME"
echo "NEW_TAG_VER : $NEW_TAG_VER"

# 현재 위치에 존재하는 DOCKER FILE을 사용하여 빌드
echo "Building image"
docker build --no-cache -t $DOCKER_REPOSITORY_NAME:$NEW_TAG_VER .

# docker hub에 push 하기위해 login
echo "Logging into Docker-hub"
docker login -u $ID -p $PW

echo "Removing previous version"
if [ $NEW_TAG_VER != "0.01" ]; then
    docker rmi $DOCKER_REPOSITORY_NAME:$TAG || true
fi

# 새로운 태그를 설정한 image를 생성
echo "Building image with new tag"
docker tag $DOCKER_REPOSITORY_NAME:$NEW_TAG_VER $ID/$DOCKER_REPOSITORY_NAME:$NEW_TAG_VER

# docker hub에 push
echo "Pushing image to Docker-hub"
docker push $ID/$DOCKER_REPOSITORY_NAME:$NEW_TAG_VER

# tag가 "latest"인 image를 최신 버전을 통해 생성
echo "Building image with latest tag"
docker tag $DOCKER_REPOSITORY_NAME:$NEW_TAG_VER $ID/$DOCKER_REPOSITORY_NAME:latest

# latest를 docker hub에 push
echo "Pusing image with latest tag to Docker-hub"
docker push $ID/$DOCKER_REPOSITORY_NAME:latest

# 버전 관리에 문제가 있어 latest를 삭제
docker rmi $ID/$DOCKER_REPOSITORY_NAME:latest || true
docker rmi $ID/$DOCKER_REPOSITORY_NAME:$NEW_TAG_VER || true