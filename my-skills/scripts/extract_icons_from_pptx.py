#!/usr/bin/env python3
"""
Extract official AWS Architecture Icons from the AWS Icon Deck PPTX.

Reads the PPTX file, finds all 80x80 Architecture SVG icons,
maps them to short kebab-case names, and writes them to target directories.

Usage:
    python3 extract_icons_from_pptx.py <pptx_path> <output_dir> [--also <extra_dir>]

Example:
    python3 extract_icons_from_pptx.py \
        /Workshop/AWS-Architecture-Icon-Decks_07312025/AWS-Architecture-Icons-Deck_For-Dark-BG_07312025.pptx \
        /Workshop/ai-skills/my-skills/aws-diagram/icons \
        --also /Workshop/ai-skills/my-skills/myslide/icons
"""

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile

# Mapping from Arch_ ID fragments to short kebab-case names.
# Only icons that match these entries will be extracted.
# "AUTO" entries are auto-generated from the Arch_ name.
ICON_NAME_MAP = {
    # Compute
    "AWS-Lambda": "lambda",
    "Amazon-EC2": "ec2",
    "AWS-Fargate": "fargate",
    "Amazon-Elastic-Container-Service": "ecs",
    "Amazon-Elastic-Kubernetes-Service": "eks",
    "Amazon-EKS-Cloud": "eks",
    "AWS-Elastic-Beanstalk": "elastic-beanstalk",
    "Amazon-Lightsail": "lightsail",
    "AWS-Auto-Scaling": "auto-scaling",
    "Amazon-EC2-Auto-Scaling": "ec2-auto-scaling",
    "AWS-App-Runner": "app-runner",
    "AWS-Batch": "batch",
    "AWS-Outposts-family": "outposts",
    "AWS-Parallel-Cluster": "parallel-cluster",
    "AWS-Compute-Optimizer": "compute-optimizer",

    # Storage
    "Amazon-Simple-Storage-Service": "s3",
    "Amazon-Simple-Storage-Service-Glacier": "s3-glacier",
    "Amazon-EFS": "efs",
    "Amazon-Elastic-Block-Store": "ebs",
    "Amazon-FSx": "fsx",
    "Amazon-FSx-for-Lustre": "fsx-lustre",
    "Amazon-FSx-for-NetApp-ONTAP": "fsx-ontap",
    "Amazon-FSx-for-OpenZFS": "fsx-openzfs",
    "Amazon-FSx-for-WFS": "fsx-wfs",
    "AWS-Storage-Gateway": "storage-gateway",
    "AWS-Backup": "backup",
    "AWS-Snowball": "snowball",
    "AWS-Snowball-Edge": "snowball-edge",
    "Amazon-File-Cache": "file-cache",

    # Database
    "Amazon-DynamoDB": "dynamodb",
    "Amazon-Aurora": "aurora",
    "Amazon-RDS": "rds",
    "Amazon-Redshift": "redshift",
    "Amazon-DocumentDB": "documentdb",
    "Amazon-ElastiCache": "elasticache",
    "Amazon-MemoryDB-for-Redis": "memorydb",
    "Amazon-Neptune": "neptune",
    "Amazon-Keyspaces": "keyspaces",
    "Amazon-Timestream": "timestream",
    "Amazon-Quantum-Ledger-Database": "qldb",

    # Networking
    "Amazon-Virtual-Private-Cloud": "vpc",
    "Amazon-CloudFront": "cloudfront",
    "Amazon-Route-53": "route53",
    "AWS-Direct-Connect": "direct-connect",
    "Amazon-API-Gateway": "api-gateway",
    "Elastic-Load-Balancing": "elb",
    "AWS-Global-Accelerator": "global-accelerator",
    "AWS-Transit-Gateway": "transit-gateway",
    "AWS-PrivateLink": "privatelink",
    "Amazon-VPC-Lattice": "vpc-lattice",
    "AWS-Cloud-WAN": "cloud-wan",
    "AWS-Client-VPN": "client-vpn",
    "AWS-Site-to-Site-VPN": "site-to-site-vpn",
    "AWS-App-Mesh": "app-mesh",
    "AWS-Network-Firewall": "network-firewall",

    # Security
    "AWS-Key-Management-Service": "kms",
    "AWS-Shield": "shield",
    "AWS-WAF": "waf",
    "AWS-Identity-and-Access-Management": "iam",
    "Amazon-GuardDuty": "guardduty",
    "AWS-Security-Hub": "security-hub",
    "Amazon-Cognito": "cognito",
    "AWS-Secrets-Manager": "secrets-manager",
    "AWS-Certificate-Manager": "acm",
    "AWS-Firewall-Manager": "firewall-manager",
    "Amazon-Detective": "detective",
    "Amazon-Inspector": "inspector",
    "Amazon-Macie": "macie",
    "AWS-CloudHSM": "cloudhsm",
    "AWS-IAM-Identity-Center": "iam-identity-center",
    "AWS-Audit-Manager": "audit-manager",
    "AWS-Artifact": "artifact",
    "Amazon-Security-Lake": "security-lake",
    "Amazon-Verified-Permissions": "verified-permissions",
    "AWS-Verified-Access": "verified-access",
    "AWS-Private-Certificate-Authority": "private-ca",
    "AWS-Signer": "signer",
    "AWS-Security-Incident-Response": "security-incident-response",

    # Application Integration
    "Amazon-EventBridge": "eventbridge",
    "Amazon-Simple-Notification-Service": "sns",
    "Amazon-Simple-Queue-Service": "sqs",
    "AWS-Step-Functions": "step-functions",
    "Amazon-AppFlow": "appflow",
    "Amazon-MQ": "mq",
    "AWS-AppSync": "appsync",
    "Amazon-Managed-Workflows-for-Apache-Airflow": "mwaa",

    # AI/ML
    "Amazon-Bedrock": "bedrock",
    "Amazon-SageMaker": "sagemaker",
    "Amazon-Rekognition": "rekognition",
    "Amazon-Textract": "textract",
    "Amazon-Comprehend": "comprehend",
    "Amazon-Lex": "lex",
    "Amazon-Polly": "polly",
    "Amazon-Transcribe": "transcribe",
    "Amazon-Translate": "translate",
    "Amazon-Kendra": "kendra",
    "Amazon-Personalize": "personalize",
    "Amazon-Forecast": "forecast",
    "Amazon-Fraud-Detector": "fraud-detector",
    "Amazon-Q": "q",
    "Amazon-CodeGuru": "codeguru",
    "Amazon-Augmented-AI-A2I": "augmented-ai",
    "Amazon-SageMaker-Ground-Truth": "sagemaker-ground-truth",
    "Amazon-Comprehend-Medical": "comprehend-medical",
    "Amazon-HealthScribe": "healthscribe",
    "Amazon-Lookout-for-Vision": "lookout-vision",
    "Amazon-Lookout-for-Metrics": "lookout-metrics",
    "AWS-DeepRacer": "deepracer",
    "AWS-Panorama": "panorama",
    "AWS-Neuron": "neuron",
    "AWS-HealthImaging": "healthimaging",

    # Analytics
    "Amazon-Athena": "athena",
    "Amazon-Kinesis": "kinesis",
    "Amazon-Kinesis-Data-Streams": "kinesis-data-streams",
    "Amazon-Kinesis-Firehose": "data-firehose",
    "Amazon-OpenSearch-Service": "opensearch",
    "Amazon-QuickSight": "quicksight",
    "Amazon-EMR": "emr",
    "AWS-Glue": "glue",
    "AWS-Lake-Formation": "lake-formation",
    "Amazon-Managed-Streaming-for-Apache-Kafka": "msk",
    "Amazon-Managed-Service-for-Apache-Flink": "managed-flink",
    "AWS-Data-Exchange": "data-exchange",
    "Amazon-DataZone": "datazone",
    "Amazon-FinSpace": "finspace",
    "AWS-Glue-DataBrew": "glue-databrew",
    "Amazon-CloudSearch": "cloudsearch",

    # Management & Governance
    "Amazon-CloudWatch": "cloudwatch",
    "AWS-CloudFormation": "cloudformation",
    "AWS-CloudTrail": "cloudtrail",
    "AWS-Config": "config",
    "AWS-Systems-Manager": "systems-manager",
    "AWS-Organizations": "organizations",
    "AWS-X-Ray": "x-ray",
    "AWS-Trusted-Advisor": "trusted-advisor",
    "AWS-Control-Tower": "control-tower",
    "AWS-Service-Catalog": "service-catalog",
    "AWS-Well-Architected-Tool": "well-architected",
    "AWS-Personal-Health-Dashboard": "health-dashboard",
    "AWS-CloudShell": "cloudshell",
    "AWS-Management-Console": "management-console",
    "AWS-Distro-for-OpenTelemetry": "otel",
    "AWS-Managed-Services": "managed-services",
    "AWS-Chatbot": "chatbot",
    "AWS-Launch-Wizard": "launch-wizard",
    "AWS-Proton": "proton",
    "AWS-Resilience-Hub": "resilience-hub",
    "AWS-AppConfig": "appconfig",
    "AWS-License-Manager": "license-manager",
    "AWS-Resource-Explorer": "resource-explorer",

    # Developer Tools
    "AWS-CodeBuild": "codebuild",
    "AWS-CodePipeline": "codepipeline",
    "AWS-CodeCommit": "codecommit",
    "AWS-CodeDeploy": "codedeploy",
    "AWS-CodeArtifact": "codeartifact",
    "AWS-Cloud9": "cloud9",
    "Amazon-CodeCatalyst": "codecatalyst",
    "Amazon-Corretto": "corretto",
    "AWS-Cloud-Development-Kit": "cdk",
    "AWS-Command-Line-Interface": "cli",

    # Containers
    "Amazon-Elastic-Container-Registry": "ecr",
    "Amazon-ECS-Anywhere": "ecs-anywhere",
    "Amazon-EKS-Anywhere": "eks-anywhere",

    # Migration & Transfer
    "AWS-Migration-Hub": "migration-hub",
    "AWS-Database-Migration-Service": "dms",
    "AWS-DataSync": "datasync",
    "AWS-Transfer-Family": "transfer-family",
    "AWS-Application-Migration-Service": "application-migration",
    "AWS-Mainframe-Modernization": "mainframe-modernization",
    "AWS-Migration-Evaluator": "migration-evaluator",

    # End User Computing
    "Amazon-WorkSpaces-Family": "workspaces",
    "Amazon-AppStream": "appstream",

    # IoT
    "AWS-IoT-Core": "iot-core",
    "AWS-IoT-Greengrass": "iot-greengrass",
    "AWS-IoT-SiteWise": "iot-sitewise",
    "AWS-IoT-Events": "iot-events",
    "AWS-IoT-Analytics": "iot-analytics",
    "AWS-IoT-Device-Management": "iot-device-management",
    "AWS-IoT-Device-Defender": "iot-device-defender",
    "AWS-IoT-TwinMaker": "iot-twinmaker",
    "AWS-IoT-FleetWise": "iot-fleetwise",

    # Media Services
    "AWS-Elemental-MediaConvert": "mediaconvert",
    "AWS-Elemental-MediaLive": "medialive",
    "AWS-Elemental-MediaPackage": "mediapackage",
    "AWS-Elemental-MediaStore": "mediastore",
    "AWS-Elemental-MediaConnect": "mediaconnect",
    "AWS-Elemental-MediaTailor": "mediatailor",
    "Amazon-Interactive-Video-Service": "ivs",
    "Amazon-Kinesis-Video-Streams": "kinesis-video",

    # Business Applications
    "Amazon-Connect": "connect",
    "Amazon-Pinpoint-APIs": "pinpoint",
    "Amazon-Simple-Email-Service": "ses",
    "Amazon-Chime": "chime",
    "Amazon-Chime-SDK": "chime-sdk",
    "Amazon-WorkDocs": "workdocs",
    "Amazon-WorkMail": "workmail",

    # Cost Management
    "AWS-Cost-Explorer": "cost-explorer",
    "AWS-Budgets": "budgets",
    "AWS-Billing-Conductor": "billing-conductor",
    "AWS-Cost-and-Usage-Report": "cost-usage-report",
    "AWS-Marketplace_Dark": "marketplace",

    # Other
    "AWS-Amplify": "amplify",
    "AWS-Device-Farm": "device-farm",
    "AWS-Ground-Station": "ground-station",
    "Amazon-Braket": "braket",
    "Amazon-Location-Service": "location",
    "Amazon-GameLift": "gamelift",
    "Amazon-Managed-Blockchain": "managed-blockchain",
    "AWS-Private-5G": "private-5g",
    "AWS-Clean-Rooms": "clean-rooms",
    "AWS-Entity-Resolution": "entity-resolution",
    "AWS-Supply-Chain": "supply-chain",
    "Amazon-Omics": "omics",
    "Amazon-HealthLake": "healthlake",
    "Amazon-Monitron": "monitron",
    "Amazon-Managed-Grafana": "managed-grafana",
    "Amazon-Managed-Service-for-Prometheus": "managed-prometheus",
    "Amazon-DevOps-Guru": "devops-guru",
    "AWS-Fault-Injection-Service": "fis",
    "Amazon-Deadline-Cloud": "deadline-cloud",
    "AWS-Elastic-Disaster-Recovery": "disaster-recovery",
    "AWS-SimSpace-Weaver": "simspace-weaver",
    "AWS-Telco-Network-Builder": "telco-network-builder",
    "AWS-Wavelength": "wavelength",
    "AWS-Local-Zones": "local-zones",
    "AWS-Serverless-Application-Repository": "serverless-repo",
    "AWS-Express-Workflow": "express-workflow",
    "AWS-Support": "support",
    "AWS-IQ": "iq",
    "AWS-Professional-Services": "professional-services",
    "AWS-Activate": "activate",
    "AWS-re:Post": "repost",
    "AWS-rePost-Private": "repost-private",
    "AWS-Training-Certification": "training",
    "AWS-Tools-and-SDKs": "tools-sdks",
    "AWS-Wickr": "wickr",
    "AWS-Payment-Cryptography": "payment-cryptography",
    "AWS-B2B-Data-Interchange": "b2b-data-interchange",
    "AWS-Resource-Access-Manager": "ram",
    "AWS-Cloud-Map": "cloud-map",
    "AWS-Cloud-Control-API": "cloud-control-api",
    "AWS-Nitro-Enclaves": "nitro-enclaves",
    "AWS-Application-Composer": "application-composer",
    "AWS-Application-Discovery-Service": "application-discovery",
    "Amazon-EC2-Image-Builder": "ec2-image-builder",
    "Amazon-Cloud-Directory": "cloud-directory",
    "AWS-Directory-Service": "directory-service",
    "Elastic-Fabric-Adapter": "efa",
    "Amazon-Elastic-Transcoder": "elastic-transcoder",
    "Amazon-Elastic-Inference": "elastic-inference",
}


