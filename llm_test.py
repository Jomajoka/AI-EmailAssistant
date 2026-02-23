from app.services.agent_service import extract_email_intelligence

subject = "Project meeting on 2nd March from 4-5pm"
body = """
Hey Joel,

We will have a project sync meeting on 2nd March from 4-5 PM
to discuss AI integration. Please prepare the draft report before Friday.

Thanks.
"""

result = extract_email_intelligence(subject, body,"2026-02-23 14:32:00")

print(result)