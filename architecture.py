"""
Generates the architecture diagram as code (Diagram as Code).
Re-run after any design change to refresh architecture.png.

Setup:
    macOS:  brew install graphviz && pip install diagrams
    Linux:  sudo apt-get install graphviz && pip install diagrams

Run:
    python3 architecture.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import Jenkins
from diagrams.onprem.security import Trivy
from diagrams.onprem.iac import Terraform
from diagrams.onprem.client import User
from diagrams.aws.compute import ECR, EKS
from diagrams.aws.network import ELB

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.4",
    "splines": "spline",
    "nodesep": "0.6",
    "ranksep": "0.9",
}

with Diagram(
    "FastAPI CI/CD Pipeline",
    filename="architecture",
    outformat="png",
    direction="LR",
    graph_attr=graph_attr,
    show=False,
):
    github = Github("GitHub")

    with Cluster("CI (on push)"):
        jenkins_ci = Jenkins("Build & Test")
        trivy = Trivy("Security Scan")
        ecr = ECR("ECR")

        jenkins_ci >> Edge(label="build") >> trivy
        trivy >> Edge(label="push") >> ecr

    with Cluster("CD (auto-deploy)"):
        jenkins_cd = Jenkins("Infra Pipeline")
        terraform = Terraform("Terraform")
        eks = EKS("EKS")
        elb = ELB("Load Balancer")

        jenkins_cd >> Edge(label="apply") >> terraform
        terraform >> Edge(label="provision") >> eks
        eks >> Edge(label="expose") >> elb

    user = User("User")

    github >> Edge(label="webhook") >> jenkins_ci
    jenkins_ci - Edge(style="invis") - jenkins_cd
    trivy - Edge(style="invis") - terraform
    ecr >> Edge(label="triggers", style="dashed") >> jenkins_cd
    ecr >> Edge(label="deploy", style="dashed") >> eks
    elb - Edge(style="invis") - user
    elb >> Edge(label="HTTP") >> user