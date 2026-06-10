"""End-to-end mock test of the customer judgement service."""
import sys
sys.path.insert(0, ".")

from app.core.security import CurrentUser
from app.schemas.customer_judgement_schema import CustomerJudgementRequest
from app.integrations.dify_client import DifyClient

# Test DifyClient mock end-to-end
client = DifyClient()
result = client.call_customer_judgement(
    customer_info_text="学员张三，25岁，北大计算机本科，GPA 3.5，托福100，意向美国硕士",
    sys_query="请研判该学员",
)
print("=== Dify Mock Result ===")
print(f"executive_summary: {result['executive_summary'][:60]}...")
print(f"is_target_customer: {result['is_target_customer']}")
print(f"overall_match_score: {result['overall_match_score']}")
print(f"overall_match_level: {result['overall_match_level']}")
print(f"customer_profile keys: {list(result['customer_profile'].keys())}")
print(f"product_a_evaluation.conclusion: {result['product_a_evaluation']['conclusion']}")
print(f"product_b_evaluation.conclusion: {result['product_b_evaluation']['conclusion']}")
print(f"final_next_steps count: {len(result['final_next_steps'])}")
print()

# Test schema validation
req = CustomerJudgementRequest(
    text="学员张三，25岁，北大计算机本科",
    sys_query="请研判",
    lead_id=1,
    target_product="美国硕士申请",
)
print(f"Schema validation OK: text={req.text[:20]}..., lead_id={req.lead_id}")

print("\nAll end-to-end tests passed!")
