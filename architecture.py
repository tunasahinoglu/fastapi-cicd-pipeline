"""
Generates the project's architecture diagram as code (Diagram as Code).
Re-run it whenever the design changes to refresh the image used in the README.

Setup:
    sudo apt-get install graphviz
    pip install diagrams

Run:
    python3 architecture.py
    # -> produces architecture.png
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import Jenkins
from diagrams.onprem.security import Trivy
from diagrams.onprem.iac import Terraform
from diagrams.aws.compute import ECR, EKS

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.4",
    "splines": "spline",
}

with Diagram(
    "FastAPI CI/CD Pipeline",
    filename="architecture",
    outformat="png",
    direction="LR",
    graph_attr=graph_attr,
    show=False,
):
    github = Github("GitHub Repo\n(push)")

    with Cluster("CI Pipeline — automatic\n(on every push)"):
        jenkins_ci = Jenkins("Build & Test\n(lint, pytest, sonarqube)")
        trivy = Trivy("Image Security Scan")
        ecr = ECR("Amazon ECR")

        jenkins_ci >> Edge(label="docker build") >> trivy
        trivy >> Edge(label="push") >> ecr

    with Cluster("CD Pipeline — manual\n(on demand)"):
        terraform = Terraform("terraform apply")
        eks = EKS("EKS Cluster")

        terraform >> Edge(label="provision") >> eks

    github >> Edge(label="webhook") >> jenkins_ci
    ecr >> Edge(label="helm deploy\n(image pull)", style="dashed") >> eks
