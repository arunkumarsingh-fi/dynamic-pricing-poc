# Dynamic iPhone Pricing System - Comprehensive HOW TO Guide

## 🏗️ Codebase Structure

```
dynamic_pricing_poc/
├── 📄 README.md                     # Project overview and basic setup
├── 📄 HOW_TO_GUIDE.md              # This comprehensive guide
├── 📄 podman-compose.yml           # Container orchestration
├── 📄 requirements.txt             # Python dependencies
├── 
├── 📁 data/                        # Data files
│   ├── processed_iphone_data.csv   # Processed iPhone pricing dataset
│   └── raw_data.csv               # Original raw data
├── 
├── 📁 ml_model/                    # Machine Learning API and models
│   ├── 📄 simple_price_api.py      # Main Flask API server
│   ├── 📄 requirements.txt         # ML API dependencies
│   ├── 📄 Dockerfile              # ML API container config
│   ├── 📄 profit_prediction.py     # Smart profit calculation logic
│   └── 📄 comprehensive_evaluation.py  # Model evaluation framework
├── 
├── 📁 ui_app/                      # Streamlit User Interface
│   ├── 📄 ui.py                   # Main Streamlit application
│   ├── 📄 requirements.txt        # UI dependencies
│   └── 📄 Dockerfile             # UI container config
├── 
├── 📁 tests/                       # Testing utilities
│   └── 📄 test_price_api.py       # API testing script
└── 
└── 📄 profit_demo.py              # Profit prediction demonstration
```

### 🔧 Core Components

#### 1. **ML API (`ml_model/simple_price_api.py`)**
- **Flask-based REST API** for price recommendations
- **iPhone model-aware pricing** with model-specific base values
- **Multi-tier pricing strategy** (Competitive/Market Rate/Premium)
- **Smart market analysis** considering inventory, damage, and specs
- **Multi currency support** with real-time conversions

#### 2. **Enhanced UI (`ui_app/ui.py`)**
- **Streamlit-based web interface** with 3 tabs:
  - 🏷️ **Price Recommendation**: iPhone model selection, specs input, smart feedback
  - 📊 **Analytics Dashboard**: Data visualization and insights
  - 📈 **Model Performance**: Feedback tracking and model metrics
- **iPhone Model Dropdown** with 18+ models (iPhone 11 to iPhone 15 Pro Max)
- **Smart Profit Calculation** based on sales outcomes
- **Real-time API integration** with error handling

#### 3. **Profit Prediction System (`ml_model/profit_prediction.py`)**
- **Automated profit calculation** replacing manual feedback
- **Sales outcome tracking**: Sold, Inventory, Returns, Price Reductions
- **Time-based penalties** for slow sales
- **Cost factor analysis** (acquisition, operational, holding costs)
- **Market-aware adjustments** for different iPhone models

## 🚀 How to Use the System

### 1. **Local Development Setup**

```bash
# Clone the repository
git clone <your-repo-url>
cd dynamic_pricing_poc

# Start the system
podman compose -f podman-compose.yml up --build -d

# Access the applications
# UI: http://localhost:8502
# API: http://localhost:5002
# Health Check: http://localhost:5002/health
```

### 2. **Using the UI**

1. **Select iPhone Model**: Choose from 18+ iPhone models with pre-filled specs
2. **Customize Specifications**: Adjust storage, RAM, battery, screen size, camera
3. **Set Market Conditions**: Configure inventory levels and market situation
4. **Get Price Recommendation**: AI-powered pricing with multiple tiers
5. **Provide Feedback**: Smart profit calculation based on actual sales outcomes

### 3. **API Usage**

```bash
# Get price recommendation
curl -X POST http://localhost:5002/recommend_price \
  -H "Content-Type: application/json" \
  -d '{
    "Model": "iPhone 15 Pro Max",
    "Storage": 256,
    "RAM": 8,
    "Battery": 95,
    "inventory_level": "low",
    "Backglass_Damage": 0,
    "Screen_Damage": 0
  }'

# Report sales outcome
curl -X POST http://localhost:5002/report_outcome \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "your-decision-id",
    "reward": 75.50
  }'
```

## 📦 How to Push Code to Git Repository

### 1. **Initialize Git Repository**

```bash
# Initialize git (if not already done)
git init

# Add remote repository
git remote add origin https://github.com/yourusername/dynamic-pricing-poc.git

# Check current status
git status
```

### 2. **Commit and Push Changes**

```bash
# Add all files
git add .

# Commit with descriptive message
git commit -m "feat: Enhanced iPhone pricing system with model selection and smart profit feedback

- Added iPhone model dropdown with 18+ models
- Integrated smart profit prediction system
- Enhanced UI with sales outcome tracking
- Improved API with model-specific pricing
- Added comprehensive evaluation framework
- Updated containers with volume mounts for live development"

# Push to main branch
git push -u origin main

# For subsequent pushes
git push origin main
```

### 3. **Git Workflow Best Practices**