def extract_arch_name(svg_content):
    """Extract the Arch_ service name from SVG content."""
    match = re.search(r'Arch_([^"]+?)_64', svg_content)
    if match:
        return match.group(1)
    return None


def extract_icons(pptx_path, output_dir, extra_dirs=None):
    """Extract Architecture SVGs from PPTX and save with mapped names."""
    if extra_dirs is None:
        extra_dirs = []

    os.makedirs(output_dir, exist_ok=True)
    for d in extra_dirs:
        os.makedirs(d, exist_ok=True)

    extracted = {}
    skipped = []

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(pptx_path, "r") as zf:
            zf.extractall(tmpdir)

        media_dir = os.path.join(tmpdir, "ppt", "media")
        if not os.path.isdir(media_dir):
            print(f"No ppt/media directory found in {pptx_path}")
            sys.exit(1)

        svg_files = sorted(f for f in os.listdir(media_dir) if f.endswith(".svg"))
        print(f"Found {len(svg_files)} SVG files in PPTX")

        for svg_file in svg_files:
            svg_path = os.path.join(media_dir, svg_file)
            with open(svg_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Only process 80x80 Architecture icons
            if 'viewBox="0 0 80 80"' not in content:
                continue

            arch_name = extract_arch_name(content)
            if not arch_name:
                continue

            if arch_name in ICON_NAME_MAP:
                short_name = ICON_NAME_MAP[arch_name]
                target_path = os.path.join(output_dir, f"{short_name}.svg")

                # Don't overwrite if same short_name already extracted
                # (first match wins for duplicates like eks)
                if short_name in extracted:
                    continue

                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(content)
                extracted[short_name] = arch_name

                for extra_dir in extra_dirs:
                    extra_path = os.path.join(extra_dir, f"{short_name}.svg")
                    shutil.copy2(target_path, extra_path)
            else:
                skipped.append(arch_name)

    print(f"\nExtracted {len(extracted)} icons to {output_dir}")
    for extra_dir in extra_dirs:
        print(f"  Also copied to {extra_dir}")

    print(f"\nSkipped {len(skipped)} unmapped icons:")
    for name in sorted(skipped):
        print(f"  {name}")

    print(f"\nMapped icon list:")
    for short_name in sorted(extracted):
        print(f"  {short_name}.svg  <-  {extracted[short_name]}")

    return extracted


def main():
    parser = argparse.ArgumentParser(
        description="Extract AWS Architecture Icons from PPTX Icon Deck"
    )
    parser.add_argument("pptx_path", help="Path to AWS Icon Deck PPTX file")
    parser.add_argument("output_dir", help="Primary output directory for icons")
    parser.add_argument(
        "--also", nargs="*", default=[],
        help="Additional directories to copy icons to"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.pptx_path):
        print(f"PPTX file not found: {args.pptx_path}")
        sys.exit(1)

    extract_icons(args.pptx_path, args.output_dir, args.also)


if __name__ == "__main__":
    main()
