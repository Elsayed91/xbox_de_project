#!/bin/bash
set -e
source "./.env"
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)



# echo "Setting Up GCP Components."
# echo "you will be prompted to login to your gcloud account, kindly do so."
# gcloud auth application-default login --project $PROJECT -q

# echo "Creating project $PROJECT"
# gcloud projects create $PROJECT >/dev/null

# echo "Setting the project as default project"
# gcloud config set project $PROJECT >/dev/null

# echo "Linking the billing account with the project. If this is your first time \
#     doing this, you might be prompted to say yes once or twice."
# gcloud beta billing projects link $PROJECT --billing-account=$GCP_BILLING_ACCOUNT >/dev/null

# echo "turning on APIs needed for the project"
# API_LIST=(iam iamcredentials compute servicemanagement storage
#     bigqueryconnection cloudresourcemanager artifactregistry containerregistry
#     container cloudbuild cloudresourcemanager bigquery)

# for SERVICE in "${API_LIST[@]}"; do
#     gcloud services enable ${SERVICE}.googleapis.com --async --project $PROJECT >/dev/null
# done


# echo "sleep 60 seconds to ensure that apis are turned on"
# sleep 60

# gcloud config set compute/zone $GCP_ZONE >/dev/null

# gcloud compute disks create --size=2GB nfs-disk

# gcloud auth configure-docker "${GCP_REGION}-docker.pkg.dev" -q >/dev/null
# gcloud config set builds/use_kaniko True
# bq --location=${GCP_REGION} mk -d \
#     twitter_data
# bq --location=${GCP_REGION} mk -d \
#     vgchartz_data
# bq --location=${GCP_REGION} mk -d \
#     metacritic_data

# gcloud container clusters create ${GKE_CLUSTER_NAME}  \
#     --zone=${GCP_ZONE} \
#     --workload-pool=${PROJECT}.svc.id.goog \
#     --machine-type=e2-standard-4  \
#     --enable-autoscaling \
#     --min-nodes=0 \
#     --max-nodes=20 \
#     --workload-metadata=GKE_METADATA \
#     --spot \
#     --disk-size=40 \
#     --num-nodes=1

# gcloud iam service-accounts create gke-sa \
#     --project=${PROJECT}

gcloud projects add-iam-policy-binding ${PROJECT} \
    --member "serviceAccount:gke-sa@${PROJECT}.iam.gserviceaccount.com" \
    --role "roles/owner"

gcloud iam service-accounts add-iam-policy-binding gke-sa@${PROJECT}.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:${PROJECT}.svc.id.goog[default/default]"

gcloud container clusters get-credentials $GKE_CLUSTER_NAME \
    --project=$PROJECT --region=$GCP_ZONE

kubectl annotate serviceaccount default --overwrite \
    iam.gke.io/gcp-service-account=gke-sa@${PROJECT}.iam.gserviceaccount.com

kubectl create secret docker-registry gcr-json-key \
    --docker-server="${DOCKER_SERVER}" --docker-username="${DOCKER_USERNAME}" \
    --docker-password="$(gcloud auth print-access-token)" --docker-email=any@valid.email

kubectl patch serviceaccount default \
    -p '{"imagePullSecrets": [{"name": "gcr-json-key"}]}'
kubectl create clusterrolebinding admin-role \
    --clusterrole=cluster-admin --serviceaccount=default:default

kubectl port-forward pod/airflow-67c48b75d9-8m972  8080:8080
# gcloud builds submit

for FILE in ./manifests/*; do
    [[ -e "$FILE" ]] || continue
    cat "$FILE" | envsubst | kubectl apply -f -
done

# kubectl wait --for=condition=Ready $(kubectl get pods -o name | grep airflow) --timeout=100s
# airflow_pod=$(kubectl get pods -o name --field-selector=status.phase=Running | grep airflow)
# sleep 20
# kubectl exec -t $airflow_pod -c scheduler -- airflow dags unpause scrapers
# pods=$(kubectl get pods | grep -E "Error|CrashLoopBackOff|Completed|Terminated|ImagePullBackOff" | cut -d' ' -f 1)
# if [ -n "$pods" ]; then
#     kubectl delete pod $pods
# fi


