#!/usr/bin/env python3
"""
ACGS-1 Enterprise Authentication Integration
SAML/OIDC integration for enterprise SSO with constitutional governance
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import uuid

import jwt
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import httpx
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnterpriseUser:
    """Enterprise user with constitutional governance roles"""
    user_id: str
    email: str
    name: str
    tenant_id: str
    roles: List[str]
    permissions: Dict[str, Any]
    constitutional_clearance_level: str
    sso_provider: str
    last_login: datetime
    
class SAMLAuthProvider:
    """SAML 2.0 authentication provider"""
    
    def __init__(self, config: Dict[str, Any]):
        self.entity_id = config['entity_id']
        self.sso_url = config['sso_url']
        self.x509_cert = config['x509_cert']
        self.private_key = config['private_key']
        self.attribute_mapping = config.get('attribute_mapping', {})
        
    def generate_auth_request(self, relay_state: str = None) -> str:
        """Generate SAML authentication request"""
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        saml_request = f"""
        <samlp:AuthnRequest 
            xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
            xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
            ID="{request_id}"
            Version="2.0"
            IssueInstant="{timestamp}"
            Destination="{self.sso_url}"
            AssertionConsumerServiceURL="{os.getenv('ACGS_BASE_URL')}/auth/saml/acs"
            ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
            <saml:Issuer>{self.entity_id}</saml:Issuer>
            <samlp:NameIDPolicy Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress" />
        </samlp:AuthnRequest>
        """
        
        # Base64 encode and URL encode the request
        import base64
        encoded_request = base64.b64encode(saml_request.encode()).decode()
        
        params = {'SAMLRequest': encoded_request}
        if relay_state:
            params['RelayState'] = relay_state
            
        return f"{self.sso_url}?{urlencode(params)}"
    
    def validate_saml_response(self, saml_response: str) -> Dict[str, Any]:
        """Validate SAML response and extract user attributes"""
        try:
            # Decode base64 SAML response
            import base64
            decoded_response = base64.b64decode(saml_response).decode()
            
            # Parse XML
            root = ET.fromstring(decoded_response)
            
            # Extract user attributes
            attributes = {}
            for attr in root.findall('.//saml:Attribute', {'saml': 'urn:oasis:names:tc:SAML:2.0:assertion'}):
                attr_name = attr.get('Name')
                attr_values = [val.text for val in attr.findall('.//saml:AttributeValue', {'saml': 'urn:oasis:names:tc:SAML:2.0:assertion'})]
                attributes[attr_name] = attr_values[0] if len(attr_values) == 1 else attr_values
            
            # Map attributes to user fields
            user_data = {}
            for saml_attr, user_field in self.attribute_mapping.items():
                if saml_attr in attributes:
                    user_data[user_field] = attributes[saml_attr]
            
            return user_data
            
        except Exception as e:
            logger.error(f"SAML response validation failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid SAML response")

class OIDCAuthProvider:
    """OpenID Connect authentication provider"""
    
    def __init__(self, config: Dict[str, Any]):
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.discovery_url = config['discovery_url']
        self.redirect_uri = config['redirect_uri']
        self.scopes = config.get('scopes', ['openid', 'email', 'profile'])
        self._discovery_doc = None
        
    async def get_discovery_document(self) -> Dict[str, Any]:
        """Get OIDC discovery document"""
        if not self._discovery_doc:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.discovery_url)
                response.raise_for_status()
                self._discovery_doc = response.json()
        return self._discovery_doc
    
    async def generate_auth_url(self, state: str = None) -> str:
        """Generate OIDC authorization URL"""
        discovery = await self.get_discovery_document()
        auth_endpoint = discovery['authorization_endpoint']
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': ' '.join(self.scopes),
            'redirect_uri': self.redirect_uri,
            'state': state or str(uuid.uuid4())
        }
        
        return f"{auth_endpoint}?{urlencode(params)}"
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        discovery = await self.get_discovery_document()
        token_endpoint = discovery['token_endpoint']
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_endpoint, data=data)
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from OIDC provider"""
        discovery = await self.get_discovery_document()
        userinfo_endpoint = discovery['userinfo_endpoint']
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_endpoint, headers=headers)
            response.raise_for_status()
            return response.json()

