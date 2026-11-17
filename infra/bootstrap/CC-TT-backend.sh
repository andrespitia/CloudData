#!/usr/bin/env bash
#Crea UNA SOLA VEZ el almacenamiento remoto del estado de Terraform.
#Uso: bash infra/bootstrap/crear_backend.sh cloudterraformandrespi
set -euo pipefail

REGION="denmarkeast"
GRUPO="H3-CC-TT-terraform"
CUENTA="${1:?cloudterraformandrespi}"
CONTENEDOR="tfstate"

echo "Grupo de recursos del estado"
az group create --name "$GRUPO" --location "$REGION" -o table

echo "Storage Account (privado, solo HTTPS, TLS 1.2)"
az storage account create \
  --name "$CUENTA" --resource-group "$GRUPO" --location "$REGION" \
  --sku Standard_LRS --kind StorageV2 \
  --min-tls-version TLS1_2 --https-only true \
  --allow-blob-public-access false -o table

echo "Versionado: guarda versiones anteriores del estado"
az storage account blob-service-properties update \
  --account-name "$CUENTA" --resource-group "$GRUPO" \
  --enable-versioning true -o table

echo "Contenedor privado para el estado"
az storage container-rm create \
  --name "$CONTENEDOR" --storage-account "$CUENTA" --resource-group "$GRUPO" \
  --public-access off -o table

echo "Backend listo: $GRUPO / $CUENTA / $CONTENEDOR"