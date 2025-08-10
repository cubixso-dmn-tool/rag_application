#!/bin/bash

# Azure deployment script for RAG Application

# Set variables
RESOURCE_GROUP="rag-app-rg"
LOCATION="eastus"
ACR_NAME="ragappregistry$(date +%s)"
APP_NAME="rag-api-app$(date +%s)"
IMAGE_NAME="rag-api"
TAG="latest"

echo "Starting Azure deployment for RAG Application..."

# Login to Azure (if not already logged in)
echo "Logging into Azure..."
az login

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Build and push Docker image
echo "Building and pushing Docker image..."
az acr build --registry $ACR_NAME --image $IMAGE_NAME:$TAG .

# Create Azure Container Instance (Alternative 1 - Simple deployment)
echo "Creating Azure Container Instance..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --image $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG \
    --registry-login-server $ACR_NAME.azurecr.io \
    --registry-username $ACR_NAME \
    --registry-password $(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv) \
    --dns-name-label $APP_NAME \
    --ports 8000 \
    --environment-variables AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
    --cpu 1 \
    --memory 2

# Get the FQDN
echo "Getting application URL..."
FQDN=$(az container show --resource-group $RESOURCE_GROUP --name $APP_NAME --query "ipAddress.fqdn" --output tsv)

echo "Deployment complete!"
echo "Application URL: http://$FQDN:8000"
echo "Health check: http://$FQDN:8000/health"
echo "API Documentation: http://$FQDN:8000/docs"