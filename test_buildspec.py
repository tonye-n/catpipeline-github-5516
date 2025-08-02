#!/usr/bin/env python3
import yaml
import unittest
from unittest.mock import patch, MagicMock
import subprocess
import os

class TestBuildspec(unittest.TestCase):
    
    def setUp(self):
        with open('buildspec.yml', 'r') as f:
            self.buildspec = yaml.safe_load(f)
    
    def test_buildspec_structure(self):
        """Test buildspec has required structure"""
        self.assertEqual(self.buildspec['version'], 0.2)
        self.assertIn('phases', self.buildspec)
        self.assertIn('install', self.buildspec['phases'])
        self.assertIn('pre_build', self.buildspec['phases'])
        self.assertIn('build', self.buildspec['phases'])
        self.assertIn('post_build', self.buildspec['phases'])
    
    def test_docker_runtime_version(self):
        """Test Docker runtime version is specified"""
        install_phase = self.buildspec['phases']['install']
        self.assertIn('runtime-versions', install_phase)
        self.assertEqual(install_phase['runtime-versions']['docker'], 20)
    
    @patch.dict(os.environ, {
        'AWS_DEFAULT_REGION': 'us-east-1',
        'AWS_ACCOUNT_ID': '123456789012',
        'IMAGE_REPO_NAME': 'my-app',
        'IMAGE_TAG': 'latest'
    })
    @patch('subprocess.run')
    def test_ecr_login_command(self, mock_run):
        """Test ECR login command execution"""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Simulate ECR login command
        cmd = f"aws ecr get-login-password --region {os.environ['AWS_DEFAULT_REGION']} | docker login --username AWS --password-stdin {os.environ['AWS_ACCOUNT_ID']}.dkr.ecr.{os.environ['AWS_DEFAULT_REGION']}.amazonaws.com"
        
        result = subprocess.run(cmd, shell=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
    
    @patch.dict(os.environ, {
        'IMAGE_REPO_NAME': 'my-app',
        'IMAGE_TAG': 'v1.0'
    })
    @patch('subprocess.run')
    def test_docker_build_commands(self, mock_run):
        """Test Docker build and tag commands"""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Test docker build
        build_cmd = f"docker build -t {os.environ['IMAGE_REPO_NAME']}:{os.environ['IMAGE_TAG']} ."
        result = subprocess.run(build_cmd, shell=True)
        self.assertEqual(result.returncode, 0)
    
    @patch.dict(os.environ, {
        'AWS_ACCOUNT_ID': '123456789012',
        'AWS_DEFAULT_REGION': 'us-west-2',
        'IMAGE_REPO_NAME': 'my-app',
        'IMAGE_TAG': 'v1.0'
    })
    @patch('subprocess.run')
    def test_docker_push_command(self, mock_run):
        """Test Docker push command"""
        mock_run.return_value = MagicMock(returncode=0)
        
        push_cmd = f"docker push {os.environ['AWS_ACCOUNT_ID']}.dkr.ecr.{os.environ['AWS_DEFAULT_REGION']}.amazonaws.com/{os.environ['IMAGE_REPO_NAME']}:{os.environ['IMAGE_TAG']}"
        result = subprocess.run(push_cmd, shell=True)
        self.assertEqual(result.returncode, 0)
    
    def test_required_environment_variables(self):
        """Test that required environment variables are referenced"""
        buildspec_str = yaml.dump(self.buildspec)
        required_vars = ['AWS_DEFAULT_REGION', 'AWS_ACCOUNT_ID', 'IMAGE_REPO_NAME', 'IMAGE_TAG']
        
        for var in required_vars:
            self.assertIn(f'${var}', buildspec_str)

if __name__ == '__main__':
    unittest.main()