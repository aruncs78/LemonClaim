# LemonClaim Insurance Application - Test Cases

## Overview

This document contains all test cases for the LemonClaim Insurance Application, organized by functional area.

**Project:** RBTES (Zephyr Scale)
**Parent Folder:** LemonClaim Insurance App (ID: 40257001)
**Total Test Cases:** 51

---

## Test Case Summary

| Category | Count | Priority High | Priority Normal |
|----------|-------|---------------|-----------------|
| Authentication | 9 | 6 | 3 |
| Policy Management | 8 | 4 | 4 |
| Claims Processing | 8 | 5 | 3 |
| AI Chatbot (Maya) | 6 | 2 | 4 |
| Payments | 6 | 3 | 3 |
| GDPR Compliance | 6 | 4 | 2 |
| Admin Dashboard | 8 | 5 | 3 |

---

## Zephyr Scale Links

- **Test Plan:** [RBTES-P10 - LemonClaim Insurance App - Master Test Plan](https://parasutest.atlassian.net/projects/RBTES?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/testPlan/RBTES-P10)
- **Test Cycle:** [RBTES-R203 - LemonClaim v1.0 - Sprint 1 Regression](https://parasutest.atlassian.net/projects/RBTES?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/testCycle/RBTES-R203)

---

## 1. Authentication Tests (Folder ID: 40257003)

### RBTES-T1272: User Registration - Valid Data
- **Priority:** High
- **Labels:** authentication, smoke, registration
- **Objective:** Verify that a new user can successfully register with valid data and GDPR consent
- **Precondition:** User is on the registration page and has not registered before

### RBTES-T1273: User Registration - Invalid Email Format
- **Priority:** High
- **Labels:** authentication, negative, validation
- **Objective:** Verify that registration fails with appropriate error when invalid email format is provided
- **Precondition:** User is on the registration page

### RBTES-T1274: User Registration - Weak Password
- **Priority:** High
- **Labels:** authentication, negative, security
- **Objective:** Verify that registration fails when password does not meet security requirements
- **Precondition:** User is on the registration page

### RBTES-T1275: User Registration - Without GDPR Consent
- **Priority:** High
- **Labels:** authentication, negative, gdpr
- **Objective:** Verify that registration fails when GDPR consent is not provided
- **Precondition:** User is on the registration page

### RBTES-T1276: User Login - Valid Credentials
- **Priority:** High
- **Labels:** authentication, smoke, login
- **Objective:** Verify that a registered user can successfully login with valid credentials
- **Precondition:** User has a registered account

### RBTES-T1277: User Login - Invalid Password
- **Priority:** High
- **Labels:** authentication, negative, security
- **Objective:** Verify that login fails with appropriate error message when wrong password is provided
- **Precondition:** User has a registered account

### RBTES-T1278: User Logout
- **Priority:** Normal
- **Labels:** authentication, smoke
- **Objective:** Verify that a logged-in user can successfully logout and session is invalidated
- **Precondition:** User is logged into the application

### RBTES-T1279: Password Reset Request
- **Priority:** Normal
- **Labels:** authentication, password-reset
- **Objective:** Verify that user can request a password reset link via email
- **Precondition:** User has a registered account with valid email

### RBTES-T1280: JWT Token Refresh
- **Priority:** High
- **Labels:** authentication, security, api
- **Objective:** Verify that access token is automatically refreshed using refresh token before expiry
- **Precondition:** User is logged in and access token is about to expire

---

## 2. Policy Management Tests (Folder ID: 40257006)

### RBTES-T1281: Get Insurance Quote - Home Insurance
- **Priority:** High
- **Labels:** policy, quote, smoke
- **Objective:** Verify that user can request and receive a quote for home insurance
- **Precondition:** User is logged in and on the policies page

### RBTES-T1282: Get Insurance Quote - Renters Insurance
- **Priority:** High
- **Labels:** policy, quote
- **Objective:** Verify that user can request and receive a quote for renters insurance
- **Precondition:** User is logged in and on the policies page

### RBTES-T1283: Get Insurance Quote - Auto Insurance
- **Priority:** High
- **Labels:** policy, quote
- **Objective:** Verify that user can request and receive a quote for auto insurance with vehicle details
- **Precondition:** User is logged in

### RBTES-T1284: Purchase Policy from Quote
- **Priority:** High
- **Labels:** policy, purchase, smoke
- **Objective:** Verify that user can purchase an insurance policy from a valid quote
- **Precondition:** User has received a valid quote that has not expired

### RBTES-T1285: View Active Policies
- **Priority:** Normal
- **Labels:** policy, dashboard
- **Objective:** Verify that user can view all their active insurance policies on the dashboard
- **Precondition:** User is logged in and has at least one active policy

### RBTES-T1286: Update Policy Coverage
- **Priority:** Normal
- **Labels:** policy, update
- **Objective:** Verify that user can update coverage amount and deductible for an active policy
- **Precondition:** User is logged in and has an active policy

### RBTES-T1287: Cancel Insurance Policy
- **Priority:** Normal
- **Labels:** policy, cancellation
- **Objective:** Verify that user can cancel an active insurance policy
- **Precondition:** User is logged in and has an active policy with no pending claims

### RBTES-T1288: Quote Expiration Validation
- **Priority:** Normal
- **Labels:** policy, quote, negative
- **Objective:** Verify that expired quotes cannot be used to purchase a policy
- **Precondition:** User has a quote that has passed its expiration date (30 days)

---

## 3. Claims Processing Tests (Folder ID: 40257008)

### RBTES-T1289: File New Claim - Property Damage
- **Priority:** High
- **Labels:** claims, smoke, file-claim
- **Objective:** Verify that user can file a property damage claim against their active policy
- **Precondition:** User is logged in and has an active home or renters insurance policy

### RBTES-T1290: Claim Auto-Approval - Low Risk
- **Priority:** High
- **Labels:** claims, ai, auto-approval
- **Objective:** Verify that low-risk claims under $1000 are automatically approved by AI
- **Precondition:** User has an active policy with established history (>30 days)

### RBTES-T1291: Upload Supporting Documents
- **Priority:** High
- **Labels:** claims, documents, upload
- **Objective:** Verify that user can upload supporting documents (photos, PDFs) for their claim
- **Precondition:** User has filed a claim and is on the claim details page

### RBTES-T1292: View Claim Status and Timeline
- **Priority:** Normal
- **Labels:** claims, status, tracking
- **Objective:** Verify that user can view their claim status and complete timeline of events
- **Precondition:** User has at least one submitted claim

### RBTES-T1293: Claim Validation - Amount Exceeds Coverage
- **Priority:** High
- **Labels:** claims, negative, validation
- **Objective:** Verify that system prevents filing claim amount exceeding policy coverage
- **Precondition:** User has an active policy with $50,000 coverage

### RBTES-T1294: Claim Validation - Future Incident Date
- **Priority:** Normal
- **Labels:** claims, negative, validation
- **Objective:** Verify that system prevents filing claim with incident date in the future
- **Precondition:** User has an active policy

### RBTES-T1295: Update Submitted Claim
- **Priority:** Normal
- **Labels:** claims, update
- **Objective:** Verify that user can update claim details while claim is still in submitted status
- **Precondition:** User has a claim in 'submitted' status

### RBTES-T1296: AI Fraud Detection - High Risk Flag
- **Priority:** High
- **Labels:** claims, ai, fraud-detection, security
- **Objective:** Verify that AI system flags high-risk claims for manual review based on fraud score
- **Precondition:** User has a new policy (<30 days) filing a high-value claim

---

## 4. AI Chatbot (Maya) Tests (Folder ID: 40257014)

### RBTES-T1297: Maya Chatbot - Greeting Response
- **Priority:** Normal
- **Labels:** chatbot, ai, maya
- **Objective:** Verify that Maya AI chatbot responds appropriately to greeting messages
- **Precondition:** User is logged in and on the chat page

### RBTES-T1298: Maya Chatbot - Quote Request Intent
- **Priority:** High
- **Labels:** chatbot, ai, maya, quote
- **Objective:** Verify that Maya correctly identifies quote request intent and guides user
- **Precondition:** User is logged in and on the chat page

### RBTES-T1299: Maya Chatbot - Claim Filing Assistance
- **Priority:** High
- **Labels:** chatbot, ai, maya, claims
- **Objective:** Verify that Maya can assist users through the claim filing process via conversation
- **Precondition:** User is logged in with an active policy

### RBTES-T1300: Maya Chatbot - Claim Status Check
- **Priority:** Normal
- **Labels:** chatbot, ai, maya, claims
- **Objective:** Verify that Maya can retrieve and display user's claim status when asked
- **Precondition:** User is logged in and has at least one claim

### RBTES-T1301: Maya Chatbot - Chat History Persistence
- **Priority:** Normal
- **Labels:** chatbot, ai, maya, history
- **Objective:** Verify that chat history is saved and can be retrieved for the session
- **Precondition:** User has had a conversation with Maya

### RBTES-T1302: Maya Chatbot - Contextual Suggestions
- **Priority:** Normal
- **Labels:** chatbot, ai, maya, ux
- **Objective:** Verify that Maya provides relevant quick-action suggestions based on conversation context
- **Precondition:** User is logged in and on the chat page

---

## 5. Payments Tests (Folder ID: 40261018)

### RBTES-T1303: Create Payment Intent
- **Priority:** High
- **Labels:** payments, stripe, smoke
- **Objective:** Verify that system can create a Stripe payment intent for policy premium
- **Precondition:** User has a policy pending payment

### RBTES-T1304: Complete Premium Payment
- **Priority:** High
- **Labels:** payments, stripe, smoke
- **Objective:** Verify that user can successfully complete a premium payment with card
- **Precondition:** User has an active payment intent

### RBTES-T1305: View Payment History
- **Priority:** Normal
- **Labels:** payments, history
- **Objective:** Verify that user can view their complete payment history with details
- **Precondition:** User has made at least one payment

### RBTES-T1306: Payment Summary Statistics
- **Priority:** Normal
- **Labels:** payments, summary
- **Objective:** Verify that payment summary displays correct totals for paid, pending, and refunded amounts
- **Precondition:** User has various payment transactions

### RBTES-T1307: Request Payment Refund
- **Priority:** Normal
- **Labels:** payments, refund
- **Objective:** Verify that user can request a refund for a completed payment
- **Precondition:** User has a completed payment that is eligible for refund

### RBTES-T1308: Claim Payout Processing
- **Priority:** High
- **Labels:** payments, claims, payout
- **Objective:** Verify that approved claim payouts are processed and recorded correctly
- **Precondition:** User has an approved claim ready for payout

---

## 6. GDPR Compliance Tests (Folder ID: 40261020)

### RBTES-T1309: GDPR - View Consent Settings
- **Priority:** High
- **Labels:** gdpr, compliance, privacy
- **Objective:** Verify that user can view all their GDPR consent settings
- **Precondition:** User is logged in and has granted initial consents during registration

### RBTES-T1310: GDPR - Update Marketing Consent
- **Priority:** Normal
- **Labels:** gdpr, compliance, consent
- **Objective:** Verify that user can update their marketing consent preferences
- **Precondition:** User is logged in

### RBTES-T1311: GDPR - Data Export (Right to Portability)
- **Priority:** High
- **Labels:** gdpr, compliance, data-export
- **Objective:** Verify that user can export all their personal data in a portable format
- **Precondition:** User is logged in with existing policies, claims, and payment data

### RBTES-T1312: GDPR - Account Deletion (Right to Erasure)
- **Priority:** High
- **Labels:** gdpr, compliance, data-deletion
- **Objective:** Verify that user can delete their account and all data is anonymized
- **Precondition:** User has no active policies or pending claims

### RBTES-T1313: GDPR - Deletion Blocked with Active Policies
- **Priority:** High
- **Labels:** gdpr, compliance, negative
- **Objective:** Verify that account deletion is blocked when user has active policies
- **Precondition:** User has an active insurance policy

### RBTES-T1314: GDPR - View Audit Log
- **Priority:** Normal
- **Labels:** gdpr, compliance, audit
- **Objective:** Verify that user can view their complete audit log of data access and changes
- **Precondition:** User has performed various actions in the system

---

## 7. Admin Dashboard Tests (Folder ID: 40261021)

### RBTES-T1315: Admin - Dashboard Statistics
- **Priority:** High
- **Labels:** admin, dashboard, smoke
- **Objective:** Verify that admin dashboard displays correct statistics for users, policies, claims, and revenue
- **Precondition:** User is logged in as admin

### RBTES-T1316: Admin - List All Users
- **Priority:** Normal
- **Labels:** admin, users
- **Objective:** Verify that admin can view paginated list of all registered users
- **Precondition:** User is logged in as admin and there are registered users

### RBTES-T1317: Admin - Deactivate User Account
- **Priority:** High
- **Labels:** admin, users, security
- **Objective:** Verify that admin can deactivate a user account
- **Precondition:** User is logged in as admin

### RBTES-T1318: Admin - Review Pending Claims
- **Priority:** High
- **Labels:** admin, claims, review
- **Objective:** Verify that admin can view and access all pending claims requiring review
- **Precondition:** User is logged in as admin and there are claims pending review

### RBTES-T1319: Admin - Approve Claim
- **Priority:** High
- **Labels:** admin, claims, approval
- **Objective:** Verify that admin can approve a claim and set the approved amount
- **Precondition:** User is logged in as admin with a claim pending review

### RBTES-T1320: Admin - Reject Claim
- **Priority:** High
- **Labels:** admin, claims, rejection
- **Objective:** Verify that admin can reject a claim with rejection notes
- **Precondition:** User is logged in as admin with a claim pending review

### RBTES-T1321: Admin - View Analytics
- **Priority:** Normal
- **Labels:** admin, analytics
- **Objective:** Verify that admin can view analytics data for configurable time periods
- **Precondition:** User is logged in as admin with historical data available

### RBTES-T1322: Admin - Access Denied for Non-Admin Users
- **Priority:** High
- **Labels:** admin, security, negative
- **Objective:** Verify that non-admin users cannot access admin endpoints
- **Precondition:** User is logged in with a regular (non-admin) account

---

## Test Execution Guidelines

### Smoke Test Suite
Run the following test cases for quick validation:
- RBTES-T1272 (Registration)
- RBTES-T1276 (Login)
- RBTES-T1278 (Logout)
- RBTES-T1281 (Quote)
- RBTES-T1284 (Purchase Policy)
- RBTES-T1289 (File Claim)
- RBTES-T1303 (Create Payment)
- RBTES-T1315 (Admin Dashboard)

### Security Test Suite
- RBTES-T1274 (Weak Password)
- RBTES-T1277 (Invalid Login)
- RBTES-T1280 (Token Refresh)
- RBTES-T1296 (Fraud Detection)
- RBTES-T1317 (User Deactivation)
- RBTES-T1322 (Admin Access Control)

### GDPR Compliance Suite
- RBTES-T1275 (GDPR Consent)
- RBTES-T1309 to RBTES-T1314 (All GDPR tests)

---

## Running Tests

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run all tests
pytest tests/ -v

# Run smoke tests only
pytest tests/ -v -m smoke

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific category
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

---

## Zephyr Scale Integration

All test cases have been uploaded to Zephyr Scale under project **RBTES** with the following folder structure:

```
LemonClaim Insurance App (40257001)
├── Authentication (40257003)
├── Policy Management (40257006)
├── Claims Processing (40257008)
├── AI Chatbot (Maya) (40257014)
├── Payments (40261018)
├── GDPR Compliance (40261020)
└── Admin Dashboard (40261021)
```

Test Case Keys: RBTES-T1272 through RBTES-T1322
