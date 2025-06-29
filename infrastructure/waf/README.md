# Temporary WAF Configuration

This directory contains a lightweight ModSecurity configuration that blocks common SQL injection patterns. It is intended as a short-term mitigation while comprehensive input validation is implemented.

## Usage

1. Deploy an Nginx or Apache reverse proxy with ModSecurity enabled.
2. Include `temp-waf-rules.conf` in the ModSecurity ruleset.
3. Monitor logs for blocked requests to verify the rule is active.

These rules should be replaced with a managed WAF service once available.