class EnterpriseAuthManager:
    """Enterprise authentication manager with constitutional governance integration"""
    
    def __init__(self, database_url: str, redis_url: str):
        self.database_url = database_url
        self.redis_url = redis_url
        self.saml_providers: Dict[str, SAMLAuthProvider] = {}
        self.oidc_providers: Dict[str, OIDCAuthProvider] = {}
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', 'acgs-enterprise-secret')
        
    async def initialize(self):
        """Initialize enterprise auth manager"""
        # Load enterprise auth providers from configuration
        await self._load_auth_providers()
        
    async def _load_auth_providers(self):
        """Load configured authentication providers"""
        # SAML providers
        saml_config = json.loads(os.getenv('SAML_PROVIDERS', '{}'))
        for provider_name, config in saml_config.items():
            self.saml_providers[provider_name] = SAMLAuthProvider(config)
            
        # OIDC providers
        oidc_config = json.loads(os.getenv('OIDC_PROVIDERS', '{}'))
        for provider_name, config in oidc_config.items():
            self.oidc_providers[provider_name] = OIDCAuthProvider(config)
            
        logger.info(f"Loaded {len(self.saml_providers)} SAML and {len(self.oidc_providers)} OIDC providers")
    
    async def authenticate_saml_user(self, provider_name: str, saml_response: str, tenant_id: str) -> EnterpriseUser:
        """Authenticate user via SAML"""
        if provider_name not in self.saml_providers:
            raise HTTPException(status_code=400, detail="Unknown SAML provider")
        
        provider = self.saml_providers[provider_name]
        user_data = provider.validate_saml_response(saml_response)
        
        # Create enterprise user
        user = EnterpriseUser(
            user_id=str(uuid.uuid4()),
            email=user_data.get('email'),
            name=user_data.get('name', user_data.get('email')),
            tenant_id=tenant_id,
            roles=self._map_enterprise_roles(user_data.get('roles', [])),
            permissions=self._get_constitutional_permissions(user_data.get('roles', [])),
            constitutional_clearance_level=self._determine_clearance_level(user_data.get('roles', [])),
            sso_provider=f"saml:{provider_name}",
            last_login=datetime.now()
        )
        
        # Store user session
        await self._store_user_session(user)
        
        return user
    
    async def authenticate_oidc_user(self, provider_name: str, code: str, tenant_id: str) -> EnterpriseUser:
        """Authenticate user via OIDC"""
        if provider_name not in self.oidc_providers:
            raise HTTPException(status_code=400, detail="Unknown OIDC provider")
        
        provider = self.oidc_providers[provider_name]
        
        # Exchange code for tokens
        tokens = await provider.exchange_code_for_tokens(code)
        
        # Get user info
        user_info = await provider.get_user_info(tokens['access_token'])
        
        # Create enterprise user
        user = EnterpriseUser(
            user_id=str(uuid.uuid4()),
            email=user_info.get('email'),
            name=user_info.get('name', user_info.get('email')),
            tenant_id=tenant_id,
            roles=self._map_enterprise_roles(user_info.get('roles', [])),
            permissions=self._get_constitutional_permissions(user_info.get('roles', [])),
            constitutional_clearance_level=self._determine_clearance_level(user_info.get('roles', [])),
            sso_provider=f"oidc:{provider_name}",
            last_login=datetime.now()
        )
        
        # Store user session
        await self._store_user_session(user)
        
        return user
    
    def _map_enterprise_roles(self, external_roles: List[str]) -> List[str]:
        """Map external roles to ACGS constitutional governance roles"""
        role_mapping = {
            'admin': ['constitutional_admin', 'policy_creator', 'governance_overseer'],
            'manager': ['policy_creator', 'governance_reviewer'],
            'user': ['policy_viewer', 'governance_participant'],
            'auditor': ['audit_viewer', 'compliance_monitor'],
            'constitutional_council': ['constitutional_reviewer', 'multi_sig_authority']
        }
        
        acgs_roles = []
        for external_role in external_roles:
            if external_role.lower() in role_mapping:
                acgs_roles.extend(role_mapping[external_role.lower()])
        
        return list(set(acgs_roles)) if acgs_roles else ['governance_participant']
    
    def _get_constitutional_permissions(self, roles: List[str]) -> Dict[str, Any]:
        """Get constitutional governance permissions based on roles"""
        permissions = {
            'can_create_policies': False,
            'can_review_policies': False,
            'can_approve_policies': False,
            'can_modify_constitution': False,
            'can_access_audit_logs': False,
            'max_governance_actions_per_hour': 10
        }
        
        if 'constitutional_admin' in roles:
            permissions.update({
                'can_create_policies': True,
                'can_review_policies': True,
                'can_approve_policies': True,
                'can_modify_constitution': True,
                'can_access_audit_logs': True,
                'max_governance_actions_per_hour': 1000
            })
        elif 'policy_creator' in roles:
            permissions.update({
                'can_create_policies': True,
                'can_review_policies': True,
                'max_governance_actions_per_hour': 100
            })
        elif 'governance_reviewer' in roles:
            permissions.update({
                'can_review_policies': True,
                'max_governance_actions_per_hour': 50
            })
        
        return permissions
    
    def _determine_clearance_level(self, roles: List[str]) -> str:
        """Determine constitutional clearance level"""
        if 'constitutional_admin' in roles:
            return 'constitutional_admin'
        elif 'constitutional_reviewer' in roles:
            return 'constitutional_reviewer'
        elif 'policy_creator' in roles:
            return 'policy_creator'
        else:
            return 'basic_user'
    
    async def _store_user_session(self, user: EnterpriseUser):
        """Store user session in Redis"""
        import redis.asyncio as redis
        redis_client = redis.from_url(self.redis_url)
        
        session_data = {
            'user_id': user.user_id,
            'email': user.email,
            'name': user.name,
            'tenant_id': user.tenant_id,
            'roles': user.roles,
            'permissions': user.permissions,
            'constitutional_clearance_level': user.constitutional_clearance_level,
            'sso_provider': user.sso_provider,
            'last_login': user.last_login.isoformat()
        }
        
        await redis_client.setex(
            f"enterprise_session:{user.user_id}",
            3600,  # 1 hour
            json.dumps(session_data)
        )
    
    def generate_jwt_token(self, user: EnterpriseUser) -> str:
        """Generate JWT token for enterprise user"""
        payload = {
            'user_id': user.user_id,
            'email': user.email,
            'tenant_id': user.tenant_id,
            'roles': user.roles,
            'constitutional_clearance_level': user.constitutional_clearance_level,
            'exp': datetime.utcnow() + timedelta(hours=8),
            'iat': datetime.utcnow(),
            'iss': 'acgs-enterprise-auth'
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")


# Global enterprise auth manager
enterprise_auth = EnterpriseAuthManager(
    database_url=os.getenv('DATABASE_URL', 'postgresql://acgs_user:password@localhost:5432/acgs_pgp_db'),
    redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)