```bash
# Create feature branch
git checkout -b feature/new-enhancement

# Make changes and commit
git add .
git commit -m "feat: Add new enhancement"

# Push feature branch
git push origin feature/new-enhancement

# Merge to main (after PR approval)
git checkout main
git pull origin main
git merge feature/new-enhancement
git push origin main

# Delete feature branch
git branch -d feature/new-enhancement
git push origin --delete feature/new-enhancement
```

## ☁️ Cloud Deployment Guide

### 🔵 Azure Deployment (Azure Container Instances)

#### Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Create resource group
az group create --name dynamic-pricing-rg --location eastus
```

#### Step 1: Push Images to Azure Container Registry

```bash
# Create Azure Container Registry
az acr create --name dynamicpricingreg --resource-group dynamic-pricing-rg --sku Standard --admin-enabled true

# Get ACR credentials
az acr credential show --name dynamicpricingreg

# Build and push ML API image
podman build -t dynamicpricingreg.azurecr.io/ml-api:latest ./ml_model
podman login dynamicpricingreg.azurecr.io
podman push dynamicpricingreg.azurecr.io/ml-api:latest

# Build and push UI image
podman build -t dynamicpricingreg.azurecr.io/ui-app:latest ./ui_app
podman push dynamicpricingreg.azurecr.io/ui-app:latest
```

#### Step 2: Deploy ML API Container

```bash
# Create ML API container instance
az container create \
  --resource-group dynamic-pricing-rg \
  --name ml-api-container \
  --image dynamicpricingreg.azurecr.io/ml-api:latest \
  --registry-login-server dynamicpricingreg.azurecr.io \
  --registry-username dynamicpricingreg \
  --registry-password <acr-password> \
  --dns-name-label dynamic-pricing-ml-api \
  --ports 5002 \
  --cpu 1 \
  --memory 2 \
  --environment-variables 'FLASK_ENV=production'
```

#### Step 3: Deploy UI Container

```bash
# Create UI container instance
az container create \
  --resource-group dynamic-pricing-rg \
  --name ui-app-container \
  --image dynamicpricingreg.azurecr.io/ui-app:latest \
  --registry-login-server dynamicpricingreg.azurecr.io \
  --registry-username dynamicpricingreg \
  --registry-password <acr-password> \
  --dns-name-label dynamic-pricing-ui \
  --ports 8502 \
  --cpu 1 \
  --memory 2 \
  --environment-variables 'ML_API_URL=http://dynamic-pricing-ml-api.eastus.azurecontainer.io:5002'
```

#### Step 4: Configure Networking (Optional - Azure Container Apps)

```bash
# For better networking, use Azure Container Apps
az extension add --name containerapp

# Create Container Apps environment
az containerapp env create \
  --name dynamic-pricing-env \
  --resource-group dynamic-pricing-rg \
  --location eastus

# Deploy ML API
az containerapp create \
  --name ml-api-app \
  --resource-group dynamic-pricing-rg \
  --environment dynamic-pricing-env \
  --image dynamicpricingreg.azurecr.io/ml-api:latest \
  --registry-server dynamicpricingreg.azurecr.io \
  --registry-username dynamicpricingreg \
  --registry-password <acr-password> \
  --target-port 5002 \
  --ingress external \
  --query properties.configuration.ingress.fqdn

# Deploy UI App
az containerapp create \
  --name ui-app \
  --resource-group dynamic-pricing-rg \
  --environment dynamic-pricing-env \
  --image dynamicpricingreg.azurecr.io/ui-app:latest \
  --registry-server dynamicpricingreg.azurecr.io \
  --registry-username dynamicpricingreg \
  --registry-password <acr-password> \
  --target-port 8502 \
  --ingress external \
  --env-vars ML_API_URL=https://<ml-api-fqdn> \
  --query properties.configuration.ingress.fqdn
```

### 🟠 AWS Deployment (Amazon ECS with Fargate)

#### Prerequisites
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure

# Install ECS CLI
sudo curl -Lo /usr/local/bin/ecs-cli https://amazon-ecs-cli.s3.amazonaws.com/ecs-cli-linux-amd64-latest
sudo chmod +x /usr/local/bin/ecs-cli
```

#### Step 1: Create ECR Repositories and Push Images

```bash
# Create ECR repositories
aws ecr create-repository --repository-name dynamic-pricing/ml-api --region us-east-1
aws ecr create-repository --repository-name dynamic-pricing/ui-app --region us-east-1

# Get ECR login token
aws ecr get-login-password --region us-east-1 | podman login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push ML API image
podman build -t <account-id>.dkr.ecr.us-east-1.amazonaws.com/dynamic-pricing/ml-api:latest ./ml_model
podman push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dynamic-pricing/ml-api:latest

# Tag and push UI image
podman build -t <account-id>.dkr.ecr.us-east-1.amazonaws.com/dynamic-pricing/ui-app:latest ./ui_app
podman push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dynamic-pricing/ui-app:latest
```

