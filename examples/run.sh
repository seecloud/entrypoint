#!/bin/bash -ex

cwd=$(dirname $0)
dockip() {
    docker inspect --format '{{ .NetworkSettings.IPAddress }}' $1
}

# 1. Build testing images

pushd $cwd/etcd
    docker build -t entry_etcd .
popd

pushd $cwd/..
   docker build -t entry_base .
popd

pushd $cwd/service
    docker build -t entry_service .
popd

# 2. Run etcd service

etcd_id=$(docker run -d --name entry_etcd entry_etcd:latest)
etcd_ip=$(dockip $etcd_id)

# 3. Upload config for the service "service-a"
sleep 5

service_a_conf='{"parameter": "value_a"}'
etcdctl --endpoint=http://${etcd_ip}:2379/ set /service-a/config "$service_a_conf"

# 4. Run container with service-a
serva_id=$(docker run -d \
            --env SERVICE_NAME=service-a \
            --env ENVIRONMENT=etcd \
            --env ETCD_HOSTS=$etcd_ip:2379 \
            entry_service:latest)
serva_ip=$(dockip $serva_id)


# 5. The service is a simple HTTP server that returns its config
# let's try to get it from service and ensure that it was get from etcd
sleep 5

service_a_cur_conf=$(curl http://$serva_ip:8000/)
[[ "$service_a_conf" == "$service_a_cur_conf" ]] && echo "SUCCESS" || echo "FAILURE"

# 6. Try to run service "service-b" with the default config

servb_id=$(docker run -d \
            --env SERVICE_NAME=service-b \
            entry_service:latest)
servb_ip=$(dockip $servb_id)

# 7. Try to get its config
sleep 5

service_default_conf='{"parameter": "default"}'
service_b_cur_conf=$(curl http://$servb_ip:8000/)
[[ "$service_b_cur_conf" == "$service_default_conf" ]] && echo "SUCCESS" || echo "FAILURE"

#. 8. That's it

echo "To stop containers and remove them run the following command:
docker kill $etcd_id $serva_id
docker rm $etcd_id $serva_id"
echo "To remove built images run the following command:
docker rmi entry_etcd entry_base entry_service"
