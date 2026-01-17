# /security-check

Thoroughly investigate the current feature for security problems, permission gaps. Act like a red-team pen-tester. Suggest fixes.

## Analysis Areas

1. **Credential Handling**
   - How are API keys/secrets stored?
   - Are credentials exposed in logs, error messages, or URLs?
   - Is settings.ini properly gitignored?

2. **Input Validation**
   - Are user inputs (URLs, playlist IDs) sanitized?
   - Can malicious input cause injection attacks?

3. **Token Security**
   - Are OAuth tokens stored securely?
   - Do tokens have appropriate scopes (principle of least privilege)?
   - Are tokens refreshed properly?

4. **Data Exposure**
   - Is sensitive data logged or printed?
   - Are API responses handled safely?

5. **Dependencies**
   - Are there known vulnerabilities in dependencies?
   - Are versions pinned appropriately?

6. **Network Security**
   - Are all API calls made over HTTPS?
   - Is there proper error handling for network failures?

## Output Format

Provide findings as:
- **CRITICAL**: Immediate security risk
- **HIGH**: Significant vulnerability
- **MEDIUM**: Should be addressed
- **LOW**: Best practice improvement

Include specific code references and suggested fixes for each finding.
