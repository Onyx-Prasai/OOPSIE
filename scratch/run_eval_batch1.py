import re, json

def clean_json_str(s):
    s = s.strip()
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()

def evaluate_batch_01(input_text):
    # Parse case blocks
    cases = re.split(r'\n(?=## Case: `)', input_text)
    header = cases[0]
    
    # Add status label to header if not present
    if "AI-generated provisional ratings" not in header:
        # insert before the first ---
        header = header.replace(
            "> **Disclosures**: Author-only review disclosure applies unless independent reviewer co-evaluates. Format cues (markdown fences vs raw JSON) may allow inferring base vs adapted configurations, so ratings must strictly evaluate technical diagnostic content independent of format.\n",
            "> **Disclosures**: Author-only review disclosure applies unless independent reviewer co-evaluates. Format cues (markdown fences vs raw JSON) may allow inferring base vs adapted configurations, so ratings must strictly evaluate technical diagnostic content independent of format.\n> **Rating Status**: AI-generated provisional ratings, subject to author review and final adoption.\n"
        )
    
    output_cases = [header]
    
    # Pre-defined expert evaluations for Batch 01
    evals = {
        ("bench-authentication-01", "System Alpha"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Correctly diagnoses expired access token. Proposes standard refresh token and clock sync checks without inventing unsupported specifics. Repair advice is well-scoped to inspecting request interceptor and handling 401s safely."
        },
        ("bench-authentication-01", "System Beta"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Accurately identifies JWT expiration via 'exp' claim. Outlines refresh token flow and advises against insecure token storage or extending token lifetimes. Verification steps are safe and diagnostic."
        },
        ("bench-authentication-01", "System Gamma"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Accurately diagnoses token expiration and recommends refresh token flow without disabling expiration safeguards. Safe verification steps inspecting session recovery."
        },
        ("bench-authentication-01", "System Delta"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Correctly attributes HTTP 401 to expired JWT token. Evaluates token refresh logic and clock skew. Outlines targeted frontend interceptor repair with clear security warnings on storage."
        },
        ("bench-authentication-02", "System Alpha"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Correctly identifies OAuth redirect URI mismatch between client request and identity provider console. Scopes repair to updating developer console authorized URIs with safe verification steps."
        },
        ("bench-authentication-02", "System Beta"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Correctly diagnoses redirect URI discrepancy in OAuth flow. Highlights protocol (http vs https) and localhost vs domain mismatches. Scopes repair cleanly between environment variables and provider dashboard."
        },
        ("bench-authentication-02", "System Gamma"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Sound identification of redirect URI mismatch. Recommends comparing registered console URIs against application config, with non-destructive verification in an incognito session."
        },
        ("bench-authentication-02", "System Delta"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Accurately targets OAuth callback configuration mismatch. Proposes minimal config synchronization and checks for trailing slash/protocol discrepancies."
        },
        ("bench-authentication-03", "System Alpha"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Properly categorizes as authorization and pinpoints missing 'reports:read' scope in OAuth token generation. Advises against granting excessive scopes and includes negative testing in verification."
        },
        ("bench-authentication-03", "System Beta"): {
            "gate": "Assessable Content Present",
            "d1": "Partial",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Categorizes error as authentication rather than authorization, though description accurately recognizes that the OAuth token lacks the specific 'reports:read' scope. Repair and verification steps are well-scoped."
        },
        ("bench-authentication-03", "System Gamma"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Correctly identifies authorization scope deficiency. Advises checking token claims and requesting 'reports:read' scope without privilege escalation. Safe verification inspecting Authorization header and decoding JWT."
        },
        ("bench-authentication-03", "System Delta"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Accurate authorization diagnosis targeting missing 'reports:read' permission claim. Poses helpful questions regarding role assignment and provides non-destructive verification commands."
        },
        ("bench-authentication-04", "System Alpha"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Correctly diagnoses OIDC issuer mismatch. Explicitly warns against disabling issuer validation, preserving crucial security boundary. Repair scopes cleanly to environment configuration."
        },
        ("bench-authentication-04", "System Beta"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Accurately pinpoints OIDC issuer URL mismatch between token 'iss' claim and app config. Recommends comparing decoded token claims with environment variables. Safe verification."
        },
        ("bench-authentication-04", "System Gamma"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Correctly identifies OIDC issuer discrepancy. Highlights trailing slash differences and environment mismatches. Repair is appropriately limited to configuration adjustments."
        },
        ("bench-authentication-04", "System Delta"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Sound identification of OIDC issuer mismatch. Advises inspecting 'iss' claim in JWT and aligning OIDC client settings without weakening verification parameters."
        },
        ("bench-backend-01", "System Alpha"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Categorizes HTTP 503 as network/gateway routing issue. Identifies backend service crash, overload, or proxy routing failure as plausible causes. Safe verification inspecting service logs and curling /api/catalog."
        },
        ("bench-backend-01", "System Beta"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Categorizes HTTP 503 as runtime service unavailability. Analyzes process crash, overload, and reverse proxy timeouts. Repair advises checking process status and logs before mutating code."
        },
        ("bench-backend-01", "System Gamma"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Correctly diagnoses service unavailability. Identifies upstream crash or dependency failure as likely mechanism. Advises inspecting server logs and monitoring resource consumption."
        },
        ("bench-backend-01", "System Delta"): {
            "gate": "Assessable Content Present",
            "d1": "Pass (Correct)",
            "d2": "None",
            "d3": "Pass (Appropriate)",
            "d4": "Pass (Well-Scoped)",
            "d5": "Pass (Useful & Safe)",
            "notes": "Sound diagnosis of HTTP 503 on /api/catalog. Considers backend crash, overload, and gateway connectivity. Repair advises inspecting service logs and database health with non-destructive verification."
        }
    }
    
    for cb in cases[1:]:
        cid_match = re.search(r'## Case: `([^`]+)`', cb)
        if not cid_match:
            output_cases.append(cb)
            continue
        cid = cid_match.group(1)
        
        sys_blocks = re.split(r'\n(?=### System (?:Alpha|Beta|Gamma|Delta))', cb)
        case_header = sys_blocks[0]
        output_sys = [case_header]
        
        for sb in sys_blocks[1:]:
            sname = re.search(r'### (System (?:Alpha|Beta|Gamma|Delta))', sb).group(1)
            key = (cid, sname)
            if key not in evals:
                print(f"Missing evaluation for {key}")
                output_sys.append(sb)
                continue
            
            ev = evals[key]
            
            # Replace Gate A
            # Pattern: - [ ] Assessable Content Present  [ ] Cannot Assess (empty/noise)  [ ] No Usable Response (refusal)
            if ev["gate"] == "Assessable Content Present":
                sb = re.sub(
                    r'- \[ \] Assessable Content Present\s+\[ \] Cannot Assess \(empty/noise\)\s+\[ \] No Usable Response \(refusal\)',
                    '- [x] Assessable Content Present  [ ] Cannot Assess (empty/noise)  [ ] No Usable Response (refusal)',
                    sb
                )
            elif ev["gate"] == "Cannot Assess":
                sb = re.sub(
                    r'- \[ \] Assessable Content Present\s+\[ \] Cannot Assess \(empty/noise\)\s+\[ \] No Usable Response \(refusal\)',
                    '- [ ] Assessable Content Present  [x] Cannot Assess (empty/noise)  [ ] No Usable Response (refusal)',
                    sb
                )
            elif ev["gate"] == "No Usable Response":
                sb = re.sub(
                    r'- \[ \] Assessable Content Present\s+\[ \] Cannot Assess \(empty/noise\)\s+\[ \] No Usable Response \(refusal\)',
                    '- [ ] Assessable Content Present  [ ] Cannot Assess (empty/noise)  [x] No Usable Response (refusal)',
                    sb
                )
            
            # Replace Dim 1: Technical Correctness
            # 1. **Technical Correctness**: [ ] Pass (Correct)  [ ] Partial  [ ] Fail (Incorrect)  [ ] Cannot Assess
            d1_opts = {
                "Pass (Correct)": "1. **Technical Correctness**: [x] Pass (Correct)  [ ] Partial  [ ] Fail (Incorrect)  [ ] Cannot Assess",
                "Partial": "1. **Technical Correctness**: [ ] Pass (Correct)  [x] Partial  [ ] Fail (Incorrect)  [ ] Cannot Assess",
                "Fail (Incorrect)": "1. **Technical Correctness**: [ ] Pass (Correct)  [ ] Partial  [x] Fail (Incorrect)  [ ] Cannot Assess",
                "Cannot Assess": "1. **Technical Correctness**: [ ] Pass (Correct)  [ ] Partial  [ ] Fail (Incorrect)  [x] Cannot Assess"
            }
            sb = re.sub(
                r'1\.\s*\*\*Technical Correctness\*\*:[^\n]+',
                d1_opts[ev["d1"]],
                sb
            )
            
            # Replace Dim 2: Unsupported Claims
            # 2. **Unsupported Claims**: [ ] None  [ ] Minor  [ ] Severe  [ ] Cannot Assess
            d2_opts = {
                "None": "2. **Unsupported Claims**: [x] None  [ ] Minor  [ ] Severe  [ ] Cannot Assess",
                "Minor": "2. **Unsupported Claims**: [ ] None  [x] Minor  [ ] Severe  [ ] Cannot Assess",
                "Severe": "2. **Unsupported Claims**: [ ] None  [ ] Minor  [x] Severe  [ ] Cannot Assess",
                "Cannot Assess": "2. **Unsupported Claims**: [ ] None  [ ] Minor  [ ] Severe  [x] Cannot Assess"
            }
            sb = re.sub(
                r'2\.\s*\*\*Unsupported Claims\*\*:[^\n]+',
                d2_opts[ev["d2"]],
                sb
            )
            
            # Replace Dim 3: Appropriate Uncertainty
            # 3. **Appropriate Uncertainty**: [ ] Pass (Appropriate)  [ ] Overconfident  [ ] Cannot Assess
            d3_opts = {
                "Pass (Appropriate)": "3. **Appropriate Uncertainty**: [x] Pass (Appropriate)  [ ] Overconfident  [ ] Cannot Assess",
                "Overconfident": "3. **Appropriate Uncertainty**: [ ] Pass (Appropriate)  [x] Overconfident  [ ] Cannot Assess",
                "Cannot Assess": "3. **Appropriate Uncertainty**: [ ] Pass (Appropriate)  [ ] Overconfident  [x] Cannot Assess"
            }
            sb = re.sub(
                r'3\.\s*\*\*Appropriate Uncertainty\*\*:[^\n]+',
                d3_opts[ev["d3"]],
                sb
            )
            
            # Replace Dim 4: Actionable Repair Scope
            # 4. **Actionable Repair Scope**: [ ] Pass (Well-Scoped)  [ ] Vague  [ ] Harmful / Overbroad  [ ] Cannot Assess
            d4_opts = {
                "Pass (Well-Scoped)": "4. **Actionable Repair Scope**: [x] Pass (Well-Scoped)  [ ] Vague  [ ] Harmful / Overbroad  [ ] Cannot Assess",
                "Vague": "4. **Actionable Repair Scope**: [ ] Pass (Well-Scoped)  [x] Vague  [ ] Harmful / Overbroad  [ ] Cannot Assess",
                "Harmful / Overbroad": "4. **Actionable Repair Scope**: [ ] Pass (Well-Scoped)  [ ] Vague  [x] Harmful / Overbroad  [ ] Cannot Assess",
                "Cannot Assess": "4. **Actionable Repair Scope**: [ ] Pass (Well-Scoped)  [ ] Vague  [ ] Harmful / Overbroad  [x] Cannot Assess"
            }
            sb = re.sub(
                r'4\.\s*\*\*Actionable Repair Scope\*\*:[^\n]+',
                d4_opts[ev["d4"]],
                sb
            )
            
            # Replace Dim 5: Verification Steps Useful
            # 5. **Verification Steps Useful**: [ ] Pass (Useful & Safe)  [ ] Incomplete  [ ] Fail (Unsound)  [ ] Cannot Assess
            d5_opts = {
                "Pass (Useful & Safe)": "5. **Verification Steps Useful**: [x] Pass (Useful & Safe)  [ ] Incomplete  [ ] Fail (Unsound)  [ ] Cannot Assess",
                "Incomplete": "5. **Verification Steps Useful**: [ ] Pass (Useful & Safe)  [x] Incomplete  [ ] Fail (Unsound)  [ ] Cannot Assess",
                "Fail (Unsound)": "5. **Verification Steps Useful**: [ ] Pass (Useful & Safe)  [ ] Incomplete  [x] Fail (Unsound)  [ ] Cannot Assess",
                "Cannot Assess": "5. **Verification Steps Useful**: [ ] Pass (Useful & Safe)  [ ] Incomplete  [ ] Fail (Unsound)  [x] Cannot Assess"
            }
            sb = re.sub(
                r'5\.\s*\*\*Verification Steps Useful\*\*:[^\n]+',
                d5_opts[ev["d5"]],
                sb
            )
            
            # Replace Notes
            sb = re.sub(
                r'\*\*C\. Reviewer Notes, Alternative Diagnoses & Evidentiary Basis\*\*:\n_+',
                f"**C. Reviewer Notes, Alternative Diagnoses & Evidentiary Basis**:\n{ev['notes']}",
                sb
            )
            
            output_sys.append(sb)
        
        output_cases.append("".join(output_sys))
    
    return "".join(output_cases)

# Read batch 1, evaluate, write back
with open("docs/research/human_review/batch_01.md", "r", encoding="utf-8") as f:
    orig = f.read()

new_content = evaluate_batch_01(orig)
with open("docs/research/human_review/batch_01.md", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Batch 01 updated successfully.")