#### Step 2: Create ECS Cluster

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name dynamic-pricing-cluster --capacity-providers FARGATE --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
```

#### Step 3: Create Task Definition

Create `ecs-task-definition.json`:

```json
{
    "family": "dynamic-pricing-tasks",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "1024",
    "memory": "2048",
    "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "ml-api",
            "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/dynamic-pricing/ml-api:latest",
            "portMappings": [
                {
                    "containerPort": 5002,
                    "protocol": "tcp"
                }
            ],
            "essential": true,
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/dynamic-pricing",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ml-api"
                }
            }
        },
        {
            "name": "ui-app",
            "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/dynamic-pricing/ui-app:latest",
            "portMappings": [
                {
                    "containerPort": 8502,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "ML_API_URL",
                    "value": "http://localhost:5002"
                }
            ],
            "dependsOn": [
                {
                    "containerName": "ml-api",
                    "condition": "START"
                }
            ],
            "essential": true,
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/dynamic-pricing",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ui-app"
                }
            }
        }
    ]
}
```

#### Step 4: Register Task Definition and Create Service

```bash
# Create CloudWatch log group
aws logs create-log-group --log-group-name /ecs/dynamic-pricing --region us-east-1

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create VPC and security groups (if needed)
aws ec2 create-vpc --cidr-block 10.0.0.0/16
# ... (additional VPC setup)

# Create ECS service
aws ecs create-service \
  --cluster dynamic-pricing-cluster \
  --service-name dynamic-pricing-service \
  --task-definition dynamic-pricing-tasks:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-67890],assignPublicIp=ENABLED}"
```

#### Step 5: Set Up Application Load Balancer

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name dynamic-pricing-alb \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-abcdef

# Create target groups for both services
aws elbv2 create-target-group \
  --name ml-api-targets \
  --protocol HTTP \
  --port 5002 \
  --vpc-id vpc-12345 \
  --target-type ip

aws elbv2 create-target-group \
  --name ui-app-targets \
  --protocol HTTP \
  --port 8502 \
  --vpc-id vpc-12345 \
  --target-type ip

# Create listeners and rules
aws elbv2 create-listener \
  --load-balancer-arn <alb-arn> \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=<ui-target-group-arn>
```

## 🔍 Monitoring and Maintenance

### Application Health Checks

```bash
# API Health Check
curl http://your-domain.com/health

# Expected Response
{
  "status": "healthy",
  "service": "Simple Price Recommendation API",
  "version": "1.0",
  "currency": "EUR"
}
```

### Log Monitoring

```bash
# Azure Container Instances
az container logs --resource-group dynamic-pricing-rg --name ml-api-container

# AWS ECS
aws logs get-log-events --log-group-name /ecs/dynamic-pricing --log-stream-name ml-api/ml-api/<task-id>
```

### Scaling Considerations

- **Horizontal Scaling**: Increase container instances during peak usage
- **Vertical Scaling**: Increase CPU/memory for individual containers
- **Database Integration**: Consider adding persistent storage for feedback data
- **Load Balancing**: Distribute traffic across multiple container instances
- **Caching**: Implement Redis for frequently accessed price recommendations

## 🛡️ Security Best Practices

1. **API Security**:
   - Implement API key authentication
   - Add rate limiting
   - Use HTTPS in production
   - Validate all input data

2. **Container Security**:
   - Use minimal base images
   - Regular security updates
   - Non-root container users
   - Secret management for credentials

3. **Cloud Security**:
   - VPC/Virtual Network isolation
   - Security groups/Network ACLs
   - Managed identity for cloud resources
   - Regular security audits

## 📈 Performance Optimization

1. **API Performance**:
   - Implement caching for model predictions
   - Use async processing for heavy operations
   - Database connection pooling
   - Response compression

2. **UI Performance**:
   - Streamlit caching for expensive operations
   - Optimize data loading
   - Progressive loading for large datasets
   - Client-side validation

3. **Infrastructure**:
   - CDN for static assets
   - Auto-scaling policies
   - Health checks and monitoring
   - Load balancer optimization

## 🎯 Next Steps and Enhancements

1. **Advanced ML Models**: Integrate actual bandit algorithms (LinTS, LinUCB)
2. **Database Integration**: Add PostgreSQL/MongoDB for persistent storage
3. **Real-time Analytics**: Implement streaming analytics with Apache Kafka
4. **A/B Testing**: Built-in experimentation framework
5. **Mobile API**: REST API for mobile applications
6. **Multi-tenant**: Support for multiple businesses/stores
7. **Advanced Security**: OAuth2, JWT tokens, audit logging
8. **CI/CD Pipeline**: GitHub Actions or Azure DevOps integration

---

## 📞 Support and Troubleshooting

### Common Issues

1. **Container won't start**: Check logs and resource limits
2. **API connection errors**: Verify network configuration and firewall rules
3. **UI not loading**: Check environment variables and API endpoints
4. **Performance issues**: Monitor resource usage and scaling policies

### Getting Help

- 📧 **Email Support**: Create issues in your Git repository
- 📚 **Documentation**: Refer to this guide and code comments
- 🔧 **Debugging**: Use container logs and health endpoints
- 🤝 **Community**: Share improvements and extensions

---

**Happy Coding! 🚀📱💰**

*This system provides a solid foundation for dynamic iPhone pricing with ML capabilities, smart profit prediction, and cloud-ready architecture. Extend and customize it based on your specific business needs.*
