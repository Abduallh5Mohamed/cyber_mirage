#!/usr/bin/env python3
"""
Cyber Mirage v5.0 - Deployment Validation Script
تحقق شامل من صحة التكوينات قبل الـ Deployment
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(title: str):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


def print_success(msg: str):
    print(f"  {GREEN}✓{RESET} {msg}")


def print_error(msg: str):
    print(f"  {RED}✗{RESET} {msg}")


def print_warning(msg: str):
    print(f"  {YELLOW}⚠{RESET} {msg}")


def print_info(msg: str):
    print(f"  {BLUE}ℹ{RESET} {msg}")


class DeploymentValidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
        
    def validate_all(self) -> Tuple[int, int, int]:
        """Run all validation checks"""
        print_header("Cyber Mirage v5.0 - Deployment Validation")
        
        self.check_required_files()
        self.check_docker_compose()
        self.check_docker_compose_production()
        self.check_dockerfiles()
        self.check_kubernetes()
        self.check_requirements()
        self.check_config_files()
        self.check_env_files()
        self.check_source_structure()
        self.check_credentials_consistency()
        
        self.print_summary()
        return len(self.successes), len(self.warnings), len(self.errors)
    
    def check_required_files(self):
        """Check for required project files"""
        print_header("Required Files Check")
        
        required_files = [
            "docker-compose.yml",
            "docker-compose.production.yml",
            "Dockerfile",
            "requirements.txt",
            "requirements-production.txt",
            "README.md",
            ".env.example",
            "config/app.yml",
            "k8s/deployment.yml",
        ]
        
        for file in required_files:
            filepath = self.project_root / file
            if filepath.exists():
                print_success(f"Found: {file}")
                self.successes.append(f"Required file exists: {file}")
            else:
                print_error(f"Missing: {file}")
                self.errors.append(f"Required file missing: {file}")
    
    def check_docker_compose(self):
        """Validate docker-compose.yml"""
        print_header("Docker Compose (Development) Validation")
        
        compose_file = self.project_root / "docker-compose.yml"
        if not compose_file.exists():
            print_error("docker-compose.yml not found")
            return
        
        try:
            with open(compose_file, encoding="utf-8") as f:
                compose = yaml.safe_load(f)
            
            # Check version
            if "version" in compose:
                print_success(f"Version: {compose['version']}")
            
            # Check services
            services = compose.get("services", {})
            required_services = ["postgres", "redis"]
            
            for svc in required_services:
                if svc in services:
                    print_success(f"Service defined: {svc}")
                    self.successes.append(f"docker-compose.yml has service: {svc}")
                else:
                    print_warning(f"Missing service: {svc}")
                    self.warnings.append(f"docker-compose.yml missing service: {svc}")
            
            # Check healthchecks
            for svc_name, svc_config in services.items():
                if "healthcheck" in svc_config:
                    print_success(f"Healthcheck defined for: {svc_name}")
                else:
                    print_warning(f"No healthcheck for: {svc_name}")
                    
        except yaml.YAMLError as e:
            print_error(f"Invalid YAML: {e}")
            self.errors.append(f"docker-compose.yml has invalid YAML: {e}")
        except Exception as e:
            print_error(f"Error reading file: {e}")
            self.errors.append(f"docker-compose.yml error: {e}")
    
    def check_docker_compose_production(self):
        """Validate docker-compose.production.yml"""
        print_header("Docker Compose (Production) Validation")
        
        compose_file = self.project_root / "docker-compose.production.yml"
        if not compose_file.exists():
            print_error("docker-compose.production.yml not found")
            return
        
        try:
            with open(compose_file, encoding="utf-8") as f:
                compose = yaml.safe_load(f)
            
            services = compose.get("services", {})
            
            # Production should have these services
            required_services = [
                "postgres", "redis", "ai-engine", "honeypots",
                "dashboard", "prometheus", "grafana"
            ]
            
            for svc in required_services:
                if svc in services:
                    print_success(f"Production service: {svc}")
                    self.successes.append(f"Production has service: {svc}")
                else:
                    print_error(f"Missing production service: {svc}")
                    self.errors.append(f"Production missing service: {svc}")
            
            # Check for resource limits
            for svc_name, svc_config in services.items():
                deploy = svc_config.get("deploy", {})
                resources = deploy.get("resources", {})
                if resources:
                    print_success(f"Resource limits for: {svc_name}")
                else:
                    print_warning(f"No resource limits for: {svc_name}")
                    self.warnings.append(f"No resource limits for: {svc_name}")
                    
        except yaml.YAMLError as e:
            print_error(f"Invalid YAML: {e}")
            self.errors.append(f"docker-compose.production.yml invalid YAML: {e}")
        except Exception as e:
            print_error(f"Error: {e}")
            self.errors.append(f"docker-compose.production.yml error: {e}")
    
    def check_dockerfiles(self):
        """Validate Dockerfiles"""
        print_header("Dockerfile Validation")
        
        dockerfiles = [
            "Dockerfile",
            "docker/Dockerfile.ai-minimal",
            "docker/Dockerfile.dashboard",
            "docker/Dockerfile.honeypot",
        ]
        
        for df in dockerfiles:
            filepath = self.project_root / df
            if filepath.exists():
                print_success(f"Found: {df}")
                
                # Basic Dockerfile checks
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()
                
                if "FROM" in content:
                    print_success(f"  Has FROM instruction")
                else:
                    print_error(f"  Missing FROM instruction")
                    self.errors.append(f"{df} missing FROM instruction")
                
                if "HEALTHCHECK" in content:
                    print_success(f"  Has HEALTHCHECK")
                else:
                    print_warning(f"  No HEALTHCHECK")
                    self.warnings.append(f"{df} missing HEALTHCHECK")
                    
                if "USER" in content and "root" not in content.split("USER")[-1].split()[0]:
                    print_success(f"  Uses non-root user")
                else:
                    print_warning(f"  May run as root")
            else:
                print_error(f"Missing: {df}")
                self.errors.append(f"Dockerfile missing: {df}")
    
    def check_kubernetes(self):
        """Validate Kubernetes manifests"""
        print_header("Kubernetes Manifests Validation")
        
        k8s_file = self.project_root / "k8s" / "deployment.yml"
        if not k8s_file.exists():
            print_error("k8s/deployment.yml not found")
            return
        
        try:
            with open(k8s_file, encoding="utf-8") as f:
                content = f.read()
            
            # Parse multi-document YAML
            docs = list(yaml.safe_load_all(content))
            
            kinds = [doc.get("kind") for doc in docs if doc]
            
            required_kinds = ["Namespace", "Secret", "ConfigMap", "Deployment", "Service"]
            
            for kind in required_kinds:
                if kind in kinds:
                    print_success(f"Has {kind} resource")
                    self.successes.append(f"K8s has {kind}")
                else:
                    print_warning(f"Missing {kind} resource")
                    self.warnings.append(f"K8s missing {kind}")
            
            # Check for important resources
            optional_kinds = ["HorizontalPodAutoscaler", "PodDisruptionBudget", "NetworkPolicy"]
            for kind in optional_kinds:
                if kind in kinds:
                    print_success(f"Has {kind} (recommended)")
                else:
                    print_info(f"Consider adding {kind}")
                    
        except yaml.YAMLError as e:
            print_error(f"Invalid YAML: {e}")
            self.errors.append(f"k8s/deployment.yml invalid YAML")
        except Exception as e:
            print_error(f"Error: {e}")
            self.errors.append(f"k8s/deployment.yml error: {e}")
    
    def check_requirements(self):
        """Validate Python requirements files"""
        print_header("Python Requirements Validation")
        
        req_files = ["requirements.txt", "requirements-production.txt"]
        
        # Essential packages that should be present
        essential_packages = [
            "psycopg2", "redis", "flask", "streamlit", "numpy",
            "torch", "prometheus-client", "aiohttp"
        ]
        
        for req_file in req_files:
            filepath = self.project_root / req_file
            if filepath.exists():
                with open(filepath, encoding="utf-8") as f:
                    content = f.read().lower()
                
                print_info(f"Checking {req_file}:")
                
                for pkg in essential_packages:
                    if pkg.lower() in content:
                        print_success(f"  Has {pkg}")
                    else:
                        print_warning(f"  Missing {pkg}")
                        self.warnings.append(f"{req_file} may be missing {pkg}")
            else:
                print_error(f"Missing: {req_file}")
                self.errors.append(f"Missing requirements file: {req_file}")
    
    def check_config_files(self):
        """Validate configuration files"""
        print_header("Configuration Files Validation")
        
        # Check config/app.yml
        app_config = self.project_root / "config" / "app.yml"
        if app_config.exists():
            try:
                with open(app_config, encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                
                required_sections = ["ai", "honeypots", "database", "redis", "monitoring"]
                for section in required_sections:
                    if section in config:
                        print_success(f"Config has section: {section}")
                    else:
                        print_warning(f"Config missing section: {section}")
                        self.warnings.append(f"config/app.yml missing: {section}")
                        
            except yaml.YAMLError as e:
                print_error(f"Invalid YAML in config/app.yml: {e}")
                self.errors.append("config/app.yml has invalid YAML")
        else:
            print_error("Missing: config/app.yml")
            self.errors.append("Missing config/app.yml")
    
    def check_env_files(self):
        """Validate environment files"""
        print_header("Environment Files Validation")
        
        env_example = self.project_root / ".env.example"
        if env_example.exists():
            with open(env_example, encoding="utf-8") as f:
                content = f.read()
            
            required_vars = [
                "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
                "REDIS_PASSWORD", "SECRET_KEY"
            ]
            
            for var in required_vars:
                if var in content:
                    print_success(f"Has {var}")
                else:
                    print_warning(f"Missing {var}")
                    self.warnings.append(f".env.example missing {var}")
        else:
            print_error("Missing .env.example")
            self.errors.append("Missing .env.example")
    
    def check_source_structure(self):
        """Validate source code structure"""
        print_header("Source Code Structure Validation")
        
        required_dirs = [
            "src/ai", "src/honeypots", "src/dashboard",
            "src/api", "src/network", "src/forensics"
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                # Check for __init__.py
                init_file = full_path / "__init__.py"
                if init_file.exists():
                    print_success(f"{dir_path}/ (with __init__.py)")
                else:
                    print_warning(f"{dir_path}/ (missing __init__.py)")
                    self.warnings.append(f"{dir_path} missing __init__.py")
            else:
                print_error(f"Missing directory: {dir_path}")
                self.errors.append(f"Missing directory: {dir_path}")
    
    def check_credentials_consistency(self):
        """Check credentials consistency across files"""
        print_header("Credentials Consistency Check")
        
        files_to_check = [
            "docker-compose.yml",
            "docker-compose.production.yml",
            ".env.example",
        ]
        
        postgres_users = set()
        postgres_passwords = set()
        
        for file in files_to_check:
            filepath = self.project_root / file
            if filepath.exists():
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()
                
                # Look for postgres credentials
                for line in content.split("\n"):
                    if "POSTGRES_USER" in line and "=" in line:
                        user = line.split("=")[-1].strip().strip('"').strip("'")
                        if user and not user.startswith("$"):
                            postgres_users.add(user)
                    if "POSTGRES_PASSWORD" in line and "=" in line:
                        pwd = line.split("=")[-1].strip().strip('"').strip("'")
                        if pwd and not pwd.startswith("$"):
                            postgres_passwords.add(pwd)
        
        if len(postgres_users) <= 1:
            print_success("PostgreSQL username is consistent")
            self.successes.append("Consistent PostgreSQL username")
        else:
            print_error(f"Inconsistent PostgreSQL usernames: {postgres_users}")
            self.errors.append(f"Inconsistent PostgreSQL usernames: {postgres_users}")
        
        if len(postgres_passwords) <= 1:
            print_success("PostgreSQL password is consistent")
            self.successes.append("Consistent PostgreSQL password")
        else:
            print_error(f"Inconsistent PostgreSQL passwords found in {len(postgres_passwords)} variations")
            self.errors.append("Inconsistent PostgreSQL passwords")
    
    def print_summary(self):
        """Print validation summary"""
        print_header("Validation Summary")
        
        total = len(self.successes) + len(self.warnings) + len(self.errors)
        
        print(f"  {GREEN}Passed:{RESET}   {len(self.successes)}")
        print(f"  {YELLOW}Warnings:{RESET} {len(self.warnings)}")
        print(f"  {RED}Errors:{RESET}   {len(self.errors)}")
        print(f"  {BLUE}Total:{RESET}    {total}")
        print()
        
        if self.errors:
            print(f"\n{RED}{BOLD}Critical Issues to Fix:{RESET}")
            for error in self.errors:
                print(f"  {RED}•{RESET} {error}")
        
        if self.warnings:
            print(f"\n{YELLOW}{BOLD}Warnings (Recommended Fixes):{RESET}")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  {YELLOW}•{RESET} {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        print()
        if not self.errors:
            print(f"{GREEN}{BOLD}✓ Deployment validation passed!{RESET}")
            print(f"{GREEN}  The project is ready for deployment.{RESET}")
        else:
            print(f"{RED}{BOLD}✗ Deployment validation failed!{RESET}")
            print(f"{RED}  Please fix the errors above before deploying.{RESET}")


def main():
    """Main entry point"""
    project_root = os.environ.get("PROJECT_ROOT", ".")
    
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    
    validator = DeploymentValidator(project_root)
    successes, warnings, errors = validator.validate_all()
    
    # Exit with error code if there are critical errors
    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
